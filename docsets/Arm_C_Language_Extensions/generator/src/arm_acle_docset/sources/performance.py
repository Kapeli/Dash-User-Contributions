"""Source-aware performance adapters for Arm instruction forms.

Performance data is inherently microarchitecture-specific.  This module does
not infer numbers from an intrinsic name and never treats an LLVM scheduling
model as a hardware measurement.  It accepts three explicit evidence classes:

``official``
    Values published by a processor vendor in a versioned source.
``measured``
    Reproducible measurements with hardware and methodology metadata.
``compiler_model``
    Estimates emitted by a pinned compiler scheduling model, such as
    ``llvm-mca``.

Every dataset is loaded through a small manifest that pins the data file by
SHA-256.  Normalized JSON and TSV datasets are supported in addition to raw
``llvm-mca --json --instruction-tables=full`` output.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import subprocess
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping, Sequence

from arm_acle_docset.model import (
    NumericRange,
    PerformanceConfidence,
    PerformanceEvidenceKind,
    PerformanceMetric,
    PerformanceRecord,
    Provenance,
    ProvenanceKind,
    SourceRef,
)


DataFormat = Literal["normalized-json", "normalized-tsv", "llvm-mca-json"]
MatchQuality = Literal["identity", "exact", "mnemonic_only"]
LLVMTargetABI = Literal["aarch32-ilp32", "aarch64-lp64"]

_ALLOWED_EVIDENCE_KINDS = {
    PerformanceEvidenceKind.OFFICIAL,
    PerformanceEvidenceKind.MEASURED,
    PerformanceEvidenceKind.COMPILER_MODEL,
}
_DATA_FORMATS: set[str] = {
    "normalized-json",
    "normalized-tsv",
    "llvm-mca-json",
}
_METRIC_RANGE_RE = re.compile(
    r"^\s*(?P<minimum>\d+(?:\.\d+)?)"
    r"(?:\s*(?:\.\.|-)\s*(?P<maximum>\d+(?:\.\d+)?))?\s*$"
)
_VERSION_RE = re.compile(r"\bversion\s+(?P<version>[^\s]+)", re.IGNORECASE)
_MNEMONIC_RE = re.compile(r"^(?P<mnemonic>[A-Za-z][A-Za-z0-9_.]*)\b")
_AARCH64_ARRANGEMENT_RE = re.compile(r"^(?P<base>.+)\.(?P<shape>\d+[bhsd])$")
_MNEMONIC_ALIASES: Mapping[str, str] = {
    # The MVE intrinsic database uses the element-width spelling while LLVM's
    # assembler printer retains the unsigned load alias.  These encode the
    # same base load instruction; no signed/unsigned arithmetic is involved.
    "vldrw.u32": "vldrw.32",
}
_ENCODING_LINE_RE = re.compile(
    r"^\s*(?P<assembly>.*?)\s*(?://|@)\s*encoding:\s*"
    r"\[(?P<encoding>[^\]]*)\]\s*$"
)
_MCINST_LINE_RE = re.compile(
    r"(?://|@)\s*<MCInst\s+#\d+\s+(?P<opcode>[A-Za-z0-9_.$-]+)"
)
_MCOPERAND_LINE_RE = re.compile(r"(?://|@)\s*<MCOperand\s+(?P<operand>.+?)(?:>>|>)\s*$")
_REGISTER_RE = re.compile(
    r"(?<![A-Za-z0-9_])"
    r"(?P<bank>za|zt|[rvqpzxwdsbh])"
    r"(?P<index>\d+|[dknamtgv][A-Za-z0-9]*)"
    r"(?P<shape>\.(?:\d+)?[bhsdq])?"
    r"(?P<pred>/[zmx])?"
    r"(?![A-Za-z0-9_])",
    re.IGNORECASE,
)
_SYMBOLIC_IMMEDIATE_RE = re.compile(
    r"#(?:imm[A-Za-z0-9_]*|[A-Za-z_][A-Za-z0-9_]*)",
    re.IGNORECASE,
)


class PerformanceFormatError(ValueError):
    """Raised when a performance manifest or data file is not trustworthy."""


class LLVMToolError(RuntimeError):
    """Raised when a pinned ``llvm-mca`` invocation cannot produce JSON."""


@dataclass(frozen=True, slots=True)
class LLVMModelProfile:
    """One reproducible LLVM 22.1.1 scheduling-model configuration."""

    display_name: str
    cpu: str
    march: str
    target_triple: str
    features: tuple[str, ...]
    model_complete: bool
    families: tuple[str, ...]
    notes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class LLVMRepresentativeProbe:
    """One reviewed ACLE instruction form backed by real assembler input.

    The mapping is deliberately explicit.  A probe may only publish a metric
    for ``documented_form`` after pinned ``llvm-mc`` proves that ``assembly``
    has the same normalized operand shape and emits a concrete opcode and
    encoding.  ``intrinsic_examples`` are explanatory examples; they are not
    used as a fuzzy join key.
    """

    id: str
    family: str
    documented_form: str
    assembly: str
    profiles: tuple[str, ...]
    intrinsic_examples: tuple[str, ...]
    note: str | None = None
    intrinsic_operand_width_bits: int | None = None

    def __post_init__(self) -> None:
        for value, field_name in (
            (self.id, "probe.id"),
            (self.family, "probe.family"),
            (self.documented_form, "probe.documented_form"),
            (self.assembly, "probe.assembly"),
        ):
            if not value.strip():
                raise PerformanceFormatError(f"{field_name} must be non-empty")
        if "\n" in self.assembly or ";" in self.assembly:
            raise PerformanceFormatError(
                f"probe {self.id!r} must contain exactly one assembly instruction"
            )
        if not self.profiles or len(set(self.profiles)) != len(self.profiles):
            raise PerformanceFormatError(
                f"probe {self.id!r} must name unique supported profiles"
            )
        if not self.intrinsic_examples or not all(
            example.strip() for example in self.intrinsic_examples
        ):
            raise PerformanceFormatError(
                f"probe {self.id!r} must name at least one intrinsic example"
            )
        if self.intrinsic_operand_width_bits is not None and (
            isinstance(self.intrinsic_operand_width_bits, bool)
            or self.intrinsic_operand_width_bits not in {8, 16, 32, 64}
        ):
            raise PerformanceFormatError(
                f"probe {self.id!r} intrinsic operand width must be 8, 16, 32, "
                "or 64 bits"
            )


LLVM_22_1_1_TAG = "llvmorg-22.1.1"
LLVM_22_1_1_COMMIT = "fef02d48c08db859ef83f84232ed78bd9d1c323a"
LLVM_22_1_1_AARCH64_SOURCE_REF = SourceRef(
    id="llvm-aarch64-schedule-model-22.1.1",
    repository="llvm/llvm-project",
    commit=LLVM_22_1_1_COMMIT,
    path="llvm/lib/Target/AArch64",
    license_id="Apache-2.0 WITH LLVM-exception",
    url=(
        "https://github.com/llvm/llvm-project/tree/"
        f"{LLVM_22_1_1_COMMIT}/llvm/lib/Target/AArch64"
    ),
)
LLVM_22_1_1_ARM_SOURCE_REF = SourceRef(
    id="llvm-arm-schedule-model-22.1.1",
    repository="llvm/llvm-project",
    commit=LLVM_22_1_1_COMMIT,
    path="llvm/lib/Target/ARM",
    license_id="Apache-2.0 WITH LLVM-exception",
    url=(
        "https://github.com/llvm/llvm-project/tree/"
        f"{LLVM_22_1_1_COMMIT}/llvm/lib/Target/ARM"
    ),
)

# Profiles deliberately describe model coverage, not hardware availability.
# A partial profile can still provide useful values, but every record carries a
# lower confidence and an explicit caveat.
LLVM_22_1_1_PROFILES: tuple[LLVMModelProfile, ...] = (
    LLVMModelProfile(
        "Cortex-A55",
        "cortex-a55",
        "aarch64",
        "aarch64-none-elf",
        ("+neon",),
        False,
        ("general", "neon"),
        ("LLVM marks this scheduling model incomplete and partly generic.",),
    ),
    LLVMModelProfile(
        "Neoverse N1",
        "neoverse-n1",
        "aarch64",
        "aarch64-none-elf",
        ("+neon",),
        True,
        ("general", "neon"),
    ),
    LLVMModelProfile(
        "Neoverse V1",
        "neoverse-v1",
        "aarch64",
        "aarch64-none-elf",
        ("+sve",),
        True,
        ("general", "neon", "sve"),
    ),
    LLVMModelProfile(
        "Neoverse N2",
        "neoverse-n2",
        "aarch64",
        "aarch64-none-elf",
        ("+sve2",),
        True,
        ("general", "neon", "sve", "sve2"),
    ),
    LLVMModelProfile(
        "Cortex-M55",
        "cortex-m55",
        "arm",
        "arm-none-eabi",
        ("+mve", "+mve.fp"),
        False,
        ("general", "mve"),
        ("LLVM marks the overall model incomplete; MVE pipelines are modelled.",),
    ),
    LLVMModelProfile(
        "Cortex-M85",
        "cortex-m85",
        "arm",
        "arm-none-eabi",
        ("+mve", "+mve.fp"),
        False,
        ("general", "mve"),
        ("LLVM marks this scheduling model incomplete.",),
    ),
)

_AARCH64_PROFILES = (
    "cortex-a55",
    "neoverse-n1",
    "neoverse-v1",
    "neoverse-n2",
)
_SVE_PROFILES = ("neoverse-v1", "neoverse-n2")
_MVE_PROFILES = ("cortex-m55", "cortex-m85")

# This is a reviewed representative set, not an assertion that one metric
# describes every intrinsic with the same mnemonic.  Each entry retains its
# exact operand shape and is checked with llvm-mc before llvm-mca values are
# exposed to the canonical catalog.
LLVM_22_1_1_REPRESENTATIVE_PROBES: tuple[LLVMRepresentativeProbe, ...] = (
    LLVMRepresentativeProbe(
        "a64-rbit-w",
        "general",
        "RBIT Wd, Wn",
        "rbit w0, w1",
        _AARCH64_PROFILES,
        ("__rbit",),
        intrinsic_operand_width_bits=32,
    ),
    LLVMRepresentativeProbe(
        "a64-rbit-x",
        "general",
        "RBIT Xd, Xn",
        "rbit x0, x1",
        _AARCH64_PROFILES,
        ("__rbitl", "__rbitll"),
        intrinsic_operand_width_bits=64,
    ),
    LLVMRepresentativeProbe(
        "a64-clz-w",
        "general",
        "CLZ Wd, Wn",
        "clz w0, w1",
        _AARCH64_PROFILES,
        ("__clz",),
        intrinsic_operand_width_bits=32,
    ),
    LLVMRepresentativeProbe(
        "a64-clz-x",
        "general",
        "CLZ Xd, Xn",
        "clz x0, x1",
        _AARCH64_PROFILES,
        ("__clzl", "__clzll"),
        intrinsic_operand_width_bits=64,
    ),
    LLVMRepresentativeProbe(
        "a64-rev-w",
        "general",
        "REV Wd, Wn",
        "rev w0, w1",
        _AARCH64_PROFILES,
        ("__rev",),
        intrinsic_operand_width_bits=32,
    ),
    LLVMRepresentativeProbe(
        "a64-rev16-w",
        "general",
        "REV16 Wd, Wn",
        "rev16 w0, w1",
        _AARCH64_PROFILES,
        ("__rev16",),
        intrinsic_operand_width_bits=32,
    ),
    LLVMRepresentativeProbe(
        "a64-rev16-x",
        "general",
        "REV16 Xd, Xn",
        "rev16 x0, x1",
        _AARCH64_PROFILES,
        ("__rev16l", "__rev16ll"),
        intrinsic_operand_width_bits=64,
    ),
    LLVMRepresentativeProbe(
        "a64-crc32w",
        "general",
        "CRC32W Wd, Wn, Wm",
        "crc32w w0, w1, w2",
        _AARCH64_PROFILES,
        ("__crc32w",),
        "Requires the CRC extension; availability remains sourced from ACLE.",
    ),
    LLVMRepresentativeProbe(
        "neon-add-4s",
        "neon",
        "ADD Vd.4S, Vn.4S, Vm.4S",
        "add v0.4s, v1.4s, v2.4s",
        _AARCH64_PROFILES,
        ("vaddq_s32", "vaddq_u32"),
    ),
    LLVMRepresentativeProbe(
        "neon-fadd-4s",
        "neon",
        "FADD Vd.4S, Vn.4S, Vm.4S",
        "fadd v0.4s, v1.4s, v2.4s",
        _AARCH64_PROFILES,
        ("vaddq_f32",),
    ),
    LLVMRepresentativeProbe(
        "neon-sub-4s",
        "neon",
        "SUB Vd.4S, Vn.4S, Vm.4S",
        "sub v0.4s, v1.4s, v2.4s",
        _AARCH64_PROFILES,
        ("vsubq_s32", "vsubq_u32"),
    ),
    LLVMRepresentativeProbe(
        "neon-fsub-4s",
        "neon",
        "FSUB Vd.4S, Vn.4S, Vm.4S",
        "fsub v0.4s, v1.4s, v2.4s",
        _AARCH64_PROFILES,
        ("vsubq_f32",),
    ),
    LLVMRepresentativeProbe(
        "neon-and-16b",
        "neon",
        "AND Vd.16B, Vn.16B, Vm.16B",
        "and v0.16b, v1.16b, v2.16b",
        _AARCH64_PROFILES,
        (
            "vandq_s8",
            "vandq_s16",
            "vandq_s32",
            "vandq_s64",
            "vandq_u8",
            "vandq_u16",
            "vandq_u32",
            "vandq_u64",
        ),
    ),
    LLVMRepresentativeProbe(
        "neon-eor-16b",
        "neon",
        "EOR Vd.16B, Vn.16B, Vm.16B",
        "eor v0.16b, v1.16b, v2.16b",
        _AARCH64_PROFILES,
        (
            "veorq_s8",
            "veorq_s16",
            "veorq_s32",
            "veorq_s64",
            "veorq_u8",
            "veorq_u16",
            "veorq_u32",
            "veorq_u64",
        ),
    ),
    LLVMRepresentativeProbe(
        "neon-smax-4s",
        "neon",
        "SMAX Vd.4S, Vn.4S, Vm.4S",
        "smax v0.4s, v1.4s, v2.4s",
        _AARCH64_PROFILES,
        ("vmaxq_s32",),
    ),
    LLVMRepresentativeProbe(
        "neon-umax-4s",
        "neon",
        "UMAX Vd.4S, Vn.4S, Vm.4S",
        "umax v0.4s, v1.4s, v2.4s",
        _AARCH64_PROFILES,
        ("vmaxq_u32",),
    ),
    LLVMRepresentativeProbe(
        "neon-smin-4s",
        "neon",
        "SMIN Vd.4S, Vn.4S, Vm.4S",
        "smin v0.4s, v1.4s, v2.4s",
        _AARCH64_PROFILES,
        ("vminq_s32",),
    ),
    LLVMRepresentativeProbe(
        "neon-umin-4s",
        "neon",
        "UMIN Vd.4S, Vn.4S, Vm.4S",
        "umin v0.4s, v1.4s, v2.4s",
        _AARCH64_PROFILES,
        ("vminq_u32",),
    ),
    LLVMRepresentativeProbe(
        "neon-mul-4s",
        "neon",
        "MUL Vd.4S, Vn.4S, Vm.4S",
        "mul v0.4s, v1.4s, v2.4s",
        _AARCH64_PROFILES,
        ("vmulq_s32", "vmulq_u32"),
    ),
    LLVMRepresentativeProbe(
        "neon-fmla-4s",
        "neon",
        "FMLA Vd.4S, Vn.4S, Vm.4S",
        "fmla v0.4s, v1.4s, v2.4s",
        _AARCH64_PROFILES,
        ("vfmaq_f32",),
    ),
    LLVMRepresentativeProbe(
        "neon-sqrdmulh-4s",
        "neon",
        "SQRDMULH Vd.4S, Vn.4S, Vm.4S",
        "sqrdmulh v0.4s, v1.4s, v2.4s",
        _AARCH64_PROFILES,
        ("vqrdmulhq_s32",),
    ),
    LLVMRepresentativeProbe(
        "neon-ld1-16b",
        "neon",
        "LD1 {Vt.16B}, [Xn]",
        "ld1 {v0.16b}, [x0]",
        _AARCH64_PROFILES,
        ("vld1q_u8", "vld1q_s8"),
    ),
    LLVMRepresentativeProbe(
        "neon-st1-16b",
        "neon",
        "ST1 {Vt.16B}, [Xn]",
        "st1 {v0.16b}, [x0]",
        _AARCH64_PROFILES,
        ("vst1q_u8", "vst1q_s8"),
    ),
    LLVMRepresentativeProbe(
        "neon-tbl-16b",
        "neon",
        "TBL Vd.16B, {Vn.16B}, Vm.16B",
        "tbl v0.16b, {v1.16b}, v2.16b",
        _AARCH64_PROFILES,
        ("vqtbl1q_u8", "vqtbl1q_s8"),
    ),
    LLVMRepresentativeProbe(
        "sve-add-s-predicated",
        "sve",
        "ADD Zdn.S, Pg/M, Zdn.S, Zm.S",
        "add z0.s, p0/m, z0.s, z1.s",
        _SVE_PROFILES,
        ("svadd_s32_x", "svadd_u32_x"),
    ),
    LLVMRepresentativeProbe(
        "sve-fadd-s-predicated",
        "sve",
        "FADD Zdn.S, Pg/M, Zdn.S, Zm.S",
        "fadd z0.s, p0/m, z0.s, z1.s",
        _SVE_PROFILES,
        ("svadd_f32_x",),
    ),
    LLVMRepresentativeProbe(
        "sve-sub-s-predicated",
        "sve",
        "SUB Zdn.S, Pg/M, Zdn.S, Zm.S",
        "sub z0.s, p0/m, z0.s, z1.s",
        _SVE_PROFILES,
        ("svsub_s32_x", "svsub_u32_x"),
    ),
    LLVMRepresentativeProbe(
        "sve-fsub-s-predicated",
        "sve",
        "FSUB Zdn.S, Pg/M, Zdn.S, Zm.S",
        "fsub z0.s, p0/m, z0.s, z1.s",
        _SVE_PROFILES,
        ("svsub_f32_x",),
    ),
    LLVMRepresentativeProbe(
        "sve-mul-s-predicated",
        "sve",
        "MUL Zdn.S, Pg/M, Zdn.S, Zm.S",
        "mul z0.s, p0/m, z0.s, z1.s",
        _SVE_PROFILES,
        ("svmul_s32_x", "svmul_u32_x"),
    ),
    LLVMRepresentativeProbe(
        "sve-fmul-s-predicated",
        "sve",
        "FMUL Zdn.S, Pg/M, Zdn.S, Zm.S",
        "fmul z0.s, p0/m, z0.s, z1.s",
        _SVE_PROFILES,
        ("svmul_f32_x",),
    ),
    LLVMRepresentativeProbe(
        "sve-and-s-predicated",
        "sve",
        "AND Zdn.S, Pg/M, Zdn.S, Zm.S",
        "and z0.s, p0/m, z0.s, z1.s",
        _SVE_PROFILES,
        ("svand_s32_x", "svand_u32_x"),
    ),
    LLVMRepresentativeProbe(
        "sve-eor-s-predicated",
        "sve",
        "EOR Zdn.S, Pg/M, Zdn.S, Zm.S",
        "eor z0.s, p0/m, z0.s, z1.s",
        _SVE_PROFILES,
        ("sveor_s32_x", "sveor_u32_x"),
    ),
    LLVMRepresentativeProbe(
        "sve-fmla-s-predicated",
        "sve",
        "FMLA Zda.S, Pg/M, Zn.S, Zm.S",
        "fmla z0.s, p0/m, z1.s, z2.s",
        _SVE_PROFILES,
        ("svmla_f32_x",),
    ),
    LLVMRepresentativeProbe(
        "sve-ld1w-s",
        "sve",
        "LD1W {Zt.S}, Pg/Z, [Xn]",
        "ld1w {z0.s}, p0/z, [x0]",
        _SVE_PROFILES,
        ("svld1_s32", "svld1_u32"),
    ),
    LLVMRepresentativeProbe(
        "sve-st1w-s",
        "sve",
        "ST1W {Zt.S}, Pg, [Xn]",
        "st1w {z0.s}, p0, [x0]",
        _SVE_PROFILES,
        ("svst1_s32", "svst1_u32"),
    ),
    LLVMRepresentativeProbe(
        "sve-whilelt-s",
        "sve",
        "WHILELT Pd.S, Xn, Xm",
        "whilelt p0.s, x0, x1",
        _SVE_PROFILES,
        ("svwhilelt_b32_s64", "svwhilelt_b32_u64"),
    ),
    LLVMRepresentativeProbe(
        "sve-ptrue-s",
        "sve",
        "PTRUE Pd.S",
        "ptrue p0.s",
        _SVE_PROFILES,
        ("svptrue_b32",),
    ),
    LLVMRepresentativeProbe(
        "sve2-eor3-d",
        "sve2",
        "EOR3 Zdn.D, Zdn.D, Zm.D, Zk.D",
        "eor3 z0.d, z0.d, z1.d, z2.d",
        ("neoverse-n2",),
        ("sveor3_u64",),
    ),
    LLVMRepresentativeProbe(
        "sve2-sqrdmulh-s",
        "sve2",
        "SQRDMULH Zd.S, Zn.S, Zm.S",
        "sqrdmulh z0.s, z1.s, z2.s",
        ("neoverse-n2",),
        ("svqrdmulh_s32",),
    ),
    LLVMRepresentativeProbe(
        "mve-rbit",
        "general",
        "RBIT Rd, Rn",
        "rbit r0, r1",
        _MVE_PROFILES,
        ("__rbit", "__rbitl"),
        intrinsic_operand_width_bits=32,
    ),
    LLVMRepresentativeProbe(
        "mve-clz",
        "general",
        "CLZ Rd, Rn",
        "clz r0, r1",
        _MVE_PROFILES,
        ("__clz", "__clzl"),
        intrinsic_operand_width_bits=32,
    ),
    LLVMRepresentativeProbe(
        "mve-rev",
        "general",
        "REV Rd, Rn",
        "rev r0, r1",
        _MVE_PROFILES,
        ("__rev",),
        intrinsic_operand_width_bits=32,
    ),
    LLVMRepresentativeProbe(
        "mve-rev16",
        "general",
        "REV16 Rd, Rn",
        "rev16 r0, r1",
        _MVE_PROFILES,
        ("__rev16", "__rev16l"),
        intrinsic_operand_width_bits=32,
    ),
    LLVMRepresentativeProbe(
        "mve-add-i32",
        "mve",
        "VADD.I32 Qd, Qn, Qm",
        "vadd.i32 q0, q1, q2",
        _MVE_PROFILES,
        ("vaddq_s32", "vaddq_u32"),
    ),
    LLVMRepresentativeProbe(
        "mve-add-f32",
        "mve",
        "VADD.F32 Qd, Qn, Qm",
        "vadd.f32 q0, q1, q2",
        _MVE_PROFILES,
        ("vaddq_f32",),
    ),
    LLVMRepresentativeProbe(
        "mve-sub-i32",
        "mve",
        "VSUB.I32 Qd, Qn, Qm",
        "vsub.i32 q0, q1, q2",
        _MVE_PROFILES,
        ("vsubq_s32", "vsubq_u32"),
    ),
    LLVMRepresentativeProbe(
        "mve-sub-f32",
        "mve",
        "VSUB.F32 Qd, Qn, Qm",
        "vsub.f32 q0, q1, q2",
        _MVE_PROFILES,
        ("vsubq_f32",),
    ),
    LLVMRepresentativeProbe(
        "mve-and",
        "mve",
        "VAND Qd, Qn, Qm",
        "vand q0, q1, q2",
        _MVE_PROFILES,
        (
            "vandq_s8",
            "vandq_s16",
            "vandq_s32",
            "vandq_s64",
            "vandq_u8",
            "vandq_u16",
            "vandq_u32",
            "vandq_u64",
        ),
    ),
    LLVMRepresentativeProbe(
        "mve-eor",
        "mve",
        "VEOR Qd, Qn, Qm",
        "veor q0, q1, q2",
        _MVE_PROFILES,
        (
            "veorq_s8",
            "veorq_s16",
            "veorq_s32",
            "veorq_s64",
            "veorq_u8",
            "veorq_u16",
            "veorq_u32",
            "veorq_u64",
        ),
    ),
    LLVMRepresentativeProbe(
        "mve-max-s32",
        "mve",
        "VMAX.S32 Qd, Qn, Qm",
        "vmax.s32 q0, q1, q2",
        _MVE_PROFILES,
        ("vmaxq_s32",),
    ),
    LLVMRepresentativeProbe(
        "mve-max-u32",
        "mve",
        "VMAX.U32 Qd, Qn, Qm",
        "vmax.u32 q0, q1, q2",
        _MVE_PROFILES,
        ("vmaxq_u32",),
    ),
    LLVMRepresentativeProbe(
        "mve-min-s32",
        "mve",
        "VMIN.S32 Qd, Qn, Qm",
        "vmin.s32 q0, q1, q2",
        _MVE_PROFILES,
        ("vminq_s32",),
    ),
    LLVMRepresentativeProbe(
        "mve-min-u32",
        "mve",
        "VMIN.U32 Qd, Qn, Qm",
        "vmin.u32 q0, q1, q2",
        _MVE_PROFILES,
        ("vminq_u32",),
    ),
    LLVMRepresentativeProbe(
        "mve-mul-i32",
        "mve",
        "VMUL.I32 Qd, Qn, Qm",
        "vmul.i32 q0, q1, q2",
        _MVE_PROFILES,
        ("vmulq_s32", "vmulq_u32"),
    ),
    LLVMRepresentativeProbe(
        "mve-vfma-f32",
        "mve",
        "VFMA.F32 Qda, Qn, Qm",
        "vfma.f32 q0, q1, q2",
        _MVE_PROFILES,
        ("vfmaq_f32",),
    ),
    LLVMRepresentativeProbe(
        "mve-vqrdmulh-s32",
        "mve",
        "VQRDMULH.S32 Qd, Qn, Qm",
        "vqrdmulh.s32 q0, q1, q2",
        _MVE_PROFILES,
        ("vqrdmulhq_s32",),
    ),
    LLVMRepresentativeProbe(
        "mve-vldrw-32",
        "mve",
        "VLDRW.32 Qd, [Rn]",
        "vldrw.u32 q0, [r0]",
        _MVE_PROFILES,
        ("vld1q_u32", "vld1q_s32", "vld1q_f32"),
    ),
    LLVMRepresentativeProbe(
        "mve-vstrw-32",
        "mve",
        "VSTRW.32 Qd, [Rn]",
        "vstrw.32 q0, [r0]",
        _MVE_PROFILES,
        ("vstrwq_u32", "vstrwq_s32"),
    ),
)

LLVM_22_1_1_UNAVAILABLE_FAMILIES: Mapping[str, str] = {
    "sme": (
        "LLVM 22.1.1 does not provide an applicable CPU scheduling model for "
        "SME; no performance number is published."
    ),
    "sme2": (
        "LLVM 22.1.1 does not provide an applicable CPU scheduling model for "
        "SME2; no performance number is published."
    ),
}

LLVM_22_1_1_NO_EXACT_FORM_REASON = (
    "No exact, assembler-validated representative instruction form is present "
    "in the LLVM 22.1.1 performance probe set; no value was inferred from a "
    "mnemonic, ISA availability, or another intrinsic."
)


@dataclass(frozen=True, slots=True)
class PerformanceSource:
    """Dataset-wide evidence metadata and its canonical provenance."""

    evidence_kind: PerformanceEvidenceKind
    name: str
    version: str
    source_ref: SourceRef
    tool_name: str | None = None
    tool_version: str | None = None
    tool_commit: str | None = None
    methodology: str | None = None
    hardware: str | None = None
    sample_count: int | None = None
    confidence: PerformanceConfidence = PerformanceConfidence.MEDIUM
    notes: tuple[str, ...] = ()
    raw_data_sha256: str | None = None

    def __post_init__(self) -> None:
        for value, field_name in (
            (self.name, "source.name"),
            (self.version, "source.version"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise PerformanceFormatError(f"{field_name} must be non-empty")

        if self.evidence_kind not in _ALLOWED_EVIDENCE_KINDS:
            raise PerformanceFormatError(
                "source.evidence_kind must be official, measured, or compiler_model"
            )
        if self.evidence_kind is PerformanceEvidenceKind.MEASURED:
            if not self.methodology or not self.hardware:
                raise PerformanceFormatError(
                    "measured data requires source.methodology and source.hardware"
                )
            if self.sample_count is None or self.sample_count < 1:
                raise PerformanceFormatError(
                    "measured data requires a positive source.sample_count"
                )
        if self.evidence_kind is PerformanceEvidenceKind.COMPILER_MODEL:
            if not self.tool_name or not self.tool_version:
                raise PerformanceFormatError(
                    "compiler_model data requires source.tool.name and source.tool.version"
                )
            if self.confidence is PerformanceConfidence.HIGH:
                raise PerformanceFormatError(
                    "compiler_model confidence cannot be high because it is not a "
                    "hardware measurement"
                )

        if self.raw_data_sha256 is not None and not re.fullmatch(
            r"[0-9a-f]{64}", self.raw_data_sha256
        ):
            raise PerformanceFormatError("raw_data_sha256 must be lowercase SHA-256")

    @property
    def provenance(self) -> Provenance:
        qualifiers = [
            f"evidence_kind={self.evidence_kind.value}",
            f"source={self.name} {self.version}",
        ]
        if self.tool_name and self.tool_version:
            qualifiers.append(f"tool={self.tool_name} {self.tool_version}")
        if self.tool_commit:
            qualifiers.append(f"tool_commit={self.tool_commit}")
        if self.raw_data_sha256:
            qualifiers.append(f"data_sha256={self.raw_data_sha256}")
        return Provenance(
            kind=ProvenanceKind.EXPLICIT,
            sources=(self.source_ref,),
            note="; ".join(qualifiers),
        )


@dataclass(frozen=True, slots=True)
class PerformanceManifest:
    """Validated description of one pinned performance data file."""

    schema_version: int
    data_file: str
    data_format: DataFormat
    sha256: str
    architecture: str
    microarchitecture: str | None
    cpu: str | None
    target_triple: str | None
    features: tuple[str, ...]
    model_complete: bool | None
    source: PerformanceSource


@dataclass(frozen=True, slots=True)
class PerformanceDataset:
    """Canonical records plus the manifest that established their provenance."""

    manifest: PerformanceManifest
    records: tuple[PerformanceRecord, ...]
    llvm_identities: tuple[LLVMInstructionIdentity, ...] = ()

    def __post_init__(self) -> None:
        if self.llvm_identities and len(self.llvm_identities) != len(self.records):
            raise PerformanceFormatError(
                "LLVM identity count must match performance record count"
            )


@dataclass(frozen=True, slots=True)
class LLVMInstructionIdentity:
    """Strong identity emitted by pinned ``llvm-mc`` tooling.

    Textual mnemonic matching is insufficient for forms whose scheduling class
    depends on operands or immediates.  A strong key therefore includes target
    scope, LLVM opcode, canonical MC operands, and exact encoding.
    """

    target_triple: str
    cpu: str
    features: tuple[str, ...]
    canonical_asm: str
    llvm_opcode: str
    encoding: tuple[int, ...]
    mc_operands: tuple[str, ...]

    @property
    def key(self) -> tuple[object, ...]:
        return (
            self.target_triple,
            self.cpu,
            self.features,
            self.llvm_opcode,
            self.mc_operands,
            self.encoding,
        )


@dataclass(frozen=True, slots=True)
class InstructionForm:
    """A conservative instruction-form key used for performance joins."""

    raw: str
    mnemonic: str
    operands: tuple[str, ...]

    @property
    def canonical(self) -> str:
        if not self.operands:
            return self.mnemonic
        return f"{self.mnemonic} {','.join(self.operands)}"


@dataclass(frozen=True, slots=True)
class PerformanceMatch:
    """A record match with an explicit indication of match precision."""

    record: PerformanceRecord
    quality: MatchQuality


def load_performance_manifest(path: Path) -> PerformanceDataset:
    """Load a SHA-pinned JSON manifest and its adjacent data file."""

    manifest_path = path.resolve()
    try:
        manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PerformanceFormatError(f"cannot read manifest {path}: {error}") from error
    if not isinstance(manifest_payload, Mapping):
        raise PerformanceFormatError("manifest root must be a JSON object")

    manifest = parse_performance_manifest(manifest_payload)
    data_path = _resolve_adjacent_data_path(manifest_path, manifest.data_file)
    try:
        data = data_path.read_bytes()
    except OSError as error:
        raise PerformanceFormatError(
            f"cannot read data file {data_path}: {error}"
        ) from error
    digest = hashlib.sha256(data).hexdigest()
    if digest != manifest.sha256:
        raise PerformanceFormatError(
            f"SHA-256 mismatch for {data_path.name}: expected {manifest.sha256}, "
            f"found {digest}"
        )

    source = replace(manifest.source, raw_data_sha256=digest)
    manifest = replace(manifest, source=source)
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise PerformanceFormatError(f"data file {data_path} is not UTF-8") from error

    if manifest.data_format == "llvm-mca-json":
        records = parse_llvm_mca_json(text, manifest=manifest)
    elif manifest.data_format == "normalized-json":
        records = parse_normalized_json(text, manifest=manifest)
    else:
        records = parse_normalized_tsv(text.splitlines(), manifest=manifest)
    return PerformanceDataset(manifest=manifest, records=records)


def parse_performance_manifest(payload: Mapping[str, Any]) -> PerformanceManifest:
    """Validate manifest primitives without accessing the filesystem."""

    schema_version = payload.get("schema_version")
    if schema_version != 1:
        raise PerformanceFormatError("manifest.schema_version must be 1")

    data = _require_mapping(payload.get("data"), "manifest.data")
    data_file = _require_text(data.get("file"), "manifest.data.file")
    data_format = _require_text(data.get("format"), "manifest.data.format")
    if data_format not in _DATA_FORMATS:
        raise PerformanceFormatError(
            f"manifest.data.format must be one of {sorted(_DATA_FORMATS)}"
        )
    sha256 = _require_text(data.get("sha256"), "manifest.data.sha256").lower()
    if not re.fullmatch(r"[0-9a-f]{64}", sha256):
        raise PerformanceFormatError("manifest.data.sha256 must be a SHA-256 digest")

    architecture = _require_text(payload.get("architecture"), "manifest.architecture")
    microarchitecture = _optional_text(payload.get("microarchitecture"))
    cpu = _optional_text(payload.get("cpu"))
    target_triple = _optional_text(payload.get("target_triple"))
    features_payload = payload.get("features", [])
    if not isinstance(features_payload, list) or not all(
        isinstance(feature, str) and feature.strip() for feature in features_payload
    ):
        raise PerformanceFormatError("manifest.features must be non-empty strings")
    features = tuple(feature.strip() for feature in features_payload)
    model_complete = payload.get("model_complete")
    if model_complete is not None and not isinstance(model_complete, bool):
        raise PerformanceFormatError("manifest.model_complete must be boolean or null")
    source = _parse_source(_require_mapping(payload.get("source"), "manifest.source"))
    if data_format == "llvm-mca-json":
        if source.evidence_kind is not PerformanceEvidenceKind.COMPILER_MODEL:
            raise PerformanceFormatError(
                "llvm-mca-json data must use compiler_model evidence"
            )
        if not microarchitecture or not cpu:
            raise PerformanceFormatError(
                "llvm-mca-json requires manifest.microarchitecture and manifest.cpu"
            )

    return PerformanceManifest(
        schema_version=schema_version,
        data_file=data_file,
        data_format=data_format,  # type: ignore[arg-type]
        sha256=sha256,
        architecture=architecture,
        microarchitecture=microarchitecture,
        cpu=cpu,
        target_triple=target_triple,
        features=features,
        model_complete=model_complete,
        source=source,
    )


def parse_normalized_json(
    text: str,
    *,
    manifest: PerformanceManifest,
) -> tuple[PerformanceRecord, ...]:
    """Parse canonical JSON records governed by ``manifest``."""

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        raise PerformanceFormatError(f"invalid normalized JSON: {error}") from error
    if isinstance(payload, Mapping):
        payload = payload.get("records")
    if not isinstance(payload, list):
        raise PerformanceFormatError(
            "normalized JSON must be an array or an object with a records array"
        )
    records = [
        _parse_normalized_record(
            _require_mapping(record, f"records[{index}]"),
            manifest=manifest,
            location=f"records[{index}]",
        )
        for index, record in enumerate(payload)
    ]
    return tuple(records)


def parse_normalized_tsv(
    lines: Iterable[str],
    *,
    manifest: PerformanceManifest,
) -> tuple[PerformanceRecord, ...]:
    """Parse canonical TSV records governed by ``manifest``."""

    reader = csv.DictReader(lines, delimiter="\t")
    required_columns = {
        "instruction_form",
        "latency",
        "reciprocal_throughput",
        "uops",
        "resources",
    }
    if reader.fieldnames is None:
        raise PerformanceFormatError("normalized TSV is missing a header")
    missing = sorted(required_columns.difference(reader.fieldnames))
    if missing:
        raise PerformanceFormatError(
            f"normalized TSV is missing required columns: {', '.join(missing)}"
        )

    records: list[PerformanceRecord] = []
    for line_number, row in enumerate(reader, start=2):
        records.append(
            _parse_normalized_record(
                row,
                manifest=manifest,
                location=f"TSV line {line_number}",
            )
        )
    return tuple(records)


def parse_llvm_mca_json(
    payload: str | Mapping[str, Any],
    *,
    manifest: PerformanceManifest,
) -> tuple[PerformanceRecord, ...]:
    """Convert raw ``llvm-mca`` JSON into canonical performance records.

    LLVM's values describe its scheduling model.  They are tagged as
    ``compiler_model`` and must not be relabelled as measured or official data.
    """

    if manifest.source.evidence_kind is not PerformanceEvidenceKind.COMPILER_MODEL:
        raise PerformanceFormatError("llvm-mca output requires compiler_model evidence")
    if isinstance(payload, str):
        try:
            decoded = json.loads(payload)
        except json.JSONDecodeError as error:
            raise PerformanceFormatError(f"invalid llvm-mca JSON: {error}") from error
    else:
        decoded = payload
    root = _require_mapping(decoded, "llvm-mca root")

    simulation = _require_mapping(
        root.get("SimulationParameters"), "llvm-mca SimulationParameters"
    )
    actual_cpu = _optional_text(simulation.get("-mcpu"))
    actual_arch = _optional_text(simulation.get("-march"))
    actual_triple = _optional_text(simulation.get("-mtriple"))
    if manifest.cpu and actual_cpu and actual_cpu != manifest.cpu:
        raise PerformanceFormatError(
            f"llvm-mca CPU mismatch: manifest has {manifest.cpu!r}, output has "
            f"{actual_cpu!r}"
        )
    if actual_arch and actual_arch.casefold() != manifest.architecture.casefold():
        raise PerformanceFormatError(
            f"llvm-mca architecture mismatch: manifest has {manifest.architecture!r}, "
            f"output has {actual_arch!r}"
        )
    if (
        manifest.target_triple
        and actual_triple
        and actual_triple.casefold() != manifest.target_triple.casefold()
    ):
        raise PerformanceFormatError(
            f"llvm-mca target triple mismatch: manifest has "
            f"{manifest.target_triple!r}, output has {actual_triple!r}"
        )

    target = _require_mapping(root.get("TargetInfo"), "llvm-mca TargetInfo")
    target_cpu = _optional_text(target.get("CPUName"))
    if manifest.cpu and target_cpu and target_cpu != manifest.cpu:
        raise PerformanceFormatError(
            f"llvm-mca TargetInfo CPU mismatch: manifest has {manifest.cpu!r}, "
            f"output has {target_cpu!r}"
        )
    resources_payload = target.get("Resources")
    if not isinstance(resources_payload, list) or not all(
        isinstance(resource, str) for resource in resources_payload
    ):
        raise PerformanceFormatError("llvm-mca TargetInfo.Resources must be strings")
    resource_names = tuple(_sanitize_resource_name(name) for name in resources_payload)

    regions = root.get("CodeRegions")
    if not isinstance(regions, list):
        raise PerformanceFormatError("llvm-mca CodeRegions must be an array")

    provenance = _record_provenance(manifest)
    record_confidence = _record_confidence(manifest)
    metric_note = "LLVM scheduling model estimate; not measured hardware behavior."
    records: list[PerformanceRecord] = []
    for region_index, region_payload in enumerate(regions):
        region = _require_mapping(region_payload, f"CodeRegions[{region_index}]")
        instructions = region.get("Instructions")
        if not isinstance(instructions, list) or not all(
            isinstance(instruction, str) for instruction in instructions
        ):
            raise PerformanceFormatError(
                f"CodeRegions[{region_index}].Instructions must be strings"
            )
        info_view = _require_mapping(
            region.get("InstructionInfoView"),
            f"CodeRegions[{region_index}].InstructionInfoView",
        )
        info_list = info_view.get("InstructionList")
        if not isinstance(info_list, list):
            raise PerformanceFormatError(
                f"CodeRegions[{region_index}].InstructionList must be an array"
            )
        pressure_by_instruction = _llvm_resource_pressure(
            region,
            instruction_count=len(instructions),
            resource_names=resource_names,
            location=f"CodeRegions[{region_index}]",
        )

        for info_position, info_payload in enumerate(info_list):
            info = _require_mapping(
                info_payload,
                f"CodeRegions[{region_index}].InstructionList[{info_position}]",
            )
            instruction_index = info.get("Instruction")
            if (
                isinstance(instruction_index, bool)
                or not isinstance(instruction_index, int)
                or instruction_index < 0
                or instruction_index >= len(instructions)
            ):
                raise PerformanceFormatError(
                    f"invalid llvm-mca instruction index {instruction_index!r}"
                )
            notes = list(manifest.source.notes)
            notes.append(metric_note)
            notes.append(_profile_note(manifest))
            if info.get("hasUnmodeledSideEffects") is True:
                notes.append("LLVM reports unmodelled side effects for this form.")
            if info.get("mayLoad") is True:
                notes.append("Instruction may load memory.")
            if info.get("mayStore") is True:
                notes.append("Instruction may store memory.")

            resource_values = pressure_by_instruction.get(instruction_index, ())
            latency_payload = info.get("Latency")
            latency_not_applicable = (info.get("mayStore") is True) or (
                info.get("hasUnmodeledSideEffects") is True and latency_payload == 0
            )
            latency_metric = (
                PerformanceMetric(
                    provenance=Provenance.unresolved(
                        "latency is not a result latency for this store or "
                        "unmodelled side-effecting instruction"
                    )
                )
                if latency_not_applicable
                else _metric_from_number(
                    latency_payload,
                    unit="cycles",
                    provenance=provenance,
                    confidence=record_confidence,
                    notes=(metric_note,),
                    location="llvm-mca Latency",
                )
            )
            records.append(
                PerformanceRecord(
                    microarchitecture=manifest.microarchitecture
                    or manifest.cpu
                    or "unknown",
                    cpu=manifest.cpu,
                    instruction_form=instructions[instruction_index],
                    latency=latency_metric,
                    reciprocal_throughput=_metric_from_number(
                        info.get("RThroughput"),
                        unit="cycles/instruction",
                        provenance=provenance,
                        confidence=record_confidence,
                        notes=(metric_note,),
                        location="llvm-mca RThroughput",
                    ),
                    uops=_metric_from_number(
                        info.get("NumMicroOpcodes"),
                        unit="uops",
                        provenance=provenance,
                        confidence=record_confidence,
                        notes=(metric_note,),
                        location="llvm-mca NumMicroOpcodes",
                    ),
                    resources=tuple(
                        f"{name}: {_format_number(usage)}"
                        for name, usage in resource_values
                    ),
                    resources_provenance=(
                        provenance
                        if resource_values
                        else Provenance.unresolved(
                            "llvm-mca did not report per-instruction resource pressure"
                        )
                    ),
                    evidence_kind=PerformanceEvidenceKind.COMPILER_MODEL,
                    provenance=provenance,
                    confidence=record_confidence,
                    notes=tuple(notes),
                )
            )
    return tuple(records)


def run_llvm_mca(
    assembly: str,
    *,
    executable: Path,
    expected_tool_version: str,
    march: str,
    mcpu: str,
    microarchitecture: str,
    source_ref: SourceRef,
    mattr: Sequence[str] = (),
    mtriple: str | None = None,
    model_complete: bool | None = None,
    timeout_seconds: float = 30.0,
) -> PerformanceDataset:
    """Run a pinned ``llvm-mca`` binary with safe argv and parse its JSON.

    The caller must supply an expected version.  A version mismatch fails
    closed rather than silently changing the scheduling model behind a docset.
    """

    if not assembly.strip():
        raise LLVMToolError("assembly must not be empty")
    if "\x00" in assembly:
        raise LLVMToolError("assembly must not contain NUL bytes")
    if timeout_seconds <= 0:
        raise LLVMToolError("timeout_seconds must be positive")

    tool_path = str(executable)
    try:
        version_process = subprocess.run(
            [tool_path, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=min(timeout_seconds, 10.0),
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise LLVMToolError(f"cannot execute llvm-mca: {error}") from error
    if version_process.returncode != 0:
        raise LLVMToolError(
            f"llvm-mca --version failed: {version_process.stderr.strip()}"
        )
    version_match = _VERSION_RE.search(version_process.stdout)
    if version_match is None:
        raise LLVMToolError("cannot parse llvm-mca version output")
    actual_version = version_match.group("version")
    if actual_version != expected_tool_version:
        raise LLVMToolError(
            f"llvm-mca version mismatch: expected {expected_tool_version!r}, "
            f"found {actual_version!r}"
        )

    argv = [
        tool_path,
        "--json",
        "--instruction-tables=full",
        f"-march={march}",
        f"-mcpu={mcpu}",
        "-iterations=1",
    ]
    if mattr:
        argv.append(f"-mattr={','.join(mattr)}")
    if mtriple:
        argv.append(f"-mtriple={mtriple}")
    try:
        process = subprocess.run(
            argv,
            input=assembly,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise LLVMToolError(f"llvm-mca invocation failed: {error}") from error
    if process.returncode != 0:
        stderr = process.stderr.strip()
        raise LLVMToolError(f"llvm-mca failed with exit {process.returncode}: {stderr}")

    data = process.stdout.encode("utf-8")
    digest = hashlib.sha256(data).hexdigest()
    confidence = (
        PerformanceConfidence.MEDIUM
        if model_complete is True
        else PerformanceConfidence.LOW
    )
    source = PerformanceSource(
        evidence_kind=PerformanceEvidenceKind.COMPILER_MODEL,
        name="LLVM llvm-mca scheduling model",
        version=actual_version,
        source_ref=source_ref,
        tool_name="llvm-mca",
        tool_version=actual_version,
        confidence=confidence,
        notes=("Compiler scheduling model estimate; not a hardware measurement.",),
        raw_data_sha256=digest,
    )
    manifest = PerformanceManifest(
        schema_version=1,
        data_file="<llvm-mca stdout>",
        data_format="llvm-mca-json",
        sha256=digest,
        architecture=march,
        microarchitecture=microarchitecture,
        cpu=mcpu,
        target_triple=mtriple,
        features=tuple(mattr),
        model_complete=model_complete,
        source=source,
    )
    records = parse_llvm_mca_json(process.stdout, manifest=manifest)
    return PerformanceDataset(manifest=manifest, records=records)


def llvm_22_1_1_profile(cpu: str) -> LLVMModelProfile:
    """Resolve one supported default profile by exact LLVM CPU name."""

    for profile in LLVM_22_1_1_PROFILES:
        if profile.cpu == cpu:
            return profile
    supported = ", ".join(profile.cpu for profile in LLVM_22_1_1_PROFILES)
    raise PerformanceFormatError(
        f"unsupported LLVM 22.1.1 performance profile {cpu!r}; expected {supported}"
    )


def run_llvm_22_1_1_profile(
    assembly: str,
    *,
    executable: Path,
    cpu: str,
    timeout_seconds: float = 30.0,
) -> PerformanceDataset:
    """Run one repository-standard LLVM 22.1.1 profile."""

    profile = llvm_22_1_1_profile(cpu)
    return run_llvm_mca(
        assembly,
        executable=executable,
        expected_tool_version="22.1.1",
        march=profile.march,
        mcpu=profile.cpu,
        microarchitecture=profile.display_name,
        source_ref=_llvm_22_1_1_source_ref(profile),
        mattr=profile.features,
        mtriple=profile.target_triple,
        model_complete=profile.model_complete,
        timeout_seconds=timeout_seconds,
    )


def _llvm_22_1_1_source_ref(profile: LLVMModelProfile) -> SourceRef:
    """Return the LLVM backend that owns one profile's scheduling model."""

    if profile.march == "aarch64":
        return LLVM_22_1_1_AARCH64_SOURCE_REF
    if profile.march == "arm":
        return LLVM_22_1_1_ARM_SOURCE_REF
    raise PerformanceFormatError(
        f"unsupported LLVM backend architecture {profile.march!r} for "
        f"profile {profile.cpu!r}"
    )


