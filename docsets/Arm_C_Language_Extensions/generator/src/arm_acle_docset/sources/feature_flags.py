"""Compiler and architecture feature requirements for Arm ACLE intrinsics.

The default mapping is a validated, in-module manifest.  It is intentionally
separate from the parsers for intrinsic declarations: ACLE feature macros,
compiler command-line spellings, and architecture defaults evolve on different
cadences.  Callers may load an external JSON manifest with the same schema for
testing or a future data-only update.

The examples are scoped to the compiler revision and target named by each
context.  They are not universal build prescriptions.  In particular,
``-mcpu`` also selects a tuning model, while ``-march`` only selects an ISA
contract; performance data must therefore remain microarchitecture-specific.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from arm_acle_docset.model import (
    AvailabilityExpr,
    CompilationRequirements,
    CompilerFlagExample,
    Provenance,
    ProvenanceKind,
    SourceRef,
)

from .acle_markdown import ACLE_MARKDOWN_LICENSE


SCHEMA_VERSION = 1
ACLE_REVISION = "62d9cbd68abb6d18dd8f06980da7758d9dbe0560"
LLVM_TAG = "llvmorg-22.1.1"
LLVM_REVISION = "fef02d48c08db859ef83f84232ed78bd9d1c323a"
GCC_MANUAL_VERSION = "16.2.0"
ARM_FEATURE_REGISTRY_DOCUMENT_ID = "109697_2025_12_en"
ARM_FEATURE_REGISTRY_TITLE = "Feature names in A-profile architecture"
ARM_FEATURE_REGISTRY_VERSION = "1.0 (2025_12)"
ARM_FEATURE_REGISTRY_LICENSE = "LicenseRef-Arm-Proprietary-Notice"
ARM_FEATURE_REGISTRY_URL = (
    "https://documentation-service.arm.com/static/69402e206efc1635355c3bb2?token="
)


class FeatureFlagManifestError(ValueError):
    """Raised when feature-flag manifest data is incomplete or inconsistent."""


class ResolutionStatus(StrEnum):
    RESOLVED = "resolved"
    PARTIAL = "partial"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True, slots=True)
class MacroGate:
    """Exact source-level condition for one ACLE macro family."""

    macro: str
    expression: AvailabilityExpr
    display: str
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.macro.strip():
            raise FeatureFlagManifestError("macro gate needs a macro")
        if not self.display.strip():
            raise FeatureFlagManifestError(f"{self.macro}: macro gate display is empty")


@dataclass(frozen=True, slots=True)
class TargetContext:
    """One execution/profile context with compiler-specific examples."""

    target: str
    architecture_min: str
    profiles: tuple[str, ...]
    execution_states: tuple[str, ...]
    compiler_flags: tuple[CompilerFlagExample, ...]
    notes: tuple[str, ...] = ()
    sources: tuple[SourceRef, ...] = ()
    status: ResolutionStatus = ResolutionStatus.RESOLVED
    unresolved_reason: str | None = None

    def __post_init__(self) -> None:
        if not self.target.strip():
            raise FeatureFlagManifestError("target must be non-empty")
        if not self.architecture_min.strip():
            raise FeatureFlagManifestError("architecture_min must be non-empty")
        if not self.profiles:
            raise FeatureFlagManifestError(f"{self.target}: profiles must not be empty")
        if not self.execution_states:
            raise FeatureFlagManifestError(
                f"{self.target}: execution_states must not be empty"
            )
        if self.status is ResolutionStatus.UNRESOLVED and not self.unresolved_reason:
            raise FeatureFlagManifestError(
                f"{self.target}: unresolved context needs unresolved_reason"
            )


@dataclass(frozen=True, slots=True)
class FeatureFlagMapping:
    """Mapping from one architectural extension family to compiler controls."""

    key: str
    title: str
    acle_macros: tuple[str, ...]
    macro_gates: tuple[MacroGate, ...]
    architecture_features: tuple[str, ...]
    extension_names: tuple[str, ...]
    implies: tuple[str, ...]
    contexts: tuple[TargetContext, ...]
    sources: tuple[SourceRef, ...]
    notes: tuple[str, ...] = ()
    status: ResolutionStatus = ResolutionStatus.RESOLVED
    unresolved_reason: str | None = None

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise FeatureFlagManifestError("feature key must be non-empty")
        if not self.title.strip():
            raise FeatureFlagManifestError(f"{self.key}: title must be non-empty")
        if not self.acle_macros:
            raise FeatureFlagManifestError(f"{self.key}: acle_macros must not be empty")
        if {gate.macro for gate in self.macro_gates} != set(self.acle_macros):
            raise FeatureFlagManifestError(
                f"{self.key}: macro_gates must cover every ACLE macro exactly"
            )
        if not self.architecture_features:
            raise FeatureFlagManifestError(
                f"{self.key}: architecture_features must not be empty"
            )
        if not self.contexts:
            raise FeatureFlagManifestError(f"{self.key}: contexts must not be empty")
        if not self.sources:
            raise FeatureFlagManifestError(f"{self.key}: sources must not be empty")
        if self.status is ResolutionStatus.UNRESOLVED and not self.unresolved_reason:
            raise FeatureFlagManifestError(
                f"{self.key}: unresolved mapping needs unresolved_reason"
            )

    def contexts_for(self, target: str) -> tuple[TargetContext, ...]:
        """Return contexts for a normalized target key such as ``aarch64``."""

        return tuple(
            context
            for context in self.contexts
            if context.target == target or context.target == "unspecified"
        )

    def gate_for(self, macro: str) -> MacroGate:
        """Return the exact source-level gate for ``macro``."""

        for gate in self.macro_gates:
            if gate.macro == macro:
                return gate
        raise KeyError(f"{macro!r} is not provided by feature {self.key!r}")

    def compilation_requirements(
        self,
        *,
        macro: str,
        target: str,
    ) -> tuple[CompilationRequirements, ...]:
        """Convert matching contexts into the generator's canonical model."""

        gate = self.gate_for(macro)

        requirements: list[CompilationRequirements] = []
        for context in self.contexts_for(target):
            sources = _deduplicate_sources((*self.sources, *context.sources))
            if (
                self.status is ResolutionStatus.UNRESOLVED
                or context.status is ResolutionStatus.UNRESOLVED
            ):
                provenance = Provenance.unresolved(
                    context.unresolved_reason or self.unresolved_reason
                )
            elif (
                self.status is ResolutionStatus.PARTIAL
                or context.status is ResolutionStatus.PARTIAL
            ):
                provenance = Provenance(
                    kind=ProvenanceKind.MANUAL_OVERRIDE,
                    sources=sources,
                    rule=(
                        "Map the exact ACLE feature macro to the pinned "
                        "LLVM/Clang feature spelling; retain Clang-only examples "
                        f"when the GCC {GCC_MANUAL_VERSION} manual does not "
                        "document that modifier."
                    ),
                )
            else:
                provenance = Provenance(
                    kind=ProvenanceKind.MANUAL_OVERRIDE,
                    sources=sources,
                    rule=(
                        "Map the ACLE feature macro to pinned LLVM/Clang feature "
                        "spellings and validate the user-facing syntax against "
                        f"the GCC {GCC_MANUAL_VERSION} manual."
                    ),
                )
            if any(source.repository == "Arm documentation" for source in sources):
                compiler_scope = (
                    "retain Clang-only examples where GCC 16.2 does not document "
                    "the exact modifier"
                    if self.status is ResolutionStatus.PARTIAL
                    or context.status is ResolutionStatus.PARTIAL
                    else "validate GCC spellings against the GCC 16.2 manual"
                )
                provenance = Provenance(
                    kind=ProvenanceKind.MANUAL_OVERRIDE,
                    sources=sources,
                    rule=(
                        "Use Arm feature registry 109697_2025_12_en for the "
                        "minimum architecture and ISA dependencies, the pinned "
                        "ACLE revision for the macro, and pinned LLVM 22.1.1 "
                        f"for Clang feature spellings; {compiler_scope}."
                    ),
                )
            requirements.append(
                CompilationRequirements(
                    architecture_min=context.architecture_min,
                    profiles=context.profiles,
                    extensions=self.extension_names,
                    feature_macros=(macro,),
                    execution_states=context.execution_states,
                    compiler_flags=context.compiler_flags,
                    availability=gate.expression,
                    provenance=provenance,
                    unresolved_reason=(
                        context.unresolved_reason
                        if context.status is ResolutionStatus.UNRESOLVED
                        else self.unresolved_reason
                        if self.status is ResolutionStatus.UNRESOLVED
                        else None
                    ),
                )
            )
        return tuple(requirements)


def _deduplicate_sources(sources: Iterable[SourceRef]) -> tuple[SourceRef, ...]:
    by_id: dict[str, SourceRef] = {}
    for source in sources:
        previous = by_id.setdefault(source.id, source)
        if previous != source:
            raise FeatureFlagManifestError(
                f"source id {source.id!r} refers to multiple locations"
            )
    return tuple(by_id.values())


