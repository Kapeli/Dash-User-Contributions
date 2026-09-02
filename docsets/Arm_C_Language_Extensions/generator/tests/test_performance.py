from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from arm_acle_docset.model import (
    PerformanceConfidence,
    PerformanceEvidenceKind,
    PerformanceRecord,
    ProvenanceKind,
    SourceRef,
)
from arm_acle_docset.sources import performance
from arm_acle_docset.sources.performance import (
    LLVMToolError,
    LLVM_22_1_1_PROFILES,
    LLVM_22_1_1_REPRESENTATIVE_PROBES,
    PerformanceFormatError,
    build_default_performance_datasets,
    instruction_form_matches,
    load_performance_manifest,
    match_representative_performance_records,
    match_performance_records,
    normalize_instruction_form,
    parse_llvm_mc_output,
    parse_performance_manifest,
    performance_unavailable_record,
    representative_probes_for_intrinsic_names,
    run_llvm_mca,
)


FIXTURES = Path(__file__).parent / "fixtures" / "performance"


def test_raw_llvm_mca_json_preserves_model_metrics_and_resource_pressure() -> None:
    dataset = load_performance_manifest(FIXTURES / "llvm_mca_neoverse_n2.manifest.json")

    assert len(dataset.records) == 2
    add, crc = dataset.records
    assert add.microarchitecture == "Neoverse N2"
    assert add.cpu == "neoverse-n2"
    assert add.evidence_kind is PerformanceEvidenceKind.COMPILER_MODEL
    assert add.confidence is PerformanceConfidence.MEDIUM
    assert add.latency.value is not None
    assert add.latency.value.minimum == 2
    assert add.reciprocal_throughput.value is not None
    assert add.reciprocal_throughput.value.minimum == 0.5
    assert add.reciprocal_throughput.value.unit == "cycles/instruction"
    assert add.uops.value is not None
    assert add.uops.value.minimum == 1
    assert add.uops.value.unit == "uops"
    assert add.resources == ("N2UnitV0: 0.5", "N2UnitV1: 0.5")
    assert add.resources_provenance.kind is ProvenanceKind.EXPLICIT
    assert "not measured hardware behavior" in " ".join(add.notes)
    assert crc.resources == ("N2UnitM0: 2",)


def test_normalized_tsv_uses_the_same_canonical_model_boundary() -> None:
    dataset = load_performance_manifest(FIXTURES / "normalized.manifest.json")

    assert [record.instruction_form for record in dataset.records] == [
        "ADD Vd.4S, Vn.4S, Vm.4S",
        "CRC32W Wd, Wn, Wm",
    ]
    assert dataset.records[0].resources == (
        "N2UnitV0: 0.5",
        "N2UnitV1: 0.5",
    )
    assert dataset.records[1].reciprocal_throughput.value is not None
    assert dataset.records[1].reciprocal_throughput.value.minimum == 2


def test_aarch64_llvm_printer_arrangement_matches_acle_form() -> None:
    llvm_form = "add.4s\tv0, v1, v2"
    acle_form = "ADD Vd.4S,Vn.4S,Vm.4S"

    assert normalize_instruction_form(llvm_form) == "add v.4s,v.4s,v.4s"
    assert instruction_form_matches(llvm_form, acle_form)


def test_aarch32_llvm_mc_at_comments_preserve_strong_identity() -> None:
    identities = parse_llvm_mc_output(
        """
        rbit r0, r1 @ encoding: [0x91,0xfa,0xa1,0xf0]
                    @ <MCInst #123 t2RBIT
                    @  <MCOperand Reg:1>
                    @  <MCOperand Reg:2>>
        """,
        target_triple="arm-none-eabi",
        cpu="cortex-m55",
        features=("+mve", "+mve.fp"),
    )

    assert len(identities) == 1
    assert identities[0].canonical_asm == "rbit r0, r1"
    assert identities[0].llvm_opcode == "t2RBIT"
    assert identities[0].encoding == (0x91, 0xFA, 0xA1, 0xF0)