def parse_llvm_mc_output(
    text: str,
    *,
    target_triple: str,
    cpu: str,
    features: Sequence[str] = (),
) -> tuple[LLVMInstructionIdentity, ...]:
    """Parse ``llvm-mc -show-inst -show-encoding`` strong identities."""

    identities: list[LLVMInstructionIdentity] = []
    current_assembly: str | None = None
    current_encoding: tuple[int, ...] = ()
    current_opcode: str | None = None
    current_operands: list[str] = []

    def finish() -> None:
        nonlocal current_assembly, current_encoding, current_opcode, current_operands
        if current_assembly is None:
            return
        if current_opcode is None:
            raise PerformanceFormatError(
                f"llvm-mc did not emit an MC opcode for {current_assembly!r}"
            )
        identities.append(
            LLVMInstructionIdentity(
                target_triple=target_triple,
                cpu=cpu,
                features=tuple(features),
                canonical_asm=current_assembly,
                llvm_opcode=current_opcode,
                encoding=current_encoding,
                mc_operands=tuple(current_operands),
            )
        )
        current_assembly = None
        current_encoding = ()
        current_opcode = None
        current_operands = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        encoding_match = _ENCODING_LINE_RE.match(line)
        if encoding_match is not None:
            finish()
            current_assembly = " ".join(encoding_match.group("assembly").split())
            encoding_items = [
                item.strip()
                for item in encoding_match.group("encoding").split(",")
                if item.strip()
            ]
            try:
                current_encoding = tuple(int(item, 0) for item in encoding_items)
            except ValueError as error:
                raise PerformanceFormatError(
                    f"invalid llvm-mc encoding at line {line_number}"
                ) from error
            if not current_encoding or any(
                byte < 0 or byte > 0xFF for byte in current_encoding
            ):
                raise PerformanceFormatError(
                    f"invalid llvm-mc encoding at line {line_number}"
                )
            continue
        opcode_match = _MCINST_LINE_RE.search(line)
        if opcode_match is not None:
            if current_assembly is None:
                raise PerformanceFormatError(
                    f"llvm-mc opcode precedes encoding at line {line_number}"
                )
            current_opcode = opcode_match.group("opcode")
            continue
        operand_match = _MCOPERAND_LINE_RE.search(line)
        if operand_match is not None:
            if current_assembly is None:
                raise PerformanceFormatError(
                    f"llvm-mc operand precedes encoding at line {line_number}"
                )
            current_operands.append(operand_match.group("operand"))
    finish()
    if not identities:
        raise PerformanceFormatError("llvm-mc output contained no instruction identity")
    return tuple(identities)