def _source_ref(data: Mapping[str, Any], *, owner: str) -> SourceRef:
    try:
        return SourceRef(
            id=str(data["id"]),
            repository=str(data["repository"]),
            commit=str(data["commit"]),
            path=str(data["path"]),
            start_line=_optional_int(data.get("start_line")),
            end_line=_optional_int(data.get("end_line")),
            license_id=_optional_text(data.get("license_id")),
            url=_optional_text(data.get("url")),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise FeatureFlagManifestError(f"{owner}: invalid source: {error}") from error


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("expected an integer or null")
    return value


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("expected a string or null")
    return value


def _string_tuple(value: Any, *, owner: str, field: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise FeatureFlagManifestError(f"{owner}.{field} must be an array")
    converted = tuple(str(item) for item in value)
    if any(not item.strip() for item in converted):
        raise FeatureFlagManifestError(f"{owner}.{field} contains an empty value")
    return converted


def _compiler_flag(
    data: Mapping[str, Any],
    *,
    owner: str,
    source_index: Mapping[str, SourceRef],
) -> CompilerFlagExample:
    source_ids = _string_tuple(
        data.get("source_ids", ()), owner=owner, field="source_ids"
    )
    try:
        sources = tuple(source_index[source_id] for source_id in source_ids)
    except KeyError as error:
        raise FeatureFlagManifestError(
            f"{owner}: unknown source id {error.args[0]!r}"
        ) from error

    default_enabled = data.get("default_enabled")
    if default_enabled is not None and not isinstance(default_enabled, bool):
        raise FeatureFlagManifestError(
            f"{owner}.default_enabled must be true, false, or null"
        )
    flags = _string_tuple(data.get("flags", ()), owner=owner, field="flags")
    if not flags:
        raise FeatureFlagManifestError(f"{owner}.flags must not be empty")

    return CompilerFlagExample(
        compiler=str(data["compiler"]),
        version=_optional_text(data.get("version")),
        base_march=_optional_text(data.get("base_march")),
        flags=flags,
        default_enabled=default_enabled,
        notes=_string_tuple(data.get("notes", ()), owner=owner, field="notes"),
        provenance=Provenance(
            kind=ProvenanceKind.MANUAL_OVERRIDE,
            sources=sources,
            rule="Pinned compiler feature spelling; example is target-scoped.",
        ),
    )


def _macro_gate(data: Mapping[str, Any], *, owner: str) -> MacroGate:
    try:
        macro = str(data["macro"])
        display = str(data["display"])
        expression_kind = str(data.get("kind", "defined"))
        if expression_kind == "defined":
            expression = AvailabilityExpr.defined(macro)
        elif expression_kind == "raw":
            expression = AvailabilityExpr.raw(display)
        else:
            raise FeatureFlagManifestError(f"{owner}.kind must be 'defined' or 'raw'")
        return MacroGate(
            macro=macro,
            expression=expression,
            display=display,
            notes=_string_tuple(data.get("notes", ()), owner=owner, field="notes"),
        )
    except (KeyError, TypeError, ValueError) as error:
        if isinstance(error, FeatureFlagManifestError):
            raise
        raise FeatureFlagManifestError(
            f"{owner}: invalid macro gate: {error}"
        ) from error


def _target_context(
    data: Mapping[str, Any],
    *,
    owner: str,
    source_index: Mapping[str, SourceRef],
) -> TargetContext:
    source_ids = _string_tuple(
        data.get("source_ids", ()), owner=owner, field="source_ids"
    )
    try:
        sources = tuple(source_index[source_id] for source_id in source_ids)
    except KeyError as error:
        raise FeatureFlagManifestError(
            f"{owner}: unknown source id {error.args[0]!r}"
        ) from error

    try:
        status = ResolutionStatus(str(data.get("status", "resolved")))
        flags_data = data.get("compiler_flags", ())
        if not isinstance(flags_data, (list, tuple)):
            raise FeatureFlagManifestError(f"{owner}.compiler_flags must be an array")
        flags = tuple(
            _compiler_flag(
                flag,
                owner=f"{owner}.compiler_flags[{index}]",
                source_index=source_index,
            )
            for index, flag in enumerate(flags_data)
        )
        return TargetContext(
            target=str(data["target"]),
            architecture_min=str(data["architecture_min"]),
            profiles=_string_tuple(data["profiles"], owner=owner, field="profiles"),
            execution_states=_string_tuple(
                data["execution_states"], owner=owner, field="execution_states"
            ),
            compiler_flags=flags,
            notes=_string_tuple(data.get("notes", ()), owner=owner, field="notes"),
            sources=sources,
            status=status,
            unresolved_reason=_optional_text(data.get("unresolved_reason")),
        )
    except (KeyError, TypeError, ValueError) as error:
        if isinstance(error, FeatureFlagManifestError):
            raise
        raise FeatureFlagManifestError(f"{owner}: invalid context: {error}") from error


def parse_feature_flag_manifest(
    data: Mapping[str, Any],
) -> tuple[FeatureFlagMapping, ...]:
    """Validate and parse a feature-flag manifest mapping."""

    if data.get("schema_version") != SCHEMA_VERSION:
        raise FeatureFlagManifestError(
            f"unsupported schema_version {data.get('schema_version')!r}; "
            f"expected {SCHEMA_VERSION}"
        )
    features_data = data.get("features")
    if not isinstance(features_data, (list, tuple)):
        raise FeatureFlagManifestError("features must be an array")

    mappings: list[FeatureFlagMapping] = []
    seen_keys: set[str] = set()
    for index, feature_data in enumerate(features_data):
        owner = f"features[{index}]"
        if not isinstance(feature_data, Mapping):
            raise FeatureFlagManifestError(f"{owner} must be an object")
        try:
            key = str(feature_data["key"])
            if key in seen_keys:
                raise FeatureFlagManifestError(f"duplicate feature key {key!r}")
            seen_keys.add(key)

            source_data = feature_data.get("sources", ())
            if not isinstance(source_data, (list, tuple)):
                raise FeatureFlagManifestError(f"{owner}.sources must be an array")
            sources = tuple(
                _source_ref(source, owner=f"{owner}.sources[{source_index}]")
                for source_index, source in enumerate(source_data)
            )
            source_index = {source.id: source for source in sources}
            if len(source_index) != len(sources):
                raise FeatureFlagManifestError(f"{owner} contains duplicate source ids")

            contexts_data = feature_data.get("contexts", ())
            if not isinstance(contexts_data, (list, tuple)):
                raise FeatureFlagManifestError(f"{owner}.contexts must be an array")
            contexts = tuple(
                _target_context(
                    context,
                    owner=f"{owner}.contexts[{context_index}]",
                    source_index=source_index,
                )
                for context_index, context in enumerate(contexts_data)
            )
            status = ResolutionStatus(str(feature_data.get("status", "resolved")))
            mappings.append(
                FeatureFlagMapping(
                    key=key,
                    title=str(feature_data["title"]),
                    acle_macros=_string_tuple(
                        feature_data["acle_macros"], owner=owner, field="acle_macros"
                    ),
                    macro_gates=tuple(
                        _macro_gate(
                            gate,
                            owner=f"{owner}.macro_gates[{gate_index}]",
                        )
                        for gate_index, gate in enumerate(
                            feature_data.get("macro_gates", ())
                        )
                    ),
                    architecture_features=_string_tuple(
                        feature_data["architecture_features"],
                        owner=owner,
                        field="architecture_features",
                    ),
                    extension_names=_string_tuple(
                        feature_data.get("extension_names", ()),
                        owner=owner,
                        field="extension_names",
                    ),
                    implies=_string_tuple(
                        feature_data.get("implies", ()), owner=owner, field="implies"
                    ),
                    contexts=contexts,
                    sources=sources,
                    notes=_string_tuple(
                        feature_data.get("notes", ()), owner=owner, field="notes"
                    ),
                    status=status,
                    unresolved_reason=_optional_text(
                        feature_data.get("unresolved_reason")
                    ),
                )
            )
        except (KeyError, TypeError, ValueError) as error:
            if isinstance(error, FeatureFlagManifestError):
                raise
            raise FeatureFlagManifestError(
                f"{owner}: invalid feature: {error}"
            ) from error

    return tuple(mappings)


def load_feature_flag_manifest(
    path: Path | str | None = None,
) -> tuple[FeatureFlagMapping, ...]:
    """Load the built-in manifest or a schema-compatible external JSON file."""

    if path is None:
        return DEFAULT_FEATURE_FLAG_MANIFEST
    manifest_path = Path(path)
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise FeatureFlagManifestError(
            f"could not load feature flag manifest {manifest_path}: {error}"
        ) from error
    if not isinstance(data, Mapping):
        raise FeatureFlagManifestError("manifest root must be an object")
    return parse_feature_flag_manifest(data)


def index_feature_flags_by_macro(
    mappings: Sequence[FeatureFlagMapping] | None = None,
) -> dict[str, tuple[FeatureFlagMapping, ...]]:
    """Build a multi-map because one macro can have target-specific spellings."""

    selected = DEFAULT_FEATURE_FLAG_MANIFEST if mappings is None else mappings
    indexed: dict[str, list[FeatureFlagMapping]] = {}
    for mapping in selected:
        for macro in mapping.acle_macros:
            indexed.setdefault(macro, []).append(mapping)
    return {macro: tuple(entries) for macro, entries in indexed.items()}


def mappings_for_macro(
    macro: str,
    mappings: Sequence[FeatureFlagMapping] | None = None,
) -> tuple[FeatureFlagMapping, ...]:
    """Return all mappings for an ACLE macro without guessing an architecture."""

    return index_feature_flags_by_macro(mappings).get(macro, ())


def compilation_requirements_for(
    macro: str,
    *,
    target: str,
    mappings: Sequence[FeatureFlagMapping] | None = None,
) -> tuple[CompilationRequirements, ...]:
    """Return canonical requirements for one macro and normalized target."""

    requirements: list[CompilationRequirements] = []
    for mapping in mappings_for_macro(macro, mappings):
        requirements.extend(
            mapping.compilation_requirements(macro=macro, target=target)
        )
    return tuple(requirements)


def unresolved_compilation_requirements(
    macro: str,
    *,
    reason: str = "No pinned feature-flag mapping exists for this ACLE macro.",
) -> CompilationRequirements:
    """Preserve an unknown macro explicitly instead of inventing a compiler flag."""

    return CompilationRequirements(
        feature_macros=(macro,),
        availability=AvailabilityExpr.defined(macro),
        provenance=Provenance.unresolved(reason),
        unresolved_reason=reason,
    )


def _source(
    key: str,
    kind: str,
    *,
    path: str,
    start_line: int | None = None,
    end_line: int | None = None,
    anchor: str | None = None,
    page: int | None = None,
) -> dict[str, Any]:
    if kind == "acle":
        base = f"https://github.com/ARM-software/acle/blob/{ACLE_REVISION}/{path}"
        return {
            "id": f"{key}:acle:{anchor or 'source'}",
            "repository": "ARM-software/acle",
            "commit": ACLE_REVISION,
            "path": path,
            "start_line": start_line,
            "end_line": end_line,
            "license_id": ACLE_MARKDOWN_LICENSE,
            "url": f"{base}#{anchor}" if anchor else base,
        }
    if kind == "llvm-aarch64":
        return {
            "id": f"{key}:llvm-aarch64",
            "repository": "llvm/llvm-project",
            "commit": LLVM_REVISION,
            "path": path,
            "start_line": start_line,
            "end_line": end_line,
            "license_id": "Apache-2.0 WITH LLVM-exception",
            "url": f"https://github.com/llvm/llvm-project/blob/{LLVM_REVISION}/{path}",
        }
    if kind == "llvm-aarch32":
        return {
            "id": f"{key}:llvm-aarch32",
            "repository": "llvm/llvm-project",
            "commit": LLVM_REVISION,
            "path": path,
            "start_line": start_line,
            "end_line": end_line,
            "license_id": "Apache-2.0 WITH LLVM-exception",
            "url": f"https://github.com/llvm/llvm-project/blob/{LLVM_REVISION}/{path}",
        }
    if kind == "gcc-aarch64":
        return {
            "id": f"{key}:gcc-aarch64",
            "repository": "gcc.gnu.org/onlinedocs",
            "commit": GCC_MANUAL_VERSION,
            "path": "gcc/AArch64-Options.html",
            "license_id": "GFDL-1.3-invariants-or-later",
            "url": (
                f"https://gcc.gnu.org/onlinedocs/gcc-{GCC_MANUAL_VERSION}/"
                "gcc/AArch64-Options.html"
            ),
        }
    if kind == "gcc-aarch32":
        return {
            "id": f"{key}:gcc-aarch32",
            "repository": "gcc.gnu.org/onlinedocs",
            "commit": GCC_MANUAL_VERSION,
            "path": "gcc/ARM-Options.html",
            "license_id": "GFDL-1.3-invariants-or-later",
            "url": (
                f"https://gcc.gnu.org/onlinedocs/gcc-{GCC_MANUAL_VERSION}/"
                "gcc/ARM-Options.html"
            ),
        }
    if kind == "arm-feature-registry":
        if page is None:
            raise AssertionError("Arm feature registry source needs a page")
        return {
            "id": f"{key}:arm-feature-registry",
            "repository": "Arm documentation",
            "commit": ARM_FEATURE_REGISTRY_DOCUMENT_ID,
            "path": f"{ARM_FEATURE_REGISTRY_TITLE}#page={page}",
            "license_id": ARM_FEATURE_REGISTRY_LICENSE,
            "url": f"{ARM_FEATURE_REGISTRY_URL}#page={page}",
        }
    raise AssertionError(f"unsupported source kind: {kind}")


def _flags(
    *,
    target: str,
    march: str | Sequence[str],
    mcpu: str | Sequence[str],
    base_march: str,
    default_enabled: bool | None,
    source_ids: Sequence[str],
    note: str,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for compiler, version, source_id in (
        ("Clang", "22.1.1", source_ids[0]),
        ("GCC", GCC_MANUAL_VERSION, source_ids[1]),
    ):
        common_notes = [
            f"Target: {target}.",
            note,
            "Use -march to state an ISA contract; use -mcpu when tuning for a concrete CPU.",
        ]
        result.append(
            {
                "compiler": compiler,
                "version": version,
                "base_march": base_march,
                "flags": [march] if isinstance(march, str) else list(march),
                "default_enabled": default_enabled,
                "notes": common_notes,
                "source_ids": [source_id],
            }
        )
        result.append(
            {
                "compiler": compiler,
                "version": version,
                "base_march": None,
                "flags": [mcpu] if isinstance(mcpu, str) else list(mcpu),
                "default_enabled": None,
                "notes": [
                    *common_notes,
                    "The selected CPU can enable additional extensions beyond this example.",
                ],
                "source_ids": [source_id],
            }
        )
    return result


def _clang_flags(
    *,
    target: str,
    march: str,
    mcpu: str,
    base_march: str,
    default_enabled: bool | None,
    source_id: str,
    note: str,
) -> list[dict[str, Any]]:
    """Return Clang-only examples when GCC does not document the modifier."""

    common_notes = [
        f"Target: {target}.",
        note,
        "Use -march to state an ISA contract; use -mcpu when tuning for a concrete CPU.",
    ]
    return [
        {
            "compiler": "Clang",
            "version": "22.1.1",
            "base_march": base_march,
            "flags": [march],
            "default_enabled": default_enabled,
            "notes": common_notes,
            "source_ids": [source_id],
        },
        {
            "compiler": "Clang",
            "version": "22.1.1",
            "base_march": None,
            "flags": [mcpu],
            "default_enabled": None,
            "notes": [
                *common_notes,
                "The selected CPU can enable additional extensions beyond this example.",
            ],
            "source_ids": [source_id],
        },
    ]


def _context(
    *,
    target: str,
    architecture_min: str,
    profiles: Sequence[str],
    execution_states: Sequence[str],
    march: str | Sequence[str],
    mcpu: str | Sequence[str],
    base_march: str,
    default_enabled: bool | None,
    llvm_source_id: str,
    gcc_source_id: str,
    note: str,
    extra_notes: Sequence[str] = (),
    status: ResolutionStatus = ResolutionStatus.RESOLVED,
) -> dict[str, Any]:
    return {
        "target": target,
        "architecture_min": architecture_min,
        "profiles": list(profiles),
        "execution_states": list(execution_states),
        "compiler_flags": _flags(
            target=target,
            march=march,
            mcpu=mcpu,
            base_march=base_march,
            default_enabled=default_enabled,
            source_ids=(llvm_source_id, gcc_source_id),
            note=note,
        ),
        "notes": list(extra_notes),
        "source_ids": [llvm_source_id, gcc_source_id],
        "status": status.value,
    }


def _feature(
    *,
    key: str,
    title: str,
    macros: Sequence[str],
    architecture_features: Sequence[str],
    extension_names: Sequence[str],
    implies: Sequence[str],
    acle_lines: tuple[int, int],
    acle_anchor: str,
    llvm_aarch64_lines: tuple[int, int] | None,
    llvm_aarch32_lines: tuple[int, int] | None,
    contexts: Sequence[dict[str, Any]],
    notes: Sequence[str] = (),
    macro_gates: Sequence[Mapping[str, Any]] | None = None,
    status: ResolutionStatus = ResolutionStatus.RESOLVED,
    include_gcc_aarch64: bool = True,
    arm_registry_page: int | None = None,
) -> dict[str, Any]:
    sources = [
        _source(
            key,
            "acle",
            path="main/acle.md",
            start_line=acle_lines[0],
            end_line=acle_lines[1],
            anchor=acle_anchor,
        )
    ]
    if llvm_aarch64_lines is not None:
        sources.append(
            _source(
                key,
                "llvm-aarch64",
                path="llvm/lib/Target/AArch64/AArch64Features.td",
                start_line=llvm_aarch64_lines[0],
                end_line=llvm_aarch64_lines[1],
            )
        )
        if include_gcc_aarch64:
            sources.append(_source(key, "gcc-aarch64", path="gcc/AArch64-Options.html"))
    if llvm_aarch32_lines is not None:
        sources.extend(
            (
                _source(
                    key,
                    "llvm-aarch32",
                    path="llvm/include/llvm/TargetParser/ARMTargetParser.def",
                    start_line=llvm_aarch32_lines[0],
                    end_line=llvm_aarch32_lines[1],
                ),
                _source(key, "gcc-aarch32", path="gcc/ARM-Options.html"),
            )
        )
    if arm_registry_page is not None:
        sources.append(
            _source(
                key,
                "arm-feature-registry",
                path=ARM_FEATURE_REGISTRY_TITLE,
                page=arm_registry_page,
            )
        )
    return {
        "key": key,
        "title": title,
        "acle_macros": list(macros),
        "macro_gates": list(
            macro_gates
            if macro_gates is not None
            else (
                {
                    "macro": macro,
                    "kind": "defined",
                    "display": f"defined({macro})",
                    "notes": [],
                }
                for macro in macros
            )
        ),
        "architecture_features": list(architecture_features),
        "extension_names": list(extension_names),
        "implies": list(implies),
        "contexts": list(contexts),
        "sources": sources,
        "notes": list(notes),
        "status": status.value,
    }


def _source_ids(key: str, target: str) -> tuple[str, str]:
    suffix = "aarch64" if target == "aarch64" else "aarch32"
    return (f"{key}:llvm-{suffix}", f"{key}:gcc-{suffix}")


def _aarch64_context(
    key: str,
    *,
    architecture_min: str,
    march: str,
    mcpu: str,
    base_march: str,
    default_enabled: bool | None,
    note: str,
    extra_notes: Sequence[str] = (),
    status: ResolutionStatus = ResolutionStatus.RESOLVED,
) -> dict[str, Any]:
    llvm_source, gcc_source = _source_ids(key, "aarch64")
    return _context(
        target="aarch64",
        architecture_min=architecture_min,
        profiles=("A",),
        execution_states=("AArch64",),
        march=march,
        mcpu=mcpu,
        base_march=base_march,
        default_enabled=default_enabled,
        llvm_source_id=llvm_source,
        gcc_source_id=gcc_source,
        note=note,
        extra_notes=extra_notes,
        status=status,
    )


def _aarch64_clang_context(
    key: str,
    *,
    architecture_min: str,
    march: str,
    mcpu: str,
    base_march: str,
    default_enabled: bool | None,
    note: str,
    extra_notes: Sequence[str] = (),
) -> dict[str, Any]:
    llvm_source, _ = _source_ids(key, "aarch64")
    return {
        "target": "aarch64",
        "architecture_min": architecture_min,
        "profiles": ["A"],
        "execution_states": ["AArch64"],
        "compiler_flags": _clang_flags(
            target="aarch64",
            march=march,
            mcpu=mcpu,
            base_march=base_march,
            default_enabled=default_enabled,
            source_id=llvm_source,
            note=note,
        ),
        "notes": list(extra_notes),
        "source_ids": [llvm_source],
        "status": ResolutionStatus.PARTIAL.value,
    }


def _aarch32_context(
    key: str,
    *,
    architecture_min: str,
    profiles: Sequence[str],
    march: str,
    mcpu: str,
    base_march: str,
    default_enabled: bool | None,
    note: str,
    extra_notes: Sequence[str] = (),
) -> dict[str, Any]:
    llvm_source, gcc_source = _source_ids(key, "aarch32")
    fp_simd_options: tuple[str, ...] = ()
    if key != "crc32":
        fp_simd_options = ("-mfpu=auto", "-mfloat-abi=softfp")
        extra_notes = (
            *extra_notes,
            "Keep -mfpu=auto so it does not override -march feature selection.",
            "softfp permits hardware instructions; hard is also valid but is ABI-incompatible with softfp.",
        )
    return _context(
        target="aarch32",
        architecture_min=architecture_min,
        profiles=profiles,
        execution_states=("AArch32", "T32"),
        march=(march, *fp_simd_options),
        mcpu=(mcpu, *fp_simd_options),
        base_march=base_march,
        default_enabled=default_enabled,
        llvm_source_id=llvm_source,
        gcc_source_id=gcc_source,
        note=note,
        extra_notes=extra_notes,
    )


def _m_profile_context(
    key: str,
    *,
    march: str,
    mcpu: str,
    note: str,
    default_enabled: bool | None,
    architecture_min: str = "Armv8.1-M Mainline",
    base_march: str = "armv8.1-m.main",
) -> dict[str, Any]:
    llvm_source, gcc_source = _source_ids(key, "aarch32")
    mode_options: tuple[str, ...]
    if key == "cde":
        mode_options = ("-mthumb",)
    else:
        mode_options = ("-mthumb", "-mfpu=auto", "-mfloat-abi=softfp")
    return _context(
        target="aarch32",
        architecture_min=architecture_min,
        profiles=("M",),
        execution_states=("T32",),
        march=(march, *mode_options),
        mcpu=(mcpu, *mode_options),
        base_march=base_march,
        default_enabled=default_enabled,
        llvm_source_id=llvm_source,
        gcc_source_id=gcc_source,
        note=note,
        extra_notes=(
            "M-profile code uses the T32 execution state.",
            "For MVE, -mfloat-abi=soft would disable vector/FP instructions; keep the project ABI consistent when choosing softfp or hard.",
        ),
    )


def _unresolved_bf16_scalar_feature() -> dict[str, Any]:
    reason = (
        "Pinned ACLE prose uses __ARM_FEATURE_BF16_SCALAR_ARITHMETIC but does "
        "not provide a normative feature definition or compiler-option mapping."
    )
    source = _source(
        "bf16_scalar_unresolved",
        "acle",
        path="main/acle.md",
        start_line=6745,
        end_line=6749,
        anchor="availability",
    )
    return {
        "key": "bf16_scalar_unresolved",
        "title": "BFloat16 scalar arithmetic (unresolved)",
        "acle_macros": ["__ARM_FEATURE_BF16_SCALAR_ARITHMETIC"],
        "macro_gates": [
            {
                "macro": "__ARM_FEATURE_BF16_SCALAR_ARITHMETIC",
                "kind": "defined",
                "display": "defined(__ARM_FEATURE_BF16_SCALAR_ARITHMETIC)",
                "notes": [reason],
            }
        ],
        "architecture_features": ["Unspecified"],
        "extension_names": [],
        "implies": [],
        "contexts": [
            {
                "target": "unspecified",
                "architecture_min": "Unspecified",
                "profiles": ["Unspecified"],
                "execution_states": ["Unspecified"],
                "compiler_flags": [],
                "notes": [reason],
                "source_ids": [source["id"]],
                "status": "unresolved",
                "unresolved_reason": reason,
            }
        ],
        "sources": [source],
        "notes": [
            reason,
            "Do not silently alias this macro to __ARM_FEATURE_BF16.",
        ],
        "status": "unresolved",
        "unresolved_reason": reason,
    }


def _target_guard_feature_data() -> tuple[dict[str, Any], ...]:
    """Mappings for exact late-model target tokens used by LLVM ACLE headers."""

    gcc_gap_note = (
        "GCC 16.2 does not document this exact modifier; do not substitute a "
        "baseline SVE, SVE2, or SME feature for it."
    )
    return (
        _feature(
            key="faminmax",
            title="Floating-point absolute minimum and maximum",
            macros=("__ARM_FEATURE_FAMINMAX",),
            architecture_features=("FEAT_FAMINMAX",),
            extension_names=("faminmax",),
            implies=(),
            acle_lines=(2286, 2288),
            acle_anchor="floating-point-absolute-minimum-and-maximum-extension",
            llvm_aarch64_lines=(478, 479),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "faminmax",
                    architecture_min="Armv9.2-A",
                    march="-march=armv9.2-a+faminmax",
                    mcpu="-mcpu=generic+faminmax",
                    base_march="armv9.2-a",
                    default_enabled=False,
                    note=(
                        "The Arm ISA requires one of FEAT_AdvSIMD, FEAT_SVE2, "
                        "or FEAT_SME2. The pinned Clang and GCC feature models "
                        "make +faminmax imply their Advanced SIMD alternative; "
                        "SVE/SME callables add the scalable alternative from "
                        "their own target guard."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_FAMINMAX as optional from Armv9.2, mandatory with FEAT_FP from Armv9.5, and requiring one of FEAT_AdvSIMD, FEAT_SVE2, or FEAT_SME2.",
                "Pinned LLVM 22.1.1 and GCC 16.2 expose the +faminmax modifier; Armv9.5-A enables it by default, but the minimum Armv9.2-A example selects it explicitly.",
            ),
            arm_registry_page=142,
        ),
        _feature(
            key="sve_f64mm",
            title="SVE 64-bit floating-point matrix multiply",
            macros=("__ARM_FEATURE_SVE_MATMUL_FP64",),
            architecture_features=("FEAT_F64MM",),
            extension_names=("f64mm",),
            implies=("sve",),
            acle_lines=(2490, 2495),
            acle_anchor="multiplication-of-64-bit-floating-point-matrices",
            llvm_aarch64_lines=(169, 171),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "sve_f64mm",
                    architecture_min="Armv8.2-A",
                    march="-march=armv8.2-a+f64mm",
                    mcpu="-mcpu=generic+f64mm",
                    base_march="armv8.2-a",
                    default_enabled=False,
                    note=(
                        "The Arm ISA requires FEAT_SVE; +f64mm also enables SVE "
                        "in the pinned Clang and GCC feature models."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_F64MM as optional from Armv8.2 with FEAT_SVE required.",
            ),
            arm_registry_page=42,
        ),
        _feature(
            key="ssve_bitperm",
            title="Streaming SVE bit permutation",
            macros=("__ARM_FEATURE_SSVE_BITPERM",),
            architecture_features=("FEAT_SSVE_BitPerm",),
            extension_names=("ssve-bitperm",),
            implies=("sme2p1",),
            acle_lines=(2504, 2505),
            acle_anchor="bit-permute-extension",
            llvm_aarch64_lines=(573, 574),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_clang_context(
                    "ssve_bitperm",
                    architecture_min="Armv9.4-A",
                    march="-march=armv9.4-a+sme2p1+ssve-bitperm",
                    mcpu="-mcpu=generic+sme2p1+ssve-bitperm",
                    base_march="armv9.4-a",
                    default_enabled=False,
                    note=(
                        "The Arm ISA requires FEAT_SME2p1, which the example "
                        "enables explicitly. Clang additionally models "
                        "+ssve-bitperm as implying +sme2 and +sve-bitperm."
                    ),
                    extra_notes=(gcc_gap_note,),
                ),
            ),
            notes=(
                gcc_gap_note,
                "Arm feature registry 109697_2025_12_en records FEAT_SSVE_BitPerm as optional from Armv9.4 and requires FEAT_SME2p1; FEAT_SVE_BitPerm follows only when FEAT_SVE2 is also present.",
            ),
            status=ResolutionStatus.PARTIAL,
            include_gcc_aarch64=False,
            arm_registry_page=163,
        ),
        _feature(
            key="sve_bitperm",
            title="SVE2 bit permutation",
            macros=("__ARM_FEATURE_SVE2_BITPERM",),
            architecture_features=("FEAT_SVE_BitPerm",),
            extension_names=("sve-bitperm",),
            implies=("sve2",),
            acle_lines=(2497, 2502),
            acle_anchor="bit-permute-extension",
            llvm_aarch64_lines=(385, 389),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "sve_bitperm",
                    architecture_min="Armv9-A",
                    march="-march=armv9-a+sve2-bitperm",
                    mcpu="-mcpu=generic+sve2-bitperm",
                    base_march="armv9-a",
                    default_enabled=False,
                    note=(
                        "+sve2-bitperm is the documented complete alias for "
                        "+sve2+sve-bitperm."
                    ),
                ),
            ),
            notes=(
                "The LLVM TableGen guard uses the exact token sve-bitperm; compiler examples use the complete sve2-bitperm alias.",
                "Arm feature registry 109697_2025_12_en records FEAT_SVE_BitPerm as optional from Armv9.0 with FEAT_SVE2 required.",
            ),
            arm_registry_page=120,
        ),
        _feature(
            key="lut",
            title="Lookup table",
            macros=("__ARM_FEATURE_LUT",),
            architecture_features=("FEAT_LUT",),
            extension_names=("lut",),
            implies=(),
            acle_lines=(2297, 2301),
            acle_anchor="lookup-table-extensions",
            llvm_aarch64_lines=(481, 482),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "lut",
                    architecture_min="Armv9.2-A",
                    march="-march=armv9.2-a+lut",
                    mcpu="-mcpu=generic+lut",
                    base_march="armv9.2-a",
                    default_enabled=False,
                    note=(
                        "The Arm ISA requires one of Advanced SIMD, SVE2, or "
                        "SME2. AArch64 provides Advanced SIMD; +lut remains "
                        "explicit because Armv9.2-A does not make LUT mandatory."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_LUT as optional from Armv9.2 and requires one of FEAT_AdvSIMD, FEAT_SVE2, or FEAT_SME2.",
                "Pinned Clang models +lut as implying Advanced SIMD; that compiler implication is distinct from the ISA's three-way requirement.",
            ),
            arm_registry_page=147,
        ),
        _feature(
            key="sve_aes2",
            title="SVE AES2",
            macros=("__ARM_FEATURE_SVE_AES2",),
            architecture_features=("FEAT_SVE_AES2",),
            extension_names=("sve-aes2",),
            implies=("sve_pmull128",),
            acle_lines=(2218, 2228),
            acle_anchor="aes-extension",
            llvm_aarch64_lines=(552, 553),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_clang_context(
                    "sve_aes2",
                    architecture_min="Armv9.5-A",
                    march="-march=armv9.5-a+sve2p1+sve-aes+sve-aes2",
                    mcpu="-mcpu=generic+sve2p1+sve-aes+sve-aes2",
                    base_march="armv9.5-a",
                    default_enabled=False,
                    note=(
                        "The non-streaming ISA path requires FEAT_SVE_PMULL128 "
                        "and FEAT_SVE2p1. The example uses +sve-aes for the "
                        "pinned compiler's SVE AES/PMULL control and names "
                        "+sve2p1 explicitly because +sve-aes2 implies neither."
                    ),
                    extra_notes=(gcc_gap_note,),
                ),
            ),
            notes=(
                gcc_gap_note,
                "Streaming declarations additionally require the distinct ssve-aes target feature; do not collapse it into sve-aes2.",
                "Arm feature registry 109697_2025_12_en records FEAT_SVE_AES2 as optional from Armv9.5 and requires FEAT_SVE_PMULL128 plus either FEAT_SVE2p1 or FEAT_SSVE_AES.",
            ),
            status=ResolutionStatus.PARTIAL,
            include_gcc_aarch64=False,
            arm_registry_page=165,
        ),
        _feature(
            key="ssve_aes",
            title="Streaming SVE AES",
            macros=("__ARM_FEATURE_SSVE_AES",),
            architecture_features=("FEAT_SSVE_AES",),
            extension_names=("ssve-aes",),
            implies=("sme2p1",),
            acle_lines=(2222, 2226),
            acle_anchor="aes-extension",
            llvm_aarch64_lines=(546, 547),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_clang_context(
                    "ssve_aes",
                    architecture_min="Armv9.5-A",
                    march="-march=armv9.5-a+sme2p1+ssve-aes",
                    mcpu="-mcpu=generic+sme2p1+ssve-aes",
                    base_march="armv9.5-a",
                    default_enabled=False,
                    note=(
                        "The Arm ISA requires FEAT_SME2p1, which the example "
                        "enables explicitly. Clang additionally models "
                        "+ssve-aes as implying +sme2 and +sve-aes; it does not "
                        "imply the distinct +sve-aes2 feature."
                    ),
                    extra_notes=(gcc_gap_note,),
                ),
            ),
            notes=(
                gcc_gap_note,
                "This streaming feature is distinct from __ARM_FEATURE_SVE2_AES and __ARM_FEATURE_SVE_AES2.",
                "Arm feature registry 109697_2025_12_en records FEAT_SSVE_AES as optional from Armv9.5 with FEAT_SME2p1 required.",
            ),
            status=ResolutionStatus.PARTIAL,
            include_gcc_aarch64=False,
            arm_registry_page=163,
        ),
        _feature(
            key="fp8fma",
            title="Modal FP8 multiply-accumulate",
            macros=("__ARM_FEATURE_FP8FMA",),
            architecture_features=("FEAT_FP8FMA",),
            extension_names=("fp8fma",),
            implies=("fp8",),
            acle_lines=(2312, 2314),
            acle_anchor="modal-8-bit-floating-point-extensions",
            llvm_aarch64_lines=(487, 488),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "fp8fma",
                    architecture_min="Armv9.2-A",
                    march="-march=armv9.2-a+faminmax+lut+fp8fma",
                    mcpu="-mcpu=generic+bf16+faminmax+lut+fp8fma",
                    base_march="armv9.2-a",
                    default_enabled=False,
                    note=(
                        "The Arm ISA requires FEAT_FP8 and either Advanced SIMD "
                        "or SVE2. The examples also enable the FP8 dependencies "
                        "that Clang 22.1.1 can express; +fp8fma supplies +fp8 in "
                        "the pinned compiler model."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_FP8FMA as optional from Armv9.2 and requires FEAT_FP8 plus either FEAT_AdvSIMD or FEAT_SVE2.",
                "FEAT_FP8 in turn requires FEAT_FPMR, FEAT_FAMINMAX, FEAT_LUT, FEAT_BF16, and one of FEAT_AdvSIMD, FEAT_SVE2, or FEAT_SME2.",
                "Clang 22.1.1 has no +fpmr modifier; the official ISA dependency is retained without inventing a compiler flag.",
            ),
            arm_registry_page=145,
        ),
        _feature(
            key="ssve_fp8fma",
            title="Streaming SVE modal FP8 multiply-accumulate",
            macros=("__ARM_FEATURE_SSVE_FP8FMA",),
            architecture_features=("FEAT_SSVE_FP8FMA",),
            extension_names=("ssve-fp8fma",),
            implies=("sme2", "fp8"),
            acle_lines=(2334, 2337),
            acle_anchor="modal-8-bit-floating-point-extensions",
            llvm_aarch64_lines=(490, 491),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "ssve_fp8fma",
                    architecture_min="Armv9.2-A",
                    march=("-march=armv9.2-a+faminmax+lut+fp8+sme2+ssve-fp8fma"),
                    mcpu=("-mcpu=generic+bf16+faminmax+lut+fp8+sme2+ssve-fp8fma"),
                    base_march="armv9.2-a",
                    default_enabled=False,
                    note=(
                        "The Arm ISA requires FEAT_SME2 and FEAT_FP8. The "
                        "examples name both and enable every additional FP8 "
                        "dependency that Clang 22.1.1 can express."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_SSVE_FP8FMA as optional from Armv9.2 with FEAT_FP8 and FEAT_SME2 required.",
                "FEAT_FP8 in turn requires FEAT_FPMR, FEAT_FAMINMAX, FEAT_LUT, FEAT_BF16, and one of FEAT_AdvSIMD, FEAT_SVE2, or FEAT_SME2.",
                "Clang 22.1.1 has no +fpmr modifier; the official ISA dependency is retained without inventing a compiler flag.",
            ),
            arm_registry_page=153,
        ),
        _feature(
            key="fp8",
            title="Modal 8-bit floating point",
            macros=("__ARM_FEATURE_FP8",),
            architecture_features=("FEAT_FP8",),
            extension_names=("fp8",),
            implies=("fpmr", "faminmax", "lut", "bf16"),
            acle_lines=(2307, 2310),
            acle_anchor="modal-8-bit-floating-point-extensions",
            llvm_aarch64_lines=(484, 485),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "fp8",
                    architecture_min="Armv9.2-A",
                    march="-march=armv9.2-a+faminmax+lut+fp8",
                    mcpu="-mcpu=generic+bf16+faminmax+lut+fp8",
                    base_march="armv9.2-a",
                    default_enabled=False,
                    note=(
                        "The examples enable every FEAT_FP8 dependency that "
                        "Clang 22.1.1 can express. The AArch64 target provides "
                        "the required Advanced SIMD alternative."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_FP8 as optional from Armv9.2 and requires FEAT_FPMR, FEAT_FAMINMAX, FEAT_LUT, FEAT_BF16, and one of FEAT_AdvSIMD, FEAT_SVE2, or FEAT_SME2.",
                "Clang 22.1.1 models +fp8 as implying Advanced SIMD but has no +fpmr modifier; the official ISA dependency is retained without inventing a compiler flag.",
            ),
            arm_registry_page=143,
        ),
        _feature(
            key="sve_bfscale",
            title="SVE BFloat16 scale",
            macros=("__ARM_FEATURE_SVE_BFSCALE",),
            architecture_features=("FEAT_SVE_BFSCALE",),
            extension_names=("sve-bfscale",),
            implies=("sve_b16b16",),
            acle_lines=(2165, 2173),
            acle_anchor="brain-16-bit-floating-point-vector-multiplication-support",
            llvm_aarch64_lines=(555, 556),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "sve_bfscale",
                    architecture_min="Armv9.2-A",
                    march="-march=armv9.2-a+sve2+sve-b16b16+sve-bfscale",
                    mcpu="-mcpu=generic+sve2+sve-b16b16+sve-bfscale",
                    base_march="armv9.2-a",
                    default_enabled=False,
                    note=(
                        "The Arm ISA requires FEAT_SVE_B16B16. The non-streaming "
                        "example selects its FEAT_SVE2 alternative explicitly; "
                        "Clang's +sve-bfscale modifier does not imply either."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_SVE_BFSCALE as optional from Armv9.2 with FEAT_SVE_B16B16 required; FEAT_SVE_B16B16 requires either FEAT_SVE2 or FEAT_SME2.",
                "Pinned LLVM's version grouping and parser acceptance are compiler-model facts, not architecture-minimum evidence.",
            ),
            arm_registry_page=165,
        ),
        _feature(
            key="ssve_fexpa",
            title="Streaming SVE FEXPA",
            macros=("__ARM_FEATURE_SSVE_FEXPA",),
            architecture_features=("FEAT_SSVE_FEXPA",),
            extension_names=("ssve-fexpa",),
            implies=("sme2p1",),
            acle_lines=(2509, 2511),
            acle_anchor="streaming-sve-fexpa-extension",
            llvm_aarch64_lines=(582, 583),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_clang_context(
                    "ssve_fexpa",
                    architecture_min="Armv9.4-A",
                    march="-march=armv9.4-a+sme2p1+ssve-fexpa",
                    mcpu="-mcpu=generic+sme2p1+ssve-fexpa",
                    base_march="armv9.4-a",
                    default_enabled=False,
                    note=(
                        "The Arm ISA requires FEAT_SME2p1, which the example "
                        "enables explicitly. Clang additionally models "
                        "+ssve-fexpa as implying +sme2."
                    ),
                    extra_notes=(gcc_gap_note,),
                ),
            ),
            notes=(
                gcc_gap_note,
                "Arm feature registry 109697_2025_12_en records FEAT_SSVE_FEXPA as optional from Armv9.4 with FEAT_SME2p1 required.",
            ),
            status=ResolutionStatus.PARTIAL,
            include_gcc_aarch64=False,
            arm_registry_page=164,
        ),
        _feature(
            key="sme_f16f16",
            title="SME non-widening Float16",
            macros=("__ARM_FEATURE_SME_F16F16",),
            architecture_features=("FEAT_SME_F16F16",),
            extension_names=("sme-f16f16",),
            implies=("sme2",),
            acle_lines=(2104, 2112),
            acle_anchor="half-precision-floating-point-sme-intrinsics",
            llvm_aarch64_lines=(447, 448),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "sme_f16f16",
                    architecture_min="Armv9.2-A",
                    march="-march=armv9.2-a+sme2+sme-f16f16",
                    mcpu="-mcpu=generic+sme2+sme-f16f16",
                    base_march="armv9.2-a",
                    default_enabled=False,
                    note=(
                        "The Arm ISA requires FEAT_SME2, which the example names "
                        "explicitly; +sme-f16f16 also implies SME2 in both pinned "
                        "compiler models."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_SME_F16F16 as optional from Armv9.2 with FEAT_SME2 required.",
            ),
            arm_registry_page=136,
        ),
        _feature(
            key="sve_f32mm",
            title="SVE 32-bit floating-point matrix multiply",
            macros=("__ARM_FEATURE_SVE_MATMUL_FP32",),
            architecture_features=("FEAT_F32MM",),
            extension_names=("f32mm",),
            implies=("sve",),
            acle_lines=(2483, 2488),
            acle_anchor="multiplication-of-32-bit-floating-point-matrices",
            llvm_aarch64_lines=(165, 167),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "sve_f32mm",
                    architecture_min="Armv8.2-A",
                    march="-march=armv8.2-a+f32mm",
                    mcpu="-mcpu=generic+f32mm",
                    base_march="armv8.2-a",
                    default_enabled=False,
                    note=(
                        "The Arm ISA requires FEAT_SVE; +f32mm also enables SVE "
                        "in the pinned Clang and GCC feature models."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_F32MM as optional from Armv8.2 with FEAT_SVE required.",
            ),
            arm_registry_page=42,
        ),
        _feature(
            key="sve_f16f32mm",
            title="SVE Float16-to-Float32 matrix multiply",
            macros=("__ARM_FEATURE_SVE_F16F32MM",),
            architecture_features=("FEAT_SVE_F16F32MM",),
            extension_names=("sve-f16f32mm",),
            implies=("sve2p1",),
            acle_lines=(2462, 2466),
            acle_anchor="multiplication-of-16-bit-floating-point-matrices",
            llvm_aarch64_lines=(558, 559),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_clang_context(
                    "sve_f16f32mm",
                    architecture_min="Armv9.2-A",
                    march="-march=armv9.2-a+sve2p1+sve-f16f32mm",
                    mcpu="-mcpu=generic+sve2p1+sve-f16f32mm",
                    base_march="armv9.2-a",
                    default_enabled=False,
                    note=(
                        "The Arm ISA requires FEAT_SVE2p1, which the example "
                        "enables explicitly. Clang's +sve-f16f32mm modifier "
                        "alone implies only its lower-level +sve feature."
                    ),
                    extra_notes=(
                        gcc_gap_note,
                        "GCC's documented +f16f32mm modifier names the distinct Advanced SIMD FEAT_F16F32MM extension and is not a substitute.",
                    ),
                ),
            ),
            notes=(
                gcc_gap_note,
                "Do not alias this token to GCC's distinct +f16f32mm Advanced SIMD feature.",
                "Arm feature registry 109697_2025_12_en records FEAT_SVE_F16F32MM as optional from Armv9.2 with FEAT_SVE2p1 required.",
            ),
            status=ResolutionStatus.PARTIAL,
            include_gcc_aarch64=False,
            arm_registry_page=166,
        ),
    )