def test_form_matching_does_not_collapse_shapes_or_concrete_immediates() -> None:
    assert not instruction_form_matches(
        "ADD Vd.4S, Vn.4S, Vm.4S",
        "ADD Vd.2D, Vn.2D, Vm.2D",
    )
    assert not instruction_form_matches("LSL Xd, Xn, #1", "LSL Xd, Xn, #7")
    assert not instruction_form_matches("LSL Xd, Xn, #imm", "LSL Xd, Xn, #7")


def test_reviewed_intrinsic_mapping_is_exact_and_family_scoped() -> None:
    records = (
        PerformanceRecord(
            microarchitecture="Neoverse N2",
            instruction_form="ADD Vd.4S, Vn.4S, Vm.4S",
        ),
        PerformanceRecord(
            microarchitecture="Cortex-M55",
            instruction_form="VADD.I32 Qd, Qn, Qm",
        ),
        PerformanceRecord(
            microarchitecture="Neoverse N2",
            instruction_form="ADD Zdn.S, Pg/M, Zdn.S, Zm.S",
        ),
    )

    assert match_representative_performance_records(
        ("vaddq_s32",), records, family="neon"
    ) == (records[0],)
    assert match_representative_performance_records(
        ("vaddq_s32",), records, family="mve"
    ) == (records[1],)
    assert match_representative_performance_records(
        ("svadd_s32_x",), records, family="sve"
    ) == (records[2],)
    assert representative_probes_for_intrinsic_names(("svadd_s32",), family="sve") == ()


@pytest.mark.parametrize(
    ("name", "family", "expected_probe", "expected_form"),
    [
        ("vsubq_s32", "neon", "neon-sub-4s", "SUB Vd.4S, Vn.4S, Vm.4S"),
        ("vandq_u64", "neon", "neon-and-16b", "AND Vd.16B, Vn.16B, Vm.16B"),
        (
            "svmul_u32_x",
            "sve",
            "sve-mul-s-predicated",
            "MUL Zdn.S, Pg/M, Zdn.S, Zm.S",
        ),
        (
            "sveor_s32_x",
            "sve2",
            "sve-eor-s-predicated",
            "EOR Zdn.S, Pg/M, Zdn.S, Zm.S",
        ),
        ("vsubq_f32", "mve", "mve-sub-f32", "VSUB.F32 Qd, Qn, Qm"),
        ("vminq_u32", "mve", "mve-min-u32", "VMIN.U32 Qd, Qn, Qm"),
    ],
)
def test_common_operation_probes_are_explicit_and_family_scoped(
    name: str,
    family: str,
    expected_probe: str,
    expected_form: str,
) -> None:
    probes = representative_probes_for_intrinsic_names((name,), family=family)

    assert [(probe.id, probe.documented_form) for probe in probes] == [
        (expected_probe, expected_form)
    ]