def run_llvm_mc(
    assembly: str,
    *,
    executable: Path,
    expected_tool_version: str,
    target_triple: str,
    cpu: str,
    features: Sequence[str] = (),
    timeout_seconds: float = 30.0,
) -> tuple[LLVMInstructionIdentity, ...]:
    """Run pinned ``llvm-mc`` to obtain opcode, operands, and encoding."""

    if not assembly.strip() or "\x00" in assembly:
        raise LLVMToolError("assembly must be non-empty and contain no NUL bytes")
    tool_path = str(executable)
    actual_version = _llvm_tool_version(
        tool_path,
        expected=expected_tool_version,
        timeout_seconds=timeout_seconds,
    )
    argv = [
        tool_path,
        f"-triple={target_triple}",
        f"-mcpu={cpu}",
        "-show-inst",
        "-show-encoding",
    ]
    if features:
        argv.append(f"-mattr={','.join(features)}")
    try:
        process = subprocess.run(
            argv,
            input=assembly,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise LLVMToolError(f"llvm-mc invocation failed: {error}") from error
    if process.returncode != 0:
        raise LLVMToolError(
            f"llvm-mc {actual_version} failed with exit {process.returncode}: "
            f"{process.stderr.strip()}"
        )
    return parse_llvm_mc_output(
        process.stdout,
        target_triple=target_triple,
        cpu=cpu,
        features=features,
    )


def run_llvm_22_1_1_pipeline(
    assembly: str,
    *,
    llvm_mc_executable: Path,
    llvm_mca_executable: Path,
    cpu: str,
    timeout_seconds: float = 30.0,
) -> PerformanceDataset:
    """Run the strong-identity and scheduling-model halves of one profile."""

    profile = llvm_22_1_1_profile(cpu)
    identities = run_llvm_mc(
        assembly,
        executable=llvm_mc_executable,
        expected_tool_version="22.1.1",
        target_triple=profile.target_triple,
        cpu=profile.cpu,
        features=profile.features,
        timeout_seconds=timeout_seconds,
    )
    dataset = run_llvm_22_1_1_profile(
        assembly,
        executable=llvm_mca_executable,
        cpu=cpu,
        timeout_seconds=timeout_seconds,
    )
    if len(identities) != len(dataset.records):
        raise LLVMToolError(
            "llvm-mc identity count does not match llvm-mca instruction count"
        )
    return replace(dataset, llvm_identities=identities)


def build_default_performance_datasets(
    *,
    llvm_mca: Path,
    llvm_mc: Path | None = None,
    profiles: Sequence[str] | None = None,
    timeout_seconds: float = 30.0,
) -> tuple[PerformanceDataset, ...]:
    """Build the repository-standard six-profile representative dataset.

    ``profiles=None`` means all six fixed profiles.  A caller may request a
    strict subset by LLVM CPU name for development or targeted verification.
    ``llvm_mc`` defaults to the sibling executable beside ``llvm_mca`` so both
    halves normally come from one pinned LLVM installation.  Version checks in
    the lower-level runners fail closed unless each tool reports 22.1.1.

    The returned records use reviewed ACLE ``documented_form`` values as join
    keys.  Before that substitution, pinned ``llvm-mc`` must prove that the
    concrete assembler input has the same operand shape and supply an opcode,
    operands, and encoding.  Metrics remain the unmodified output of the
    corresponding ``llvm-mca`` scheduling model.
    """

    selected_profiles = _resolve_requested_profiles(profiles)
    _validate_representative_probe_catalog()
    llvm_mc_path = llvm_mc or llvm_mca.with_name("llvm-mc")
    datasets: list[PerformanceDataset] = []
    for profile in selected_profiles:
        selected_probes = tuple(
            probe
            for probe in LLVM_22_1_1_REPRESENTATIVE_PROBES
            if profile.cpu in probe.profiles
        )
        if not selected_probes:
            raise PerformanceFormatError(
                f"performance profile {profile.cpu!r} has no representative probes"
            )
        assembly = "\n".join(probe.assembly for probe in selected_probes) + "\n"
        dataset = run_llvm_22_1_1_pipeline(
            assembly,
            llvm_mc_executable=llvm_mc_path,
            llvm_mca_executable=llvm_mca,
            cpu=profile.cpu,
            timeout_seconds=timeout_seconds,
        )
        if len(dataset.records) != len(selected_probes):
            raise LLVMToolError(
                f"profile {profile.cpu!r} produced {len(dataset.records)} records "
                f"for {len(selected_probes)} representative probes"
            )

        mapped_records: list[PerformanceRecord] = []
        for probe, record, identity in zip(
            selected_probes,
            dataset.records,
            dataset.llvm_identities,
            strict=True,
        ):
            if not instruction_form_matches(probe.assembly, identity.canonical_asm):
                raise LLVMToolError(
                    f"llvm-mc canonical form drifted for probe {probe.id!r}: "
                    f"input {probe.assembly!r}, output {identity.canonical_asm!r}"
                )
            if not instruction_form_matches(
                identity.canonical_asm, probe.documented_form
            ):
                raise LLVMToolError(
                    f"probe {probe.id!r} does not exactly match its documented "
                    f"ACLE form: {identity.canonical_asm!r} versus "
                    f"{probe.documented_form!r}"
                )
            mapping_note = (
                f"Representative probe {probe.id}; ACLE examples: "
                f"{', '.join(probe.intrinsic_examples)}; llvm-mca input: "
                f"{probe.assembly}; LLVM opcode: {identity.llvm_opcode}; "
                "metrics apply only to this exact instruction form."
            )
            notes = (
                *record.notes,
                "LLVM scheduling model estimate, not measured hardware data.",
                mapping_note,
            )
            if probe.note:
                notes = (*notes, probe.note)
            mapped_records.append(
                replace(
                    record,
                    instruction_form=probe.documented_form,
                    notes=tuple(dict.fromkeys(notes)),
                )
            )
        datasets.append(replace(dataset, records=tuple(mapped_records)))
    return tuple(datasets)


def performance_unavailable_record(
    family: str,
    *,
    instruction_form: str | None = None,
    reason: str | None = None,
) -> PerformanceRecord:
    """Return an explicit no-number record without manufacturing metrics."""

    unavailable_reason = (
        reason
        or LLVM_22_1_1_UNAVAILABLE_FAMILIES.get(family)
        or LLVM_22_1_1_NO_EXACT_FORM_REASON
    )
    return PerformanceRecord(
        microarchitecture="LLVM 22.1.1 scheduling models",
        instruction_form=instruction_form,
        unresolved_reason=unavailable_reason,
        notes=(
            "LLVM scheduling model estimate, not measured hardware data.",
            "No metric was inferred from a related instruction or microarchitecture.",
        ),
    )


def _resolve_requested_profiles(
    profiles: Sequence[str] | None,
) -> tuple[LLVMModelProfile, ...]:
    requested = (
        tuple(profile.cpu for profile in LLVM_22_1_1_PROFILES)
        if profiles is None
        else tuple(profiles)
    )
    if not requested:
        raise PerformanceFormatError("at least one performance profile is required")
    if len(set(requested)) != len(requested):
        raise PerformanceFormatError("performance profiles must be unique")
    return tuple(llvm_22_1_1_profile(cpu) for cpu in requested)


def _validate_representative_probe_catalog() -> None:
    profile_cpus = {profile.cpu for profile in LLVM_22_1_1_PROFILES}
    ids: set[str] = set()
    forms: set[tuple[str, str]] = set()
    for probe in LLVM_22_1_1_REPRESENTATIVE_PROBES:
        if probe.id in ids:
            raise PerformanceFormatError(
                f"duplicate representative performance probe id {probe.id!r}"
            )
        ids.add(probe.id)
        unknown_profiles = sorted(set(probe.profiles).difference(profile_cpus))
        if unknown_profiles:
            raise PerformanceFormatError(
                f"probe {probe.id!r} uses unknown profiles: "
                + ", ".join(unknown_profiles)
            )
        documented = normalize_instruction_form(probe.documented_form)
        key = (probe.family, documented)
        if key in forms:
            raise PerformanceFormatError(
                f"duplicate representative form for family {probe.family!r}: "
                f"{probe.documented_form!r}"
            )
        forms.add(key)
        # This catches placeholder shape mistakes before invoking either tool.
        parse_instruction_form(probe.assembly)


def match_performance_identity(
    identity: LLVMInstructionIdentity,
    dataset: PerformanceDataset,
) -> tuple[PerformanceMatch, ...]:
    """Match on target, features, LLVM opcode, MC operands, and encoding."""

    return tuple(
        PerformanceMatch(record, "identity")
        for record, candidate in zip(
            dataset.records, dataset.llvm_identities, strict=True
        )
        if candidate.key == identity.key
    )


def parse_instruction_form(text: str) -> InstructionForm:
    """Normalize one Arm instruction form without guessing semantic aliases."""

    if not isinstance(text, str) or not text.strip():
        raise PerformanceFormatError("instruction form must be non-empty")
    line = text.strip().split("//", 1)[0].strip()
    if "\n" in line or ";" in line:
        raise PerformanceFormatError("instruction form must contain one instruction")
    match = _MNEMONIC_RE.match(line)
    if match is None:
        raise PerformanceFormatError(f"cannot parse instruction form {text!r}")
    mnemonic = match.group("mnemonic").lower()
    operand_text = line[match.end() :].strip()
    operands = _split_operands(operand_text) if operand_text else ()

    arrangement: str | None = None
    arrangement_match = _AARCH64_ARRANGEMENT_RE.match(mnemonic)
    if arrangement_match is not None:
        mnemonic = arrangement_match.group("base")
        arrangement = f".{arrangement_match.group('shape')}"
    mnemonic = _MNEMONIC_ALIASES.get(mnemonic, mnemonic)

    normalized_operands = tuple(
        _normalize_operand(operand, arrangement=arrangement) for operand in operands
    )
    return InstructionForm(raw=text, mnemonic=mnemonic, operands=normalized_operands)


def normalize_instruction_form(text: str) -> str:
    """Return the stable string key used by instruction-form matching."""

    return parse_instruction_form(text).canonical


def instruction_form_matches(left: str, right: str) -> bool:
    """Return true only for exact normalized forms, never mnemonic guesses."""

    return normalize_instruction_form(left) == normalize_instruction_form(right)


def match_performance_records(
    instruction_form: str,
    records: Iterable[PerformanceRecord],
    *,
    microarchitecture: str | None = None,
    cpu: str | None = None,
    allow_mnemonic_only: bool = False,
) -> tuple[PerformanceMatch, ...]:
    """Join one documented instruction form to scoped performance records.

    Mnemonic-only matching is disabled by default.  When enabled it is only
    used if either side has no operands, and the result carries an explicit
    ``mnemonic_only`` quality marker.
    """

    query = parse_instruction_form(instruction_form)
    matches: list[PerformanceMatch] = []
    for record in records:
        if record.instruction_form is None:
            continue
        if (
            microarchitecture
            and record.microarchitecture.casefold() != microarchitecture.casefold()
        ):
            continue
        if cpu and (record.cpu is None or record.cpu.casefold() != cpu.casefold()):
            continue
        candidate = parse_instruction_form(record.instruction_form)
        if query.canonical == candidate.canonical:
            matches.append(PerformanceMatch(record, "exact"))
        elif (
            allow_mnemonic_only
            and query.mnemonic == candidate.mnemonic
            and (not query.operands or not candidate.operands)
        ):
            matches.append(PerformanceMatch(record, "mnemonic_only"))
    return tuple(matches)


def _llvm_target_abi_for_cpu(cpu: str | None) -> LLVMTargetABI | None:
    if cpu is None:
        return None
    normalized_cpu = cpu.casefold()
    for profile in LLVM_22_1_1_PROFILES:
        if profile.cpu.casefold() != normalized_cpu:
            continue
        if profile.march == "aarch64":
            return "aarch64-lp64"
        if profile.march == "arm":
            return "aarch32-ilp32"
    return None


def _probe_supports_target_abi(
    probe: LLVMRepresentativeProbe,
    target_abi: LLVMTargetABI,
) -> bool:
    return any(_llvm_target_abi_for_cpu(cpu) == target_abi for cpu in probe.profiles)


def _integer_operand_width_bits(
    type_name: str,
    *,
    target_abi: LLVMTargetABI,
) -> int | None:
    """Resolve only integer widths guaranteed by the two reviewed Arm ABIs."""

    tokens = tuple(
        token.casefold()
        for token in type_name.split()
        if token.casefold() not in {"const", "restrict", "volatile"}
    )
    normalized = " ".join(tokens)
    fixed_widths = {
        "int32_t": 32,
        "uint32_t": 32,
        "int64_t": 64,
        "uint64_t": 64,
    }
    if normalized in fixed_widths:
        return fixed_widths[normalized]
    if normalized in {"int", "signed", "signed int", "unsigned", "unsigned int"}:
        return 32
    if normalized in {
        "long long",
        "long long int",
        "signed long long",
        "signed long long int",
        "unsigned long long",
        "unsigned long long int",
    }:
        return 64
    if normalized in {
        "long",
        "long int",
        "signed long",
        "signed long int",
        "unsigned long",
        "unsigned long int",
    }:
        return 64 if target_abi == "aarch64-lp64" else 32
    return None


def representative_probes_for_intrinsic_names(
    names: Iterable[str],
    *,
    family: str,
    signature_width_bits: int | None = None,
    target_abi: LLVMTargetABI | None = None,
) -> tuple[LLVMRepresentativeProbe, ...]:
    """Resolve only explicit, reviewed intrinsic-name performance mappings.

    This is the intended bridge for SVE/SVE2 declaration pages, whose generated
    Clang headers do not carry instruction-form tables.  It is also useful for
    general ACLE declarations.  Matching is case-sensitive and exact; prefixes,
    suffixes, and overloaded spellings are never guessed.  When a signature
    width is supplied, its target ABI is mandatory so ABI-sized C types cannot
    silently select the wrong register form.
    """

    if (signature_width_bits is None) != (target_abi is None):
        raise ValueError(
            "signature_width_bits and target_abi must be provided together"
        )
    if target_abi is not None and target_abi not in {
        "aarch32-ilp32",
        "aarch64-lp64",
    }:
        raise ValueError(f"unsupported target ABI {target_abi!r}")
    if signature_width_bits is not None and signature_width_bits not in {
        8,
        16,
        32,
        64,
    }:
        raise ValueError("signature_width_bits must be 8, 16, 32, or 64")

    name_set = {name for name in names if name}
    family_root = family.split(".", 1)[0]
    compatible_families = (
        {"sve", "sve2"} if family_root in {"sve", "sve2"} else {family_root}
    )
    return tuple(
        probe
        for probe in LLVM_22_1_1_REPRESENTATIVE_PROBES
        if probe.family in compatible_families
        and name_set.intersection(probe.intrinsic_examples)
        and (target_abi is None or _probe_supports_target_abi(probe, target_abi))
        and (
            signature_width_bits is None
            or probe.intrinsic_operand_width_bits is None
            or probe.intrinsic_operand_width_bits == signature_width_bits
        )
    )


def match_representative_performance_records(
    names: Iterable[str],
    records: Iterable[PerformanceRecord],
    *,
    family: str,
    signature_operand_type: str | None = None,
) -> tuple[PerformanceRecord, ...]:
    """Match records through the exact reviewed intrinsic-to-form map.

    Scalar mappings with ABI-sized operands are resolved per record CPU.  This
    keeps AArch64 LP64 ``long`` on X-register forms while the same declaration
    uses 32-bit core-register forms for AArch32 ILP32 profiles.
    """

    name_values = tuple(names)
    probes = representative_probes_for_intrinsic_names(name_values, family=family)
    if not probes:
        return ()
    needs_signature_width = any(
        probe.intrinsic_operand_width_bits is not None for probe in probes
    )
    matches: list[PerformanceRecord] = []
    for record in records:
        if record.instruction_form is None:
            continue
        record_probes = probes
        if signature_operand_type is not None and needs_signature_width:
            target_abi = _llvm_target_abi_for_cpu(record.cpu)
            if target_abi is None:
                continue
            signature_width_bits = _integer_operand_width_bits(
                signature_operand_type,
                target_abi=target_abi,
            )
            if signature_width_bits is None:
                continue
            record_probes = representative_probes_for_intrinsic_names(
                name_values,
                family=family,
                signature_width_bits=signature_width_bits,
                target_abi=target_abi,
            )
        normalized_form = normalize_instruction_form(record.instruction_form)
        for probe in record_probes:
            if record.cpu is not None and record.cpu.casefold() not in {
                cpu.casefold() for cpu in probe.profiles
            }:
                continue
            if normalized_form != normalize_instruction_form(probe.documented_form):
                continue
            if record not in matches:
                matches.append(record)
            break
    return tuple(matches)


def _parse_source(payload: Mapping[str, Any]) -> PerformanceSource:
    kind_text = _require_text(payload.get("evidence_kind"), "source.evidence_kind")
    try:
        evidence_kind = PerformanceEvidenceKind(kind_text)
    except ValueError as error:
        raise PerformanceFormatError(
            f"unsupported evidence kind {kind_text!r}"
        ) from error

    source_ref_payload = _require_mapping(
        payload.get("source_ref"), "source.source_ref"
    )
    source_ref = SourceRef(
        id=_require_text(source_ref_payload.get("id"), "source.source_ref.id"),
        repository=_require_text(
            source_ref_payload.get("repository"), "source.source_ref.repository"
        ),
        commit=_require_text(
            source_ref_payload.get("commit"), "source.source_ref.commit"
        ),
        path=_require_text(source_ref_payload.get("path"), "source.source_ref.path"),
        license_id=_optional_text(source_ref_payload.get("license_id")),
        url=_optional_text(source_ref_payload.get("url")),
    )
    tool_payload = payload.get("tool")
    if tool_payload is None:
        tool: Mapping[str, Any] = {}
    else:
        tool = _require_mapping(tool_payload, "source.tool")
    notes_payload = payload.get("notes", ())
    if not isinstance(notes_payload, list) or not all(
        isinstance(note, str) and note.strip() for note in notes_payload
    ):
        raise PerformanceFormatError("source.notes must be non-empty strings")
    confidence_text = payload.get("confidence")
    if confidence_text is None:
        confidence = (
            PerformanceConfidence.HIGH
            if evidence_kind is PerformanceEvidenceKind.OFFICIAL
            else PerformanceConfidence.MEDIUM
        )
    else:
        try:
            confidence = PerformanceConfidence(confidence_text)
        except ValueError as error:
            raise PerformanceFormatError(
                f"unsupported source.confidence {confidence_text!r}"
            ) from error
        if confidence is PerformanceConfidence.UNRESOLVED:
            raise PerformanceFormatError(
                "resolved datasets cannot use unresolved confidence"
            )

    sample_count = payload.get("sample_count")
    if sample_count is not None and (
        isinstance(sample_count, bool) or not isinstance(sample_count, int)
    ):
        raise PerformanceFormatError("source.sample_count must be an integer")
    return PerformanceSource(
        evidence_kind=evidence_kind,
        name=_require_text(payload.get("name"), "source.name"),
        version=_require_text(payload.get("version"), "source.version"),
        source_ref=source_ref,
        tool_name=_optional_text(tool.get("name")),
        tool_version=_optional_text(tool.get("version")),
        tool_commit=_optional_text(tool.get("commit")),
        methodology=_optional_text(payload.get("methodology")),
        hardware=_optional_text(payload.get("hardware")),
        sample_count=sample_count,
        confidence=confidence,
        notes=tuple(note.strip() for note in notes_payload),
    )


def _parse_normalized_record(
    payload: Mapping[str, Any],
    *,
    manifest: PerformanceManifest,
    location: str,
) -> PerformanceRecord:
    microarchitecture = _optional_text(payload.get("microarchitecture"))
    if microarchitecture is None:
        microarchitecture = manifest.microarchitecture
    cpu = _optional_text(payload.get("cpu")) or manifest.cpu
    instruction_form = _require_text(
        payload.get("instruction_form"), f"{location}.instruction_form"
    )
    # Parse eagerly so malformed forms cannot enter the join index.
    parse_instruction_form(instruction_form)

    provenance = _record_provenance(manifest)
    record_confidence = _record_confidence(manifest)
    metric_note = _evidence_note(manifest.source.evidence_kind)
    latency = _parse_metric(
        payload.get("latency"),
        unit="cycles",
        provenance=provenance,
        confidence=record_confidence,
        notes=(metric_note,),
        location=f"{location}.latency",
    )
    reciprocal_throughput = _parse_metric(
        payload.get("reciprocal_throughput"),
        unit="cycles/instruction",
        provenance=provenance,
        confidence=record_confidence,
        notes=(metric_note,),
        location=f"{location}.reciprocal_throughput",
    )
    uops = _parse_metric(
        payload.get("uops"),
        unit="uops",
        provenance=provenance,
        confidence=record_confidence,
        notes=(metric_note,),
        location=f"{location}.uops",
    )
    if not any(metric.is_resolved for metric in (latency, reciprocal_throughput, uops)):
        raise PerformanceFormatError(f"{location} has no performance metric")

    resources = _parse_resources(
        payload.get("resources"), location=f"{location}.resources"
    )
    record_notes = _parse_record_notes(
        payload.get("notes"), location=f"{location}.notes"
    )
    notes = tuple(
        (*manifest.source.notes, metric_note, _profile_note(manifest), *record_notes)
    )
    return PerformanceRecord(
        microarchitecture=microarchitecture or cpu or "unknown",
        cpu=cpu,
        instruction_form=instruction_form,
        latency=latency,
        reciprocal_throughput=reciprocal_throughput,
        uops=uops,
        resources=resources,
        resources_provenance=(
            provenance
            if resources
            else Provenance.unresolved("source did not provide resource usage")
        ),
        evidence_kind=manifest.source.evidence_kind,
        provenance=provenance,
        confidence=record_confidence,
        notes=notes,
    )


def _parse_metric(
    payload: Any,
    *,
    unit: str,
    provenance: Provenance,
    confidence: PerformanceConfidence,
    notes: tuple[str, ...],
    location: str,
) -> PerformanceMetric:
    if payload is None or payload == "":
        return PerformanceMetric(
            provenance=Provenance.unresolved(f"{location} is not provided")
        )
    if isinstance(payload, Mapping):
        minimum = payload.get("minimum", payload.get("value"))
        maximum = payload.get("maximum")
        actual_unit = payload.get("unit", unit)
        if actual_unit != unit:
            raise PerformanceFormatError(
                f"{location}.unit must be {unit!r}, found {actual_unit!r}"
            )
        minimum_number = _require_number(minimum, f"{location}.minimum")
        maximum_number = (
            _require_number(maximum, f"{location}.maximum")
            if maximum is not None
            else None
        )
    elif isinstance(payload, str):
        match = _METRIC_RANGE_RE.match(payload)
        if match is None:
            raise PerformanceFormatError(
                f"{location} must be a number or min-max range, found {payload!r}"
            )
        minimum_number = _parse_number_text(match.group("minimum"))
        maximum_text = match.group("maximum")
        maximum_number = (
            _parse_number_text(maximum_text) if maximum_text is not None else None
        )
    else:
        minimum_number = _require_number(payload, location)
        maximum_number = None
    try:
        value = NumericRange(minimum_number, maximum_number, unit)
    except (TypeError, ValueError) as error:
        raise PerformanceFormatError(f"invalid {location}: {error}") from error
    return PerformanceMetric(
        value=value,
        provenance=provenance,
        confidence=confidence,
        notes=notes,
    )


def _metric_from_number(
    payload: Any,
    *,
    unit: str,
    provenance: Provenance,
    confidence: PerformanceConfidence,
    notes: tuple[str, ...],
    location: str,
) -> PerformanceMetric:
    if payload is None:
        return PerformanceMetric(
            provenance=Provenance.unresolved(f"{location} is not provided")
        )
    return _parse_metric(
        payload,
        unit=unit,
        provenance=provenance,
        confidence=confidence,
        notes=notes,
        location=location,
    )


def _parse_resources(payload: Any, *, location: str) -> tuple[str, ...]:
    if payload is None or payload == "":
        return ()
    if isinstance(payload, str):
        try:
            decoded = json.loads(payload)
        except json.JSONDecodeError:
            decoded = None
        if isinstance(decoded, list):
            payload = decoded
        else:
            values: list[str] = []
            for item in payload.split(";"):
                item = item.strip()
                if not item:
                    continue
                name, separator, usage_text = item.partition("=")
                if not separator or not name.strip():
                    raise PerformanceFormatError(
                        f"{location} items must use name=usage syntax"
                    )
                usage = _require_number(
                    _parse_number_text(usage_text.strip()), f"{location}.{name.strip()}"
                )
                values.append(f"{name.strip()}: {_format_number(usage)}")
            return tuple(values)
    if not isinstance(payload, list):
        raise PerformanceFormatError(f"{location} must be an array or name=usage list")
    values = []
    for index, item in enumerate(payload):
        mapping = _require_mapping(item, f"{location}[{index}]")
        name = _require_text(mapping.get("name"), f"{location}[{index}].name")
        usage = _require_number(mapping.get("usage"), f"{location}[{index}].usage")
        values.append(f"{name}: {_format_number(usage)}")
    return tuple(values)


def _llvm_resource_pressure(
    region: Mapping[str, Any],
    *,
    instruction_count: int,
    resource_names: tuple[str, ...],
    location: str,
) -> dict[int, tuple[tuple[str, int | float], ...]]:
    pressure_view = region.get("ResourcePressureView")
    if pressure_view is None:
        return {}
    pressure_mapping = _require_mapping(
        pressure_view, f"{location}.ResourcePressureView"
    )
    info_payload = pressure_mapping.get("ResourcePressureInfo")
    if not isinstance(info_payload, list):
        raise PerformanceFormatError(
            f"{location}.ResourcePressureInfo must be an array"
        )
    pressure: dict[int, dict[str, int | float]] = {}
    for item_index, item_payload in enumerate(info_payload):
        item = _require_mapping(
            item_payload,
            f"{location}.ResourcePressureInfo[{item_index}]",
        )
        instruction_index = item.get("InstructionIndex")
        resource_index = item.get("ResourceIndex")
        if (
            isinstance(instruction_index, bool)
            or not isinstance(instruction_index, int)
            or instruction_index < 0
        ):
            raise PerformanceFormatError("invalid llvm-mca resource instruction index")
        # LLVM emits an extra block-total row at InstructionIndex == count.
        if instruction_index == instruction_count:
            continue
        if instruction_index > instruction_count:
            raise PerformanceFormatError(
                "llvm-mca resource instruction index is out of range"
            )
        if (
            isinstance(resource_index, bool)
            or not isinstance(resource_index, int)
            or resource_index < 0
            or resource_index >= len(resource_names)
        ):
            raise PerformanceFormatError("llvm-mca resource index is out of range")
        usage = _require_number(item.get("ResourceUsage"), "llvm-mca ResourceUsage")
        name = resource_names[resource_index]
        by_name = pressure.setdefault(instruction_index, {})
        by_name[name] = by_name.get(name, 0) + usage
    return {
        instruction_index: tuple(values.items())
        for instruction_index, values in pressure.items()
    }


def _resolve_adjacent_data_path(manifest_path: Path, data_file: str) -> Path:
    relative_path = Path(data_file)
    if relative_path.is_absolute():
        raise PerformanceFormatError("manifest.data.file must be relative")
    base = manifest_path.parent.resolve()
    resolved = (base / relative_path).resolve()
    try:
        resolved.relative_to(base)
    except ValueError as error:
        raise PerformanceFormatError(
            "manifest.data.file must remain inside the manifest directory"
        ) from error
    return resolved


def _split_operands(text: str) -> tuple[str, ...]:
    operands: list[str] = []
    current: list[str] = []
    depth = 0
    for character in text:
        if character in "[({":
            depth += 1
        elif character in "])}":
            depth -= 1
            if depth < 0:
                raise PerformanceFormatError("unbalanced instruction operands")
        if character == "," and depth == 0:
            operand = "".join(current).strip()
            if not operand:
                raise PerformanceFormatError("empty instruction operand")
            operands.append(operand)
            current = []
        else:
            current.append(character)
    if depth != 0:
        raise PerformanceFormatError("unbalanced instruction operands")
    final_operand = "".join(current).strip()
    if final_operand:
        operands.append(final_operand)
    return tuple(operands)


def _normalize_operand(operand: str, *, arrangement: str | None) -> str:
    value = operand.lower()
    if arrangement:
        value = re.sub(
            r"(?<![a-z0-9_])(v(?:\d+|[dnamtgv][a-z0-9]*))(?![a-z0-9_.])",
            rf"\1{arrangement}",
            value,
        )

    def normalize_register(match: re.Match[str]) -> str:
        bank = match.group("bank").lower()
        shape = (match.group("shape") or "").lower()
        predication = (match.group("pred") or "").lower()
        return f"{bank}{shape}{predication}"

    value = _REGISTER_RE.sub(normalize_register, value)
    value = re.sub(r"(?<![a-z0-9_])xzr(?![a-z0-9_])", "xzr", value)
    value = re.sub(r"(?<![a-z0-9_])wzr(?![a-z0-9_])", "wzr", value)
    # Preserve concrete immediates.  Different encodings can select different
    # scheduling classes, so ``#0`` must not silently match ``#7``.  Only
    # abstract source placeholders are normalized.
    value = _SYMBOLIC_IMMEDIATE_RE.sub("#imm", value)
    return re.sub(r"\s+", "", value)


def _sanitize_resource_name(name: str) -> str:
    # LLVM encodes resource-group members with small control-character suffixes.
    # Preserve their identity in printable decimal form instead of dropping them.
    return "".join(
        str(ord(character)) if ord(character) < 32 else character for character in name
    )


def _parse_record_notes(payload: Any, *, location: str) -> tuple[str, ...]:
    if payload is None or payload == "":
        return ()
    if isinstance(payload, str):
        return (payload.strip(),) if payload.strip() else ()
    if not isinstance(payload, list) or not all(
        isinstance(note, str) and note.strip() for note in payload
    ):
        raise PerformanceFormatError(f"{location} must be a string or string array")
    return tuple(note.strip() for note in payload)


def _evidence_note(kind: PerformanceEvidenceKind) -> str:
    if kind is PerformanceEvidenceKind.OFFICIAL:
        return "Official published value; scoped to the named microarchitecture."
    if kind is PerformanceEvidenceKind.MEASURED:
        return "Measured value; scoped to the documented hardware and methodology."
    return "Compiler scheduling model estimate; not measured hardware behavior."


def _record_confidence(manifest: PerformanceManifest) -> PerformanceConfidence:
    if (
        manifest.source.evidence_kind is PerformanceEvidenceKind.COMPILER_MODEL
        and manifest.model_complete is not True
    ):
        return PerformanceConfidence.LOW
    return manifest.source.confidence


def _profile_note(manifest: PerformanceManifest) -> str:
    fields = [
        f"architecture={manifest.architecture}",
        f"cpu={manifest.cpu or 'unspecified'}",
        f"target_triple={manifest.target_triple or 'unspecified'}",
        "features=" + (",".join(manifest.features) if manifest.features else "default"),
    ]
    if manifest.model_complete is True:
        fields.append("llvm_model_status=complete")
    elif manifest.model_complete is False:
        fields.append("llvm_model_status=partial")
    else:
        fields.append("llvm_model_status=unspecified")
    return "; ".join(fields)


def _record_provenance(manifest: PerformanceManifest) -> Provenance:
    source_note = manifest.source.provenance.note
    note = _profile_note(manifest)
    if source_note:
        note = f"{source_note}; {note}"
    return Provenance(
        kind=ProvenanceKind.EXPLICIT,
        sources=(manifest.source.source_ref,),
        note=note,
    )


def _llvm_tool_version(
    tool_path: str,
    *,
    expected: str,
    timeout_seconds: float,
) -> str:
    try:
        process = subprocess.run(
            [tool_path, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=min(timeout_seconds, 10.0),
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise LLVMToolError(f"cannot execute LLVM tool: {error}") from error
    if process.returncode != 0:
        raise LLVMToolError(f"LLVM tool --version failed: {process.stderr.strip()}")
    match = _VERSION_RE.search(process.stdout)
    if match is None:
        raise LLVMToolError("cannot parse LLVM tool version output")
    actual = match.group("version")
    if actual != expected:
        raise LLVMToolError(
            f"LLVM tool version mismatch: expected {expected!r}, found {actual!r}"
        )
    return actual


def _require_mapping(payload: Any, location: str) -> Mapping[str, Any]:
    if not isinstance(payload, Mapping):
        raise PerformanceFormatError(f"{location} must be an object")
    return payload


def _require_text(payload: Any, location: str) -> str:
    if not isinstance(payload, str) or not payload.strip():
        raise PerformanceFormatError(f"{location} must be a non-empty string")
    return payload.strip()


def _optional_text(payload: Any) -> str | None:
    if payload is None:
        return None
    if not isinstance(payload, str):
        raise PerformanceFormatError(f"expected optional string, found {payload!r}")
    value = payload.strip()
    return value or None


def _require_number(payload: Any, location: str) -> int | float:
    if isinstance(payload, bool) or not isinstance(payload, (int, float)):
        raise PerformanceFormatError(f"{location} must be numeric")
    if not math.isfinite(payload) or payload < 0:
        raise PerformanceFormatError(f"{location} must be finite and non-negative")
    return payload


def _parse_number_text(text: str) -> int | float:
    value = float(text)
    return int(value) if value.is_integer() else value


def _format_number(value: int | float) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return f"{value:g}"