def _late_exact_feature_data() -> tuple[dict[str, Any], ...]:
    """Exact ACLE-to-compiler mappings for late A-profile extensions."""

    gcc_gap_note = (
        "GCC 16.2 does not document this exact modifier; the examples are "
        "therefore scoped to Clang 22.1.1."
    )
    return (
        _feature(
            key="sme_i16i64",
            title="SME 16-bit to 64-bit integer widening",
            macros=("__ARM_FEATURE_SME_I16I64",),
            architecture_features=("FEAT_SME_I16I64",),
            extension_names=("sme-i16i64",),
            implies=("sme",),
            acle_lines=(2513, 2523),
            acle_anchor="16-bit-to-64-bit-integer-widening-outer-product-intrinsics",
            llvm_aarch64_lines=(417, 418),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "sme_i16i64",
                    architecture_min="Armv9.2-A",
                    march="-march=armv9.2-a+sme+sme-i16i64",
                    mcpu="-mcpu=generic+sme+sme-i16i64",
                    base_march="armv9.2-a",
                    default_enabled=False,
                    note=(
                        "The Arm ISA requires FEAT_SME; the example names the "
                        "dependency explicitly."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_SME_I16I64 as optional from Armv9.2 with FEAT_SME required.",
            ),
            arm_registry_page=126,
        ),
        _feature(
            key="sme_f64f64",
            title="SME double-precision outer product",
            macros=("__ARM_FEATURE_SME_F64F64",),
            architecture_features=("FEAT_SME_F64F64",),
            extension_names=("sme-f64f64",),
            implies=("sme",),
            acle_lines=(2525, 2534),
            acle_anchor="double-precision-floating-point-outer-product-intrinsics",
            llvm_aarch64_lines=(414, 415),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "sme_f64f64",
                    architecture_min="Armv9.2-A",
                    march="-march=armv9.2-a+sme+sme-f64f64",
                    mcpu="-mcpu=generic+sme+sme-f64f64",
                    base_march="armv9.2-a",
                    default_enabled=False,
                    note=(
                        "The Arm ISA requires FEAT_SME; the example names the "
                        "dependency explicitly."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_SME_F64F64 as optional from Armv9.2 with FEAT_SME required.",
            ),
            arm_registry_page=126,
        ),
        _feature(
            key="sme_lutv2",
            title="SME lookup table v2",
            macros=("__ARM_FEATURE_SME_LUTv2",),
            architecture_features=("FEAT_SME_LUTv2",),
            extension_names=("sme-lutv2",),
            implies=("sme2",),
            acle_lines=(2297, 2305),
            acle_anchor="lookup-table-extensions",
            llvm_aarch64_lines=(505, 506),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "sme_lutv2",
                    architecture_min="Armv9.2-A",
                    march="-march=armv9.2-a+sme2+sme-lutv2",
                    mcpu="-mcpu=generic+sme2+sme-lutv2",
                    base_march="armv9.2-a",
                    default_enabled=False,
                    note=(
                        "The Arm ISA requires FEAT_SME2; the example names the "
                        "dependency explicitly."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_SME_LUTv2 as optional from Armv9.2 with FEAT_SME2 required.",
            ),
            arm_registry_page=150,
        ),
        _feature(
            key="sme_mop4",
            title="SME quarter-tile outer product",
            macros=("__ARM_FEATURE_SME_MOP4",),
            architecture_features=("FEAT_SME_MOP4",),
            extension_names=("sme-mop4",),
            implies=("sme2p1",),
            acle_lines=(2548, 2557),
            acle_anchor="quarter-tile-outer-product-intrinsics",
            llvm_aarch64_lines=(576, 577),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_clang_context(
                    "sme_mop4",
                    architecture_min="Armv9.4-A",
                    march="-march=armv9.4-a+sme2p1+sme-mop4",
                    mcpu="-mcpu=generic+sme2p1+sme-mop4",
                    base_march="armv9.4-a",
                    default_enabled=False,
                    note=(
                        "The Arm ISA requires FEAT_SME2p1; the example names "
                        "the dependency explicitly."
                    ),
                    extra_notes=(gcc_gap_note,),
                ),
            ),
            notes=(
                gcc_gap_note,
                "Arm feature registry 109697_2025_12_en records FEAT_SME_MOP4 as optional from Armv9.4 with FEAT_SME2p1 required.",
            ),
            status=ResolutionStatus.PARTIAL,
            include_gcc_aarch64=False,
            arm_registry_page=161,
        ),
        _feature(
            key="sme_tmop",
            title="SME structured sparsity outer product",
            macros=("__ARM_FEATURE_SME_TMOP",),
            architecture_features=("FEAT_SME_TMOP",),
            extension_names=("sme-tmop",),
            implies=("sme2p1",),
            acle_lines=(2536, 2546),
            acle_anchor="structured-sparsity-outer-product-intrinsics",
            llvm_aarch64_lines=(579, 580),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_clang_context(
                    "sme_tmop",
                    architecture_min="Armv9.4-A",
                    march="-march=armv9.4-a+sme2p1+sme-tmop",
                    mcpu="-mcpu=generic+sme2p1+sme-tmop",
                    base_march="armv9.4-a",
                    default_enabled=False,
                    note=(
                        "The Arm ISA requires FEAT_SME2p1; the example names "
                        "the dependency explicitly."
                    ),
                    extra_notes=(gcc_gap_note,),
                ),
            ),
            notes=(
                gcc_gap_note,
                "Arm feature registry 109697_2025_12_en records FEAT_SME_TMOP as optional from Armv9.4 with FEAT_SME2p1 required.",
            ),
            status=ResolutionStatus.PARTIAL,
            include_gcc_aarch64=False,
            arm_registry_page=161,
        ),
        _feature(
            key="fp8dot4",
            title="FP8 four-way dot product",
            macros=("__ARM_FEATURE_FP8DOT4",),
            architecture_features=("FEAT_FP8DOT4",),
            extension_names=("fp8dot4",),
            implies=("fp8fma",),
            acle_lines=(2312, 2323),
            acle_anchor="modal-8-bit-floating-point-extensions",
            llvm_aarch64_lines=(493, 494),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "fp8dot4",
                    architecture_min="Armv9.2-A",
                    march="-march=armv9.2-a+faminmax+lut+fp8fma+fp8dot4",
                    mcpu="-mcpu=generic+bf16+faminmax+lut+fp8fma+fp8dot4",
                    base_march="armv9.2-a",
                    default_enabled=False,
                    note=(
                        "The example enables FEAT_FP8FMA and every expressible "
                        "FEAT_FP8 dependency; AArch64 supplies the Advanced SIMD "
                        "alternative."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_FP8DOT4 as optional from Armv9.2 with FEAT_FP8FMA and either FEAT_AdvSIMD or FEAT_SVE2 required.",
            ),
            arm_registry_page=145,
        ),
        _feature(
            key="fp8dot2",
            title="FP8 two-way dot product",
            macros=("__ARM_FEATURE_FP8DOT2",),
            architecture_features=("FEAT_FP8DOT2",),
            extension_names=("fp8dot2",),
            implies=("fp8dot4",),
            acle_lines=(2312, 2323),
            acle_anchor="modal-8-bit-floating-point-extensions",
            llvm_aarch64_lines=(496, 497),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "fp8dot2",
                    architecture_min="Armv9.2-A",
                    march="-march=armv9.2-a+faminmax+lut+fp8fma+fp8dot4+fp8dot2",
                    mcpu="-mcpu=generic+bf16+faminmax+lut+fp8fma+fp8dot4+fp8dot2",
                    base_march="armv9.2-a",
                    default_enabled=False,
                    note=(
                        "The example enables FEAT_FP8DOT4, FEAT_FP8FMA, and "
                        "every expressible FEAT_FP8 dependency."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_FP8DOT2 as optional from Armv9.2 with FEAT_FP8DOT4 and either FEAT_AdvSIMD or FEAT_SVE2 required.",
            ),
            arm_registry_page=144,
        ),
        _feature(
            key="ssve_fp8dot4",
            title="Streaming SVE FP8 four-way dot product",
            macros=("__ARM_FEATURE_SSVE_FP8DOT4",),
            architecture_features=("FEAT_SSVE_FP8DOT4",),
            extension_names=("ssve-fp8dot4",),
            implies=("sme2", "ssve_fp8fma"),
            acle_lines=(2312, 2323),
            acle_anchor="modal-8-bit-floating-point-extensions",
            llvm_aarch64_lines=(499, 500),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "ssve_fp8dot4",
                    architecture_min="Armv9.2-A",
                    march="-march=armv9.2-a+faminmax+lut+sme2+ssve-fp8fma+ssve-fp8dot4",
                    mcpu="-mcpu=generic+bf16+faminmax+lut+sme2+ssve-fp8fma+ssve-fp8dot4",
                    base_march="armv9.2-a",
                    default_enabled=False,
                    note=(
                        "The example enables FEAT_SME2, FEAT_SSVE_FP8FMA, and "
                        "every expressible FEAT_FP8 dependency."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_SSVE_FP8DOT4 as optional from Armv9.2 with FEAT_SSVE_FP8FMA required.",
            ),
            arm_registry_page=152,
        ),
        _feature(
            key="ssve_fp8dot2",
            title="Streaming SVE FP8 two-way dot product",
            macros=("__ARM_FEATURE_SSVE_FP8DOT2",),
            architecture_features=("FEAT_SSVE_FP8DOT2",),
            extension_names=("ssve-fp8dot2",),
            implies=("ssve_fp8dot4",),
            acle_lines=(2312, 2323),
            acle_anchor="modal-8-bit-floating-point-extensions",
            llvm_aarch64_lines=(502, 503),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "ssve_fp8dot2",
                    architecture_min="Armv9.2-A",
                    march="-march=armv9.2-a+faminmax+lut+sme2+ssve-fp8fma+ssve-fp8dot4+ssve-fp8dot2",
                    mcpu="-mcpu=generic+bf16+faminmax+lut+sme2+ssve-fp8fma+ssve-fp8dot4+ssve-fp8dot2",
                    base_march="armv9.2-a",
                    default_enabled=False,
                    note=(
                        "The example enables the four-way streaming form, "
                        "FEAT_SSVE_FP8FMA, and every expressible FEAT_FP8 dependency."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_SSVE_FP8DOT2 as optional from Armv9.2.",
            ),
            arm_registry_page=152,
        ),
        _feature(
            key="sme_f8f32",
            title="SME FP8 to single-precision operations",
            macros=("__ARM_FEATURE_SME_F8F32",),
            architecture_features=("FEAT_SME_F8F32",),
            extension_names=("sme-f8f32",),
            implies=("sme2", "fp8"),
            acle_lines=(2339, 2343),
            acle_anchor="modal-8-bit-floating-point-extensions",
            llvm_aarch64_lines=(508, 509),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "sme_f8f32",
                    architecture_min="Armv9.2-A",
                    march="-march=armv9.2-a+faminmax+lut+fp8+sme2+sme-f8f32",
                    mcpu="-mcpu=generic+bf16+faminmax+lut+fp8+sme2+sme-f8f32",
                    base_march="armv9.2-a",
                    default_enabled=False,
                    note=(
                        "The example enables FEAT_SME2 and every expressible "
                        "FEAT_FP8 dependency."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_SME_F8F32 as optional from Armv9.2 with FEAT_SME2 and FEAT_FP8 required.",
            ),
            arm_registry_page=149,
        ),
        _feature(
            key="sme_f8f16",
            title="SME FP8 to half-precision operations",
            macros=("__ARM_FEATURE_SME_F8F16",),
            architecture_features=("FEAT_SME_F8F16",),
            extension_names=("sme-f8f16",),
            implies=("sme_f8f32",),
            acle_lines=(2344, 2348),
            acle_anchor="modal-8-bit-floating-point-extensions",
            llvm_aarch64_lines=(511, 512),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "sme_f8f16",
                    architecture_min="Armv9.2-A",
                    march="-march=armv9.2-a+faminmax+lut+fp8+sme2+sme-f8f32+sme-f8f16",
                    mcpu="-mcpu=generic+bf16+faminmax+lut+fp8+sme2+sme-f8f32+sme-f8f16",
                    base_march="armv9.2-a",
                    default_enabled=False,
                    note=(
                        "The example enables FEAT_SME_F8F32 and all of its "
                        "expressible FEAT_FP8 and FEAT_SME2 dependencies."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_SME_F8F16 as optional from Armv9.2 with FEAT_SME_F8F32 required.",
            ),
            arm_registry_page=149,
        ),
        _feature(
            key="qrdmx",
            title="Advanced SIMD rounding doubling multiply-accumulate",
            macros=("__ARM_FEATURE_QRDMX",),
            architecture_features=("FEAT_RDM",),
            extension_names=("rdma",),
            implies=("neon",),
            acle_lines=(2398, 2402),
            acle_anchor="rounding-doubling-multiplies",
            llvm_aarch64_lines=(111, 114),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "qrdmx",
                    architecture_min="Armv8-A",
                    march="-march=armv8-a+simd+rdma",
                    mcpu="-mcpu=generic+simd+rdma",
                    base_march="armv8-a",
                    default_enabled=False,
                    note=(
                        "FEAT_RDM is optional from Armv8.0 and requires "
                        "Advanced SIMD. +rdma is the common GCC spelling and "
                        "a Clang 22.1.1 accepted alias for LLVM's +rdm token."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_RDM as optional from Armv8.0 and selected by default with Advanced SIMD from Armv8.1.",
                "Only the AArch64 compiler context is pinned; AArch32 remains explicitly unresolved.",
            ),
            arm_registry_page=38,
        ),
        _feature(
            key="complex",
            title="Advanced SIMD floating-point complex arithmetic",
            macros=("__ARM_FEATURE_COMPLEX",),
            architecture_features=("FEAT_FCMA",),
            extension_names=("fcma",),
            implies=("neon",),
            acle_lines=(2423, 2433),
            acle_anchor="complex-number-intrinsics",
            llvm_aarch64_lines=(193, 197),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "complex",
                    architecture_min="Armv8.2-A",
                    march="-march=armv8.2-a+simd+fcma",
                    mcpu="-mcpu=generic+simd+fcma",
                    base_march="armv8.2-a",
                    default_enabled=False,
                    note=(
                        "FEAT_FCMA is optional from Armv8.2 and requires "
                        "floating point; the callable's __ARM_NEON branch adds "
                        "the Advanced SIMD requirement explicitly."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_FCMA as optional from Armv8.2 and selected by default with floating point from Armv8.3.",
                "Only the AArch64 compiler context is pinned; AArch32 remains explicitly unresolved.",
            ),
            arm_registry_page=55,
        ),
        _feature(
            key="frint",
            title="Floating-point rounding to integer format",
            macros=("__ARM_FEATURE_FRINT",),
            architecture_features=("FEAT_FRINTTS",),
            extension_names=(),
            implies=("fp", "neon"),
            acle_lines=(2373, 2383),
            acle_anchor="armv85-a-floating-point-rounding-extension",
            llvm_aarch64_lines=(248, 251),
            llvm_aarch32_lines=None,
            contexts=(
                {
                    "target": "aarch64",
                    "architecture_min": "Armv8.4-A",
                    "profiles": ["A"],
                    "execution_states": ["AArch64"],
                    "compiler_flags": [
                        {
                            "compiler": "Clang",
                            "version": "22.1.1",
                            "base_march": "armv8.5-a",
                            "flags": ["-march=armv8.5-a+simd"],
                            "default_enabled": True,
                            "notes": [
                                "Target: aarch64.",
                                "Clang 22.1.1 has no accepted explicit FEAT_FRINTTS modifier; Armv8.5-A enables it with floating point.",
                            ],
                            "source_ids": ["frint:llvm-aarch64"],
                        },
                        {
                            "compiler": "GCC",
                            "version": GCC_MANUAL_VERSION,
                            "base_march": "armv8.4-a",
                            "flags": ["-march=armv8.4-a+simd+frintts"],
                            "default_enabled": False,
                            "notes": [
                                "Target: aarch64.",
                                "GCC 16.2 documents +frintts as the explicit FEAT_FRINTTS modifier.",
                            ],
                            "source_ids": ["frint:gcc-aarch64"],
                        },
                    ],
                    "notes": [
                        "Compiler-specific spellings are retained instead of inventing a common modifier."
                    ],
                    "source_ids": [
                        "frint:llvm-aarch64",
                        "frint:gcc-aarch64",
                    ],
                    "status": ResolutionStatus.RESOLVED.value,
                },
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_FRINTTS as optional from Armv8.4 and mandatory with floating point from Armv8.5.",
                "ACLE restricts __ARM_FEATURE_FRINT to AArch64.",
            ),
            arm_registry_page=75,
        ),
        _feature(
            key="f16f32dot",
            title="Advanced SIMD Float16-to-Float32 dot product",
            macros=("__ARM_FEATURE_F16F32DOT",),
            architecture_features=("FEAT_F16F32DOT",),
            extension_names=("f16f32dot",),
            implies=("fp16fml", "neon"),
            acle_lines=(2411, 2421),
            acle_anchor="half-precision-to-single-precision-dot-product-extension",
            llvm_aarch64_lines=(619, 620),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "f16f32dot",
                    architecture_min="Armv9.4-A",
                    march="-march=armv9.4-a+fp16fml+f16f32dot",
                    mcpu="-mcpu=generic+fp16fml+f16f32dot",
                    base_march="armv9.4-a",
                    default_enabled=False,
                    note=(
                        "The Arm ISA requires FEAT_FHM; +fp16fml names that "
                        "dependency explicitly and also enables Advanced SIMD."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_F16F32DOT as optional from Armv9.4 with FEAT_FHM required.",
            ),
            arm_registry_page=168,
        ),
        _feature(
            key="f16f32mm",
            title="Advanced SIMD Float16-to-Float32 matrix multiply",
            macros=("__ARM_FEATURE_F16F32MM",),
            architecture_features=("FEAT_F16F32MM",),
            extension_names=("f16f32mm",),
            implies=("f16f32dot",),
            acle_lines=(2468, 2477),
            acle_anchor="multiplication-of-16-bit-floating-point-matrices-advsimd",
            llvm_aarch64_lines=(622, 623),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "f16f32mm",
                    architecture_min="Armv9.4-A",
                    march="-march=armv9.4-a+fp16fml+f16f32dot+f16f32mm",
                    mcpu="-mcpu=generic+fp16fml+f16f32dot+f16f32mm",
                    base_march="armv9.4-a",
                    default_enabled=False,
                    note=(
                        "The Arm ISA requires FEAT_F16F32DOT, whose FEAT_FHM "
                        "dependency is named by +fp16fml."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_F16F32MM as optional from Armv9.4 with FEAT_F16F32DOT required.",
            ),
            arm_registry_page=168,
        ),
        _feature(
            key="f16mm",
            title="Advanced SIMD non-widening Float16 matrix multiply",
            macros=("__ARM_FEATURE_F16MM",),
            architecture_features=("FEAT_F16MM",),
            extension_names=("f16mm",),
            implies=("fp16", "neon_or_sve2p2"),
            acle_lines=(2478, 2481),
            acle_anchor="multiplication-of-16-bit-floating-point-matrices-advsimd",
            llvm_aarch64_lines=(616, 617),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "f16mm",
                    architecture_min="Armv9.6-A",
                    march="-march=armv9.6-a+fp16+f16mm",
                    mcpu="-mcpu=generic+fp16+f16mm",
                    base_march="armv9.6-a",
                    default_enabled=False,
                    note=(
                        "The Arm ISA requires FEAT_FP16 and either Advanced "
                        "SIMD or FEAT_SVE2p2; this Advanced SIMD example names "
                        "the FP16 dependency explicitly."
                    ),
                ),
            ),
            notes=(
                "Arm feature registry 109697_2025_12_en records FEAT_F16MM as optional from Armv9.6 with FEAT_FP16 and either FEAT_AdvSIMD or FEAT_SVE2p2 required.",
            ),
            arm_registry_page=169,
        ),
        _feature(
            key="f8f16mm",
            title="FP8-to-Float16 matrix multiply",
            macros=("__ARM_FEATURE_F8F16MM",),
            architecture_features=("FEAT_F8F16MM",),
            extension_names=("f8f16mm",),
            implies=("fp8dot2",),
            acle_lines=(2448, 2461),
            acle_anchor="multiplication-of-modal-8-bit-floating-point-matrices",
            llvm_aarch64_lines=(533, 534),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_clang_context(
                    "f8f16mm",
                    architecture_min="Armv9.2-A",
                    march="-march=armv9.2-a+faminmax+lut+fp8fma+fp8dot4+fp8dot2+f8f16mm",
                    mcpu="-mcpu=generic+bf16+faminmax+lut+fp8fma+fp8dot4+fp8dot2+f8f16mm",
                    base_march="armv9.2-a",
                    default_enabled=False,
                    note=(
                        "The example enables FEAT_FP8DOT2 and all of its "
                        "expressible dependencies."
                    ),
                    extra_notes=(gcc_gap_note,),
                ),
            ),
            notes=(
                gcc_gap_note,
                "Arm feature registry 109697_2025_12_en records FEAT_F8F16MM as optional from Armv9.2 with FEAT_FP8DOT2 required.",
            ),
            status=ResolutionStatus.PARTIAL,
            include_gcc_aarch64=False,
            arm_registry_page=154,
        ),
        _feature(
            key="f8f32mm",
            title="FP8-to-Float32 matrix multiply",
            macros=("__ARM_FEATURE_F8F32MM",),
            architecture_features=("FEAT_F8F32MM",),
            extension_names=("f8f32mm",),
            implies=("fp8dot4",),
            acle_lines=(2448, 2461),
            acle_anchor="multiplication-of-modal-8-bit-floating-point-matrices",
            llvm_aarch64_lines=(530, 531),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_clang_context(
                    "f8f32mm",
                    architecture_min="Armv9.2-A",
                    march="-march=armv9.2-a+faminmax+lut+fp8fma+fp8dot4+f8f32mm",
                    mcpu="-mcpu=generic+bf16+faminmax+lut+fp8fma+fp8dot4+f8f32mm",
                    base_march="armv9.2-a",
                    default_enabled=False,
                    note=(
                        "The example enables FEAT_FP8DOT4 and all of its "
                        "expressible dependencies."
                    ),
                    extra_notes=(gcc_gap_note,),
                ),
            ),
            notes=(
                gcc_gap_note,
                "Arm feature registry 109697_2025_12_en records FEAT_F8F32MM as optional from Armv9.2 with FEAT_FP8DOT4 required.",
            ),
            status=ResolutionStatus.PARTIAL,
            include_gcc_aarch64=False,
            arm_registry_page=155,
        ),
        _feature(
            key="jcvt",
            title="JavaScript floating-point conversion",
            macros=("__ARM_FEATURE_JCVT",),
            architecture_features=("FEAT_JSCVT",),
            extension_names=("jscvt",),
            implies=("fp",),
            acle_lines=(2387, 2392),
            acle_anchor="javascript-floating-point-conversion",
            llvm_aarch64_lines=(183, 186),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "jcvt",
                    architecture_min="Armv8.3-A",
                    march="-march=armv8.3-a+jscvt",
                    mcpu="-mcpu=generic+jscvt",
                    base_march="armv8.3-a",
                    default_enabled=True,
                    note=(
                        "GCC and the compiler-facing LLVM spelling use +jscvt; "
                        "LLVM's internal feature token is +jsconv."
                    ),
                ),
            ),
            notes=(
                "ACLE permits an AArch32 VJCVT form, but this pinned mapping is AArch64-only because no exact AArch32 compiler modifier is claimed.",
            ),
            status=ResolutionStatus.PARTIAL,
        ),
        _feature(
            key="rng",
            title="Random number generation",
            macros=("__ARM_FEATURE_RNG",),
            architecture_features=("FEAT_RNG",),
            extension_names=("rng",),
            implies=(),
            acle_lines=(1736, 1741),
            acle_anchor="random-number-generation-extension",
            llvm_aarch64_lines=(268, 270),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "rng",
                    architecture_min="Armv8.5-A",
                    march="-march=armv8.5-a+rng",
                    mcpu="-mcpu=generic+rng",
                    base_march="armv8.5-a",
                    default_enabled=False,
                    note=(
                        "GCC and LLVM expose +rng to users; LLVM's internal "
                        "feature token is +rand."
                    ),
                ),
            ),
            notes=(
                "The associated ACLE intrinsics are restricted to AArch64 execution state.",
            ),
        ),
        _feature(
            key="memory_tagging",
            title="Memory Tagging Extension",
            macros=("__ARM_FEATURE_MEMORY_TAGGING",),
            architecture_features=("FEAT_MTE", "FEAT_MTE2"),
            extension_names=("memtag",),
            implies=(),
            acle_lines=(5254, 5299),
            acle_anchor="mte-intrinsics",
            llvm_aarch64_lines=(272, 276),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "memory_tagging",
                    architecture_min="Armv8.5-A",
                    march="-march=armv8.5-a+memtag",
                    mcpu="-mcpu=generic+memtag",
                    base_march="armv8.5-a",
                    default_enabled=False,
                    note=(
                        "For -march and target attributes, +memtag enables "
                        "both FEAT_MTE and FEAT_MTE2 in the pinned compiler models."
                    ),
                ),
            ),
        ),
        _feature(
            key="ls64",
            title="Load/store 64-byte extension",
            macros=("__ARM_FEATURE_LS64",),
            architecture_features=("FEAT_LS64", "FEAT_LS64_V", "FEAT_LS64_ACCDATA"),
            extension_names=("ls64",),
            implies=(),
            acle_lines=(1798, 1805),
            acle_anchor="armv87-a-loadstore-64-byte-extension",
            llvm_aarch64_lines=(309, 311),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "ls64",
                    architecture_min="Armv8.7-A",
                    march="-march=armv8.7-a+ls64",
                    mcpu="-mcpu=generic+ls64",
                    base_march="armv8.7-a",
                    default_enabled=True,
                    note=(
                        "+ls64 controls the base, volatile-store, and "
                        "acceleration-data variants as one compiler extension."
                    ),
                ),
            ),
            notes=(
                "ACLE restricts this feature macro to AArch64 execution state.",
            ),
        ),
        _feature(
            key="sysreg128",
            title="128-bit system registers",
            macros=("__ARM_FEATURE_SYSREG128",),
            architecture_features=("FEAT_SYSREG128", "FEAT_SYSINSTR128"),
            extension_names=("d128",),
            implies=("lse128",),
            acle_lines=(1841, 1847),
            acle_anchor="128-bit-system-registers",
            llvm_aarch64_lines=(466, 473),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "sysreg128",
                    architecture_min="Armv9.4-A",
                    march="-march=armv9.4-a+d128",
                    mcpu="-mcpu=generic+d128",
                    base_march="armv9.4-a",
                    default_enabled=True,
                    note=(
                        "+d128 is the compiler umbrella for FEAT_D128, "
                        "FEAT_LVA3, FEAT_SYSREG128, and FEAT_SYSINSTR128."
                    ),
                ),
            ),
            notes=(
                "ACLE restricts this feature macro to AArch64 execution state.",
            ),
        ),
        _feature(
            key="sve_b16mm",
            title="SVE non-widening BFloat16 matrix multiply",
            macros=("__ARM_FEATURE_SVE_B16MM",),
            architecture_features=("FEAT_SVE_B16MM",),
            extension_names=("sve-b16mm",),
            implies=("sve",),
            acle_lines=(2178, 2190),
            acle_anchor="brain-16-bit-floating-point-matrix-multiplication-support",
            llvm_aarch64_lines=(613, 614),
            llvm_aarch32_lines=None,
            contexts=(
                _aarch64_context(
                    "sve_b16mm",
                    architecture_min="Armv9.7-A",
                    march="-march=armv9.7-a+sve-b16mm",
                    mcpu="-mcpu=generic+sve-b16mm",
                    base_march="armv9.7-a",
                    default_enabled=True,
                    note="+sve-b16mm implies SVE in the pinned compiler models.",
                ),
            ),
            notes=("ACLE marks SVE B16MM as Alpha.",),
        ),
        _feature(
            key="simd32",
            title="AArch32 32-bit SIMD instructions",
            macros=("__ARM_FEATURE_SIMD32",),
            architecture_features=("Armv6 32-bit SIMD",),
            extension_names=(),
            implies=(),
            acle_lines=(1699, 1712),
            acle_anchor="32-bit-simd-instructions",
            llvm_aarch64_lines=None,
            llvm_aarch32_lines=(85, 105),
            contexts=(
                _context(
                    target="aarch32",
                    architecture_min="Armv6",
                    profiles=("A", "R"),
                    execution_states=("AArch32", "T32"),
                    march="-march=armv6",
                    mcpu="-mcpu=arm1136jf-s",
                    base_march="armv6",
                    default_enabled=True,
                    llvm_source_id="simd32:llvm-aarch32",
                    gcc_source_id="simd32:gcc-aarch32",
                    note=(
                        "ACLE defines these instructions from Armv6 for A and "
                        "R profiles; the architecture selection itself enables "
                        "the facility."
                    ),
                ),
                _context(
                    target="aarch32",
                    architecture_min="Armv7E-M",
                    profiles=("M",),
                    execution_states=("T32",),
                    march=("-march=armv7e-m", "-mthumb"),
                    mcpu=("-mcpu=cortex-m4", "-mthumb"),
                    base_march="armv7e-m",
                    default_enabled=True,
                    llvm_source_id="simd32:llvm-aarch32",
                    gcc_source_id="simd32:gcc-aarch32",
                    note=(
                        "ACLE defines the 32-bit SIMD intrinsics for M-profile "
                        "from Armv7E-M; M-profile executes in T32 state."
                    ),
                ),
            ),
            notes=(
                "ACLE marks __ARM_FEATURE_SIMD32 as AArch32-only and deprecated for A-profile while retaining full M- and R-profile support.",
                "There is no separate compiler extension modifier: the selected architecture or CPU supplies the facility.",
            ),
        ),
    )