@pytest.mark.parametrize(
    ("name", "signature_width_bits", "target_abi", "expected"),
    [
        (
            "__rbit",
            32,
            "aarch64-lp64",
            ("a64-rbit-w", "RBIT Wd, Wn", "rbit w0, w1"),
        ),
        (
            "__rbitl",
            64,
            "aarch64-lp64",
            ("a64-rbit-x", "RBIT Xd, Xn", "rbit x0, x1"),
        ),
        (
            "__rbitl",
            32,
            "aarch32-ilp32",
            ("mve-rbit", "RBIT Rd, Rn", "rbit r0, r1"),
        ),
        (
            "__rbitll",
            64,
            "aarch64-lp64",
            ("a64-rbit-x", "RBIT Xd, Xn", "rbit x0, x1"),
        ),
        (
            "__clz",
            32,
            "aarch64-lp64",
            ("a64-clz-w", "CLZ Wd, Wn", "clz w0, w1"),
        ),
        (
            "__clzl",
            64,
            "aarch64-lp64",
            ("a64-clz-x", "CLZ Xd, Xn", "clz x0, x1"),
        ),
        (
            "__clzl",
            32,
            "aarch32-ilp32",
            ("mve-clz", "CLZ Rd, Rn", "clz r0, r1"),
        ),
        (
            "__clzll",
            64,
            "aarch64-lp64",
            ("a64-clz-x", "CLZ Xd, Xn", "clz x0, x1"),
        ),
        (
            "__rev16",
            32,
            "aarch64-lp64",
            ("a64-rev16-w", "REV16 Wd, Wn", "rev16 w0, w1"),
        ),
        (
            "__rev16l",
            64,
            "aarch64-lp64",
            ("a64-rev16-x", "REV16 Xd, Xn", "rev16 x0, x1"),
        ),
        (
            "__rev16l",
            32,
            "aarch32-ilp32",
            ("mve-rev16", "REV16 Rd, Rn", "rev16 r0, r1"),
        ),
        (
            "__rev16ll",
            64,
            "aarch64-lp64",
            ("a64-rev16-x", "REV16 Xd, Xn", "rev16 x0, x1"),
        ),
    ],
)
def test_scalar_intrinsic_signature_width_and_target_abi_select_exact_probe(
    name: str,
    signature_width_bits: int,
    target_abi: performance.LLVMTargetABI,
    expected: tuple[str, str, str],
) -> None:
    probes = representative_probes_for_intrinsic_names(
        (name,),
        family="general",
        signature_width_bits=signature_width_bits,
        target_abi=target_abi,
    )

    assert [(probe.id, probe.documented_form, probe.assembly) for probe in probes] == [
        expected
    ]


@pytest.mark.parametrize("name", ["__rbitll", "__clzll", "__rev16ll"])
def test_fixed_64_bit_scalar_intrinsics_do_not_claim_one_aarch32_register_probe(
    name: str,
) -> None:
    assert (
        representative_probes_for_intrinsic_names(
            (name,),
            family="general",
            signature_width_bits=64,
            target_abi="aarch32-ilp32",
        )
        == ()
    )


@pytest.mark.parametrize(
    ("name", "signature_operand_type", "expected_forms"),
    [
        ("__rbitl", "unsigned long", ("RBIT Xd, Xn", "RBIT Rd, Rn")),
        ("__clzl", "unsigned long", ("CLZ Xd, Xn", "CLZ Rd, Rn")),
        (
            "__rev16",
            "uint32_t",
            ("REV16 Wd, Wn", "REV16 Rd, Rn"),
        ),
        (
            "__rev16l",
            "unsigned long",
            ("REV16 Xd, Xn", "REV16 Rd, Rn"),
        ),
    ],
)
def test_scalar_record_matching_uses_signature_width_for_each_profile_abi(
    name: str,
    signature_operand_type: str,
    expected_forms: tuple[str, ...],
) -> None:
    records = tuple(
        PerformanceRecord(
            microarchitecture=cpu,
            cpu=cpu,
            instruction_form=form,
        )
        for cpu, form in (
            ("neoverse-n2", "RBIT Wd, Wn"),
            ("neoverse-n2", "RBIT Xd, Xn"),
            ("cortex-m55", "RBIT Rd, Rn"),
            ("neoverse-n2", "CLZ Wd, Wn"),
            ("neoverse-n2", "CLZ Xd, Xn"),
            ("cortex-m55", "CLZ Rd, Rn"),
            ("neoverse-n2", "REV Wd, Wn"),
            ("cortex-m55", "REV Rd, Rn"),
            ("neoverse-n2", "REV16 Wd, Wn"),
            ("neoverse-n2", "REV16 Xd, Xn"),
            ("cortex-m55", "REV16 Rd, Rn"),
        )
    )

    matches = match_representative_performance_records(
        (name,),
        records,
        family="general",
        signature_operand_type=signature_operand_type,
    )

    assert tuple(record.instruction_form for record in matches) == expected_forms


def test_mve_load_printer_alias_matches_database_element_width_form() -> None:
    assert instruction_form_matches(
        "vldrw.u32 q0, [r0]",
        "VLDRW.32 Qd, [Rn]",
    )


