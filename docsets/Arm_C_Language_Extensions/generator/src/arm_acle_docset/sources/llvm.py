"""Parse public Arm ACLE declarations from pinned Clang resource headers.

LLVM is a declaration oracle, not the semantic source for the docset.  The
adapter consumes headers that Clang generated from its TableGen descriptions
and preserves the LLVM builtin-alias identity.  That identity is the reliable
link between a concrete spelling and its C/C++ overloaded spellings.

The upstream llvm-project source archive does not contain generated
``arm_sve.h``, ``arm_sme.h``, or ``arm_mve.h`` files.  Reproducible builds must
therefore either:

* pass the resource include directory from the pinned LLVM 22.1.1 toolchain;
  or
* consume a normalized inventory previously produced by this module.

No developer.arm.com data is used here.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Literal, Mapping, Sequence

from ..model import (
    Alias,
    AvailabilityExpr,
    CallableKind,
    CompilationRequirements,
    ConcreteCallable,
    Diagnostic,
    FieldProvenance,
    Maturity,
    NameRole as ModelNameRole,
    Parameter,
    Provenance,
    ProvenanceKind,
    Semantics,
    Signature,
    SourceRef,
)
from ..normalize import normalize_callable, parse_availability_guard


LLVM_RELEASE_TAG = "llvmorg-22.1.1"
LLVM_COMMIT = "fef02d48c08db859ef83f84232ed78bd9d1c323a"
LLVM_LICENSE = "Apache-2.0 WITH LLVM-exception"
LLVM_TOOL_VERSION = "22.1.1"

# These hashes describe the resource headers generated from the eight pinned
# TableGen files with clang-tblgen 22.1.1.  The same bytes are present in the
# matching Homebrew LLVM bottle.  A different official artifact must provide
# its own explicit hash mapping rather than silently claiming to be this input.
PINNED_HEADER_SHA256: Mapping[str, str] = {
    "arm_sve.h": "52c7dd2eb8ddb280ce24d041a6504d1d5937cc46a288ec78c0041d14ec71ce72",
    "arm_sme.h": "0dae22d987ada9594b197285e1f1528b1c51eafd4579345d2949367c3e788943",
    "arm_mve.h": "8e6fa1bb91c0e5403e6f6152380b4ff318833028b0d4e9c91911e4dd107bd762",
    "arm_neon.h": "ed8fc4135aef7c5af5f30ca3715d96ee9ad5a2bc97f558214fadda5704742b26",
}

LLVM_TABLEGEN_FILES: tuple[str, ...] = (
    "arm_immcheck_incl.td",
    "arm_neon.td",
    "arm_neon_incl.td",
    "arm_mve.td",
    "arm_mve_defs.td",
    "arm_sve.td",
    "arm_sme.td",
    "arm_sve_sme_incl.td",
)
_HEADER_GENERATORS: Mapping[str, tuple[str, str]] = {
    "arm_sve.h": ("-gen-arm-sve-header", "arm_sve.td"),
    "arm_sme.h": ("-gen-arm-sme-header", "arm_sme.td"),
    "arm_mve.h": ("-gen-arm-mve-header", "arm_mve.td"),
    "arm_neon.h": ("-gen-arm-neon", "arm_neon.td"),
}

_HEADER_FAMILIES: Mapping[str, Literal["sve", "sme", "mve", "neon"]] = {
    "arm_sve.h": "sve",
    "arm_sme.h": "sme",
    "arm_mve.h": "mve",
    "arm_neon.h": "neon",
}
_BUILTIN_ALIAS_RE = re.compile(
    r"__clang_arm_builtin_alias\(\s*(?P<builtin>__builtin_[A-Za-z0-9_]+)\s*\)"
)
_TARGET_ATTRIBUTE_RE = re.compile(
    r"__attribute__\s*\(\(\s*target\s*\(\s*"
    r'"(?P<features>(?:\\.|[^\"])*)"\s*\)\s*\)\)'
)
_FUNCTION_NAME_RE = re.compile(r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*$")
_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_WHITESPACE_RE = re.compile(r"\s+")
_LEADING_STORAGE_RE = re.compile(
    r"^(?:(?:static|extern|inline|__inline__|__inline|__ai|__aio)\s+)+"
)
_PUBLIC_NAME_PREFIXES: Mapping[str, tuple[str, ...]] = {
    "sve": ("sv", "__arm_"),
    "sme": ("sv", "__arm_"),
    "mve": ("v", "__arm_v"),
    "neon": ("v",),
}
_CONTROL_PREFIXES = ("return ", "if ", "while ", "for ", "switch ")
_TYPE_KEYWORDS = {
    "_Bool",
    "bool",
    "char",
    "const",
    "double",
    "float",
    "int",
    "long",
    "restrict",
    "short",
    "signed",
    "unsigned",
    "void",
    "volatile",
}
_NORMALIZED_INVENTORY_SCHEMA = 1


Family = Literal["sve", "sme", "mve", "neon"]
NameRole = Literal["explicit", "overloaded"]
Namespace = Literal["prefixed", "unprefixed", "default"]


class LLVMFormatError(ValueError):
    """Raised when a generated header or normalized inventory is malformed."""


class LLVMPinMismatch(LLVMFormatError):
    """Raised when an input does not match its declared pinned digest."""


@dataclass(frozen=True, slots=True)
class LLVMSourceRef:
    """Line-addressable provenance for one generated Clang declaration."""

    repository: str
    commit: str
    release_tag: str
    header: str
    line: int
    sha256: str
    license: str = LLVM_LICENSE


@dataclass(frozen=True, slots=True)
class LLVMDiagnostic:
    """A conservative parser or completeness observation."""

    code: str
    message: str
    source_ref: LLVMSourceRef | None = None


@dataclass(frozen=True, slots=True)
class LLVMParameter:
    """A parameter as written in a generated resource header."""

    raw: str
    type: str
    name: str | None


@dataclass(frozen=True, slots=True)
class LLVMPrototype:
    """Normalized and raw forms of a public declaration."""

    raw: str
    return_type: str
    parameters: tuple[LLVMParameter, ...]
    attributes: tuple[str, ...] = ()

    @property
    def signature(self) -> str:
        parameters = ", ".join(parameter.type for parameter in self.parameters)
        return f"{self.return_type} ({parameters})"


@dataclass(frozen=True, slots=True)
class LLVMName:
    """One public spelling associated with a concrete LLVM builtin."""

    spelling: str
    role: NameRole
    namespace: Namespace
    availability: str | None
    source_ref: LLVMSourceRef


@dataclass(frozen=True, slots=True)
class LLVMCallable:
    """One concrete compiler declaration plus its public alias set."""

    family: Family
    builtin: str | None
    prototype: LLVMPrototype
    names: tuple[LLVMName, ...]
    source_refs: tuple[LLVMSourceRef, ...]
    target_features: tuple[str, ...] = ()
    diagnostics: tuple[LLVMDiagnostic, ...] = ()

    @property
    def explicit_names(self) -> tuple[str, ...]:
        return tuple(name.spelling for name in self.names if name.role == "explicit")

    @property
    def aliases(self) -> tuple[str, ...]:
        return tuple(name.spelling for name in self.names if name.role == "overloaded")

    @property
    def primary_name(self) -> str:
        if self.explicit_names:
            return self.explicit_names[0]
        return self.names[0].spelling


@dataclass(frozen=True, slots=True)
class LLVMInventory:
    """Deterministic declaration inventory for one pinned LLVM input."""

    release_tag: str
    commit: str
    header_sha256: tuple[tuple[str, str], ...]
    callables: tuple[LLVMCallable, ...]
    diagnostics: tuple[LLVMDiagnostic, ...] = ()

    def canonical_data(self) -> dict[str, object]:
        """Return stable JSON-compatible data for vendoring or review."""

        return {
            "schema_version": _NORMALIZED_INVENTORY_SCHEMA,
            "release_tag": self.release_tag,
            "commit": self.commit,
            "license": LLVM_LICENSE,
            "header_sha256": dict(self.header_sha256),
            "callables": [_callable_data(callable_) for callable_ in self.callables],
            "diagnostics": [_diagnostic_data(item) for item in self.diagnostics],
        }

    def canonical_json(self) -> str:
        """Serialize with stable ordering and a trailing newline."""

        return (
            json.dumps(
                self.canonical_data(),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )


@dataclass(frozen=True, slots=True)
class LLVMTargetGuard:
    """One TableGen intrinsic spelling with its scoped SVE/SME guards."""

    spelling: str
    sve_guard: AvailabilityExpr | None
    sme_guard: AvailabilityExpr | None
    source: SourceRef
    record_name: str | None = None
    record_class: str | None = None
    name_pattern: str | None = None
    prototype: str | None = None
    type_spec: str | None = None
    merge_suffix: str | None = None
    diagnostics: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class _RawDeclaration:
    family: Family
    header: str
    name: str
    builtin: str | None
    prototype: LLVMPrototype
    source_ref: LLVMSourceRef
    namespace: Namespace
    availability: str | None
    target_features: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _PinnedSInstExpansion:
    """One direct SInst identity expanded from an exact pinned defm."""

    record_name: str
    name_pattern: str
    prototype: str
    type_spec: str


# These are the only multiclass layouts whose definitions in the pinned
# arm_sve.td are interpreted here.  The value is the zero-based template
# argument containing the SVE type string; unknown multiclasses stay opaque.
_TABLEGEN_MULTICLASS_TYPE_ARGUMENTS: Mapping[str, int] = {
    "SInstZPZ": 1,
    "SInstZPZZ": 1,
    "SInstZPZZZ": 1,
    "SInstZPZxZ": 1,
    "SInstWideDSPAcc": 1,
    "SInstCvtMXZ": 3,
    "SInstCvtMX": 3,
}
_TABLEGEN_MERGE_SUFFIXES: Mapping[str, str] = {
    "MergeNone": "",
    "MergeOp1": "_m",
    "MergeAny": "_x",
    "MergeAnyExp": "_x",
    "MergeZero": "_z",
    "MergeZeroExp": "_z",
}
_PINNED_MINMAX_DEFM_ARGUMENTS: Mapping[str, tuple[str, str, str, str]] = {
    "MAX_SINGLE_X2": ("max", "_single", "x2", "22d"),
    "MAX_MULTI_X2": ("max", "", "x2", "222"),
    "MAX_SINGLE_X4": ("max", "_single", "x4", "44d"),
    "MAX_MULTI_X4": ("max", "", "x4", "444"),
    "MIN_SINGLE_X2": ("min", "_single", "x2", "22d"),
    "MIN_MULTI_X2": ("min", "", "x2", "222"),
    "MIN_SINGLE_X4": ("min", "_single", "x4", "44d"),
    "MIN_MULTI_X4": ("min", "", "x4", "444"),
}
_PINNED_BF_MULTI_VECTOR_ARGUMENTS: Mapping[str, str] = {
    "SVBFMIN": "min",
    "SVBFMAX": "max",
    "SVBFMINNM": "minnm",
    "SVBFMAXNM": "maxnm",
    "SVBFMUL": "mul",
}
_PINNED_MINMAX_BY_VECTOR_ARGUMENTS: Mapping[str, str] = {
    "SVMAXNM": "max",
    "SVMINNM": "min",
}
_PINNED_MINMAX_DEFM_RE = re.compile(
    r"\s*defm\s+(?P<record>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*"
    r"MinMaxIntr\s*<\s*\"(?P<operation>(?:\\.|[^\"])*)\"\s*,\s*"
    r"\"(?P<zeroing_mode>(?:\\.|[^\"])*)\"\s*,\s*"
    r"\"(?P<multiplicity>(?:\\.|[^\"])*)\"\s*,\s*"
    r"\"(?P<prototype>(?:\\.|[^\"])*)\"\s*>\s*;\s*",
    re.DOTALL,
)
_PINNED_BF_MULTI_VECTOR_DEFM_RE = re.compile(
    r"\s*defm\s+(?P<record>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*"
    r"BfSingleMultiVector\s*<\s*"
    r"\"(?P<operation>(?:\\.|[^\"])*)\"\s*>\s*;\s*",
    re.DOTALL,
)
_PINNED_MINMAX_BY_VECTOR_DEFM_RE = re.compile(
    r"\s*defm\s+(?P<record>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*"
    r"SInstMinMaxByVector\s*<\s*"
    r'"(?P<operation>(?:\\.|[^\"])*)"\s*>\s*;\s*',
    re.DOTALL,
)


def _expand_pinned_sve_defm(
    statement: str,
) -> tuple[int, tuple[_PinnedSInstExpansion, ...]] | None:
    """Expand only defm layouts whose complete pinned identity is known."""

    minmax_match = _PINNED_MINMAX_DEFM_RE.fullmatch(statement)
    if minmax_match is not None:
        record_name = minmax_match.group("record")
        arguments = (
            minmax_match.group("operation"),
            minmax_match.group("zeroing_mode"),
            minmax_match.group("multiplicity"),
            minmax_match.group("prototype"),
        )
        if _PINNED_MINMAX_DEFM_ARGUMENTS.get(record_name) != arguments:
            return None
        operation, zeroing_mode, multiplicity, prototype = arguments
        pattern = f"sv{operation}[{zeroing_mode}_{{d}}_{multiplicity}]"
        return minmax_match.start("record"), tuple(
            _PinnedSInstExpansion(
                record_name=f"{prefix}{record_name}",
                name_pattern=pattern,
                prototype=prototype,
                type_spec=type_spec,
            )
            for prefix, type_spec in (
                ("SVS", "csil"),
                ("SVU", "UcUsUiUl"),
                ("SVF", "hfd"),
            )
        )

    bf_match = _PINNED_BF_MULTI_VECTOR_DEFM_RE.fullmatch(statement)
    if bf_match is not None:
        record_name = bf_match.group("record")
        operation = bf_match.group("operation")
        if _PINNED_BF_MULTI_VECTOR_ARGUMENTS.get(record_name) != operation:
            return None
        return bf_match.start("record"), tuple(
            _PinnedSInstExpansion(
                record_name=f"{record_name}{record_suffix}",
                name_pattern=f"sv{operation}[{name_suffix}]",
                prototype=prototype,
                type_spec="b",
            )
            for record_suffix, name_suffix, prototype in (
                ("_SINGLE_X2", "_single_{d}_x2", "22d"),
                ("_SINGLE_X4", "_single_{d}_x4", "44d"),
                ("_X2", "_{d}_x2", "222"),
                ("_X4", "_{d}_x4", "444"),
            )
        )

    minmax_by_vector_match = _PINNED_MINMAX_BY_VECTOR_DEFM_RE.fullmatch(statement)
    if minmax_by_vector_match is None:
        return None
    record_name = minmax_by_vector_match.group("record")
    operation = minmax_by_vector_match.group("operation")
    if _PINNED_MINMAX_BY_VECTOR_ARGUMENTS.get(record_name) != operation:
        return None
    return minmax_by_vector_match.start("record"), tuple(
        _PinnedSInstExpansion(
            record_name=f"{record_name}{record_suffix}",
            name_pattern=f"sv{operation}nm[{name_suffix}]",
            prototype=prototype,
            type_spec="hfd",
        )
        for record_suffix, name_suffix, prototype in (
            ("_SINGLE_X2", "_single_{d}_x2", "22d"),
            ("_SINGLE_X4", "_single_{d}_x4", "44d"),
            ("_X2", "_{d}_x2", "222"),
            ("_X4", "_{d}_x4", "444"),
        )
    )


def parse_sve_target_guards(
    text: str,
    *,
    path: str = "clang/include/clang/Basic/arm_sve.td",
    commit: str = LLVM_COMMIT,
) -> tuple[LLVMTargetGuard, ...]:
    """Parse scoped target guards from the pinned ``arm_sve.td`` structure.

    This is deliberately a narrow TableGen parser. It understands nested
    ``let ... in {}`` scopes and terminated ``def``/``defm`` records while
    ignoring braces and semicolons in comments or strings. It does not try to
    evaluate arbitrary TableGen classes. Direct Inst/SInst/MInst identities
    and a small allowlist of pinned multiclass layouts are recognized; every
    other multiclass stays opaque.
    """

    cleaned = _strip_tablegen_comments(text)
    scopes: list[dict[str, str | None]] = [{"sve": "sve", "sme": "sme"}]
    records: list[LLVMTargetGuard] = []
    segment_start = 0
    in_string = False
    escaped = False

    for index, character in enumerate(cleaned):
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            continue
        if character == '"':
            in_string = True
            continue
        if character == "{":
            prefix = cleaned[segment_start:index]
            scoped = dict(scopes[-1])
            let_match = re.search(
                r"\blet\s+(?P<body>.*?)\s*\bin\s*$",
                prefix,
                re.DOTALL,
            )
            if let_match is not None:
                scoped.update(_tablegen_guard_assignments(let_match.group("body")))
            scopes.append(scoped)
            segment_start = index + 1
            continue
        if character == "}":
            if len(scopes) == 1:
                raise LLVMFormatError("arm_sve.td has an unmatched closing brace")
            scopes.pop()
            segment_start = index + 1
            continue
        if character != ";":
            continue

        statement = cleaned[segment_start : index + 1]
        statement_offset = segment_start
        segment_start = index + 1
        pinned_expansion = _expand_pinned_sve_defm(statement)
        if pinned_expansion is not None:
            record_offset, expanded_records = pinned_expansion
            line = cleaned.count("\n", 0, statement_offset + record_offset) + 1
            sve_guard, sme_guard, diagnostics = _tablegen_scope_guards(scopes[-1])
            source = _tablegen_target_guard_source(
                path=path,
                commit=commit,
                line=line,
            )
            records.extend(
                LLVMTargetGuard(
                    spelling=expanded.name_pattern.split("[", 1)[0],
                    sve_guard=sve_guard,
                    sme_guard=sme_guard,
                    source=source,
                    record_name=expanded.record_name,
                    record_class="SInst",
                    name_pattern=expanded.name_pattern,
                    prototype=expanded.prototype,
                    type_spec=expanded.type_spec,
                    merge_suffix="",
                    diagnostics=diagnostics,
                )
                for expanded in expanded_records
            )
            continue
        record_match = re.search(
            r"\b(?P<kind>def|defm)\s+"
            r"(?P<record>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*"
            r"(?P<class>[A-Za-z_][A-Za-z0-9_]*)\s*"
            r"<\s*\"(?P<pattern>sv[^\"]+)\"",
            statement,
            re.DOTALL,
        )
        if record_match is None:
            continue
        name_pattern = record_match.group("pattern")
        record_kind = record_match.group("kind")
        record_class = record_match.group("class")
        emitted_record_class = (
            "SInst" if record_kind == "def" and record_class == "Inst" else record_class
        )
        string_arguments = (
            name_pattern,
            *_leading_tablegen_string_arguments(statement[record_match.end() :]),
        )
        prototype = None
        type_spec = None
        merge_suffix = None
        if record_kind == "def" and record_class in {"Inst", "SInst", "MInst"}:
            if len(string_arguments) >= 3:
                prototype = string_arguments[1]
                type_spec = string_arguments[2]
            if record_class == "MInst":
                # The pinned MInst class lowers to SInst with MergeNone; its
                # fourth argument is a flag list, not a MergeType parameter.
                merge_suffix = ""
            else:
                merge_match = re.match(
                    r"\s*,\s*\"(?:\\.|[^\"])*\"\s*,\s*"
                    r"\"(?:\\.|[^\"])*\"\s*,\s*"
                    r"(?P<merge>[A-Za-z_][A-Za-z0-9_]*)",
                    statement[record_match.end() :],
                    re.DOTALL,
                )
                if merge_match is not None:
                    merge_suffix = _TABLEGEN_MERGE_SUFFIXES.get(
                        merge_match.group("merge")
                    )
                    if merge_suffix is not None and ">" in (prototype or ""):
                        merge_suffix += "_fpm"
        elif record_kind == "defm":
            type_argument = _TABLEGEN_MULTICLASS_TYPE_ARGUMENTS.get(record_class)
            if type_argument is not None and len(string_arguments) > type_argument:
                type_spec = string_arguments[type_argument]
        exact_direct_inst = (
            record_kind == "def"
            and record_class == "Inst"
            and prototype is not None
            and type_spec is not None
            and merge_suffix is not None
        )
        spelling = _tablegen_spelling_base(
            name_pattern,
            allow_placeholder_before_bracket=exact_direct_inst,
        )
        if spelling is None:
            continue
        line = cleaned.count("\n", 0, statement_offset + record_match.start()) + 1
        sve_guard, sme_guard, diagnostics = _tablegen_scope_guards(scopes[-1])
        records.append(
            LLVMTargetGuard(
                spelling=spelling,
                sve_guard=sve_guard,
                sme_guard=sme_guard,
                source=_tablegen_target_guard_source(
                    path=path,
                    commit=commit,
                    line=line,
                ),
                record_name=record_match.group("record"),
                record_class=emitted_record_class,
                name_pattern=name_pattern,
                prototype=prototype,
                type_spec=type_spec,
                merge_suffix=merge_suffix,
                diagnostics=diagnostics,
            )
        )

    if len(scopes) != 1:
        raise LLVMFormatError("arm_sve.td has an unclosed scoped brace")
    return tuple(records)


def _tablegen_spelling_base(
    name_pattern: str,
    *,
    allow_placeholder_before_bracket: bool,
) -> str | None:
    """Return the conservative public spelling prefix for one name pattern."""

    bracket = name_pattern.find("[")
    boundary = len(name_pattern) if bracket < 0 else bracket
    placeholder = re.search(r"\{(?:d|[0-3])\}", name_pattern[:boundary])
    if placeholder is not None:
        if not allow_placeholder_before_bracket:
            return None
        boundary = placeholder.start()
    spelling = name_pattern[:boundary].split("#", 1)[0].strip().rstrip("_")
    return spelling if re.fullmatch(r"sv[A-Za-z0-9_]+", spelling) else None


def _leading_tablegen_string_arguments(text: str) -> tuple[str, ...]:
    """Read consecutive simple string arguments following a parsed name.

    Stopping at the first non-string argument is intentional: it prevents a
    later string nested in flags or another expression from being mistaken for
    a positional multiclass parameter.
    """

    result = []
    remaining = text
    while True:
        match = re.match(
            r"\s*,\s*\"(?P<value>(?:\\.|[^\"])*)\"",
            remaining,
            re.DOTALL,
        )
        if match is None:
            break
        result.append(bytes(match.group("value"), "utf-8").decode("unicode_escape"))
        remaining = remaining[match.end() :]
    return tuple(result)


def load_sve_target_guards(path: Path) -> tuple[LLVMTargetGuard, ...]:
    """Load target guards from the verified pinned TableGen file."""

    return parse_sve_target_guards(Path(path).read_text(encoding="utf-8"))


def _tablegen_scope_guards(
    scope: Mapping[str, str | None],
) -> tuple[AvailabilityExpr | None, AvailabilityExpr | None, tuple[str, ...]]:
    sve_guard, sve_diagnostic = _parse_tablegen_guard(scope["sve"])
    sme_guard, sme_diagnostic = _parse_tablegen_guard(scope["sme"])
    diagnostics = tuple(
        detail
        for label, detail in (
            ("SVETargetGuard", sve_diagnostic),
            ("SMETargetGuard", sme_diagnostic),
        )
        if detail
        for detail in (f"{label}: {detail}",)
    )
    return sve_guard, sme_guard, diagnostics


def _tablegen_target_guard_source(*, path: str, commit: str, line: int) -> SourceRef:
    return SourceRef(
        id=f"llvm:{commit}:arm_sve.td:{line}",
        repository="llvm/llvm-project",
        commit=commit,
        path=path,
        start_line=line,
        end_line=line,
        license_id=LLVM_LICENSE,
        url=(f"https://github.com/llvm/llvm-project/blob/{commit}/{path}#L{line}"),
    )


def _parse_tablegen_guard(
    value: str | None,
) -> tuple[AvailabilityExpr | None, str | None]:
    if value is None or not value.strip():
        return None, None
    expression, diagnostic = parse_availability_guard(value)
    return expression, diagnostic


def _tablegen_guard_assignments(body: str) -> dict[str, str | None]:
    result: dict[str, str | None] = {}
    for match in re.finditer(
        r"(?P<mode>SVE|SME)TargetGuard\s*=\s*"
        r"(?P<value>InvalidMode|\"(?:\\.|[^\"])*\")",
        body,
        re.DOTALL,
    ):
        raw = match.group("value")
        result[match.group("mode").lower()] = (
            None
            if raw == "InvalidMode"
            else bytes(raw[1:-1], "utf-8").decode("unicode_escape")
        )
    return result


def _strip_tablegen_comments(text: str) -> str:
    output = list(text)
    index = 0
    in_string = False
    escaped = False
    while index < len(text):
        character = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            index += 1
            continue
        if character == '"':
            in_string = True
            index += 1
            continue
        if text.startswith("//", index):
            end = text.find("\n", index)
            end = len(text) if end < 0 else end
            for offset in range(index, end):
                output[offset] = " "
            index = end
            continue
        if text.startswith("/*", index):
            end = text.find("*/", index + 2)
            if end < 0:
                raise LLVMFormatError("arm_sve.td has an unclosed block comment")
            for offset in range(index, end + 2):
                if output[offset] != "\n":
                    output[offset] = " "
            index = end + 2
            continue
        index += 1
    return "".join(output)


def load_llvm_include_dir(
    include_dir: Path,
    *,
    expected_hashes: Mapping[str, str] | None = PINNED_HEADER_SHA256,
    release_tag: str = LLVM_RELEASE_TAG,
    commit: str = LLVM_COMMIT,
    headers: Sequence[str] = tuple(_HEADER_FAMILIES),
) -> LLVMInventory:
    """Parse generated resource headers from one explicit include directory.

    ``expected_hashes=None`` is intended for fixture and exploratory parsing.
    Release builds should always supply a complete hash mapping.
    """

    include_dir = Path(include_dir)
    all_callables: list[LLVMCallable] = []
    all_diagnostics: list[LLVMDiagnostic] = []
    digests: list[tuple[str, str]] = []

    for header in headers:
        if header not in _HEADER_FAMILIES:
            raise ValueError(f"unsupported LLVM resource header: {header!r}")
        path = include_dir / header
        if not path.is_file():
            raise LLVMFormatError(f"missing LLVM resource header: {path}")
        digest = _sha256(path)
        if expected_hashes is not None:
            expected = expected_hashes.get(header)
            if expected is None:
                raise LLVMPinMismatch(f"no pinned SHA-256 was provided for {header}")
            if digest != expected:
                raise LLVMPinMismatch(
                    f"{header} SHA-256 mismatch: expected {expected}, found {digest}"
                )

        parsed = parse_llvm_header(
            path.read_text(encoding="utf-8"),
            header=header,
            sha256=digest,
            release_tag=release_tag,
            commit=commit,
        )
        all_callables.extend(parsed.callables)
        all_diagnostics.extend(parsed.diagnostics)
        digests.append((header, digest))

    return LLVMInventory(
        release_tag=release_tag,
        commit=commit,
        header_sha256=tuple(sorted(digests)),
        callables=tuple(sorted(all_callables, key=_callable_sort_key)),
        diagnostics=tuple(all_diagnostics),
    )


def generate_headers(
    tablegen_dir: Path,
    clang_tblgen: Path,
    output_dir: Path,
    *,
    expected_hashes: Mapping[str, str] = PINNED_HEADER_SHA256,
    expected_version: str = LLVM_TOOL_VERSION,
    timeout_seconds: int = 120,
) -> LLVMInventory:
    """Generate the four resource headers from the pinned TableGen inputs.

    Only eight small files from the fixed llvm-project commit are required.
    The tool version and each generated byte stream are hard gates, so a local
    ``clang-tblgen`` cannot silently change the compiler declaration oracle.
    """

    tablegen_dir = Path(tablegen_dir)
    clang_tblgen = Path(clang_tblgen)
    output_dir = Path(output_dir)
    if not clang_tblgen.is_file():
        raise LLVMFormatError(f"clang-tblgen is not a file: {clang_tblgen}")
    missing = [
        name for name in LLVM_TABLEGEN_FILES if not (tablegen_dir / name).is_file()
    ]
    if missing:
        raise LLVMFormatError(
            "missing pinned LLVM TableGen inputs: " + ", ".join(sorted(missing))
        )
    unknown_hashes = set(expected_hashes) - set(_HEADER_GENERATORS)
    missing_hashes = set(_HEADER_GENERATORS) - set(expected_hashes)
    if unknown_hashes or missing_hashes:
        raise LLVMPinMismatch(
            "expected_hashes must cover exactly the generated headers; "
            f"missing={sorted(missing_hashes)!r}, unknown={sorted(unknown_hashes)!r}"
        )

    try:
        version = subprocess.run(
            [str(clang_tblgen), "--version"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        raise LLVMFormatError(
            f"cannot execute clang-tblgen --version: {error}"
        ) from error
    version_text = f"{version.stdout}\n{version.stderr}"
    if re.search(rf"\bversion\s+{re.escape(expected_version)}\b", version_text) is None:
        compact = _WHITESPACE_RE.sub(" ", version_text).strip()
        raise LLVMPinMismatch(
            f"clang-tblgen version mismatch: expected {expected_version}, found {compact!r}"
        )

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="arm-acle-llvm-headers-", dir=output_dir.parent
    ) as temporary:
        temporary_dir = Path(temporary)
        for header, (action, source_name) in _HEADER_GENERATORS.items():
            generated_path = temporary_dir / header
            command = [
                str(clang_tblgen),
                action,
                "-I",
                str(tablegen_dir),
                str(tablegen_dir / source_name),
                "-o",
                str(generated_path),
            ]
            try:
                subprocess.run(
                    command,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                )
            except subprocess.CalledProcessError as error:
                detail = _bounded_process_detail(error.stdout, error.stderr)
                raise LLVMFormatError(
                    f"clang-tblgen failed for {header}: {detail}"
                ) from error
            except (OSError, subprocess.TimeoutExpired) as error:
                raise LLVMFormatError(
                    f"cannot generate {header} with clang-tblgen: {error}"
                ) from error
            digest = _sha256(generated_path)
            if digest != expected_hashes[header]:
                raise LLVMPinMismatch(
                    f"generated {header} SHA-256 mismatch: expected "
                    f"{expected_hashes[header]}, found {digest}"
                )

        output_dir.mkdir(parents=True, exist_ok=True)
        for header in _HEADER_GENERATORS:
            (temporary_dir / header).replace(output_dir / header)

    return load_llvm_include_dir(
        output_dir,
        expected_hashes=expected_hashes,
        headers=tuple(_HEADER_GENERATORS),
    )


def parse_llvm_header(
    text: str,
    *,
    header: str,
    sha256: str,
    release_tag: str = LLVM_RELEASE_TAG,
    commit: str = LLVM_COMMIT,
) -> LLVMInventory:
    """Parse one generated Clang resource header from memory."""

    try:
        family = _HEADER_FAMILIES[header]
    except KeyError as error:
        raise ValueError(f"unsupported LLVM resource header: {header!r}") from error

    if not re.fullmatch(r"[0-9a-f]{64}", sha256):
        raise ValueError("sha256 must be a lowercase 64-character hexadecimal digest")

    declarations, diagnostics = _parse_declarations(
        text,
        family=family,
        header=header,
        sha256=sha256,
        release_tag=release_tag,
        commit=commit,
    )
    callables = _group_declarations(declarations)
    if family == "neon":
        diagnostics.append(
            LLVMDiagnostic(
                code="llvm.neon_macros_not_enumerated",
                message=(
                    "Function-like Neon macros are not used as declaration facts; "
                    "the Arm ACLE tabular source remains authoritative for Neon."
                ),
            )
        )

    return LLVMInventory(
        release_tag=release_tag,
        commit=commit,
        header_sha256=((header, sha256),),
        callables=tuple(sorted(callables, key=_callable_sort_key)),
        diagnostics=tuple(diagnostics),
    )


def write_normalized_inventory(inventory: LLVMInventory, path: Path) -> None:
    """Write a deterministic, reviewable inventory for later offline input."""

    Path(path).write_text(inventory.canonical_json(), encoding="utf-8")


def load_normalized_inventory(path: Path) -> LLVMInventory:
    """Load and validate an inventory produced by :func:`canonical_json`."""

    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise LLVMFormatError(
            f"cannot load normalized LLVM inventory: {error}"
        ) from error
    if not isinstance(data, dict):
        raise LLVMFormatError("normalized LLVM inventory must be a JSON object")
    if data.get("schema_version") != _NORMALIZED_INVENTORY_SCHEMA:
        raise LLVMFormatError(
            "unsupported normalized LLVM inventory schema: "
            f"{data.get('schema_version')!r}"
        )
    if data.get("license") != LLVM_LICENSE:
        raise LLVMFormatError("normalized LLVM inventory has an unexpected license")

    release_tag = _required_string(data, "release_tag")
    commit = _required_string(data, "commit")
    header_hashes = data.get("header_sha256")
    if not isinstance(header_hashes, dict):
        raise LLVMFormatError("header_sha256 must be a JSON object")
    normalized_hashes: list[tuple[str, str]] = []
    for header, digest in header_hashes.items():
        if header not in _HEADER_FAMILIES:
            raise LLVMFormatError(f"unsupported inventory header: {header!r}")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise LLVMFormatError(f"invalid SHA-256 for {header!r}")
        normalized_hashes.append((header, digest))

    raw_callables = data.get("callables")
    if not isinstance(raw_callables, list):
        raise LLVMFormatError("callables must be a JSON array")
    callables = tuple(
        _callable_from_data(item, release_tag=release_tag, commit=commit)
        for item in raw_callables
    )
    raw_diagnostics = data.get("diagnostics", [])
    if not isinstance(raw_diagnostics, list):
        raise LLVMFormatError("diagnostics must be a JSON array")

    return LLVMInventory(
        release_tag=release_tag,
        commit=commit,
        header_sha256=tuple(sorted(normalized_hashes)),
        callables=callables,
        diagnostics=tuple(_diagnostic_from_data(item) for item in raw_diagnostics),
    )


def to_model_callables(
    inventory: LLVMInventory,
    *,
    families: Sequence[Family] = ("sve", "sme"),
) -> tuple[ConcreteCallable, ...]:
    """Bridge LLVM declaration facts into the canonical docset IR.

    SVE and SME are enabled by default because LLVM fills declaration gaps in
    the prose-first ACLE source.  Neon and MVE remain disabled by default: the
    official ACLE tabular databases own those entities, and enabling compiler
    declarations here would create competing records.  Callers may request
    MVE explicitly for validation or for a narrowly identified LLVM-only gap.
    """

    requested = tuple(dict.fromkeys(families))
    unsupported = set(requested) - set(_HEADER_FAMILIES.values())
    if unsupported:
        raise ValueError(f"unsupported LLVM model families: {sorted(unsupported)!r}")

    result: list[ConcreteCallable] = []
    for item in inventory.callables:
        if item.family not in requested:
            continue
        primary = _primary_model_name(item)
        sources = tuple(_model_source_ref(source) for source in item.source_refs)
        source_by_line = {
            (source.header, source.line): model_source
            for source, model_source in zip(item.source_refs, sources, strict=True)
        }
        aliases = tuple(
            Alias(
                name=name.spelling,
                role=_model_name_role(name),
                availability=(
                    AvailabilityExpr.raw(name.availability)
                    if name.availability is not None
                    else None
                ),
                provenance=Provenance(
                    kind=ProvenanceKind.EXPLICIT,
                    sources=(
                        source_by_line[(name.source_ref.header, name.source_ref.line)],
                    ),
                    note="Public spelling emitted by the pinned Clang resource header.",
                ),
            )
            for name in item.names
            if name.spelling != primary.spelling
        )
        signature = Signature(
            return_type=item.prototype.return_type,
            parameters=tuple(
                Parameter(name=parameter.name, type_name=parameter.type)
                for parameter in item.prototype.parameters
            ),
            attributes=item.prototype.attributes,
            raw=item.prototype.raw,
        )
        fact_provenance = Provenance(
            kind=ProvenanceKind.EXPLICIT,
            sources=sources,
            note="Generated by Clang from the pinned LLVM TableGen declarations.",
        )
        diagnostics = tuple(
            _model_diagnostic(diagnostic) for diagnostic in item.diagnostics
        )
        result.append(
            normalize_callable(
                ConcreteCallable(
                    family=item.family,
                    name=primary.spelling,
                    signature=signature,
                    kind=_model_callable_kind(item),
                    name_role=_model_primary_name_role(primary),
                    name_availability=(
                        AvailabilityExpr.raw(primary.availability)
                        if primary.availability is not None
                        else None
                    ),
                    aliases=aliases,
                    availability=AvailabilityExpr.always(),
                    maturity=Maturity.UNSPECIFIED,
                    semantics=Semantics(
                        provenance=Provenance.unresolved(
                            "LLVM validates declarations; Arm ACLE supplies semantics."
                        )
                    ),
                    compilation=CompilationRequirements(
                        headers=(item.source_refs[0].header,),
                        provenance=Provenance.unresolved(
                            "Feature requirements must be merged from Arm ACLE."
                        ),
                        unresolved_reason=(
                            "The generated Clang header does not provide a stable "
                            "per-declaration ACLE availability expression."
                        ),
                    ),
                    headers=(item.source_refs[0].header,),
                    sources=sources,
                    field_provenance=(
                        FieldProvenance("name", fact_provenance),
                        FieldProvenance("signature", fact_provenance),
                        FieldProvenance(
                            "availability",
                            Provenance.unresolved(
                                "Merge availability from the Arm ACLE semantic source."
                            ),
                        ),
                        FieldProvenance(
                            "maturity",
                            Provenance.unresolved(
                                "LLVM declarations do not encode ACLE support level."
                            ),
                        ),
                    ),
                    diagnostics=diagnostics,
                )
            )
        )
    return tuple(sorted(result, key=lambda item: (item.family, item.name, item.id)))


def _primary_model_name(item: LLVMCallable) -> LLVMName:
    explicit = [name for name in item.names if name.role == "explicit"]
    if not explicit:
        return item.names[0]
    if item.family == "mve":
        # The prefixed namespace is always available; the unprefixed spelling
        # is conditional on __ARM_MVE_PRESERVE_USER_NAMESPACE.
        prefixed = [name for name in explicit if name.namespace == "prefixed"]
        if prefixed:
            return prefixed[0]
    return explicit[0]


def _model_name_role(name: LLVMName) -> ModelNameRole:
    if name.role == "overloaded":
        return ModelNameRole.OVERLOADED
    if name.namespace == "prefixed":
        return ModelNameRole.PREFIXED
    if name.namespace == "unprefixed":
        return ModelNameRole.UNPREFIXED
    return ModelNameRole.ALTERNATE


def _model_primary_name_role(name: LLVMName) -> ModelNameRole:
    if name.role == "overloaded":
        return ModelNameRole.OVERLOADED
    if name.namespace == "prefixed":
        return ModelNameRole.PREFIXED
    if name.namespace == "unprefixed":
        return ModelNameRole.UNPREFIXED
    return ModelNameRole.TYPED


def _model_callable_kind(item: LLVMCallable) -> CallableKind:
    primary = _primary_model_name(item).spelling
    if primary.startswith("__arm_") and not primary.startswith("__arm_v"):
        return CallableKind.SUPPORT_FUNCTION
    return CallableKind.INTRINSIC


def _model_source_ref(source: LLVMSourceRef) -> SourceRef:
    return SourceRef(
        id=(f"llvm:{source.commit}:{source.header}:{source.line}:{source.sha256[:12]}"),
        repository=source.repository,
        commit=source.commit,
        path=f"lib/clang/22/include/{source.header}",
        start_line=source.line,
        end_line=source.line,
        license_id=source.license,
        url=(f"https://github.com/llvm/llvm-project/releases/tag/{source.release_tag}"),
    )


def _model_diagnostic(item: LLVMDiagnostic) -> Diagnostic:
    sources = (
        (_model_source_ref(item.source_ref),) if item.source_ref is not None else ()
    )
    return Diagnostic(code=item.code, message=item.message, sources=sources)


def _parse_declarations(
    text: str,
    *,
    family: Family,
    header: str,
    sha256: str,
    release_tag: str,
    commit: str,
) -> tuple[list[_RawDeclaration], list[LLVMDiagnostic]]:
    lines = text.splitlines()
    declarations: list[_RawDeclaration] = []
    diagnostics: list[LLVMDiagnostic] = []
    consumed_lines: set[int] = set()

    for index, line in enumerate(lines):
        match = _BUILTIN_ALIAS_RE.search(line)
        if match is None:
            continue
        declaration_index = _next_declaration_line(lines, index + 1)
        if declaration_index is None:
            source_ref = _source_ref(
                header, index + 1, sha256, release_tag=release_tag, commit=commit
            )
            diagnostics.append(
                LLVMDiagnostic(
                    code="llvm.declaration_missing",
                    message=f"No declaration follows builtin alias {match.group('builtin')}",
                    source_ref=source_ref,
                )
            )
            continue
        declaration_text = lines[declaration_index].strip()
        try:
            name, prototype = _parse_prototype_line(declaration_text)
        except LLVMFormatError as error:
            source_ref = _source_ref(
                header,
                declaration_index + 1,
                sha256,
                release_tag=release_tag,
                commit=commit,
            )
            diagnostics.append(
                LLVMDiagnostic(
                    code="llvm.declaration_unparsed",
                    message=str(error),
                    source_ref=source_ref,
                )
            )
            continue
        if not _is_public_name(name, family):
            continue
        source_ref = _source_ref(
            header,
            declaration_index + 1,
            sha256,
            release_tag=release_tag,
            commit=commit,
        )
        namespace, availability = _namespace(name, family)
        declarations.append(
            _RawDeclaration(
                family=family,
                header=header,
                name=name,
                builtin=match.group("builtin"),
                prototype=prototype,
                source_ref=source_ref,
                namespace=namespace,
                availability=availability,
                target_features=_target_features(declaration_text),
            )
        )
        consumed_lines.add(declaration_index)

    # Capture the small public surface that is implemented directly rather
    # than through __clang_arm_builtin_alias.  This also records ordinary Neon
    # inline definitions, while deliberately ignoring function-like macros.
    for index, line in enumerate(lines):
        if index in consumed_lines:
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "(" not in stripped:
            continue
        if "__builtin_" in stripped or "=" in stripped:
            continue
        if stripped.startswith(_CONTROL_PREFIXES) or stripped.startswith("typedef "):
            continue
        if not (stripped.endswith(";") or stripped.endswith("{")):
            continue
        try:
            name, prototype = _parse_prototype_line(stripped)
        except LLVMFormatError:
            continue
        if not _is_public_name(name, family):
            continue
        source_ref = _source_ref(
            header, index + 1, sha256, release_tag=release_tag, commit=commit
        )
        namespace, availability = _namespace(name, family)
        declarations.append(
            _RawDeclaration(
                family=family,
                header=header,
                name=name,
                builtin=None,
                prototype=prototype,
                source_ref=source_ref,
                namespace=namespace,
                availability=availability,
                target_features=_target_features(stripped),
            )
        )

    return declarations, diagnostics


def _group_declarations(
    declarations: Iterable[_RawDeclaration],
) -> list[LLVMCallable]:
    groups: dict[tuple[Family, str | None, str], list[_RawDeclaration]] = {}
    for declaration in declarations:
        # Direct functions have no builtin identity, so their normalized
        # spelling and signature form a stable grouping key.
        direct_key = (
            f"{declaration.name}\0{declaration.prototype.signature}"
            if declaration.builtin is None
            else ""
        )
        key = (declaration.family, declaration.builtin, direct_key)
        groups.setdefault(key, []).append(declaration)

    callables: list[LLVMCallable] = []
    for (_, builtin, _), grouped_items in groups.items():
        target_feature_sets = {item.target_features for item in grouped_items}
        items = _deduplicate_declarations(grouped_items)
        explicit_spellings, inferred = _explicit_spellings(items, builtin)
        primary = next(
            (item for item in items if item.name in explicit_spellings),
            items[0],
        )
        names = tuple(
            LLVMName(
                spelling=item.name,
                role=("explicit" if item.name in explicit_spellings else "overloaded"),
                namespace=item.namespace,
                availability=item.availability,
                source_ref=item.source_ref,
            )
            for item in sorted(
                items,
                key=lambda item: (
                    {"prefixed": 0, "default": 1, "unprefixed": 2}[item.namespace],
                    0 if item.name in explicit_spellings else 1,
                    item.name,
                ),
            )
        )
        source_items = grouped_items if len(target_feature_sets) > 1 else items
        source_refs = tuple(
            item.source_ref
            for item in sorted(source_items, key=lambda item: item.source_ref.line)
        )
        diagnostics: list[LLVMDiagnostic] = []
        if not explicit_spellings and builtin is not None:
            diagnostics.append(
                LLVMDiagnostic(
                    code="llvm.explicit_declaration_missing",
                    message=(
                        f"{builtin} exposes only polymorphic public spellings; "
                        "the concrete declaration must be joined from the Arm source."
                    ),
                    source_ref=primary.source_ref,
                )
            )
        elif inferred and builtin is not None:
            diagnostics.append(
                LLVMDiagnostic(
                    code="llvm.explicit_name_inferred",
                    message=(
                        f"The explicit public spelling for {builtin} was selected "
                        "by specificity because it did not match the builtin name."
                    ),
                    source_ref=primary.source_ref,
                )
            )
        signatures = {item.prototype.signature for item in items}
        if len(signatures) > 1:
            diagnostics.append(
                LLVMDiagnostic(
                    code="llvm.alias_signature_mismatch",
                    message=(
                        f"Declarations for {builtin or primary.name} do not share "
                        "one normalized signature."
                    ),
                    source_ref=primary.source_ref,
                )
            )
        if len(target_feature_sets) > 1:
            rendered_feature_sets = ", ".join(
                "[" + ", ".join(features) + "]"
                for features in sorted(target_feature_sets)
            )
            diagnostics.append(
                LLVMDiagnostic(
                    code="llvm.target_feature_mismatch",
                    message=(
                        f"Declarations for {builtin or primary.name} do not share "
                        "one target feature set; callable target features remain "
                        f"unresolved ({rendered_feature_sets})."
                    ),
                    source_ref=primary.source_ref,
                )
            )
            target_features: tuple[str, ...] = ()
        else:
            target_features = next(iter(target_feature_sets), ())
        callables.append(
            LLVMCallable(
                family=primary.family,
                builtin=builtin,
                prototype=primary.prototype,
                names=names,
                source_refs=source_refs,
                target_features=target_features,
                diagnostics=tuple(diagnostics),
            )
        )
    return callables


def _explicit_spellings(
    items: Sequence[_RawDeclaration],
    builtin: str | None,
) -> tuple[set[str], bool]:
    if builtin is None:
        return {item.name for item in items}, False

    if items[0].family == "mve" and "_polymorphic_" in builtin:
        return set(), False

    normalized_to_names: dict[str, set[str]] = {}
    for item in items:
        normalized_to_names.setdefault(
            _normalize_namespace(item.name, item.family), set()
        ).add(item.name)

    expected = _expected_public_name(builtin, items[0].family)
    expected_candidates = (
        {expected, f"sv{expected}"}
        if items[0].family == "sve" and not expected.startswith(("sv", "__arm_"))
        else {expected}
    )
    for candidate in expected_candidates:
        if candidate in normalized_to_names:
            return set(normalized_to_names[candidate]), False

    # Alias spellings remove disambiguating or type suffixes.  Selecting the
    # most specific normalized spelling is conservative when LLVM uses an
    # implementation-only suffix that has no exact public counterpart.
    best = max(normalized_to_names, key=lambda name: (len(name), name.count("_"), name))
    return set(normalized_to_names[best]), True


def _expected_public_name(builtin: str, family: Family) -> str:
    prefixes = {
        "sve": "__builtin_sve_",
        "sme": "__builtin_sme_",
        "mve": "__builtin_arm_mve_",
        "neon": "__builtin_neon_",
    }
    prefix = prefixes[family]
    return builtin[len(prefix) :] if builtin.startswith(prefix) else builtin


def _normalize_namespace(name: str, family: Family) -> str:
    if family == "mve" and name.startswith("__arm_"):
        return name[len("__arm_") :]
    return name


def _namespace(name: str, family: Family) -> tuple[Namespace, str | None]:
    if family != "mve":
        return "default", None
    if name.startswith("__arm_"):
        return "prefixed", None
    return "unprefixed", "!defined(__ARM_MVE_PRESERVE_USER_NAMESPACE)"


def _target_features(declaration: str) -> tuple[str, ...]:
    """Extract one canonical target feature set from a declaration line."""

    feature_sets: list[tuple[str, ...]] = []
    for match in _TARGET_ATTRIBUTE_RE.finditer(declaration):
        raw_features = bytes(match.group("features"), "utf-8").decode("unicode_escape")
        features = tuple(feature.strip() for feature in raw_features.split(","))
        if any(not feature for feature in features):
            raise LLVMFormatError("target attribute contains an empty feature")
        if len(set(features)) != len(features):
            raise LLVMFormatError("target attribute contains a duplicate feature")
        feature_sets.append(tuple(sorted(features)))
    if not feature_sets:
        return ()
    if any(features != feature_sets[0] for features in feature_sets[1:]):
        raise LLVMFormatError("declaration contains conflicting target attributes")
    return feature_sets[0]


def _parse_prototype_line(line: str) -> tuple[str, LLVMPrototype]:
    raw = line.strip()
    if raw.endswith((";", "{")):
        raw = raw[:-1].rstrip()
    parseable = _remove_attributes(raw)
    open_parenthesis = parseable.find("(")
    if open_parenthesis < 0:
        raise LLVMFormatError(f"not a function declaration: {line!r}")
    close_parenthesis = _matching_parenthesis(parseable, open_parenthesis)
    left = parseable[:open_parenthesis].rstrip()
    name_match = _FUNCTION_NAME_RE.search(left)
    if name_match is None:
        raise LLVMFormatError(f"cannot find a public function name in {line!r}")
    name = name_match.group("name")
    return_type = _clean_return_type(left[: name_match.start()].strip())
    if not return_type:
        raise LLVMFormatError(f"cannot find a return type for {name!r}")
    parameters_raw = parseable[open_parenthesis + 1 : close_parenthesis]
    parameters = tuple(
        _parse_parameter(item)
        for item in _split_parameters(parameters_raw)
        if item.strip() and item.strip() != "void"
    )
    attributes_raw = parseable[close_parenthesis + 1 :].strip()
    attributes = tuple(_WHITESPACE_RE.sub(" ", attributes_raw).split())
    normalized_raw = _WHITESPACE_RE.sub(" ", raw)
    return name, LLVMPrototype(
        raw=normalized_raw,
        return_type=return_type,
        parameters=parameters,
        attributes=attributes,
    )


def _clean_return_type(value: str) -> str:
    value = _LEADING_STORAGE_RE.sub("", value).strip()
    value = _remove_attributes(value)
    value = _LEADING_STORAGE_RE.sub("", value).strip()
    return _WHITESPACE_RE.sub(" ", value)


def _remove_attributes(value: str) -> str:
    marker = "__attribute__(("
    while marker in value:
        start = value.index(marker)
        open_parenthesis = start + len("__attribute__")
        try:
            end = _matching_parenthesis(value, open_parenthesis)
        except LLVMFormatError:
            break
        value = value[:start] + " " + value[end + 1 :]
    return _WHITESPACE_RE.sub(" ", value).strip()


def _matching_parenthesis(value: str, start: int) -> int:
    if start >= len(value) or value[start] != "(":
        raise LLVMFormatError("parenthesis matcher did not start at '('")
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(value)):
        character = value[index]
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            continue
        if character == '"':
            in_string = True
        elif character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth == 0:
                return index
    raise LLVMFormatError("unbalanced function declaration parentheses")


def _split_parameters(value: str) -> list[str]:
    if not value.strip():
        return []
    parameters: list[str] = []
    start = 0
    paren_depth = 0
    bracket_depth = 0
    for index, character in enumerate(value):
        if character == "(":
            paren_depth += 1
        elif character == ")":
            paren_depth -= 1
        elif character == "[":
            bracket_depth += 1
        elif character == "]":
            bracket_depth -= 1
        elif character == "," and paren_depth == 0 and bracket_depth == 0:
            parameters.append(value[start:index].strip())
            start = index + 1
    parameters.append(value[start:].strip())
    return parameters


def _parse_parameter(raw: str) -> LLVMParameter:
    normalized = _WHITESPACE_RE.sub(" ", raw.strip())
    if not normalized:
        raise LLVMFormatError("empty parameter")
    name: str | None = None
    type_name = normalized
    match = re.search(r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*$", normalized)
    if match is not None:
        candidate = match.group("name")
        prefix = normalized[: match.start()].rstrip()
        # Generated SVE/SME/MVE declarations omit names.  Only detach a final
        # identifier when there is an unambiguous preceding type expression.
        if (
            prefix
            and (" " in normalized or "*" in prefix or "]" in prefix)
            and candidate not in _TYPE_KEYWORDS
        ):
            name = candidate
            type_name = prefix
    return LLVMParameter(raw=normalized, type=type_name, name=name)


def _next_declaration_line(lines: Sequence[str], start: int) -> int | None:
    for index in range(start, min(len(lines), start + 5)):
        stripped = lines[index].strip()
        if not stripped or stripped.startswith("//") or stripped.startswith("/*"):
            continue
        if "(" in stripped and (stripped.endswith(";") or stripped.endswith("{")):
            return index
    return None


def _is_public_name(name: str, family: Family) -> bool:
    if name.startswith(("__builtin_", "__noswap_")):
        return False
    if not _IDENTIFIER_RE.fullmatch(name):
        return False
    return name.startswith(_PUBLIC_NAME_PREFIXES[family])


def _deduplicate_declarations(
    declarations: Iterable[_RawDeclaration],
) -> list[_RawDeclaration]:
    result: list[_RawDeclaration] = []
    seen: set[tuple[str, str, Namespace]] = set()
    for declaration in declarations:
        key = (
            declaration.name,
            declaration.prototype.signature,
            declaration.namespace,
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(declaration)
    return result


def _source_ref(
    header: str,
    line: int,
    sha256: str,
    *,
    release_tag: str,
    commit: str,
) -> LLVMSourceRef:
    return LLVMSourceRef(
        repository="llvm/llvm-project",
        commit=commit,
        release_tag=release_tag,
        header=header,
        line=line,
        sha256=sha256,
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _bounded_process_detail(stdout: str | None, stderr: str | None) -> str:
    lines = [
        line for line in f"{stdout or ''}\n{stderr or ''}".splitlines() if line.strip()
    ]
    if not lines:
        return "no diagnostic output"
    return " | ".join(lines[-12:])


def _callable_sort_key(item: LLVMCallable) -> tuple[str, str, str]:
    return item.family, item.primary_name, item.prototype.signature


def _callable_data(item: LLVMCallable) -> dict[str, object]:
    return {
        "family": item.family,
        "builtin": item.builtin,
        "prototype": asdict(item.prototype),
        "names": [asdict(name) for name in item.names],
        "source_refs": [asdict(source) for source in item.source_refs],
        "target_features": list(item.target_features),
        "diagnostics": [
            _diagnostic_data(diagnostic) for diagnostic in item.diagnostics
        ],
    }


def _diagnostic_data(item: LLVMDiagnostic) -> dict[str, object]:
    return {
        "code": item.code,
        "message": item.message,
        "source_ref": asdict(item.source_ref) if item.source_ref is not None else None,
    }


def _source_ref_from_data(value: object) -> LLVMSourceRef:
    if not isinstance(value, dict):
        raise LLVMFormatError("source_ref must be a JSON object")
    try:
        return LLVMSourceRef(**value)
    except TypeError as error:
        raise LLVMFormatError(f"invalid source_ref: {error}") from error


def _diagnostic_from_data(value: object) -> LLVMDiagnostic:
    if not isinstance(value, dict):
        raise LLVMFormatError("diagnostic must be a JSON object")
    source = value.get("source_ref")
    return LLVMDiagnostic(
        code=_required_string(value, "code"),
        message=_required_string(value, "message"),
        source_ref=(_source_ref_from_data(source) if source is not None else None),
    )


def _callable_from_data(
    value: object,
    *,
    release_tag: str,
    commit: str,
) -> LLVMCallable:
    if not isinstance(value, dict):
        raise LLVMFormatError("callable must be a JSON object")
    family = _family_from_data(value)
    prototype_data = value.get("prototype")
    if not isinstance(prototype_data, dict):
        raise LLVMFormatError("callable prototype must be a JSON object")
    parameters_data = prototype_data.get("parameters", [])
    if not isinstance(parameters_data, list):
        raise LLVMFormatError("prototype parameters must be a JSON array")
    try:
        prototype = LLVMPrototype(
            raw=_required_string(prototype_data, "raw"),
            return_type=_required_string(prototype_data, "return_type"),
            parameters=tuple(LLVMParameter(**item) for item in parameters_data),
            attributes=tuple(prototype_data.get("attributes", ())),
        )
    except (TypeError, ValueError) as error:
        raise LLVMFormatError(f"invalid prototype: {error}") from error

    names_data = value.get("names")
    if not isinstance(names_data, list) or not names_data:
        raise LLVMFormatError("callable names must be a non-empty JSON array")
    names: list[LLVMName] = []
    for item in names_data:
        if not isinstance(item, dict):
            raise LLVMFormatError("callable name must be a JSON object")
        source_ref = _source_ref_from_data(item.get("source_ref"))
        if source_ref.release_tag != release_tag or source_ref.commit != commit:
            raise LLVMFormatError("name provenance does not match inventory pin")
        names.append(
            LLVMName(
                spelling=_required_string(item, "spelling"),
                role=_name_role_from_data(item),
                namespace=_namespace_from_data(item),
                availability=_optional_string(item, "availability"),
                source_ref=source_ref,
            )
        )
    source_refs_data = value.get("source_refs", [])
    if not isinstance(source_refs_data, list):
        raise LLVMFormatError("source_refs must be a JSON array")
    diagnostics_data = value.get("diagnostics", [])
    if not isinstance(diagnostics_data, list):
        raise LLVMFormatError("callable diagnostics must be a JSON array")
    builtin = value.get("builtin")
    if builtin is not None and not isinstance(builtin, str):
        raise LLVMFormatError("callable builtin must be a string or null")
    target_features_data = value.get("target_features", [])
    if not isinstance(target_features_data, list) or any(
        not isinstance(feature, str) or not feature for feature in target_features_data
    ):
        raise LLVMFormatError(
            "callable target_features must be an array of non-empty strings"
        )
    target_features = tuple(target_features_data)
    if target_features != tuple(sorted(set(target_features))):
        raise LLVMFormatError(
            "callable target_features must be sorted and contain no duplicates"
        )
    return LLVMCallable(
        family=family,
        builtin=builtin,
        prototype=prototype,
        names=tuple(names),
        source_refs=tuple(_source_ref_from_data(item) for item in source_refs_data),
        target_features=target_features,
        diagnostics=tuple(_diagnostic_from_data(item) for item in diagnostics_data),
    )


def _required_string(value: Mapping[str, object], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item:
        raise LLVMFormatError(f"{key} must be a non-empty string")
    return item


def _optional_string(value: Mapping[str, object], key: str) -> str | None:
    item = value.get(key)
    if item is not None and not isinstance(item, str):
        raise LLVMFormatError(f"{key} must be a string or null")
    return item


def _family_from_data(value: Mapping[str, object]) -> Family:
    family = value.get("family")
    if family == "sve":
        return "sve"
    if family == "sme":
        return "sme"
    if family == "mve":
        return "mve"
    if family == "neon":
        return "neon"
    raise LLVMFormatError(f"unsupported callable family: {family!r}")


def _name_role_from_data(value: Mapping[str, object]) -> NameRole:
    role = value.get("role")
    if role == "explicit":
        return "explicit"
    if role == "overloaded":
        return "overloaded"
    raise LLVMFormatError(f"unsupported callable name role: {role!r}")


def _namespace_from_data(value: Mapping[str, object]) -> Namespace:
    namespace = value.get("namespace")
    if namespace == "prefixed":
        return "prefixed"
    if namespace == "unprefixed":
        return "unprefixed"
    if namespace == "default":
        return "default"
    raise LLVMFormatError(f"unsupported callable namespace: {namespace!r}")