_FEATURE_DATA: tuple[dict[str, Any], ...] = (
    *_target_guard_feature_data(),
    *_late_exact_feature_data(),
    _feature(
        key="crc32",
        title="CRC32 extension",
        macros=("__ARM_FEATURE_CRC32",),
        architecture_features=("FEAT_CRC32",),
        extension_names=("crc",),
        implies=(),
        acle_lines=(1731, 1735),
        acle_anchor="crc32-extension",
        llvm_aarch64_lines=(91, 92),
        llvm_aarch32_lines=(224, 224),
        contexts=(
            _aarch64_context(
                "crc32",
                architecture_min="Armv8-A",
                march="-march=armv8-a+crc",
                mcpu="-mcpu=generic+crc",
                base_march="armv8-a",
                default_enabled=False,
                note="CRC is optional in Armv8.0-A and enabled explicitly by +crc.",
                extra_notes=(
                    "In the pinned LLVM model, CRC is an architecture default from Armv8.1-A.",
                ),
            ),
            _aarch32_context(
                "crc32",
                architecture_min="Armv8-A or Armv8-R",
                profiles=("A", "R"),
                march="-march=armv8-a+crc",
                mcpu="-mcpu=cortex-a53+crc",
                base_march="armv8-a",
                default_enabled=None,
                note=(
                    "AArch32 architecture defaults vary with compiler target and CPU; "
                    "use +crc when the binary contract requires CRC instructions."
                ),
            ),
        ),
        notes=(
            "The macro is available only when __ARM_ARCH is at least 8.",
            "Do not infer latency or throughput from +crc; use the selected CPU's data.",
        ),
    ),
    _feature(
        key="advsimd",
        title="Advanced SIMD (Neon)",
        macros=("__ARM_NEON", "__ARM_NEON_FP"),
        architecture_features=("FEAT_AdvSIMD",),
        extension_names=("simd",),
        implies=("fp",),
        acle_lines=(1925, 1952),
        acle_anchor="advanced-simd-architecture-extension-neon",
        llvm_aarch64_lines=(70, 72),
        llvm_aarch32_lines=(237, 237),
        contexts=(
            _aarch64_context(
                "advsimd",
                architecture_min="Armv8-A",
                march="-march=armv8-a+simd",
                mcpu="-mcpu=generic+simd",
                base_march="armv8-a",
                default_enabled=True,
                note="Advanced SIMD and floating point are baseline for AArch64 Armv8-A.",
            ),
            _aarch32_context(
                "advsimd",
                architecture_min="Armv7-A",
                profiles=("A",),
                march="-march=armv8-a+simd",
                mcpu="-mcpu=cortex-a53+simd",
                base_march="armv8-a",
                default_enabled=None,
                note=(
                    "For AArch32, Neon availability depends on the architecture/CPU and "
                    "floating-point selection; +simd requests it explicitly."
                ),
            ),
        ),
        notes=(
            "__ARM_NEON is always 1 in AArch64; __ARM_NEON_FP is a capability bitmap.",
        ),
    ),
    _feature(
        key="crypto",
        title="Deprecated crypto umbrella",
        macros=("__ARM_FEATURE_CRYPTO",),
        architecture_features=("FEAT_Crypto",),
        extension_names=("crypto",),
        implies=("simd", "aes", "sha2"),
        acle_lines=(2197, 2204),
        acle_anchor="crypto-extension",
        llvm_aarch64_lines=(81, 89),
        llvm_aarch32_lines=(225, 225),
        contexts=(
            _aarch64_context(
                "crypto",
                architecture_min="Armv8-A",
                march="-march=armv8-a+crypto",
                mcpu="-mcpu=generic+crypto",
                base_march="armv8-a",
                default_enabled=False,
                note="+crypto is a compatibility umbrella for +aes+sha2+simd.",
            ),
            _aarch32_context(
                "crypto",
                architecture_min="Armv8-A",
                profiles=("A",),
                march="-march=armv8-a+crypto",
                mcpu="-mcpu=cortex-a53+crypto",
                base_march="armv8-a",
                default_enabled=None,
                note="Use the fine-grained +aes and +sha2 controls for new code.",
            ),
        ),
        notes=(
            "ACLE deprecates __ARM_FEATURE_CRYPTO in favor of fine-grained macros.",
            "The meaning of +crypto is context-sensitive for later architecture revisions.",
        ),
    ),
    _feature(
        key="aes",
        title="AES and polynomial multiply",
        macros=("__ARM_FEATURE_AES",),
        architecture_features=("FEAT_AES", "FEAT_PMULL"),
        extension_names=("aes",),
        implies=("simd",),
        acle_lines=(2207, 2216),
        acle_anchor="aes-extension",
        llvm_aarch64_lines=(77, 78),
        llvm_aarch32_lines=(227, 227),
        contexts=(
            _aarch64_context(
                "aes",
                architecture_min="Armv8-A",
                march="-march=armv8-a+aes",
                mcpu="-mcpu=generic+aes",
                base_march="armv8-a",
                default_enabled=False,
                note="+aes enables FEAT_AES and FEAT_PMULL and implies Advanced SIMD.",
            ),
            _aarch32_context(
                "aes",
                architecture_min="Armv8-A",
                profiles=("A",),
                march="-march=armv8-a+aes",
                mcpu="-mcpu=cortex-a53+aes",
                base_march="armv8-a",
                default_enabled=None,
                note="AArch32 compiler defaults are CPU-dependent; +aes is explicit.",
            ),
        ),
    ),
    _feature(
        key="sha2",
        title="SHA-1 and SHA-256",
        macros=("__ARM_FEATURE_SHA2",),
        architecture_features=("FEAT_SHA1", "FEAT_SHA256"),
        extension_names=("sha2",),
        implies=("simd",),
        acle_lines=(2232, 2238),
        acle_anchor="sha2-extension",
        llvm_aarch64_lines=(74, 75),
        llvm_aarch32_lines=(226, 226),
        contexts=(
            _aarch64_context(
                "sha2",
                architecture_min="Armv8-A",
                march="-march=armv8-a+sha2",
                mcpu="-mcpu=generic+sha2",
                base_march="armv8-a",
                default_enabled=False,
                note="+sha2 enables SHA-1 and SHA-256 and implies Advanced SIMD.",
            ),
            _aarch32_context(
                "sha2",
                architecture_min="Armv8-A",
                profiles=("A",),
                march="-march=armv8-a+sha2",
                mcpu="-mcpu=cortex-a53+sha2",
                base_march="armv8-a",
                default_enabled=None,
                note="AArch32 compiler defaults are CPU-dependent; +sha2 is explicit.",
            ),
        ),
    ),
    _feature(
        key="sha3_sha512",
        title="SHA-3 and SHA-512",
        macros=("__ARM_FEATURE_SHA3", "__ARM_FEATURE_SHA512"),
        architecture_features=("FEAT_SHA3", "FEAT_SHA512"),
        extension_names=("sha3",),
        implies=("sha2", "simd"),
        acle_lines=(2240, 2258),
        acle_anchor="sha3-extension",
        llvm_aarch64_lines=(135, 136),
        llvm_aarch32_lines=None,
        contexts=(
            _aarch64_context(
                "sha3_sha512",
                architecture_min="Armv8.2-A",
                march="-march=armv8.2-a+sha3",
                mcpu="-mcpu=generic+sha3",
                base_march="armv8.2-a",
                default_enabled=False,
                note="+sha3 enables FEAT_SHA3 and FEAT_SHA512 and implies +sha2+simd.",
            ),
        ),
        notes=("The compiler extension +sha3 controls both ACLE feature macros.",),
    ),
    _feature(
        key="sm3_sm4",
        title="SM3 and SM4",
        macros=("__ARM_FEATURE_SM3", "__ARM_FEATURE_SM4"),
        architecture_features=("FEAT_SM3", "FEAT_SM4"),
        extension_names=("sm4",),
        implies=("simd",),
        acle_lines=(2262, 2282),
        acle_anchor="sm4-extension",
        llvm_aarch64_lines=(132, 133),
        llvm_aarch32_lines=None,
        contexts=(
            _aarch64_context(
                "sm3_sm4",
                architecture_min="Armv8.2-A",
                march="-march=armv8.2-a+sm4",
                mcpu="-mcpu=generic+sm4",
                base_march="armv8.2-a",
                default_enabled=False,
                note="+sm4 enables both FEAT_SM3 and FEAT_SM4 and implies Advanced SIMD.",
            ),
        ),
    ),
    _feature(
        key="dotprod",
        title="Dot product",
        macros=("__ARM_FEATURE_DOTPROD",),
        architecture_features=("FEAT_DotProd",),
        extension_names=("dotprod",),
        implies=("simd",),
        acle_lines=(2405, 2410),
        acle_anchor="dot-product-extension",
        llvm_aarch64_lines=(212, 213),
        llvm_aarch32_lines=(228, 228),
        contexts=(
            _aarch64_context(
                "dotprod",
                architecture_min="Armv8.2-A",
                march="-march=armv8.2-a+dotprod",
                mcpu="-mcpu=generic+dotprod",
                base_march="armv8.2-a",
                default_enabled=False,
                note="+dotprod is optional in Armv8.2-A and implies Advanced SIMD.",
                extra_notes=(
                    "It is an architecture default from Armv8.4-A in the pinned LLVM model.",
                ),
            ),
            _aarch32_context(
                "dotprod",
                architecture_min="Armv8.2-A",
                profiles=("A",),
                march="-march=armv8.2-a+dotprod",
                mcpu="-mcpu=cortex-a55+dotprod",
                base_march="armv8.2-a",
                default_enabled=False,
                note="+dotprod implies Neon; Armv8.4-A includes it by architecture level.",
            ),
        ),
    ),
    _feature(
        key="fp16",
        title="Half-precision arithmetic",
        macros=(
            "__ARM_FEATURE_FP16_SCALAR_ARITHMETIC",
            "__ARM_FEATURE_FP16_VECTOR_ARITHMETIC",
        ),
        architecture_features=("FEAT_FP16",),
        extension_names=("fp16",),
        implies=("fp",),
        acle_lines=(2078, 2097),
        acle_anchor="16-bit-floating-point-data-processing-operations",
        llvm_aarch64_lines=(141, 143),
        llvm_aarch32_lines=(240, 240),
        contexts=(
            _aarch64_context(
                "fp16",
                architecture_min="Armv8.2-A",
                march="-march=armv8.2-a+fp16",
                mcpu="-mcpu=generic+fp16",
                base_march="armv8.2-a",
                default_enabled=False,
                note="The user-visible +fp16 spelling maps to LLVM's fullfp16 feature.",
                extra_notes=(
                    "Full FP16 is an architecture default in Armv9-A in the pinned LLVM model.",
                ),
            ),
            _aarch32_context(
                "fp16",
                architecture_min="Armv8.2-A",
                profiles=("A",),
                march="-march=armv8.2-a+fp16",
                mcpu="-mcpu=cortex-a55+fp16",
                base_march="armv8.2-a",
                default_enabled=False,
                note="The user-visible +fp16 spelling maps to LLVM's fullfp16 feature.",
            ),
        ),
        notes=(
            "The scalar and vector macros are separate; pages should show the exact macro they require.",
        ),
    ),
    _feature(
        key="fp16fml",
        title="FP16 FML",
        macros=("__ARM_FEATURE_FP16_FML",),
        architecture_features=("FEAT_FHM",),
        extension_names=("fp16fml",),
        implies=("fp16", "simd"),
        acle_lines=(2099, 2104),
        acle_anchor="fp16-fml-extension",
        llvm_aarch64_lines=(209, 210),
        llvm_aarch32_lines=(247, 247),
        contexts=(
            _aarch64_context(
                "fp16fml",
                architecture_min="Armv8.2-A",
                march="-march=armv8.2-a+fp16fml",
                mcpu="-mcpu=generic+fp16fml",
                base_march="armv8.2-a",
                default_enabled=False,
                note="+fp16fml implies full FP16 and Advanced SIMD.",
            ),
            _aarch32_context(
                "fp16fml",
                architecture_min="Armv8.2-A",
                profiles=("A",),
                march="-march=armv8.2-a+fp16fml",
                mcpu="-mcpu=cortex-a55+fp16fml",
                base_march="armv8.2-a",
                default_enabled=False,
                note="+fp16fml implies full FP16 and Neon.",
            ),
        ),
    ),
    _feature(
        key="bf16",
        title="BFloat16 arithmetic",
        macros=("__ARM_FEATURE_BF16", "__ARM_FEATURE_BF16_VECTOR_ARITHMETIC"),
        architecture_features=("FEAT_BF16",),
        extension_names=("bf16",),
        implies=("simd", "fp"),
        acle_lines=(2116, 2133),
        acle_anchor="brain-16-bit-floating-point-support",
        llvm_aarch64_lines=(282, 283),
        llvm_aarch32_lines=(248, 248),
        contexts=(
            _aarch64_context(
                "bf16",
                architecture_min="Armv8.2-A",
                march="-march=armv8.2-a+bf16",
                mcpu="-mcpu=generic+bf16",
                base_march="armv8.2-a",
                default_enabled=False,
                note="+bf16 implies Advanced SIMD and floating point.",
                extra_notes=(
                    "BF16 is an architecture default from Armv8.6-A in the pinned LLVM model.",
                ),
            ),
            _aarch32_context(
                "bf16",
                architecture_min="Armv8.2-A",
                profiles=("A",),
                march="-march=armv8.2-a+bf16",
                mcpu="-mcpu=cortex-a510+bf16",
                base_march="armv8.2-a",
                default_enabled=False,
                note="+bf16 implies Neon and floating point.",
            ),
        ),
    ),
    _feature(
        key="sve_bf16",
        title="SVE BFloat16",
        macros=("__ARM_FEATURE_SVE_BF16",),
        architecture_features=("FEAT_BF16", "FEAT_SVE"),
        extension_names=("sve", "bf16"),
        implies=("bf16", "sve", "simd"),
        acle_lines=(2130, 2134),
        acle_anchor="brain-16-bit-floating-point-support",
        llvm_aarch64_lines=(158, 163),
        llvm_aarch32_lines=None,
        contexts=(
            _aarch64_context(
                "sve_bf16",
                architecture_min="Armv8.2-A",
                march="-march=armv8.2-a+sve+bf16",
                mcpu="-mcpu=generic+sve+bf16",
                base_march="armv8.2-a",
                default_enabled=False,
                note="Both +sve and +bf16 are required for SVE BF16 intrinsics.",
            ),
        ),
    ),
    _unresolved_bf16_scalar_feature(),
    _feature(
        key="i8mm",
        title="8-bit integer matrix multiply",
        macros=("__ARM_FEATURE_MATMUL_INT8",),
        architecture_features=("FEAT_I8MM",),
        extension_names=("i8mm",),
        implies=("simd",),
        acle_lines=(2436, 2446),
        acle_anchor="multiplication-of-8-bit-integer-matrices",
        llvm_aarch64_lines=(162, 163),
        llvm_aarch32_lines=(250, 250),
        contexts=(
            _aarch64_context(
                "i8mm",
                architecture_min="Armv8.2-A",
                march="-march=armv8.2-a+i8mm",
                mcpu="-mcpu=generic+i8mm",
                base_march="armv8.2-a",
                default_enabled=False,
                note="+i8mm implies Advanced SIMD and floating point.",
                extra_notes=(
                    "I8MM is an architecture default from Armv8.6-A in the pinned LLVM model.",
                ),
            ),
            _aarch32_context(
                "i8mm",
                architecture_min="Armv8.2-A",
                profiles=("A",),
                march="-march=armv8.2-a+i8mm",
                mcpu="-mcpu=cortex-a510+i8mm",
                base_march="armv8.2-a",
                default_enabled=False,
                note="+i8mm implies Neon.",
            ),
        ),
    ),
    _feature(
        key="sve_i8mm",
        title="SVE 8-bit integer matrix multiply",
        macros=("__ARM_FEATURE_SVE_MATMUL_INT8",),
        architecture_features=("FEAT_I8MM", "FEAT_SVE"),
        extension_names=("sve", "i8mm"),
        implies=("i8mm", "sve", "simd"),
        acle_lines=(2443, 2451),
        acle_anchor="multiplication-of-8-bit-integer-matrices",
        llvm_aarch64_lines=(158, 163),
        llvm_aarch32_lines=None,
        contexts=(
            _aarch64_context(
                "sve_i8mm",
                architecture_min="Armv8.2-A",
                march="-march=armv8.2-a+sve+i8mm",
                mcpu="-mcpu=generic+sve+i8mm",
                base_march="armv8.2-a",
                default_enabled=False,
                note="Both +sve and +i8mm are required for the SVE forms.",
            ),
        ),
    ),
    _feature(
        key="sve",
        title="Scalable Vector Extension",
        macros=("__ARM_FEATURE_SVE",),
        architecture_features=("FEAT_SVE",),
        extension_names=("sve",),
        implies=("fp16", "simd"),
        acle_lines=(1956, 1961),
        acle_anchor="scalable-vector-extension-sve",
        llvm_aarch64_lines=(158, 159),
        llvm_aarch32_lines=None,
        contexts=(
            _aarch64_context(
                "sve",
                architecture_min="Armv8.2-A",
                march="-march=armv8.2-a+sve",
                mcpu="-mcpu=generic+sve",
                base_march="armv8.2-a",
                default_enabled=False,
                note="+sve implies full FP16; ACLE also requires Neon and Neon FP macros.",
                extra_notes=(
                    "SVE is an architecture default in Armv9-A in the pinned LLVM model.",
                ),
            ),
        ),
        notes=(
            "Vector length is independent of -march; use -msve-vector-bits only when a fixed compile-time contract is intended.",
        ),
    ),
    _feature(
        key="sve2",
        title="Scalable Vector Extension 2",
        macros=("__ARM_FEATURE_SVE2",),
        architecture_features=("FEAT_SVE2",),
        extension_names=("sve2",),
        implies=("sve",),
        acle_lines=(2003, 2006),
        acle_anchor="sve2",
        llvm_aarch64_lines=(362, 364),
        llvm_aarch32_lines=None,
        contexts=(
            _aarch64_context(
                "sve2",
                architecture_min="Armv9-A",
                march="-march=armv9-a+sve2",
                mcpu="-mcpu=generic+sve2",
                base_march="armv9-a",
                default_enabled=True,
                note="SVE2 implies SVE and is an Armv9-A architecture default.",
            ),
        ),
    ),
    _feature(
        key="sve2p1",
        title="SVE2.1",
        macros=("__ARM_FEATURE_SVE2p1",),
        architecture_features=("FEAT_SVE2p1",),
        extension_names=("sve2p1",),
        implies=("sve2",),
        acle_lines=(2007, 2010),
        acle_anchor="sve2",
        llvm_aarch64_lines=(437, 438),
        llvm_aarch32_lines=None,
        contexts=(
            _aarch64_context(
                "sve2p1",
                architecture_min="Armv9.4-A",
                march="-march=armv9.4-a+sve2p1",
                mcpu="-mcpu=generic+sve2p1",
                base_march="armv9.4-a",
                default_enabled=True,
                note="SVE2.1 implies SVE2 and is an Armv9.4-A architecture default.",
            ),
        ),
    ),
    _feature(
        key="sve_b16b16",
        title="SVE non-widening BFloat16",
        macros=("__ARM_FEATURE_SVE_B16B16",),
        architecture_features=("FEAT_SVE_B16B16",),
        extension_names=("sve-b16b16",),
        implies=(),
        acle_lines=(2141, 2160),
        acle_anchor="non-widening-brain-16-bit-floating-point-support",
        llvm_aarch64_lines=(440, 441),
        llvm_aarch32_lines=None,
        contexts=(
            _aarch64_context(
                "sve_b16b16",
                architecture_min="Armv9.2-A",
                march="-march=armv9.2-a+sve2+sve-b16b16",
                mcpu="-mcpu=generic+sve2+sve-b16b16",
                base_march="armv9.2-a",
                default_enabled=False,
                note=(
                    "The Arm ISA requires either FEAT_SVE2 or FEAT_SME2. This "
                    "non-streaming example selects FEAT_SVE2 explicitly; "
                    "+sve-b16b16 alone is ineffective."
                ),
                extra_notes=(
                    "ACLE requires SVE for the non-streaming SVE intrinsic subset.",
                ),
            ),
            _aarch64_context(
                "sve_b16b16",
                architecture_min="Armv9.2-A",
                march="-march=armv9.2-a+sme2+sve-b16b16",
                mcpu="-mcpu=generic+sme2+sve-b16b16",
                base_march="armv9.2-a",
                default_enabled=False,
                note=(
                    "The Arm ISA requires either FEAT_SVE2 or FEAT_SME2. This "
                    "streaming-compatible example selects FEAT_SME2 explicitly; "
                    "+sve-b16b16 alone is ineffective."
                ),
                extra_notes=(
                    "ACLE requires SME for the streaming-compatible and streaming forms.",
                ),
            ),
        ),
        notes=(
            "ACLE marks B16B16 as Alpha.",
            "Arm feature registry 109697_2025_12_en records FEAT_SVE_B16B16 as optional from Armv9.2 and requires either FEAT_SVE2 or FEAT_SME2.",
        ),
        arm_registry_page=137,
    ),
    _feature(
        key="sve2p2",
        title="SVE2.2",
        macros=("__ARM_FEATURE_SVE2p2",),
        architecture_features=("FEAT_SVE2p2",),
        extension_names=("sve2p2",),
        implies=("sve2p1", "sve2"),
        acle_lines=(2011, 2014),
        acle_anchor="sve2",
        llvm_aarch64_lines=(549, 550),
        llvm_aarch32_lines=None,
        contexts=(
            _aarch64_context(
                "sve2p2",
                architecture_min="Armv9.6-A",
                march="-march=armv9.6-a+sve2p2",
                mcpu="-mcpu=generic+sve2p2",
                base_march="armv9.6-a",
                default_enabled=False,
                note="SVE2.2 implies SVE2.1; the pinned LLVM model does not make it a v9.6-A default.",
            ),
        ),
    ),
    _feature(
        key="sve2p3",
        title="SVE2.3",
        macros=("__ARM_FEATURE_SVE2p3",),
        architecture_features=("FEAT_SVE2p3",),
        extension_names=("sve2p3",),
        implies=("sve2p2", "sve2p1", "sve2"),
        acle_lines=(2015, 2018),
        acle_anchor="sve2",
        llvm_aarch64_lines=(607, 608),
        llvm_aarch32_lines=None,
        contexts=(
            _aarch64_context(
                "sve2p3",
                architecture_min="Armv9.7-A",
                march="-march=armv9.7-a+sve2p3",
                mcpu="-mcpu=generic+sve2p3",
                base_march="armv9.7-a",
                default_enabled=True,
                note="SVE2.3 implies SVE2.2 and is an Armv9.7-A architecture default.",
            ),
        ),
    ),
    _feature(
        key="sve2_aes",
        title="SVE2 AES",
        macros=("__ARM_FEATURE_SVE2_AES",),
        architecture_features=("FEAT_SVE_AES", "FEAT_SVE_PMULL128"),
        extension_names=("sve2-aes",),
        implies=("sve2", "aes"),
        acle_lines=(2213, 2216),
        acle_anchor="aes-extension",
        llvm_aarch64_lines=(366, 371),
        llvm_aarch32_lines=None,
        contexts=(
            _aarch64_context(
                "sve2_aes",
                architecture_min="Armv9-A",
                march="-march=armv9-a+sve2-aes",
                mcpu="-mcpu=generic+sve2-aes",
                base_march="armv9-a",
                default_enabled=False,
                note="+sve2-aes is shorthand for +sve2+sve-aes.",
            ),
        ),
    ),
    _feature(
        key="sve2_sha3",
        title="SVE2 SHA-3",
        macros=("__ARM_FEATURE_SVE2_SHA3",),
        architecture_features=("FEAT_SVE_SHA3",),
        extension_names=("sve2-sha3",),
        implies=("sve2", "sha3"),
        acle_lines=(2255, 2258),
        acle_anchor="sha3-extension",
        llvm_aarch64_lines=(379, 383),
        llvm_aarch32_lines=None,
        contexts=(
            _aarch64_context(
                "sve2_sha3",
                architecture_min="Armv9-A",
                march="-march=armv9-a+sve2-sha3",
                mcpu="-mcpu=generic+sve2-sha3",
                base_march="armv9-a",
                default_enabled=False,
                note="+sve2-sha3 is shorthand for +sve2+sve-sha3.",
            ),
        ),
    ),
    _feature(
        key="sve2_sm4",
        title="SVE2 SM3 and SM4",
        macros=("__ARM_FEATURE_SVE2_SM3", "__ARM_FEATURE_SVE2_SM4"),
        architecture_features=("FEAT_SVE_SM4",),
        extension_names=("sve2-sm4",),
        implies=("sve2", "sm4"),
        acle_lines=(2267, 2282),
        acle_anchor="sm4-extension",
        llvm_aarch64_lines=(373, 377),
        llvm_aarch32_lines=None,
        contexts=(
            _aarch64_context(
                "sve2_sm4",
                architecture_min="Armv9-A",
                march="-march=armv9-a+sve2-sm4",
                mcpu="-mcpu=generic+sve2-sm4",
                base_march="armv9-a",
                default_enabled=False,
                note="+sve2-sm4 is shorthand for +sve2+sve-sm4.",
            ),
        ),
    ),
    _feature(
        key="sme",
        title="Scalable Matrix Extension",
        macros=("__ARM_FEATURE_SME",),
        architecture_features=("FEAT_SME",),
        extension_names=("sme",),
        implies=("bf16", "fp16"),
        acle_lines=(2027, 2049),
        acle_anchor="scalable-matrix-extension-sme",
        llvm_aarch64_lines=(411, 412),
        llvm_aarch32_lines=None,
        contexts=(
            _aarch64_context(
                "sme",
                architecture_min="Armv9.2-A",
                march="-march=armv9.2-a+sme",
                mcpu="-mcpu=generic+sme",
                base_march="armv9.2-a",
                default_enabled=False,
                note="SME is optional and implies BF16 and full FP16 in the pinned LLVM model.",
            ),
        ),
        notes=(
            "SME callable availability can additionally depend on streaming mode and ZA/ZT0 state.",
        ),
    ),
    _feature(
        key="sme2",
        title="Scalable Matrix Extension 2",
        macros=("__ARM_FEATURE_SME2",),
        architecture_features=("FEAT_SME2",),
        extension_names=("sme2",),
        implies=("sme",),
        acle_lines=(2037, 2049),
        acle_anchor="scalable-matrix-extension-sme",
        llvm_aarch64_lines=(427, 428),
        llvm_aarch32_lines=None,
        contexts=(
            _aarch64_context(
                "sme2",
                architecture_min="Armv9.3-A",
                march="-march=armv9.3-a+sme2",
                mcpu="-mcpu=generic+sme2",
                base_march="armv9.3-a",
                default_enabled=False,
                note="SME2 is optional and implies SME.",
            ),
        ),
    ),
    _feature(
        key="sme2p1",
        title="SME2.1",
        macros=("__ARM_FEATURE_SME2p1",),
        architecture_features=("FEAT_SME2p1",),
        extension_names=("sme2p1",),
        implies=("sme2", "sme"),
        acle_lines=(2037, 2049),
        acle_anchor="scalable-matrix-extension-sme",
        llvm_aarch64_lines=(450, 451),
        llvm_aarch32_lines=None,
        contexts=(
            _aarch64_context(
                "sme2p1",
                architecture_min="Armv9.4-A",
                march="-march=armv9.4-a+sme2p1",
                mcpu="-mcpu=generic+sme2p1",
                base_march="armv9.4-a",
                default_enabled=False,
                note="SME2.1 is optional and implies SME2.",
            ),
        ),
    ),
    _feature(
        key="sme_b16b16",
        title="SME non-widening BFloat16",
        macros=("__ARM_FEATURE_SME_B16B16",),
        architecture_features=("FEAT_SME_B16B16",),
        extension_names=("sme-b16b16",),
        implies=("sme2", "sve_b16b16"),
        acle_lines=(2161, 2163),
        acle_anchor="non-widening-brain-16-bit-floating-point-support",
        llvm_aarch64_lines=(443, 445),
        llvm_aarch32_lines=None,
        contexts=(
            _aarch64_context(
                "sme_b16b16",
                architecture_min="Armv9.2-A",
                march=("-march=armv9.2-a+sme2+sve-b16b16+sme-b16b16"),
                mcpu="-mcpu=generic+sme2+sve-b16b16+sme-b16b16",
                base_march="armv9.2-a",
                default_enabled=False,
                note=(
                    "The Arm ISA requires FEAT_SME2 and FEAT_SVE_B16B16. The "
                    "example names both explicitly; +sme-b16b16 also implies "
                    "them in the pinned Clang and GCC feature models."
                ),
            ),
        ),
        notes=(
            "ACLE marks B16B16 as Alpha.",
            "Arm feature registry 109697_2025_12_en records FEAT_SME_B16B16 as optional from Armv9.2 and requires FEAT_SME2 plus FEAT_SVE_B16B16.",
        ),
        arm_registry_page=135,
    ),
    _feature(
        key="sme2p2",
        title="SME2.2",
        macros=("__ARM_FEATURE_SME2p2",),
        architecture_features=("FEAT_SME2p2",),
        extension_names=("sme2p2",),
        implies=("sme2p1", "sme2", "sme"),
        acle_lines=(2037, 2049),
        acle_anchor="scalable-matrix-extension-sme",
        llvm_aarch64_lines=(543, 544),
        llvm_aarch32_lines=None,
        contexts=(
            _aarch64_context(
                "sme2p2",
                architecture_min="Armv9.6-A",
                march="-march=armv9.6-a+sme2p2",
                mcpu="-mcpu=generic+sme2p2",
                base_march="armv9.6-a",
                default_enabled=False,
                note="SME2.2 is optional and implies SME2.1.",
            ),
        ),
    ),
    _feature(
        key="sme2p3",
        title="SME2.3",
        macros=("__ARM_FEATURE_SME2p3",),
        architecture_features=("FEAT_SME2p3",),
        extension_names=("sme2p3",),
        implies=("sme2p2", "sme2p1", "sme2", "sme"),
        acle_lines=(2037, 2049),
        acle_anchor="scalable-matrix-extension-sme",
        llvm_aarch64_lines=(610, 611),
        llvm_aarch32_lines=None,
        contexts=(
            _aarch64_context(
                "sme2p3",
                architecture_min="Armv9.7-A",
                march="-march=armv9.7-a+sme2p3",
                mcpu="-mcpu=generic+sme2p3",
                base_march="armv9.7-a",
                default_enabled=False,
                note="SME2.3 is optional and implies SME2.2.",
            ),
        ),
    ),
    _feature(
        key="mve",
        title="M-profile Vector Extension (integer)",
        macros=("__ARM_FEATURE_MVE",),
        architecture_features=("FEAT_MVE",),
        extension_names=("mve",),
        implies=("dsp",),
        acle_lines=(2055, 2062),
        acle_anchor="m-profile-vector-extension",
        llvm_aarch64_lines=None,
        llvm_aarch32_lines=(232, 232),
        contexts=(
            _m_profile_context(
                "mve",
                march="-march=armv8.1-m.main+mve",
                mcpu="-mcpu=cortex-m55",
                note="+mve enables integer MVE; Cortex-M55 enables MVE by default.",
                default_enabled=False,
            ),
        ),
        notes=("Test bit 0 of __ARM_FEATURE_MVE for integer MVE availability.",),
        macro_gates=(
            {
                "macro": "__ARM_FEATURE_MVE",
                "kind": "raw",
                "display": "(__ARM_FEATURE_MVE & 0x1) != 0",
                "notes": ["Bit 0 denotes integer MVE support."],
            },
        ),
    ),
    _feature(
        key="mve_fp",
        title="M-profile Vector Extension (floating point)",
        macros=("__ARM_FEATURE_MVE",),
        architecture_features=("FEAT_MVE", "MVE floating-point"),
        extension_names=("mve.fp",),
        implies=("mve", "dsp", "fp", "fp16"),
        acle_lines=(2055, 2062),
        acle_anchor="m-profile-vector-extension",
        llvm_aarch64_lines=None,
        llvm_aarch32_lines=(233, 234),
        contexts=(
            _m_profile_context(
                "mve_fp",
                march="-march=armv8.1-m.main+mve.fp",
                mcpu="-mcpu=cortex-m55",
                note=(
                    "+mve.fp enables integer and floating-point MVE; the ABI may also "
                    "need an explicit -mfloat-abi choice for the surrounding program."
                ),
                default_enabled=False,
            ),
        ),
        notes=(
            "Test (__ARM_FEATURE_MVE & 3) == 3 for integer plus floating-point MVE.",
        ),
        macro_gates=(
            {
                "macro": "__ARM_FEATURE_MVE",
                "kind": "raw",
                "display": "(__ARM_FEATURE_MVE & 0x3) == 0x3",
                "notes": [
                    "The floating-point form requires both the integer and FP bits."
                ],
            },
        ),
    ),
    _feature(
        key="cde",
        title="Custom Datapath Extension",
        macros=("__ARM_FEATURE_CDE", "__ARM_FEATURE_CDE_COPROC"),
        architecture_features=("FEAT_CDE",),
        extension_names=("cdecp<N>",),
        implies=(),
        acle_lines=(2648, 2664),
        acle_anchor="custom-datapath-extension",
        llvm_aarch64_lines=None,
        llvm_aarch32_lines=(252, 259),
        contexts=(
            _m_profile_context(
                "cde",
                march="-march=armv8-m.main+cdecp0",
                mcpu="-mcpu=cortex-m55+cdecp0",
                note=(
                    "There is no standalone user-facing +cde modifier. Enable one or "
                    "more coprocessors with +cdecp0 through +cdecp7."
                ),
                default_enabled=False,
                architecture_min="Armv8-M Mainline",
                base_march="armv8-m.main",
            ),
        ),
        notes=(
            "Each +cdecpN modifier sets bit N in __ARM_FEATURE_CDE_COPROC and implies CDE.",
            "The selected coprocessor numbers are part of the source/binary contract and must not be guessed.",
        ),
        macro_gates=(
            {
                "macro": "__ARM_FEATURE_CDE",
                "kind": "defined",
                "display": "defined(__ARM_FEATURE_CDE)",
                "notes": [],
            },
            {
                "macro": "__ARM_FEATURE_CDE_COPROC",
                "kind": "raw",
                "display": "(__ARM_FEATURE_CDE_COPROC & (1u << N)) != 0",
                "notes": [
                    "Substitute the intrinsic's constant coprocessor number N (0-7)."
                ],
            },
        ),
    ),
)


_DEFAULT_MANIFEST_DATA: Mapping[str, Any] = {
    "schema_version": SCHEMA_VERSION,
    "features": _FEATURE_DATA,
}

DEFAULT_FEATURE_FLAG_MANIFEST = parse_feature_flag_manifest(_DEFAULT_MANIFEST_DATA)


__all__ = [
    "ACLE_REVISION",
    "ARM_FEATURE_REGISTRY_DOCUMENT_ID",
    "ARM_FEATURE_REGISTRY_LICENSE",
    "ARM_FEATURE_REGISTRY_TITLE",
    "ARM_FEATURE_REGISTRY_URL",
    "ARM_FEATURE_REGISTRY_VERSION",
    "DEFAULT_FEATURE_FLAG_MANIFEST",
    "FeatureFlagManifestError",
    "FeatureFlagMapping",
    "GCC_MANUAL_VERSION",
    "LLVM_REVISION",
    "LLVM_TAG",
    "ResolutionStatus",
    "SCHEMA_VERSION",
    "TargetContext",
    "compilation_requirements_for",
    "index_feature_flags_by_macro",
    "load_feature_flag_manifest",
    "mappings_for_macro",
    "parse_feature_flag_manifest",
    "unresolved_compilation_requirements",
]