def test_unavailable_records_explain_missing_model_or_exact_form() -> None:
    sme = performance_unavailable_record("sme")
    generic = performance_unavailable_record("neon")

    assert sme.unresolved_reason is not None
    assert (
        "does not provide an applicable CPU scheduling model" in sme.unresolved_reason
    )
    assert generic.unresolved_reason is not None
    assert "No exact, assembler-validated representative" in generic.unresolved_reason
    assert not generic.latency.is_resolved
    assert not generic.reciprocal_throughput.is_resolved


def test_record_matching_is_scoped_by_cpu_and_is_exact_by_default() -> None:
    dataset = load_performance_manifest(FIXTURES / "llvm_mca_neoverse_n2.manifest.json")

    matches = match_performance_records(
        "ADD Vd.4S,Vn.4S,Vm.4S",
        dataset.records,
        cpu="neoverse-n2",
    )
    assert [(match.quality, match.record.cpu) for match in matches] == [
        ("exact", "neoverse-n2")
    ]
    assert (
        match_performance_records(
            "ADD Vd.4S,Vn.4S,Vm.4S",
            dataset.records,
            cpu="cortex-a55",
        )
        == ()
    )
    assert match_performance_records("ADD", dataset.records) == ()
    assert [
        match.quality
        for match in match_performance_records(
            "ADD", dataset.records, allow_mnemonic_only=True
        )
    ] == ["mnemonic_only"]


@pytest.mark.parametrize(
    "source_update, expected_message",
    [
        (
            {
                "evidence_kind": "measured",
                "tool": None,
            },
            "requires source.methodology and source.hardware",
        ),
        (
            {
                "evidence_kind": "compiler_model",
                "confidence": "high",
            },
            "compiler_model confidence cannot be high",
        ),
    ],
)
def test_evidence_classes_fail_closed_without_required_metadata(
    source_update: dict[str, object], expected_message: str
) -> None:
    payload = _manifest_payload()
    source = payload["source"]
    assert isinstance(source, dict)
    source.update(source_update)

    with pytest.raises(PerformanceFormatError, match=expected_message):
        parse_performance_manifest(payload)


def test_manifest_hash_mismatch_is_rejected(tmp_path: Path) -> None:
    data_path = tmp_path / "records.json"
    data_path.write_text("[]\n", encoding="utf-8")
    payload = _manifest_payload()
    data = payload["data"]
    assert isinstance(data, dict)
    data["file"] = data_path.name
    data["format"] = "normalized-json"
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(PerformanceFormatError, match="SHA-256 mismatch"):
        load_performance_manifest(manifest_path)


def test_llvm_runner_uses_safe_argv_version_gate_and_model_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_json = (FIXTURES / "llvm_mca_neoverse_n2.json").read_text(encoding="utf-8")
    invocations: list[tuple[list[str], str | None]] = []

    def fake_run(argv: list[str], **kwargs: object) -> SimpleNamespace:
        input_text = kwargs.get("input")
        invocations.append(
            (
                argv,
                input_text if isinstance(input_text, str) else None,
            )
        )
        if argv[-1] == "--version":
            return SimpleNamespace(
                returncode=0,
                stdout="Homebrew LLVM version 22.1.1\n",
                stderr="",
            )
        return SimpleNamespace(returncode=0, stdout=raw_json, stderr="")

    monkeypatch.setattr(performance.subprocess, "run", fake_run)
    source_ref = SourceRef(
        id="llvm-aarch64-22.1.1",
        repository="llvm/llvm-project",
        commit="llvmorg-22.1.1",
        path="llvm/lib/Target/AArch64",
        license_id="Apache-2.0 WITH LLVM-exception",
    )
    dataset = run_llvm_mca(
        "add v0.4s, v1.4s, v2.4s\ncrc32w w0, w1, w2\n",
        executable=Path("/opt/llvm/bin/llvm-mca"),
        expected_tool_version="22.1.1",
        march="aarch64",
        mcpu="neoverse-n2",
        microarchitecture="Neoverse N2",
        source_ref=source_ref,
        mattr=("+sve2",),
        mtriple="aarch64-apple-darwin25.6.0",
    )

    assert invocations[0][0] == ["/opt/llvm/bin/llvm-mca", "--version"]
    assert invocations[1][0] == [
        "/opt/llvm/bin/llvm-mca",
        "--json",
        "--instruction-tables=full",
        "-march=aarch64",
        "-mcpu=neoverse-n2",
        "-iterations=1",
        "-mattr=+sve2",
        "-mtriple=aarch64-apple-darwin25.6.0",
    ]
    assert invocations[1][1] is not None
    assert dataset.records[0].evidence_kind is PerformanceEvidenceKind.COMPILER_MODEL
    assert dataset.manifest.source.raw_data_sha256 is not None


def test_llvm_runner_rejects_tool_version_drift(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        performance.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0,
            stdout="LLVM version 23.0.0\n",
            stderr="",
        ),
    )
    source_ref = SourceRef(
        id="llvm-test",
        repository="llvm/llvm-project",
        commit="llvmorg-22.1.1",
        path="llvm/lib/Target/AArch64",
    )

    with pytest.raises(LLVMToolError, match="version mismatch"):
        run_llvm_mca(
            "add x0, x1, x2\n",
            executable=Path("llvm-mca"),
            expected_tool_version="22.1.1",
            march="aarch64",
            mcpu="neoverse-n2",
            microarchitecture="Neoverse N2",
            source_ref=source_ref,
        )


def test_representative_probe_catalog_covers_all_six_profiles_without_fuzzy_keys() -> (
    None
):
    profile_cpus = {profile.cpu for profile in LLVM_22_1_1_PROFILES}
    covered_cpus = {
        cpu for probe in LLVM_22_1_1_REPRESENTATIVE_PROBES for cpu in probe.profiles
    }

    assert covered_cpus == profile_cpus
    assert len(LLVM_22_1_1_PROFILES) == 6
    assert {probe.family for probe in LLVM_22_1_1_REPRESENTATIVE_PROBES} >= {
        "general",
        "neon",
        "mve",
        "sve",
        "sve2",
    }
    assert len({probe.id for probe in LLVM_22_1_1_REPRESENTATIVE_PROBES}) == len(
        LLVM_22_1_1_REPRESENTATIVE_PROBES
    )
    assert all(probe.intrinsic_examples for probe in LLVM_22_1_1_REPRESENTATIVE_PROBES)


def test_default_performance_builder_rejects_unknown_and_duplicate_profiles() -> None:
    with pytest.raises(PerformanceFormatError, match="unsupported LLVM"):
        build_default_performance_datasets(
            llvm_mca=Path("llvm-mca"),
            profiles=("not-a-real-cpu",),
        )
    with pytest.raises(PerformanceFormatError, match="must be unique"):
        build_default_performance_datasets(
            llvm_mca=Path("llvm-mca"),
            profiles=("neoverse-n2", "neoverse-n2"),
        )


@pytest.mark.parametrize(
    ("cpu", "expected_march", "expected_backend"),
    [
        ("cortex-a55", "aarch64", "llvm/lib/Target/AArch64"),
        ("neoverse-n1", "aarch64", "llvm/lib/Target/AArch64"),
        ("neoverse-v1", "aarch64", "llvm/lib/Target/AArch64"),
        ("neoverse-n2", "aarch64", "llvm/lib/Target/AArch64"),
        ("cortex-m55", "arm", "llvm/lib/Target/ARM"),
        ("cortex-m85", "arm", "llvm/lib/Target/ARM"),
    ],
)
def test_standard_profile_uses_its_own_llvm_backend_provenance(
    monkeypatch: pytest.MonkeyPatch,
    cpu: str,
    expected_march: str,
    expected_backend: str,
) -> None:
    captured: dict[str, object] = {}
    marker = object()

    def fake_run_llvm_mca(assembly: str, **kwargs: object) -> object:
        captured["assembly"] = assembly
        captured.update(kwargs)
        return marker

    monkeypatch.setattr(performance, "run_llvm_mca", fake_run_llvm_mca)

    result = performance.run_llvm_22_1_1_profile(
        "rbit r0, r1\n",
        executable=Path("llvm-mca"),
        cpu=cpu,
    )

    assert result is marker
    assert captured["march"] == expected_march
    source_ref = captured["source_ref"]
    assert isinstance(source_ref, SourceRef)
    assert source_ref.path == expected_backend
    assert source_ref.url is not None
    assert source_ref.url.endswith(expected_backend)


@pytest.mark.skipif(
    not Path("/opt/homebrew/opt/llvm/bin/llvm-mca").is_file()
    or not Path("/opt/homebrew/opt/llvm/bin/llvm-mc").is_file(),
    reason="Homebrew LLVM 22.1.1 tools are not installed",
)
def test_representative_probe_set_runs_on_pinned_llvm_22_1_1() -> None:
    llvm_mca = Path("/opt/homebrew/opt/llvm/bin/llvm-mca")
    version = subprocess.run(
        [str(llvm_mca), "--version"],
        check=False,
        capture_output=True,
        text=True,
    ).stdout
    if "version 22.1.1" not in version:
        pytest.skip("installed Homebrew llvm-mca is not version 22.1.1")

    datasets = build_default_performance_datasets(llvm_mca=llvm_mca)

    assert [dataset.manifest.cpu for dataset in datasets] == [
        profile.cpu for profile in LLVM_22_1_1_PROFILES
    ]
    assert all(dataset.records for dataset in datasets)
    assert all(
        record.latency.is_resolved
        or record.reciprocal_throughput.is_resolved
        or record.uops.is_resolved
        for dataset in datasets
        for record in dataset.records
    )
    assert all(
        record.reciprocal_throughput.is_resolved and record.uops.is_resolved
        for dataset in datasets
        for record in dataset.records
    )
    assert all(record.resources for dataset in datasets for record in dataset.records)
    for dataset in datasets:
        expected_backend = (
            "llvm/lib/Target/ARM"
            if dataset.manifest.architecture == "arm"
            else "llvm/lib/Target/AArch64"
        )
        assert dataset.manifest.source.source_ref.path == expected_backend
        for record in dataset.records:
            assert record.provenance.sources[0].path == expected_backend
            for metric in (
                record.latency,
                record.reciprocal_throughput,
                record.uops,
            ):
                if metric.is_resolved:
                    assert metric.provenance.sources[0].path == expected_backend
            assert record.resources_provenance.sources[0].path == expected_backend
    assert all(
        "LLVM scheduling model estimate, not measured hardware data." in record.notes
        for dataset in datasets
        for record in dataset.records
    )
    assert (
        len(
            {
                (
                    record.latency.value.minimum if record.latency.value else None,
                    record.reciprocal_throughput.value.minimum
                    if record.reciprocal_throughput.value
                    else None,
                    record.uops.value.minimum if record.uops.value else None,
                )
                for dataset in datasets
                for record in dataset.records
            }
        )
        > 3
    )


def _manifest_payload() -> dict[str, object]:
    return {
        "schema_version": 1,
        "architecture": "aarch64",
        "microarchitecture": "Neoverse N2",
        "cpu": "neoverse-n2",
        "data": {
            "file": "records.json",
            "format": "llvm-mca-json",
            "sha256": "0" * 64,
        },
        "source": {
            "evidence_kind": "compiler_model",
            "name": "LLVM schedule model",
            "version": "22.1.1",
            "confidence": "medium",
            "source_ref": {
                "id": "llvm-test",
                "repository": "llvm/llvm-project",
                "commit": "llvmorg-22.1.1",
                "path": "llvm/lib/Target/AArch64",
            },
            "tool": {"name": "llvm-mca", "version": "22.1.1"},
            "notes": ["Test fixture."],
        },
    }
