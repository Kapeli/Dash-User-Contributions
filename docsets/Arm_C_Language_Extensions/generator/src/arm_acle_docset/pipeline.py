"""Build one source-aware ACLE catalog from the pinned heterogeneous inputs."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
from itertools import product
import re
from pathlib import Path
from typing import Iterable, Mapping, Sequence, cast

from .model import (
    AvailabilityExpr,
    AvailabilityOp,
    Catalog,
    CompilationRequirements,
    CompilerFlagExample,
    ConcreteCallable,
    Diagnostic,
    DiagnosticSeverity,
    Family,
    FieldProvenance,
    InstructionMapping,
    InstructionRelationKind,
    Maturity,
    ModeAvailability,
    Parameter,
    PerformanceRecord,
    Provenance,
    ProvenanceKind,
    Semantics,
    Signature,
    SourceRef,
    StateAccess,
    StateAccessMode,
)
from .normalize import (
    canonical_json,
    normalize_availability,
    normalize_c_type,
    normalize_callable,
    normalize_families,
    normalize_mode_availability,
    normalize_whitespace,
    signature_identity,
)
from .provenance import collect_callable_sources
from .sources.acle_markdown import (
    _availability_to_model,
    parse_acle_markdown_file,
    to_enrichment_records,
    to_ir_records,
)
from .sources.feature_flags import (
    DEFAULT_FEATURE_FLAG_MANIFEST,
    FeatureFlagMapping,
    index_feature_flags_by_macro,
)
from .sources.llvm import (
    LLVMCallable,
    LLVMSourceRef,
    LLVMTargetGuard,
    PINNED_HEADER_SHA256,
    load_llvm_include_dir,
    load_sve_target_guards,
    to_model_callables,
)
from .sources.manifest import ACLE_REVISION
from .sources.performance import (
    PerformanceDataset,
    match_performance_records,
    match_representative_performance_records,
    performance_unavailable_record,
)
from .sources.tabular import load_tabular_sources, to_concrete_callables


CATALOG_VERSION = f"{ACLE_REVISION[:12]}/{ACLE_REVISION}"
ACLE_REPOSITORY = "ARM-software/acle"
ACLE_SOURCE_URL = f"https://github.com/ARM-software/acle/blob/{ACLE_REVISION}"
ACLE_CONTENT_LICENSE = "CC-BY-SA-4.0 AND Apache-Patent-License"
ACLE_DATA_LICENSE = "Apache-2.0"

_MARKDOWN_FAMILIES = (
    "general",
    "sve",
    "sve2",
    "sve2.1",
    "sve2.2",
    "sve2.3",
    "sme",
    "sme2",
    "sme2.1",
    "sme2.2",
    "sme2.3",
)
_FAMILY_TITLES = {
    "general": "General ACLE",
    "neon": "Advanced SIMD (Neon)",
    "mve": "M-profile Vector Extension (Helium)",
    "sve": "Scalable Vector Extension",
    "sve2": "Scalable Vector Extension 2",
    "sve2.1": "Scalable Vector Extension 2.1",
    "sve2.2": "Scalable Vector Extension 2.2",
    "sve2.3": "Scalable Vector Extension 2.3",
    "sme": "Scalable Matrix Extension",
    "sme2": "Scalable Matrix Extension 2",
    "sme2.1": "Scalable Matrix Extension 2.1",
    "sme2.2": "Scalable Matrix Extension 2.2",
    "sme2.3": "Scalable Matrix Extension 2.3",
}
_FEATURE_MACRO_RE = re.compile(r"\b__ARM(?:_FEATURE)?_[A-Za-z0-9_]+\b|\b__ARM_NEON\b")


@dataclass(frozen=True, slots=True)
class CompletenessReport:
    """Reviewable coverage counters for a generated catalog."""

    callables: int
    families: Mapping[str, int]
    maturity: Mapping[str, int]
    missing_semantics: int
    missing_instruction_mapping: int
    missing_compiler_flags: int
    with_performance_data: int
    without_performance_data: int
    diagnostics: Mapping[str, int]
    release_blockers: int

    def canonical_data(self) -> dict[str, object]:
        return {
            "callables": self.callables,
            "families": dict(sorted(self.families.items())),
            "maturity": dict(sorted(self.maturity.items())),
            "missing_semantics": self.missing_semantics,
            "missing_instruction_mapping": self.missing_instruction_mapping,
            "missing_compiler_flags": self.missing_compiler_flags,
            "with_performance_data": self.with_performance_data,
            "without_performance_data": self.without_performance_data,
            "diagnostics": dict(sorted(self.diagnostics.items())),
            "release_blockers": self.release_blockers,
        }


def build_catalog(
    source_paths: Mapping[str, Path],
    llvm_include_dir: Path,
    *,
    llvm_expected_hashes: Mapping[str, str] | None = PINNED_HEADER_SHA256,
    feature_db: Sequence[FeatureFlagMapping] | None = None,
    performance_db: Sequence[PerformanceDataset | PerformanceRecord] | None = None,
) -> Catalog:
    """Fetch-independent conversion entry point used by the CLI and tests."""

    required = {
        "acle/main/acle.md",
        "acle/tools/intrinsic_db/advsimd.csv",
        "acle/tools/intrinsic_db/advsimd_classification.csv",
        "acle/tools/intrinsic_db/mve.csv",
        "acle/tools/intrinsic_db/mve_classification.csv",
    }
    missing = sorted(required - set(source_paths))
    if missing:
        raise ValueError(
            f"canonical pipeline is missing source path(s): {', '.join(missing)}"
        )

    tabular_results = (
        load_tabular_sources(
            source_paths["acle/tools/intrinsic_db/advsimd.csv"],
            source_paths["acle/tools/intrinsic_db/advsimd_classification.csv"],
            family="neon",
            definitions_source="tools/intrinsic_db/advsimd.csv",
            classifications_source="tools/intrinsic_db/advsimd_classification.csv",
        ),
        load_tabular_sources(
            source_paths["acle/tools/intrinsic_db/mve.csv"],
            source_paths["acle/tools/intrinsic_db/mve_classification.csv"],
            family="mve",
            definitions_source="tools/intrinsic_db/mve.csv",
            classifications_source="tools/intrinsic_db/mve_classification.csv",
        ),
    )
    callables: list[ConcreteCallable] = []
    for result in tabular_results:
        callables.extend(
            to_concrete_callables(
                result.intrinsics,
                repository=ACLE_REPOSITORY,
                commit=ACLE_REVISION,
                source_url_base=ACLE_SOURCE_URL,
            )
        )

    llvm_inventory = load_llvm_include_dir(
        Path(llvm_include_dir),
        expected_hashes=llvm_expected_hashes,
    )
    callables = _apply_llvm_neon_target_features(
        callables,
        llvm_inventory.callables,
        require_complete=llvm_expected_hashes is not None,
    )
    callables.extend(to_model_callables(llvm_inventory, families=("sve", "sme")))

    selected_features = (
        DEFAULT_FEATURE_FLAG_MANIFEST if feature_db is None else tuple(feature_db)
    )
    sve_tablegen = source_paths.get("llvm/td/arm_sve.td")
    target_guards = (
        load_sve_target_guards(sve_tablegen) if sve_tablegen is not None else ()
    )
    if target_guards:
        # Reclassify LLVM declarations before the exact Markdown join. In
        # particular, InvalidMode + SMETargetGuard records originate in
        # arm_sve.h but describe streaming-only SME callables.
        callables = _apply_llvm_target_guards(
            callables,
            target_guards,
            selected_features,
        )

    parsed_markdown = parse_acle_markdown_file(
        source_paths["acle/main/acle.md"],
        source_commit=ACLE_REVISION,
    )
    markdown_callables = to_ir_records(
        parsed_markdown,
        families=_MARKDOWN_FAMILIES,
    )
    callables, version_diagnostics = _merge_markdown_declarations(
        callables,
        markdown_callables,
    )
    callables = _apply_markdown_enrichments(
        callables,
        to_enrichment_records(parsed_markdown),
    )

    feature_index = index_feature_flags_by_macro(selected_features)
    if target_guards:
        # Preserve the previous enrichment behavior for unmatched Markdown
        # declarations and make the pre-merge classification pass explicit.
        callables = _apply_llvm_target_guards(
            callables,
            target_guards,
            selected_features,
        )
    performance_records = _flatten_performance(performance_db or ())
    callables = [
        _attach_performance(
            _attach_feature_flags(callable_, feature_index),
            performance_records,
        )
        for callable_ in callables
    ]
    callables = _deduplicate_callables(callables)

    diagnostics = [*version_diagnostics]
    diagnostics.extend(_markdown_document_diagnostics(parsed_markdown))
    diagnostics.extend(
        Diagnostic(
            code=item.code,
            message=item.message,
            severity=DiagnosticSeverity.WARNING,
        )
        for item in llvm_inventory.diagnostics
    )
    families = _families_from_callables(callables)
    sources = _unique_sources(
        source for callable_ in callables for source in callable_.sources
    )
    return Catalog(
        version=CATALOG_VERSION,
        source_commit=ACLE_REVISION,
        families=families,
        callables=tuple(
            sorted(callables, key=lambda item: (item.family, item.name, item.id))
        ),
        provenance=Provenance(
            kind=ProvenanceKind.DERIVED,
            sources=sources,
            rule="arm-acle-canonical-pipeline-v1",
            note=(
                "ACLE supplies semantics and tabular Neon/MVE facts; pinned LLVM "
                "generated headers complete SVE/SME declarations."
            ),
        ),
        diagnostics=tuple(_unique_diagnostics(diagnostics)),
    )


def completeness_report(catalog: Catalog) -> CompletenessReport:
    family_counts = Counter(
        family for item in catalog.callables for family in item.families
    )
    maturity_counts = Counter(item.maturity.value for item in catalog.callables)
    diagnostics = Counter(
        diagnostic.severity.value
        for callable_ in catalog.callables
        for diagnostic in callable_.diagnostics
    )
    diagnostics.update(diagnostic.severity.value for diagnostic in catalog.diagnostics)
    with_performance = sum(
        any(
            metric.is_resolved
            for record in item.performance
            for metric in (record.latency, record.reciprocal_throughput, record.uops)
        )
        for item in catalog.callables
    )
    missing_license_sources = {
        (
            source.repository,
            source.commit,
            source.path,
            source.start_line,
            source.end_line,
        )
        for item in catalog.callables
        for source in collect_callable_sources(item)
        if not source.license_id
    }
    return CompletenessReport(
        callables=len(catalog.callables),
        families=family_counts,
        maturity=maturity_counts,
        missing_semantics=sum(
            not any(
                (
                    item.semantics.summary,
                    item.semantics.description,
                    item.semantics.operation,
                )
            )
            for item in catalog.callables
        ),
        missing_instruction_mapping=sum(
            not item.instructions for item in catalog.callables
        ),
        missing_compiler_flags=sum(
            not item.compilation.compiler_flags for item in catalog.callables
        ),
        with_performance_data=with_performance,
        without_performance_data=len(catalog.callables) - with_performance,
        diagnostics=diagnostics,
        release_blockers=sum(
            diagnostic.severity is DiagnosticSeverity.ERROR
            for callable_ in catalog.callables
            for diagnostic in callable_.diagnostics
        )
        + sum(
            diagnostic.severity is DiagnosticSeverity.ERROR
            for diagnostic in catalog.diagnostics
        )
        + len(missing_license_sources),
    )


def _merge_markdown_declarations(
    existing: Sequence[ConcreteCallable],
    markdown: Sequence[ConcreteCallable],
) -> tuple[list[ConcreteCallable], list[Diagnostic]]:
    result = list(existing)
    diagnostics: list[Diagnostic] = []
    by_spelling: dict[str, list[int]] = {}
    for index, callable_ in enumerate(result):
        for spelling in _callable_spellings(callable_):
            by_spelling.setdefault(spelling, []).append(index)

    for candidate in markdown:
        match_indices = by_spelling.get(candidate.name, [])
        matches = [result[index] for index in match_indices]
        identity = signature_identity(candidate.signature)
        exact_indices = [
            index
            for index in match_indices
            if signature_identity(result[index].signature) == identity
            and _declarations_are_merge_compatible(result[index], candidate)
        ]
        attribute_enrichment_indices = [
            index
            for index in match_indices
            if not result[index].signature.attributes
            and _is_llvm_sme_header_declaration(result[index])
            and bool(candidate.signature.attributes)
            and _signature_type_identity(result[index].signature)
            == _signature_type_identity(candidate.signature)
            and _declarations_are_merge_compatible(result[index], candidate)
        ]
        merge_indices = exact_indices or attribute_enrichment_indices
        if len(merge_indices) == 1:
            exact_index = merge_indices[0]
            merged = _merge_equivalent_declarations(
                result[exact_index],
                candidate,
                prefer_specification_signature=True,
            )
            result[exact_index] = merged
            for spelling in _callable_spellings(merged):
                indices = by_spelling.setdefault(spelling, [])
                if exact_index not in indices:
                    indices.append(exact_index)
            continue
        if matches:
            ambiguity = len(merge_indices) > 1
            diagnostics.append(
                Diagnostic(
                    code=(
                        "pipeline.llvm_acle_signature_ambiguous"
                        if ambiguity
                        else "pipeline.llvm_acle_signature_drift"
                    ),
                    message=(
                        (
                            f"{candidate.name} has an ACLE declaration matching "
                            f"{len(merge_indices)} compatible LLVM declarations; "
                            "the source-backed ACLE form is retained separately."
                        )
                        if ambiguity
                        else (
                            f"{candidate.name} has an ACLE declaration not represented "
                            "by the pinned LLVM declaration set; the source-backed ACLE "
                            "form is retained as a separate callable."
                        )
                    ),
                    severity=DiagnosticSeverity.WARNING,
                    field="signature",
                    sources=candidate.sources,
                )
            )
        result.append(candidate)
        candidate_index = len(result) - 1
        for spelling in _callable_spellings(candidate):
            by_spelling.setdefault(spelling, []).append(candidate_index)
    return result, diagnostics


def _signature_type_identity(signature: Signature) -> tuple[str, tuple[str, ...]]:
    """Identify a C callable by result and parameter types, excluding attributes."""

    identity = signature_identity(signature)
    return (
        str(identity["return_type"]),
        tuple(str(parameter) for parameter in identity["parameters"]),
    )


def _is_llvm_sme_header_declaration(callable_: ConcreteCallable) -> bool:
    """Return whether a declaration is sourced from Clang's Arm SME header."""

    return any(source.path.endswith("/arm_sme.h") for source in callable_.sources)


def _merge_equivalent_declarations(
    declaration: ConcreteCallable,
    specification: ConcreteCallable,
    *,
    prefer_specification_signature: bool = False,
) -> ConcreteCallable:
    """Merge one exact ACLE declaration without discarding richer table facts."""

    family = _preferred_specification_family(declaration, specification)
    reclassified_general = (
        declaration.family == "neon"
        and family == "general"
        and specification.family == "general"
    )
    availability = (
        specification.availability
        if specification.availability != AvailabilityExpr.always()
        else declaration.availability
    )
    maturity = (
        specification.maturity
        if specification.maturity is not Maturity.UNSPECIFIED
        else declaration.maturity
    )
    headers = tuple(
        sorted(
            set(
                specification.headers
                if reclassified_general and specification.headers
                else (*declaration.headers, *specification.headers)
            )
        )
    )
    compilation = _merge_compilation(
        declaration.compilation,
        specification.compilation,
        prefer_right_mode_availability=True,
    )
    compilation = replace(
        compilation,
        headers=headers,
        availability=availability,
    )

    instructions = tuple(declaration.instructions)
    if reclassified_general:
        instructions = tuple(
            replace(mapping, instruction_set=None) for mapping in instructions
        )
    instructions = _canonical_union(instructions, specification.instructions)
    diagnostics = [*declaration.diagnostics, *specification.diagnostics]
    if maturity is not Maturity.UNSPECIFIED:
        diagnostics = [
            item for item in diagnostics if item.code != "tabular.maturity_unspecified"
        ]
    if (
        specification.compilation.feature_macros
        or specification.availability != AvailabilityExpr.always()
    ):
        diagnostics = [
            item for item in diagnostics if item.code != "tabular.features_unspecified"
        ]

    sources = _unique_sources((*declaration.sources, *specification.sources))
    families = (
        tuple(dict.fromkeys((*specification.families, family)))
        if reclassified_general
        else tuple(
            dict.fromkeys((*declaration.families, *specification.families, family))
        )
    )
    return normalize_callable(
        replace(
            declaration,
            family=family,
            families=families,
            signature=(
                specification.signature
                if prefer_specification_signature
                else declaration.signature
            ),
            aliases=_canonical_union(declaration.aliases, specification.aliases),
            availability=availability,
            maturity=maturity,
            semantics=_merge_semantics(
                declaration.semantics,
                specification.semantics,
            ),
            instructions=instructions,
            state_access=_canonical_union(
                declaration.state_access,
                specification.state_access,
            ),
            compilation=compilation,
            headers=headers,
            taxonomy=_canonical_union(
                declaration.taxonomy,
                specification.taxonomy,
            ),
            related=tuple(
                dict.fromkeys((*declaration.related, *specification.related))
            ),
            sources=sources,
            field_provenance=_canonical_union(
                declaration.field_provenance,
                specification.field_provenance,
            ),
            diagnostics=tuple(_unique_diagnostics(diagnostics)),
        )
    )


def _preferred_specification_family(
    declaration: ConcreteCallable,
    specification: ConcreteCallable,
) -> str:
    if declaration.family == specification.family:
        return declaration.family
    if (
        declaration.family == "neon"
        and specification.family == "general"
        and specification.name.startswith("__crc")
    ):
        return "general"
    if declaration.family.startswith("sve") and specification.family.startswith("sve"):
        return specification.family
    if declaration.family.startswith("sme") and specification.family.startswith("sme"):
        return specification.family
    return declaration.family


def _declarations_are_merge_compatible(
    declaration: ConcreteCallable,
    specification: ConcreteCallable,
) -> bool:
    """Reject exact-signature joins that cross incompatible ISA families."""

    declaration_roots = {_family_root(item) for item in declaration.families}
    specification_roots = {_family_root(item) for item in specification.families}
    if declaration_roots & specification_roots:
        return True
    return (
        declaration_roots == {"neon"}
        and specification_roots == {"general"}
        and specification.name.startswith("__crc")
    )


def _merge_semantics(left: Semantics, right: Semantics) -> Semantics:
    sources = _unique_sources((*left.provenance.sources, *right.provenance.sources))
    resolved = any(
        value is not None
        for value in (
            right.summary,
            right.description,
            right.operation,
            right.result,
        )
    )
    return Semantics(
        summary=right.summary or left.summary,
        description=right.description or left.description,
        operation=right.operation or left.operation,
        result=right.result or left.result,
        parameters=_canonical_union(left.parameters, right.parameters),
        constraints=_canonical_union(left.constraints, right.constraints),
        notes=tuple(dict.fromkeys((*left.notes, *right.notes))),
        provenance=(
            Provenance(
                ProvenanceKind.DERIVED,
                sources,
                rule="merge-equivalent-ACLE-declaration-semantics",
            )
            if resolved
            else left.provenance
        ),
    )


def _canonical_union(left: Sequence, right: Sequence) -> tuple:
    values = []
    seen: set[str] = set()
    for value in (*left, *right):
        key = canonical_json(value)
        if key not in seen:
            seen.add(key)
            values.append(value)
    return tuple(values)


def _source_signature_identity(value: object) -> dict[str, object]:
    """Normalize an ACLE enrichment signature for exact declaration matching."""

    if not isinstance(value, Mapping):
        raise ValueError("ACLE enrichment source_signature must be a mapping or null")
    return_type = value.get("return_type")
    parameters = value.get("parameters", ())
    attributes = value.get("attributes", ())
    if not isinstance(return_type, str):
        raise ValueError("ACLE enrichment source_signature lacks a return type")
    if not isinstance(parameters, Sequence) or isinstance(parameters, str):
        raise ValueError(
            "ACLE enrichment source_signature parameters must be a sequence"
        )
    parameter_types = []
    for parameter in parameters:
        if not isinstance(parameter, Mapping) or not isinstance(
            parameter.get("type"), str
        ):
            raise ValueError("ACLE enrichment source_signature parameter lacks a type")
        parameter_types.append(normalize_c_type(parameter["type"]))
    if not isinstance(attributes, Sequence) or isinstance(attributes, str):
        raise ValueError(
            "ACLE enrichment source_signature attributes must be a sequence"
        )
    normalized_attributes = []
    for attribute in attributes:
        if not isinstance(attribute, str):
            raise ValueError(
                "ACLE enrichment source_signature attributes must be strings"
            )
        normalized_attributes.append(normalize_whitespace(attribute))
    return {
        "return_type": normalize_c_type(return_type),
        "parameters": parameter_types,
        "attributes": sorted(set(normalized_attributes)),
    }


def _enrichment_families(
    callable_: ConcreteCallable,
    value: object,
) -> tuple[str, tuple[str, ...]]:
    patch_families = (
        tuple(item for item in value if isinstance(item, str) and item.strip())
        if isinstance(value, Sequence) and not isinstance(value, str)
        else ()
    )
    families = normalize_families(
        callable_.family,
        (*callable_.families, *patch_families),
    )
    primary = callable_.family
    broad = _family_root(primary)
    matching = [family for family in patch_families if _family_root(family) == broad]
    if matching:
        primary = max(matching, key=_family_precision)
    if primary not in families:
        primary = max(families, key=_family_precision)
    return primary, families


def _family_precision(family: str) -> tuple[int, tuple[int, ...], str]:
    match = re.fullmatch(r"(?:sve|sme)(\d+)?(?:\.(\d+))?", family)
    if match is None:
        return (0, (), family)
    values = tuple(int(value) for value in match.groups() if value is not None)
    return (1, values, family)


def _family_root(family: str) -> str:
    if family.startswith("sve"):
        return "sve"
    if family.startswith("sme"):
        return "sme"
    return family.split(".", 1)[0]


def _apply_markdown_enrichments(
    callables: Sequence[ConcreteCallable],
    patches: Sequence[Mapping[str, object]],
) -> list[ConcreteCallable]:
    # The Markdown adapter emits one declaration per applicable ACLE family.
    # A single public callable can therefore arrive as equivalent SVE and SME
    # records before its shared variant prose is reconciled.  Collapse those
    # already-equivalent declarations first so one logical exemplar and one
    # exact public spelling remain for the atomic group join.
    result = _deduplicate_callables(
        _collapse_acle_source_declaration_branches(callables)
    )
    source_callables = tuple(result)
    ordered = sorted(
        patches,
        key=lambda patch: 0 if patch.get("match", {}).get("base_names") else 1,  # type: ignore[union-attr]
    )
    name_index: dict[str, set[int]] = {}
    for index, callable_ in enumerate(result):
        for spelling in _callable_spellings(callable_):
            name_index.setdefault(spelling, set()).add(index)

    for patch in ordered:
        match = patch.get("match")
        if not isinstance(match, Mapping):
            continue
        indices: set[int] = set()
        for name in match.get("names", ()):
            if isinstance(name, str):
                indices.update(name_index.get(name, ()))
        base_names = tuple(
            item for item in match.get("base_names", ()) if isinstance(item, str)
        )
        if base_names:
            for index, callable_ in enumerate(result):
                if any(
                    spelling == base or spelling.startswith(f"{base}_")
                    for spelling in _callable_spellings(callable_)
                    for base in base_names
                ):
                    indices.add(index)
        source_signature = patch.get("source_signature")
        source_identity = (
            _source_signature_identity(source_signature)
            if source_signature is not None
            else None
        )
        for index in sorted(indices):
            if not _patch_family_matches(result[index], patch.get("family")):
                continue
            if (
                source_identity is not None
                and signature_identity(result[index].signature) != source_identity
            ):
                continue
            matched_names = {
                item for item in match.get("names", ()) if isinstance(item, str)
            }
            primary_matched = result[index].name in matched_names or any(
                result[index].name == base or result[index].name.startswith(f"{base}_")
                for base in base_names
            )
            result[index] = _apply_enrichment(
                result[index],
                patch,
                alias_only=not primary_matched,
                matched_names=matched_names,
            )
    return _reconcile_variant_groups(result, ordered, name_index, source_callables)


def _collapse_acle_source_declaration_branches(
    callables: Sequence[ConcreteCallable],
) -> list[ConcreteCallable]:
    """Merge SVE/SME family branches for one exact ACLE declaration."""

    result: list[ConcreteCallable] = []
    by_declaration: dict[str, int] = {}
    for callable_ in callables:
        acle_locations = tuple(
            sorted(
                (
                    source.repository,
                    source.commit,
                    source.path,
                    source.start_line,
                    source.end_line,
                )
                for source in callable_.sources
                if source.repository == ACLE_REPOSITORY
                and source.start_line is not None
                and source.end_line is not None
            )
        )
        if not acle_locations:
            result.append(callable_)
            continue
        key = canonical_json(
            {
                "name": callable_.name,
                "signature": signature_identity(callable_.signature),
                "acle_locations": acle_locations,
            }
        )
        index = by_declaration.get(key)
        if index is None:
            by_declaration[key] = len(result)
            result.append(callable_)
            continue
        previous = result[index]
        conflicts = _equivalent_fact_conflict_diagnostics(previous, callable_)
        merged = _merge_equivalent_declarations(previous, callable_)
        if conflicts:
            merged = normalize_callable(
                replace(
                    merged,
                    diagnostics=tuple(
                        _unique_diagnostics((*merged.diagnostics, *conflicts))
                    ),
                )
            )
        result[index] = merged
    return result


def _reconcile_variant_groups(
    callables: Sequence[ConcreteCallable],
    patches: Sequence[Mapping[str, object]],
    name_index: Mapping[str, set[int]],
    source_callables: Sequence[ConcreteCallable],
) -> list[ConcreteCallable]:
    """Apply complex ACLE variants only after an atomic inventory join.

    The Markdown adapter deliberately does not synthesize signatures for
    widening, narrowing, multi-bracket, or conditional variant lists.  This
    pass instead requires every source-declared public spelling in one group
    to identify exactly one compatible declaration from the pinned LLVM
    headers.  No partial group is applied.
    """

    result = list(callables)
    dynamic_name_index = {name: set(indices) for name, indices in name_index.items()}
    for patch in patches:
        group = patch.get("variant_group")
        if not isinstance(group, Mapping) or group.get("exhaustive") is not True:
            continue
        expected = group.get("expected_variants")
        if (
            not isinstance(expected, Sequence)
            or isinstance(expected, str)
            or not expected
        ):
            continue

        exemplar_indices = _variant_exemplar_indices(
            result,
            patch,
            dynamic_name_index,
            source_callables,
        )
        failure: str | None = None
        if len(exemplar_indices) != 1:
            failure = (
                "the exemplar does not identify exactly one declaration with "
                "the source signature"
            )

        planned: list[tuple[int, Mapping[str, object]]] = []
        derived: list[tuple[ConcreteCallable, Mapping[str, object]]] = []
        if failure is None:
            for item in expected:
                if not isinstance(item, Mapping):
                    failure = "the structured variant list contains a non-object item"
                    break
                explicit_name = item.get("explicit_name")
                if not isinstance(explicit_name, str) or not explicit_name:
                    failure = "a structured variant has no exact public spelling"
                    break
                raw_indices = dynamic_name_index.get(explicit_name, set())
                indices = _variant_inventory_indices(
                    result,
                    patch,
                    item,
                    raw_indices,
                )
                if len(indices) == 1:
                    planned.append((indices[0], item))
                    continue
                if not indices and not raw_indices:
                    source_variant = _derive_source_declared_variant(
                        result[exemplar_indices[0]],
                        patch,
                        item,
                    )
                    if source_variant is not None:
                        derived.append((source_variant, item))
                        continue
                if len(indices) != 1:
                    failure = (
                        f"{explicit_name} identifies {len(indices)} compatible "
                        "pinned-header declarations"
                    )
                    break

        if failure is None:
            by_index: dict[int, list[Mapping[str, object]]] = {}
            for index, item in planned:
                by_index.setdefault(index, []).append(item)
            for index, items in by_index.items():
                if len(items) == 1:
                    continue
                names = {str(item.get("explicit_name")) for item in items}
                availabilities = {
                    canonical_json(item.get("availability")) for item in items
                }
                if result[index].name in names or len(availabilities) != 1:
                    failure = (
                        "multiple variants collapse onto one declaration without "
                        "equivalent alias-only availability"
                    )
                    break

        if failure is not None:
            if len(exemplar_indices) == 1:
                index = exemplar_indices[0]
                result[index] = _variant_reconciliation_error(
                    result[index],
                    patch,
                    group,
                    failure,
                )
            continue

        updated = list(result)
        source_attributes = _variant_source_attributes(patch.get("source_signature"))
        for index, item in planned:
            explicit_name = str(item["explicit_name"])
            variant_patch = _variant_enrichment_patch(patch, item)
            primary_matched = updated[index].name == explicit_name
            if (
                not primary_matched
                and updated[index].signature.attributes != source_attributes
            ):
                failure = (
                    f"{explicit_name} is an alias whose source-declared signature "
                    "attributes cannot be represented on the shared declaration"
                )
                break
            if not primary_matched and not _variant_alias_availability_is_representable(
                variant_patch,
                patch,
            ):
                failure = (
                    f"{explicit_name} is an alias whose variant-specific "
                    "availability cannot be represented on shared compiler flags"
                )
                break
            if primary_matched:
                source_families = tuple(
                    family
                    for family in cast(
                        Iterable[object],
                        variant_patch.get("family", ()),
                    )
                    if isinstance(family, str) and family.strip()
                )
                if source_families:
                    source_family = max(source_families, key=_family_precision)
                    updated[index] = normalize_callable(
                        replace(
                            updated[index],
                            family=source_family,
                            families=normalize_families(
                                source_family,
                                source_families,
                            ),
                        )
                    )
                updated[index] = normalize_callable(
                    replace(
                        updated[index],
                        signature=replace(
                            updated[index].signature,
                            attributes=source_attributes,
                        ),
                    )
                )
            updated[index] = _apply_enrichment(
                updated[index],
                variant_patch,
                alias_only=not primary_matched,
                matched_names={explicit_name},
            )

        if failure is None:
            for source_variant, item in derived:
                updated.append(
                    _apply_enrichment(
                        source_variant,
                        _variant_enrichment_patch(patch, item),
                        matched_names={str(item["explicit_name"])},
                    )
                )

        if failure is not None:
            index = exemplar_indices[0]
            result[index] = _variant_reconciliation_error(
                result[index],
                patch,
                group,
                failure,
            )
            continue

        exemplar_index = exemplar_indices[0]
        updated[exemplar_index] = normalize_callable(
            replace(
                updated[exemplar_index],
                diagnostics=tuple(
                    diagnostic
                    for diagnostic in updated[exemplar_index].diagnostics
                    if diagnostic.code != "unexpanded_variant_prose"
                ),
            )
        )
        result = updated
        for index in range(len(result) - len(derived), len(result)):
            for spelling in _callable_spellings(result[index]):
                dynamic_name_index.setdefault(spelling, set()).add(index)
    return result


_VARIANT_NAME_TYPE_ATOM_RE = re.compile(r"(?:bf|mf|[suf])(?:8|16|32|64)")
_VARIANT_C_TYPE_ATOM_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?P<sv>sv)?"
    r"(?P<root>bfloat|mfloat|float|uint|int)(?P<bits>8|16|32|64)"
    r"(?P<vector>x\d+)?_t\b"
)
_VARIANT_C_ROOT_TO_ATOM = {
    "int": "s",
    "uint": "u",
    "float": "f",
    "bfloat": "bf",
    "mfloat": "mf",
}
_VARIANT_ATOM_TO_C_ROOT = {value: key for key, value in _VARIANT_C_ROOT_TO_ATOM.items()}


def _derive_source_declared_variant(
    exemplar: ConcreteCallable,
    patch: Mapping[str, object],
    variant: Mapping[str, object],
) -> ConcreteCallable | None:
    explicit_name = variant.get("explicit_name")
    if not isinstance(explicit_name, str):
        return None
    mappings = _variant_signature_mappings(exemplar.name, explicit_name)
    if mappings is None:
        return None
    atom_mapping, shape_mapping = mappings
    source_signature = _signature_from_source_payload(patch.get("source_signature"))
    if source_signature is None:
        return None
    rewritten_signature = _rewrite_variant_signature(
        source_signature,
        old_name=exemplar.name,
        new_name=explicit_name,
        atom_mapping=atom_mapping,
        shape_mapping=shape_mapping,
    )
    if rewritten_signature is None:
        return None

    source = _patch_source(patch)
    provenance = Provenance(
        ProvenanceKind.DERIVED,
        (source,),
        rule=(
            "derive-source-declared-variant-by-simultaneous-exact-C-type-and-"
            "tuple-shape-substitution"
        ),
    )
    return normalize_callable(
        replace(
            exemplar,
            name=explicit_name,
            signature=rewritten_signature,
            aliases=tuple(
                replace(alias, provenance=provenance) for alias in exemplar.aliases
            ),
            sources=(source,),
            field_provenance=tuple(
                (
                    *(
                        item
                        for item in exemplar.field_provenance
                        if item.field not in {"name", "names", "signature"}
                    ),
                    FieldProvenance("name", provenance),
                    FieldProvenance("signature", provenance),
                )
            ),
            diagnostics=tuple(
                diagnostic
                for diagnostic in exemplar.diagnostics
                if diagnostic.code != "unexpanded_variant_prose"
            ),
        )
    )


def _variant_signature_mappings(
    old_name: str,
    new_name: str,
) -> tuple[dict[str, str], dict[tuple[str, str], str]] | None:
    old_components = old_name.split("_")
    new_components = new_name.split("_")
    if len(old_components) != len(new_components):
        return None
    atom_mapping: dict[str, str] = {}
    shape_mapping: dict[tuple[str, str], str] = {}
    for index, (old, new) in enumerate(
        zip(old_components, new_components, strict=True)
    ):
        if old == new:
            continue
        if (
            _VARIANT_NAME_TYPE_ATOM_RE.fullmatch(old)
            and _VARIANT_NAME_TYPE_ATOM_RE.fullmatch(new)
        ):
            previous = atom_mapping.setdefault(old, new)
            if previous != new:
                return None
            continue
        if not (
            re.fullmatch(r"x\d+", old)
            and re.fullmatch(r"x\d+", new)
            and index > 0
            and _VARIANT_NAME_TYPE_ATOM_RE.fullmatch(old_components[index - 1])
            and _VARIANT_NAME_TYPE_ATOM_RE.fullmatch(new_components[index - 1])
        ):
            return None
        key = (old_components[index - 1], old)
        previous = shape_mapping.setdefault(key, new)
        if previous != new:
            return None
    if not atom_mapping and not shape_mapping:
        return None
    return atom_mapping, shape_mapping


def _signature_from_source_payload(value: object) -> Signature | None:
    if not isinstance(value, Mapping):
        return None
    return_type = value.get("return_type")
    parameters = value.get("parameters", ())
    attributes = value.get("attributes", ())
    raw = value.get("raw")
    if not isinstance(return_type, str):
        return None
    if not isinstance(parameters, Sequence) or isinstance(parameters, str):
        return None
    if not isinstance(attributes, Sequence) or isinstance(attributes, str):
        return None
    converted_parameters = []
    for item in parameters:
        if not isinstance(item, Mapping) or not isinstance(item.get("type"), str):
            return None
        name = item.get("name")
        converted_parameters.append(
            Parameter(
                name if isinstance(name, str) else None,
                str(item["type"]),
            )
        )
    return Signature(
        return_type,
        tuple(converted_parameters),
        tuple(item for item in attributes if isinstance(item, str)),
        raw if isinstance(raw, str) else None,
    )


def _rewrite_variant_signature(
    signature: Signature,
    *,
    old_name: str,
    new_name: str,
    atom_mapping: Mapping[str, str],
    shape_mapping: Mapping[tuple[str, str], str],
) -> Signature | None:
    seen_atoms: set[str] = set()
    seen_shapes: set[tuple[str, str]] = set()

    def rewrite(value: str) -> str:
        def replacement(match: re.Match[str]) -> str:
            atom = (
                f"{_VARIANT_C_ROOT_TO_ATOM[match.group('root')]}{match.group('bits')}"
            )
            vector = match.group("vector") or ""
            new_atom = atom_mapping.get(atom, atom)
            new_vector = shape_mapping.get((atom, vector), vector)
            if atom in atom_mapping:
                seen_atoms.add(atom)
            if (atom, vector) in shape_mapping:
                seen_shapes.add((atom, vector))
            if new_atom == atom and new_vector == vector:
                return match.group(0)
            atom_match = re.fullmatch(r"(?P<root>bf|mf|[suf])(?P<bits>\d+)", new_atom)
            assert atom_match is not None
            new_root = _VARIANT_ATOM_TO_C_ROOT[atom_match.group("root")]
            return (
                f"{match.group('sv') or ''}{new_root}{atom_match.group('bits')}"
                f"{new_vector}_t"
            )

        return _VARIANT_C_TYPE_ATOM_RE.sub(replacement, value)

    rewritten = Signature(
        rewrite(signature.return_type),
        tuple(
            replace(parameter, type_name=rewrite(parameter.type_name))
            for parameter in signature.parameters
        ),
        signature.attributes,
        (
            rewrite(signature.raw.replace(old_name, new_name, 1))
            if signature.raw
            else None
        ),
    )
    if seen_atoms != set(atom_mapping) or seen_shapes != set(shape_mapping):
        return None
    return rewritten


def _variant_exemplar_indices(
    callables: Sequence[ConcreteCallable],
    patch: Mapping[str, object],
    name_index: Mapping[str, set[int]],
    source_callables: Sequence[ConcreteCallable],
) -> list[int]:
    match = patch.get("match")
    if not isinstance(match, Mapping):
        return []
    names = tuple(item for item in match.get("names", ()) if isinstance(item, str))
    indices = {index for name in names for index in name_index.get(name, set())}
    source_signature = patch.get("source_signature")
    source_identity = (
        _source_signature_identity(source_signature)
        if source_signature is not None
        else None
    )
    matches = [
        index
        for index in sorted(indices)
        if _patch_family_matches(callables[index], patch.get("family"))
        and (
            source_identity is None
            or signature_identity(callables[index].signature) == source_identity
        )
    ]
    source = _patch_source(patch)
    local_source_matches = [
        index
        for index in matches
        if any(
            candidate.repository == source.repository
            and candidate.commit == source.commit
            and candidate.path == source.path
            and candidate.start_line is not None
            and candidate.end_line is not None
            and source.start_line is not None
            and source.end_line is not None
            and candidate.start_line <= source.end_line
            and source.start_line <= candidate.end_line
            for candidate in source_callables[index].sources
        )
    ]
    return local_source_matches or matches


def _variant_inventory_indices(
    callables: Sequence[ConcreteCallable],
    patch: Mapping[str, object],
    variant: Mapping[str, object],
    indices: Iterable[int],
) -> list[int]:
    explicit_name = variant.get("explicit_name")
    if not isinstance(explicit_name, str):
        return []
    result = []
    for index in sorted(indices):
        callable_ = callables[index]
        if explicit_name not in _callable_spellings(callable_):
            continue
        # ACLE's source section is authoritative for the public family here.
        # Both Clang's declaration header and the preliminary family inferred
        # from it can legitimately differ; the enrichment below reclassifies
        # the exact public spelling using the pinned ACLE declaration.
        llvm_sources = tuple(
            source
            for source in callable_.sources
            if source.repository == "llvm/llvm-project"
        )
        if not llvm_sources:
            continue
        result.append(index)
    return result


def _variant_source_attributes(value: object) -> tuple[str, ...]:
    if not isinstance(value, Mapping):
        return ()
    attributes = value.get("attributes", ())
    if not isinstance(attributes, Sequence) or isinstance(attributes, str):
        return ()
    return tuple(
        normalize_whitespace(attribute)
        for attribute in attributes
        if isinstance(attribute, str)
    )


def _variant_enrichment_patch(
    patch: Mapping[str, object],
    variant: Mapping[str, object],
) -> dict[str, object]:
    explicit_name = str(variant["explicit_name"])
    result = dict(patch)
    result["match"] = {"names": [explicit_name], "base_names": []}
    result.pop("source_signature", None)
    result.pop("variant_group", None)
    result["diagnostics"] = tuple(
        item
        for item in cast(Iterable[object], patch.get("diagnostics", ()))
        if not isinstance(item, Mapping)
        or item.get("code") != "unexpanded_variant_prose"
    )

    availability = patch.get("availability")
    variant_availability = variant.get("availability")
    if isinstance(availability, Mapping) and isinstance(variant_availability, Mapping):
        merged_availability = dict(availability)
        base_expression = availability.get("expression")
        if variant.get("availability_merge") == "broaden_sme":
            merged_availability["expression"] = (
                {
                    "op": "any",
                    "args": [base_expression, dict(variant_availability)],
                }
                if isinstance(base_expression, Mapping)
                else dict(variant_availability)
            )
            by_mode = availability.get("by_mode")
            if isinstance(by_mode, Mapping):
                merged_availability["by_mode"] = {
                    mode: (
                        _broaden_sme_mode_availability(value)
                        if mode in {"streaming", "streaming_compatible"}
                        and isinstance(value, Mapping)
                        else value
                    )
                    for mode, value in by_mode.items()
                }
        elif variant_availability.get("op") != "always":
            merged_availability["expression"] = (
                {"op": "all", "args": [base_expression, dict(variant_availability)]}
                if isinstance(base_expression, Mapping)
                else dict(variant_availability)
            )
        result["availability"] = merged_availability

    provenance = patch.get("provenance")
    line = variant.get("line")
    if isinstance(provenance, Mapping) and isinstance(line, int):
        merged_provenance = dict(provenance)
        source = provenance.get("source")
        if isinstance(source, Mapping):
            merged_source = dict(source)
            start = source.get("start_line")
            end = source.get("end_line")
            merged_source["start_line"] = min(
                line, start if isinstance(start, int) else line
            )
            merged_source["end_line"] = max(line, end if isinstance(end, int) else line)
            merged_provenance["source"] = merged_source
            result["provenance"] = merged_provenance
    return result


def _broaden_sme_mode_availability(value: Mapping[str, object]) -> dict[str, object]:
    result = dict(value)
    macro = result.get("macro")
    if isinstance(macro, str) and macro.startswith("__ARM_FEATURE_SME2"):
        result["op"] = "defined"
        result["macro"] = "__ARM_FEATURE_SME"
        result.pop("comparator", None)
        result.pop("value", None)
    args = result.get("args")
    if isinstance(args, Sequence) and not isinstance(args, str):
        result["args"] = [
            _broaden_sme_mode_availability(item) if isinstance(item, Mapping) else item
            for item in args
        ]
    return result


def _variant_alias_availability_is_representable(
    variant_patch: Mapping[str, object],
    exemplar_patch: Mapping[str, object],
) -> bool:
    variant_availability = variant_patch.get("availability")
    exemplar_availability = exemplar_patch.get("availability")
    return canonical_json(variant_availability) == canonical_json(exemplar_availability)


def _variant_reconciliation_error(
    callable_: ConcreteCallable,
    patch: Mapping[str, object],
    group: Mapping[str, object],
    reason: str,
) -> ConcreteCallable:
    source = _patch_source(patch)
    group_id = str(group.get("group_id") or "unknown variant group")
    diagnostic = Diagnostic(
        code="acle.variant_inventory_reconciliation_failed",
        message=f"{group_id}: {reason}.",
        severity=DiagnosticSeverity.ERROR,
        field="names",
        sources=(source,),
    )
    return normalize_callable(
        replace(
            callable_,
            diagnostics=tuple(
                _unique_diagnostics((*callable_.diagnostics, diagnostic))
            ),
        )
    )


def _apply_enrichment(
    callable_: ConcreteCallable,
    patch: Mapping[str, object],
    *,
    alias_only: bool = False,
    matched_names: set[str] | None = None,
) -> ConcreteCallable:
    source = _patch_source(patch)
    explicit = Provenance(ProvenanceKind.EXPLICIT, (source,))
    family, families = (
        (callable_.family, callable_.families)
        if alias_only
        else _enrichment_families(callable_, patch.get("family"))
    )
    availability_payload = patch.get("availability")
    availability = callable_.availability
    compilation = callable_.compilation
    aliases = callable_.aliases
    if isinstance(availability_payload, Mapping):
        expression = availability_payload.get("expression")
        if isinstance(expression, dict):
            patch_availability = _availability_to_model(expression)
            if alias_only:
                aliases = tuple(
                    replace(
                        alias,
                        availability=patch_availability,
                        provenance=explicit,
                    )
                    if alias.name in (matched_names or set())
                    else alias
                    for alias in aliases
                )
            else:
                availability = patch_availability
        macros = tuple(sorted(_macros_from_availability_payload(availability_payload)))
        headers = tuple(
            item["name"]
            for item in cast(Iterable[object], patch.get("header", ()))
            if isinstance(item, Mapping) and isinstance(item.get("name"), str)
        )
        execution_states = tuple(
            item
            for item in availability_payload.get("execution_states", ())
            if isinstance(item, str)
        )
        extensions = tuple(
            item
            for item in availability_payload.get("extensions", ())
            if isinstance(item, str)
        )
        modes = []
        mode_payload = availability_payload.get("by_mode")
        if isinstance(mode_payload, Mapping):
            for mode, value in sorted(mode_payload.items()):
                if isinstance(mode, str) and isinstance(value, dict):
                    modes.append(
                        ModeAvailability(
                            mode=mode,
                            availability=_availability_to_model(value),
                            provenance=explicit,
                        )
                    )
        if not alias_only:
            compilation = _merge_compilation(
                compilation,
                CompilationRequirements(
                    extensions=extensions,
                    feature_macros=macros,
                    headers=headers,
                    execution_states=execution_states,
                    availability=availability,
                    availability_by_mode=tuple(modes),
                    provenance=explicit,
                ),
                prefer_right_mode_availability=True,
            )

    maturity = callable_.maturity
    maturity_payload = patch.get("maturity")
    if isinstance(maturity_payload, Mapping):
        value = maturity_payload.get("support_level")
        if isinstance(value, str) and value in {item.value for item in Maturity}:
            maturity = Maturity(value)

    semantics = callable_.semantics
    semantics_text = patch.get("semantics")
    if isinstance(semantics_text, str) and semantics_text.strip():
        semantics = replace(
            semantics,
            description=semantics_text.strip(),
            provenance=explicit,
        )

    instructions = list(callable_.instructions)
    for item in cast(Iterable[object], patch.get("instructions", ())):
        if not isinstance(item, Mapping):
            continue
        try:
            relation = InstructionRelationKind(str(item.get("relation", "unknown")))
        except ValueError:
            relation = InstructionRelationKind.UNKNOWN
        mnemonics = item.get("mnemonics") or (None,)
        if not isinstance(mnemonics, Sequence) or isinstance(mnemonics, str):
            mnemonics = (None,)
        for mnemonic in mnemonics:
            mapping = InstructionMapping(
                relation=relation,
                mnemonic=mnemonic if isinstance(mnemonic, str) else None,
                form=str(item.get("form") or item.get("raw") or "") or None,
                guaranteed_emission=bool(item.get("guaranteed_emission", False)),
                provenance=explicit,
            )
            if canonical_json(mapping) not in {
                canonical_json(value) for value in instructions
            }:
                instructions.append(mapping)

    states = list(callable_.state_access)
    for item in cast(Iterable[object], patch.get("state", ())):
        if not isinstance(item, Mapping):
            continue
        try:
            state = StateAccess(
                state=str(item["state"]),
                mode=StateAccessMode(str(item["mode"])),
                provenance=explicit,
            )
        except (KeyError, ValueError):
            continue
        if canonical_json(state) not in {canonical_json(value) for value in states}:
            states.append(state)

    taxonomy = list(callable_.taxonomy)
    path = patch.get("taxonomy_path")
    if isinstance(path, Sequence) and not isinstance(path, str):
        normalized_path = tuple(item for item in path if isinstance(item, str))
        if normalized_path and normalized_path not in taxonomy:
            taxonomy.append(normalized_path)

    diagnostics = list(callable_.diagnostics)
    for item in cast(Iterable[object], patch.get("diagnostics", ())):
        if not isinstance(item, Mapping):
            continue
        if item.get("code") == "signature_missing_use_declaration_inventory":
            continue
        try:
            severity = DiagnosticSeverity(str(item.get("severity", "warning")))
        except ValueError:
            severity = DiagnosticSeverity.ERROR
        diagnostic = Diagnostic(
            code=str(item.get("code") or "acle.enrichment"),
            message=str(item.get("message") or "ACLE enrichment diagnostic."),
            severity=severity,
            sources=(source,),
        )
        if diagnostic not in diagnostics:
            diagnostics.append(diagnostic)

    sources = _unique_sources((*callable_.sources, source))
    field_provenance = list(callable_.field_provenance)
    provenance_fields = (
        ("aliases", "maturity", "semantics", "instructions")
        if alias_only
        else ("availability", "maturity", "semantics", "instructions")
    )
    for field_name in provenance_fields:
        field_provenance.append(FieldProvenance(field_name, explicit))
    return normalize_callable(
        replace(
            callable_,
            family=family,
            families=families,
            aliases=aliases,
            availability=availability,
            maturity=maturity,
            semantics=semantics,
            instructions=tuple(instructions),
            state_access=tuple(states),
            compilation=compilation,
            headers=tuple(sorted(set((*callable_.headers, *compilation.headers)))),
            taxonomy=tuple(taxonomy),
            sources=sources,
            field_provenance=tuple(field_provenance),
            diagnostics=tuple(diagnostics),
        )
    )


def _apply_llvm_target_guards(
    callables: Sequence[ConcreteCallable],
    guards: Sequence[LLVMTargetGuard],
    feature_db: Sequence[FeatureFlagMapping],
) -> list[ConcreteCallable]:
    """Attach authoritative per-record TableGen target guards."""

    token_index = _target_guard_macro_index(feature_db)
    by_spelling: dict[str, list[LLVMTargetGuard]] = {}
    for guard in guards:
        by_spelling.setdefault(guard.spelling, []).append(guard)

    result = []
    for callable_ in callables:
        has_acle_source = any(
            source.repository == ACLE_REPOSITORY for source in callable_.sources
        )
        has_llvm_header_source = any(
            source.repository == "llvm/llvm-project" and "/include/arm_" in source.path
            for source in callable_.sources
        )
        if has_acle_source and not has_llvm_header_source:
            # A prose-only ACLE declaration can be newer than the pinned Clang
            # inventory.  A same-prefix TableGen record is not evidence for it.
            result.append(callable_)
            continue
        # arm_sve.td is the source for arm_sve.h.  SME declarations can share
        # short base spellings such as ``svadd`` while being generated by the
        # separate arm_sme.td schema; borrowing an SVE record by prefix would
        # therefore manufacture an unrelated guard.
        if callable_.headers and "arm_sve.h" not in callable_.headers:
            result.append(callable_)
            continue
        candidate_groups = [
            (base, values)
            for base, values in by_spelling.items()
            if callable_.name == base or callable_.name.startswith(f"{base}_")
        ]
        if not candidate_groups:
            result.append(callable_)
            continue
        longest = max(len(base) for base, _ in candidate_groups)
        candidate_guards = tuple(
            guard
            for base, values in candidate_groups
            if len(base) == longest
            for guard in values
        )
        selected, ambiguity = _select_target_guards(callable_, candidate_guards)
        if selected:
            result.append(
                _apply_llvm_target_guard(
                    callable_,
                    selected,
                    token_index,
                    feature_db,
                )
            )
            continue
        reason = ambiguity or (
            "Pinned LLVM records with different target guards could not be "
            "matched to this concrete callable without guessing."
        )
        result.append(
            normalize_callable(
                replace(
                    callable_,
                    compilation=replace(
                        callable_.compilation,
                        unresolved_reason=_merge_unresolved_reasons(
                            callable_.compilation.unresolved_reason,
                            f"LLVM target guard is unresolved: {reason}",
                        ),
                    ),
                    diagnostics=tuple(
                        _unique_diagnostics(
                            (
                                *callable_.diagnostics,
                                Diagnostic(
                                    code="llvm.target_guard_ambiguous",
                                    message=reason,
                                    severity=DiagnosticSeverity.ERROR,
                                    field="compilation.compiler_flags",
                                    sources=tuple(
                                        _unique_sources(
                                            guard.source for guard in candidate_guards
                                        )
                                    ),
                                ),
                            )
                        )
                    ),
                )
            )
        )
    return result


def _select_target_guards(
    callable_: ConcreteCallable,
    guards: Sequence[LLVMTargetGuard],
) -> tuple[tuple[LLVMTargetGuard, ...], str | None]:
    """Select guards without combining distinct TableGen conditions.

    When every record for one base spelling has the same complete SVE/SME
    condition, the condition is safe to share even for a defm whose multiclass
    argument layout is intentionally opaque.  If conditions differ, only a
    concrete name produced by a known direct-record or allowlisted multiclass
    pattern/type identity may select a condition.  Ambiguity is retained as a
    diagnostic instead of weakening the source condition with an OR.
    """

    ordered = tuple(sorted(guards, key=lambda item: item.source.start_line or 0))
    by_condition: dict[str, list[LLVMTargetGuard]] = {}
    for guard in ordered:
        by_condition.setdefault(_target_guard_condition_identity(guard), []).append(
            guard
        )
    if len(by_condition) == 1:
        exact = tuple(
            guard
            for guard in ordered
            if _target_guard_matches_callable(guard, callable_)
        )
        return (exact[:1] or ordered[:1]), None

    exact = tuple(
        guard for guard in ordered if _target_guard_matches_callable(guard, callable_)
    )
    exact_conditions = {_target_guard_condition_identity(guard) for guard in exact}
    if len(exact_conditions) == 1:
        selected_condition = next(iter(exact_conditions))
        return (
            tuple(
                guard
                for guard in exact
                if _target_guard_condition_identity(guard) == selected_condition
            ),
            None,
        )
    if not exact:
        return (), (
            f"{callable_.name}: multiple pinned LLVM target guards share the base "
            "spelling, but no known direct or allowlisted multiclass pattern and "
            "type set identifies this concrete callable."
        )
    return (), (
        f"{callable_.name}: multiple pinned LLVM records generate this concrete "
        "name with different target guards; prototype semantics are not guessed."
    )


def _target_guard_condition_identity(guard: LLVMTargetGuard) -> str:
    return canonical_json((guard.sve_guard, guard.sme_guard, guard.diagnostics))


_TABLEGEN_TYPE_SUFFIXES = {
    "b": ("bf", 16),
    "c": ("s", 8),
    "d": ("f", 64),
    "f": ("f", 32),
    "h": ("f", 16),
    "i": ("s", 32),
    "l": ("s", 64),
    "m": ("mf", 8),
    "q": ("s", 128),
    "s": ("s", 16),
}
_TABLEGEN_MULTICLASS_MERGE_FORMS = {
    "SInstZPZ": ("_m", "_x", "_z"),
    "SInstZPZZ": ("_m", "_x", "_z"),
    "SInstZPZZZ": ("_m", "_x", "_z"),
    "SInstZPZxZ": ("_m", "_x", "_z"),
    "SInstCvtMXZ": ("_m", "_x", "_z"),
    "SInstCvtMX": ("_m", "_x"),
}


def _target_guard_matches_callable(
    guard: LLVMTargetGuard,
    callable_: ConcreteCallable,
) -> bool:
    """Match one TableGen record to one concrete, typed public spelling."""

    return callable_.name in _target_guard_concrete_names(guard)


def _target_guard_concrete_names(guard: LLVMTargetGuard) -> tuple[str, ...]:
    pattern = guard.name_pattern
    if not pattern:
        return ()

    forms: tuple[tuple[str, str], ...]
    if guard.record_class in _TABLEGEN_MULTICLASS_MERGE_FORMS:
        if guard.record_class in {
            "SInstZPZ",
            "SInstZPZZ",
            "SInstZPZZZ",
            "SInstZPZxZ",
        }:
            patterns = (f"{pattern}[_{{d}}]",)
            if guard.record_class != "SInstZPZ":
                patterns += (f"{pattern}[_n_{{d}}]",)
        else:
            patterns = (pattern,)
        forms = tuple(
            (item, merge)
            for item in patterns
            for merge in _TABLEGEN_MULTICLASS_MERGE_FORMS[guard.record_class]
        )
    elif guard.record_class == "SInstWideDSPAcc":
        forms = (
            (f"{pattern}[_{{d}}]", ""),
            (f"{pattern}[_n_{{d}}]", ""),
        )
    elif guard.record_class in {"SInst", "MInst"}:
        if guard.prototype is None or guard.merge_suffix is None:
            return ()
        forms = ((pattern, guard.merge_suffix),)
    else:
        # Unknown multiclasses remain opaque rather than assuming that their
        # second string argument is a type set or that they add type suffixes.
        return ()

    candidates = {
        expanded
        for type_spec in _tablegen_type_specs(guard.type_spec)
        for item, merge_suffix in forms
        if (
            expanded := _expand_tablegen_name_pattern(
                item,
                prototype=guard.prototype,
                type_spec=type_spec,
                merge_suffix=merge_suffix,
            )
        )
        is not None
    }
    return tuple(sorted(candidates))


def _tablegen_type_specs(type_spec: str | None) -> tuple[str, ...]:
    if type_spec is None:
        return ()
    matches = tuple(re.finditer(r"[A-Z]*[a-z]", type_spec))
    if "".join(match.group(0) for match in matches) != type_spec:
        return ()
    return tuple(dict.fromkeys(match.group(0) for match in matches))


def _expand_tablegen_name_pattern(
    pattern: str,
    *,
    prototype: str | None,
    type_spec: str,
    merge_suffix: str,
) -> str | None:
    """Expand the pinned SveEmitter ``{d}``/``{0}``... name syntax."""

    expanded = pattern.replace("[", "").replace("]", "")
    for placeholder in re.findall(r"\{(?P<operand>d|[0-3])\}", expanded):
        if placeholder == "d":
            modifier = "d"
        elif prototype is not None:
            modifier = _tablegen_proto_modifier(prototype, int(placeholder))
        else:
            modifier = None
        if modifier is None:
            return None
        suffix = _tablegen_type_suffix(type_spec, modifier)
        if suffix is None:
            return None
        expanded = expanded.replace(f"{{{placeholder}}}", suffix)
    if "{" in expanded or "}" in expanded:
        return None
    return f"{expanded}{merge_suffix}"


def _tablegen_proto_modifier(prototype: str, operand: int) -> str | None:
    """Mirror SveEmitter's pinned ``getProtoModifier`` operand indexing."""

    index = 0
    position = 0
    while position < len(prototype):
        modifier = prototype[position]
        consumed = 1
        if modifier in "234":
            modifier = "d"
            if position + 2 < len(prototype) and prototype[position + 1] == ".":
                modifier = prototype[position + 2]
                consumed = 3
        if index == operand:
            return modifier
        index += 1
        position += consumed
    return None


def _tablegen_type_suffix(type_spec: str, modifier: str) -> str | None:
    """Return one explicit name suffix using pinned SveEmitter type rules."""

    match = re.fullmatch(r"(?P<modifiers>[A-Z]*)(?P<base>[a-z])", type_spec)
    if match is None:
        return None
    base = _TABLEGEN_TYPE_SUFFIXES.get(match.group("base"))
    if base is None:
        return None
    kind, width = base
    if "U" in match.group("modifiers"):
        kind = "u"

    if modifier in {"d", "c", "p", "{", "s", "a"}:
        pass
    elif modifier == "e":
        kind, width = "u", width // 2
    elif modifier == "h":
        width //= 2
    elif modifier == "q":
        width //= 4
    elif modifier == "b":
        kind, width = "u", width // 4
    elif modifier == "o":
        width *= 4
    elif modifier == "R":
        width //= 2
    elif modifier == "r":
        width //= 4
    elif modifier == "@":
        kind, width = "u", width // 4
    elif modifier == "K":
        kind = "s"
    elif modifier == "L":
        kind = "u"
    elif modifier == "u":
        kind = "u"
    elif modifier == "x":
        kind = "s"
    elif modifier in {"t", "C", "U"}:
        kind, width = "s", 32
    elif modifier in {"z", "G", "Y"}:
        kind, width = "u", 32
    elif modifier in {"A", "S"}:
        kind, width = "s", 8
    elif modifier in {"E", "W"}:
        kind, width = "u", 8
    elif modifier in {"B", "T"}:
        kind, width = "s", 16
    elif modifier in {"F", "X"}:
        kind, width = "u", 16
    elif modifier == "D":
        kind, width = "s", 64
    elif modifier == "O":
        kind, width = "f", 16
    elif modifier == "M":
        kind, width = "f", 32
    elif modifier == "N":
        kind, width = "f", 64
    elif modifier == "$":
        kind, width = "bf", 16
    elif modifier in {"~", "!"}:
        kind, width = "mf", 8
    else:
        return None

    if width <= 0:
        return None
    return f"{kind}{width}"


def _apply_llvm_target_guard(
    callable_: ConcreteCallable,
    guards: Sequence[LLVMTargetGuard],
    token_index: Mapping[str, tuple[str, ...]],
    feature_db: Sequence[FeatureFlagMapping],
) -> ConcreteCallable:
    sve_values: list[AvailabilityExpr] = []
    sme_values: list[AvailabilityExpr] = []
    unknown_tokens: set[str] = set()
    diagnostics = list(callable_.diagnostics)
    sources = []
    for guard in guards:
        sources.append(guard.source)
        if guard.sve_guard is not None:
            value, unknown = _translate_target_guard(guard.sve_guard, token_index)
            sve_values.append(value)
            unknown_tokens.update(unknown)
        if guard.sme_guard is not None:
            value, unknown = _translate_target_guard(guard.sme_guard, token_index)
            # A streaming-only target feature is meaningful only in SME mode.
            if _availability_contains_token(guard.sme_guard, "ssve-") and not any(
                macro.startswith("__ARM_FEATURE_SME")
                for macro in _availability_macros(value)
            ):
                value = normalize_availability(
                    AvailabilityExpr.all(
                        AvailabilityExpr.defined("__ARM_FEATURE_SME"), value
                    )
                )
            sme_values.append(value)
            unknown_tokens.update(unknown)
        for detail in guard.diagnostics:
            diagnostics.append(
                Diagnostic(
                    code="llvm.target_guard_unparsed",
                    message=detail,
                    field="availability",
                    sources=(guard.source,),
                )
            )

    sve_guard = _availability_alternative(sve_values)
    sme_guard = _availability_alternative(sme_values)
    global_guard = _availability_alternative(
        tuple(item for item in (sve_guard, sme_guard) if item is not None)
    )
    if global_guard is None:
        return callable_

    if unknown_tokens:
        diagnostics.append(
            Diagnostic(
                code="llvm.target_guard_feature_unmapped",
                message=(
                    "Pinned LLVM target guard token(s) have no ACLE feature mapping: "
                    + ", ".join(sorted(unknown_tokens))
                ),
                field="compilation.compiler_flags",
                sources=tuple(_unique_sources(sources)),
            )
        )

    macros = _availability_macros(global_guard)
    supported_vector_roots = {
        root
        for root, value in (("sve", sve_guard), ("sme", sme_guard))
        if value is not None
    }
    family_candidates = tuple(
        family
        for family in (
            *callable_.families,
            *_families_for_feature_macros(macros, feature_db),
        )
        if _family_root(family) not in {"sve", "sme"}
        or _family_root(family) in supported_vector_roots
    )
    if not family_candidates:
        family_candidates = callable_.families
    families = normalize_families(family_candidates[0], family_candidates)
    signature = callable_.signature
    field_provenance = callable_.field_provenance
    if sve_guard is None and sme_guard is not None:
        signature = replace(
            signature,
            attributes=tuple(dict.fromkeys((*signature.attributes, "__arm_streaming"))),
        )
        field_provenance = _canonical_union(
            field_provenance,
            (
                FieldProvenance(
                    "signature.attributes",
                    Provenance(
                        ProvenanceKind.DERIVED,
                        tuple(_unique_sources(sources)),
                        rule=(
                            "derive-streaming-attribute-from-LLVM-InvalidMode-"
                            "and-SMETargetGuard"
                        ),
                    ),
                ),
            ),
        )
    mode_availability = []
    if sve_guard is not None:
        mode_availability.append(
            ModeAvailability(
                "non_streaming",
                sve_guard,
                Provenance(
                    ProvenanceKind.EXPLICIT,
                    tuple(_unique_sources(sources)),
                    rule="inherit-SVETargetGuard-from-scoped-LLVM-TableGen-record",
                ),
            )
        )
    if sme_guard is not None:
        mode_availability.append(
            ModeAvailability(
                "streaming",
                sme_guard,
                Provenance(
                    ProvenanceKind.EXPLICIT,
                    tuple(_unique_sources(sources)),
                    rule="inherit-SMETargetGuard-from-scoped-LLVM-TableGen-record",
                ),
            )
        )

    has_source_availability = (
        callable_.availability != AvailabilityExpr.always()
        or callable_.compilation.availability != AvailabilityExpr.always()
        or bool(callable_.compilation.availability_by_mode)
    )
    availability = callable_.availability if has_source_availability else global_guard
    compilation = callable_.compilation
    if not has_source_availability:
        compilation = replace(
            compilation,
            availability=global_guard,
            availability_by_mode=tuple(mode_availability),
        )
    compilation = replace(
        compilation,
        feature_macros=tuple(sorted(set((*compilation.feature_macros, *macros)))),
        provenance=Provenance(
            ProvenanceKind.EXPLICIT,
            tuple(_unique_sources((*compilation.provenance.sources, *sources))),
            rule="map-pinned-LLVM-TableGen-target-guard-to-ACLE-feature-gates",
        ),
    )
    return normalize_callable(
        replace(
            callable_,
            family=families[0],
            families=families,
            signature=signature,
            availability=availability,
            compilation=compilation,
            sources=_unique_sources((*callable_.sources, *sources)),
            field_provenance=field_provenance,
            diagnostics=tuple(_unique_diagnostics(diagnostics)),
        )
    )


def _target_guard_macro_index(
    feature_db: Sequence[FeatureFlagMapping],
) -> dict[str, tuple[str, ...]]:
    values: dict[str, set[str]] = {
        "sve": {"__ARM_FEATURE_SVE"},
        "sve2": {"__ARM_FEATURE_SVE2"},
        "sve2p1": {"__ARM_FEATURE_SVE2p1"},
        "sve2p2": {"__ARM_FEATURE_SVE2p2"},
        "sve2p3": {"__ARM_FEATURE_SVE2p3"},
        "sme": {"__ARM_FEATURE_SME"},
        "sme2": {"__ARM_FEATURE_SME2"},
        "sme2p1": {"__ARM_FEATURE_SME2p1"},
        "sme2p2": {"__ARM_FEATURE_SME2p2"},
        "sme2p3": {"__ARM_FEATURE_SME2p3"},
        # These spellings are pinned LLVM target tokens with direct ACLE
        # feature-macro definitions. They are not aliases for baseline SVE.
        "sve-b16b16": {"__ARM_FEATURE_SVE_B16B16"},
        "sme-b16b16": {"__ARM_FEATURE_SME_B16B16"},
    }
    explicit: dict[str, set[str]] = {}
    heuristic: dict[str, set[str]] = {}
    for mapping in feature_db:
        normalized_key = mapping.key.replace("_", "-").lower()
        aliases = {normalized_key}
        if normalized_key.startswith("sve2-"):
            suffix = normalized_key.removeprefix("sve2-")
            aliases.update((f"sve-{suffix}", f"ssve-{suffix}"))
        for alias in aliases:
            heuristic.setdefault(alias, set()).update(mapping.acle_macros)

        if mapping.extension_names:
            extension_name = "-".join(mapping.extension_names).lower()
            explicit.setdefault(extension_name, set()).update(mapping.acle_macros)

    for alias, macros in heuristic.items():
        values.setdefault(alias, set()).update(macros)
    for extension_name, macros in explicit.items():
        # A pinned explicit extension name is authoritative for that exact
        # token.  It must not inherit macros from a key-derived convenience
        # alias such as sve2-* -> ssve-*.
        values[extension_name] = set(macros)
    # ``arm_sve.td`` names the architectural target features, not the generic
    # ACLE macro families.  Inside the SVE header adapter these two tokens gate
    # the SVE forms specifically; mapping them to the generic BF16/I8MM macros
    # would omit the required scalable-vector feature from compiler examples.
    values["bf16"] = {"__ARM_FEATURE_SVE_BF16"}
    values["i8mm"] = {"__ARM_FEATURE_SVE_MATMUL_INT8"}
    return {key: tuple(sorted(macros)) for key, macros in values.items()}


def _translate_target_guard(
    expression: AvailabilityExpr,
    token_index: Mapping[str, tuple[str, ...]],
) -> tuple[AvailabilityExpr, set[str]]:
    if expression.op is AvailabilityOp.DEFINED:
        token = (expression.key or "").lower()
        macros = token_index.get(token)
        if not macros:
            return AvailabilityExpr.raw(f"LLVM target feature {token!r}"), {token}
        return normalize_availability(
            AvailabilityExpr.all(*(AvailabilityExpr.defined(macro) for macro in macros))
        ), set()
    if expression.op in {AvailabilityOp.ALL, AvailabilityOp.ANY}:
        values = [
            _translate_target_guard(item, token_index) for item in expression.arguments
        ]
        children = tuple(value for value, _ in values)
        unknown = set().union(*(items for _, items in values))
        return normalize_availability(
            AvailabilityExpr(expression.op, arguments=children)
        ), unknown
    if expression.op is AvailabilityOp.NOT:
        child, unknown = _translate_target_guard(expression.arguments[0], token_index)
        return AvailabilityExpr.not_(child), unknown
    if expression.op is AvailabilityOp.RAW:
        return expression, {expression.text or "unparsed"}
    return expression, set()


def _availability_contains_token(expression: AvailabilityExpr, prefix: str) -> bool:
    return bool(expression.key and expression.key.lower().startswith(prefix)) or any(
        _availability_contains_token(item, prefix) for item in expression.arguments
    )


def _availability_alternative(
    values: Sequence[AvailabilityExpr],
) -> AvailabilityExpr | None:
    if not values:
        return None
    return normalize_availability(AvailabilityExpr.any(*values))


def _families_for_feature_macros(
    macros: Iterable[str],
    feature_db: Sequence[FeatureFlagMapping],
) -> tuple[str, ...]:
    result = []
    family_by_key = {
        "sve": "sve",
        "sve2": "sve2",
        "sve2p1": "sve2.1",
        "sve2p2": "sve2.2",
        "sve2p3": "sve2.3",
        "sme": "sme",
        "sme2": "sme2",
        "sme2p1": "sme2.1",
        "sme2p2": "sme2.2",
        "sme2p3": "sme2.3",
    }
    by_macro = index_feature_flags_by_macro(feature_db)
    for macro in macros:
        direct = re.match(
            r"__ARM_FEATURE_(SVE2p[123]|SME2p[123]|SVE2|SME2|SVE|SME)", macro
        )
        if direct:
            result.append(family_by_key[direct.group(1).lower()])
        for mapping in by_macro.get(macro, ()):
            candidates = (mapping.key, *mapping.implies)
            result.extend(
                family_by_key[item] for item in candidates if item in family_by_key
            )
    return tuple(dict.fromkeys(result))


def _attach_feature_flags(
    callable_: ConcreteCallable,
    feature_index: Mapping[str, Sequence[FeatureFlagMapping]],
) -> ConcreteCallable:
    global_availability = normalize_availability(
        AvailabilityExpr.all(
            callable_.availability,
            callable_.compilation.availability,
        )
    )
    global_macros = _availability_macros(global_availability)
    mode_macros = {
        macro
        for item in callable_.compilation.availability_by_mode
        for macro in _availability_macros(item.availability)
    }
    macros = set(callable_.compilation.feature_macros)
    macros.update(global_macros)
    macros.update(mode_macros)
    neon_feature_evidence_errors = tuple(
        diagnostic
        for diagnostic in callable_.diagnostics
        if diagnostic.code in _NEON_FEATURE_EVIDENCE_ERRORS
    )
    unresolved_target_guard = any(
        diagnostic.code == "llvm.target_guard_ambiguous"
        for diagnostic in callable_.diagnostics
    )
    derived_macros = _derived_family_macros(
        callable_,
        infer_family_macros=not macros and not unresolved_target_guard,
    )
    macros.update(derived_macros)

    if neon_feature_evidence_errors:
        reason = "; ".join(
            dict.fromkeys(item.message for item in neon_feature_evidence_errors)
        )
        return normalize_callable(
            replace(
                callable_,
                compilation=replace(
                    callable_.compilation,
                    feature_macros=tuple(sorted(macros)),
                    compiler_flags=(),
                    unresolved_reason=_merge_unresolved_reasons(
                        callable_.compilation.unresolved_reason,
                        f"Neon target-feature evidence is unresolved: {reason}",
                    ),
                ),
            )
        )

    if not macros:
        return normalize_callable(callable_)

    global_availability = _replace_feature_macro_gates(
        global_availability,
        callable_,
        feature_index,
    )
    mode_availability = tuple(
        replace(
            item,
            availability=_replace_feature_macro_gates(
                item.availability,
                callable_,
                feature_index,
            ),
        )
        for item in callable_.compilation.availability_by_mode
    )
    for macro in sorted(macros - mode_macros - global_macros):
        global_availability = normalize_availability(
            AvailabilityExpr.all(
                global_availability,
                _exact_feature_macro_gate(callable_, macro, feature_index),
            )
        )

    target_names = _targets_for_callable(callable_)
    metadata_requirements = [
        replace(
            callable_.compilation,
            availability=global_availability,
            availability_by_mode=mode_availability,
            compiler_flags=(),
        )
    ]
    unresolved_details: list[str] = []
    for macro in sorted(macros):
        mappings = _feature_mappings_for_macro(callable_, macro, feature_index)
        if not mappings:
            unresolved_details.append(
                f"{macro}: no pinned compiler-flag mapping exists"
            )
            continue
        for target in target_names:
            target_requirements = [
                requirement
                for mapping in mappings
                for requirement in mapping.compilation_requirements(
                    macro=macro,
                    target=target,
                )
            ]
            if not target_requirements:
                unresolved_details.append(
                    f"{macro}: no {target} compiler context is pinned"
                )
                continue
            for requirement in target_requirements:
                metadata_requirements.append(
                    replace(
                        requirement,
                        availability=AvailabilityExpr.always(),
                        compiler_flags=(),
                    )
                )
                if requirement.unresolved_reason:
                    unresolved_details.append(
                        f"{macro} ({target}): {requirement.unresolved_reason}"
                    )
                if not requirement.architecture_min:
                    unresolved_details.append(
                        f"{macro} ({target}): minimum architecture is unresolved"
                    )
                if not requirement.compiler_flags:
                    unresolved_details.append(
                        f"{macro} ({target}): compiler flags are unresolved"
                    )

    flag_availability = _compiler_flag_availability(global_availability)
    mode_branch_specs = [
        (
            mode.mode,
            normalize_availability(
                AvailabilityExpr.all(flag_availability, mode.availability)
            ),
        )
        for mode in mode_availability
    ]
    branch_specs: list[tuple[str | None, AvailabilityExpr]] = (
        list(mode_branch_specs) if mode_branch_specs else [(None, flag_availability)]
    )
    flag_examples: list[CompilerFlagExample] = []
    branch_architecture_mins: list[str] = []
    mappable_raw_gates = _mappable_raw_feature_gates(
        callable_,
        macros,
        feature_index,
    )
    for mode, expression in branch_specs:
        branches, dnf_error = _availability_to_dnf(expression)
        label = mode or "global"
        if dnf_error:
            unresolved_details.append(f"{label}: {dnf_error}")
            continue
        for branch in branches:
            branch_expression = normalize_availability(AvailabilityExpr.all(*branch))
            effective_mode = mode or _unique_positive_calling_context(branch)
            unsupported = _unsupported_flag_branch_leaves(
                branch,
                mappable_raw_gates=mappable_raw_gates,
            )
            if unsupported:
                unresolved_details.append(
                    f"{label} branch {_availability_label(branch_expression)}: "
                    + ", ".join(unsupported)
                )
                continue
            branch_macros = sorted(_availability_macros(branch_expression))
            if not branch_macros:
                continue
            for target in target_names:
                examples, reason, architecture_mins = _compiler_examples_for_branch(
                    callable_,
                    branch_expression,
                    branch_macros,
                    mode=effective_mode,
                    target=target,
                    feature_index=feature_index,
                )
                flag_examples.extend(examples)
                branch_architecture_mins.extend(architecture_mins)
                if reason:
                    unresolved_details.append(reason)

    merged = metadata_requirements[0]
    for requirement in metadata_requirements[1:]:
        merged = _merge_compilation(merged, requirement)
    flag_examples = list(_canonical_union((), flag_examples))
    merged = replace(
        merged,
        architecture_min=(
            " / ".join(dict.fromkeys(branch_architecture_mins))
            if branch_architecture_mins
            else merged.architecture_min
        ),
        headers=tuple(sorted(set((*merged.headers, *callable_.headers)))),
        feature_macros=tuple(sorted(macros)),
        compiler_flags=tuple(flag_examples),
        unresolved_reason=(
            "Partial feature-to-compiler mapping: "
            + "; ".join(dict.fromkeys(unresolved_details))
            if unresolved_details
            else None
            if macros
            and merged.architecture_min
            and flag_examples
            and _is_superseded_adapter_reason(merged.unresolved_reason)
            else merged.unresolved_reason
        ),
    )
    return normalize_callable(
        replace(
            callable_,
            availability=global_availability,
            compilation=merged,
            headers=tuple(sorted(set((*callable_.headers, *merged.headers)))),
        )
    )


_TABULAR_TARGET_SCOPE_RE = re.compile(
    r"(?:v\d+(?:\.\d+)?|A32|A64|MVE|NEON)"
    r"(?:\s*/\s*(?:v\d+(?:\.\d+)?|A32|A64|MVE|NEON))*",
    re.IGNORECASE,
)


def _compiler_flag_availability(expression: AvailabilityExpr) -> AvailabilityExpr:
    """Remove tabular target labels from feature-flag branch conditions.

    The ACLE CSV ``Supported architectures`` column is preserved verbatim on
    each callable as RAW availability.  Values such as ``v7/A32/A64`` and
    ``MVE/NEON`` select target families; they are not feature expressions and
    must not prevent a source-backed ``-march`` example from being derived.
    Unknown RAW prose remains untouched and therefore unresolved.
    """

    if expression.op is AvailabilityOp.RAW:
        text = (expression.text or "").strip()
        if _TABULAR_TARGET_SCOPE_RE.fullmatch(text):
            return AvailabilityExpr.always()
        return expression
    if expression.op in {AvailabilityOp.ALL, AvailabilityOp.ANY}:
        return normalize_availability(
            AvailabilityExpr(
                expression.op,
                arguments=tuple(
                    _compiler_flag_availability(item) for item in expression.arguments
                ),
            )
        )
    if expression.op is AvailabilityOp.NOT:
        return normalize_availability(
            AvailabilityExpr.not_(_compiler_flag_availability(expression.arguments[0]))
        )
    return expression


def _attach_performance(
    callable_: ConcreteCallable,
    records: Sequence[PerformanceRecord],
) -> ConcreteCallable:
    matches: list[PerformanceRecord] = []
    for mapping in callable_.instructions:
        if not mapping.form:
            continue
        try:
            found = match_performance_records(mapping.form, records)
        except ValueError:
            continue
        for match in found:
            if match.record not in matches:
                matches.append(match.record)
    signature_operand_type = (
        callable_.signature.parameters[0].type_name
        if callable_.signature.parameters
        else None
    )
    for family in callable_.families:
        for match in match_representative_performance_records(
            _callable_spellings(callable_),
            records,
            family=family,
            signature_operand_type=signature_operand_type,
        ):
            if match not in matches:
                matches.append(match)
    if not matches:
        matches.append(performance_unavailable_record(callable_.family))
    return normalize_callable(replace(callable_, performance=tuple(matches)))


def _merge_compilation(
    left: CompilationRequirements,
    right: CompilationRequirements,
    *,
    prefer_right_mode_availability: bool = False,
) -> CompilationRequirements:
    architecture_values = tuple(
        dict.fromkeys(
            value
            for architecture in (left.architecture_min, right.architecture_min)
            if architecture
            for value in architecture.split(" / ")
            if value
        )
    )
    availability = left.availability
    if right.availability != AvailabilityExpr.always():
        availability = AvailabilityExpr.all(left.availability, right.availability)
    sources = _unique_sources((*left.provenance.sources, *right.provenance.sources))
    resolved = any(
        item.provenance.kind is not ProvenanceKind.UNRESOLVED for item in (left, right)
    )
    availability_by_mode = _merge_mode_availability(
        left.availability_by_mode,
        right.availability_by_mode,
        prefer_right=prefer_right_mode_availability,
    )
    return CompilationRequirements(
        architecture_min=" / ".join(architecture_values) or None,
        profiles=tuple(sorted(set((*left.profiles, *right.profiles)))),
        extensions=tuple(sorted(set((*left.extensions, *right.extensions)))),
        feature_macros=tuple(
            sorted(set((*left.feature_macros, *right.feature_macros)))
        ),
        headers=tuple(sorted(set((*left.headers, *right.headers)))),
        execution_states=tuple(
            sorted(set((*left.execution_states, *right.execution_states)))
        ),
        compiler_flags=tuple(
            dict.fromkeys((*left.compiler_flags, *right.compiler_flags))
        ),
        availability=availability,
        availability_by_mode=availability_by_mode,
        provenance=(
            Provenance(
                ProvenanceKind.MANUAL_OVERRIDE,
                sources,
                rule="merge-source-availability-with-pinned-compiler-flags",
            )
            if resolved
            else Provenance.unresolved(
                right.unresolved_reason or left.unresolved_reason
            )
        ),
        unresolved_reason=_merge_unresolved_reasons(
            left.unresolved_reason,
            right.unresolved_reason,
        ),
    )


def _merge_mode_availability(
    left: Sequence[ModeAvailability],
    right: Sequence[ModeAvailability],
    *,
    prefer_right: bool,
) -> tuple[ModeAvailability, ...]:
    """Apply an explicit source policy before enforcing one condition per mode."""

    selected = right if prefer_right and right else (*left, *right)
    normalized = normalize_mode_availability(selected)
    assert len({item.mode for item in normalized}) == len(normalized)
    return normalized


_DNF_BRANCH_LIMIT = 32
_FLAG_COMBINATION_LIMIT = 32


def _availability_to_dnf(
    expression: AvailabilityExpr,
) -> tuple[tuple[tuple[AvailabilityExpr, ...], ...], str | None]:
    """Expand a normalized condition into bounded, absorbed DNF branches."""

    try:
        raw = _availability_to_dnf_inner(normalize_availability(expression))
    except ValueError as error:
        return (), str(error)
    unique: dict[tuple[str, ...], tuple[AvailabilityExpr, ...]] = {}
    for branch in raw:
        leaves = {canonical_json(item): item for item in branch}
        key = tuple(sorted(leaves))
        unique.setdefault(key, tuple(leaves[item] for item in key))
    keys = sorted(unique, key=lambda item: (len(item), item))
    absorbed = [key for key in keys if not any(set(other) < set(key) for other in keys)]
    if len(absorbed) > _DNF_BRANCH_LIMIT:
        return (), f"DNF expansion exceeds {_DNF_BRANCH_LIMIT} branches"
    return tuple(unique[key] for key in absorbed), None


def _availability_to_dnf_inner(
    expression: AvailabilityExpr,
) -> list[tuple[AvailabilityExpr, ...]]:
    if expression.op is AvailabilityOp.ALWAYS:
        return [()]
    if expression.op is AvailabilityOp.ANY:
        result = [
            branch
            for child in expression.arguments
            for branch in _availability_to_dnf_inner(child)
        ]
    elif expression.op is AvailabilityOp.ALL:
        result = [()]
        for child in expression.arguments:
            child_branches = _availability_to_dnf_inner(child)
            if len(result) * len(child_branches) > _DNF_BRANCH_LIMIT:
                raise ValueError(f"DNF expansion exceeds {_DNF_BRANCH_LIMIT} branches")
            result = [(*left, *right) for left in result for right in child_branches]
    else:
        result = [(expression,)]
    if len(result) > _DNF_BRANCH_LIMIT:
        raise ValueError(f"DNF expansion exceeds {_DNF_BRANCH_LIMIT} branches")
    return result


def _unsupported_flag_branch_leaves(
    branch: Sequence[AvailabilityExpr],
    *,
    mappable_raw_gates: frozenset[str] = frozenset(),
) -> list[str]:
    result = []
    for leaf in branch:
        if leaf.op is AvailabilityOp.RAW and leaf.text not in mappable_raw_gates:
            result.append(f"raw condition {leaf.text!r} cannot be mapped to flags")
        elif leaf.op is AvailabilityOp.NOT:
            result.append(
                "negated feature conditions cannot be proven by an enable flag"
            )
    return result


def _mappable_raw_feature_gates(
    callable_: ConcreteCallable,
    macros: Iterable[str],
    feature_index: Mapping[str, Sequence[FeatureFlagMapping]],
) -> frozenset[str]:
    """Identify exact manifest RAW gates with no unbound source placeholder."""

    result: set[str] = set()

    def visit(expression: AvailabilityExpr) -> None:
        if expression.op is AvailabilityOp.RAW and expression.text:
            scrubbed = _FEATURE_MACRO_RE.sub("", expression.text)
            scrubbed = re.sub(
                r"\b(?:0[xX][0-9A-Fa-f]+|\d+)[uUlL]*\b",
                "",
                scrubbed,
            )
            if not re.search(r"[A-Za-z_]\w*", scrubbed):
                result.add(expression.text)
            return
        for child in expression.arguments:
            visit(child)

    for macro in macros:
        visit(_exact_feature_macro_gate(callable_, macro, feature_index))
    return frozenset(result)


def _unique_positive_calling_context(
    branch: Sequence[AvailabilityExpr],
) -> str | None:
    """Return one unambiguous positive calling context from a DNF branch."""

    def contains_calling_context(expression: AvailabilityExpr) -> bool:
        return expression.op is AvailabilityOp.CALLING_CONTEXT or any(
            contains_calling_context(child) for child in expression.arguments
        )

    if any(
        leaf.op is AvailabilityOp.NOT and contains_calling_context(leaf)
        for leaf in branch
    ):
        return None
    contexts = [leaf for leaf in branch if leaf.op is AvailabilityOp.CALLING_CONTEXT]
    if len(contexts) != 1:
        return None
    raw = contexts[0].value
    values = (raw,) if isinstance(raw, str) else raw
    if not isinstance(values, (tuple, list)) or not values:
        return None
    normalized = {
        re.sub(r"[\s-]+", "_", value.strip().lower())
        for value in values
        if isinstance(value, str) and value.strip()
    }
    return normalized.pop() if len(normalized) == 1 else None


def _feature_mappings_for_macro(
    callable_: ConcreteCallable,
    macro: str,
    feature_index: Mapping[str, Sequence[FeatureFlagMapping]],
) -> list[FeatureFlagMapping]:
    mappings = list(feature_index.get(macro, ()))
    if macro == "__ARM_FEATURE_MVE":
        wants_fp = _callable_uses_floating_point(callable_)
        key = "mve_fp" if wants_fp else "mve"
        mappings = [mapping for mapping in mappings if mapping.key == key]
    return mappings


def _exact_feature_macro_gate(
    callable_: ConcreteCallable,
    macro: str,
    feature_index: Mapping[str, Sequence[FeatureFlagMapping]],
) -> AvailabilityExpr:
    """Return the exact manifest gate for one callable-selected feature macro."""

    gates: dict[str, AvailabilityExpr] = {}
    for mapping in _feature_mappings_for_macro(callable_, macro, feature_index):
        gate = normalize_availability(mapping.gate_for(macro).expression)
        gates[canonical_json(gate)] = gate
    if not gates:
        return AvailabilityExpr.defined(macro)
    values = tuple(gates[key] for key in sorted(gates))
    return normalize_availability(AvailabilityExpr.any(*values))


def _replace_feature_macro_gates(
    expression: AvailabilityExpr,
    callable_: ConcreteCallable,
    feature_index: Mapping[str, Sequence[FeatureFlagMapping]],
) -> AvailabilityExpr:
    """Replace bare macro tests without changing the surrounding Boolean shape."""

    if expression.op is AvailabilityOp.DEFINED and expression.key:
        return _exact_feature_macro_gate(callable_, expression.key, feature_index)
    if expression.op in {AvailabilityOp.ALL, AvailabilityOp.ANY}:
        return normalize_availability(
            AvailabilityExpr(
                expression.op,
                arguments=tuple(
                    _replace_feature_macro_gates(child, callable_, feature_index)
                    for child in expression.arguments
                ),
            )
        )
    if expression.op is AvailabilityOp.NOT:
        return normalize_availability(
            AvailabilityExpr.not_(
                _replace_feature_macro_gates(
                    expression.arguments[0],
                    callable_,
                    feature_index,
                )
            )
        )
    return expression


def _compiler_examples_for_branch(
    callable_: ConcreteCallable,
    branch: AvailabilityExpr,
    macros: Sequence[str],
    *,
    mode: str | None,
    target: str,
    feature_index: Mapping[str, Sequence[FeatureFlagMapping]],
) -> tuple[tuple[CompilerFlagExample, ...], str | None, tuple[str, ...]]:
    options_by_macro: dict[
        str,
        dict[
            tuple[str, str | None, str],
            list[tuple[CompilationRequirements, CompilerFlagExample]],
        ],
    ] = {}
    for macro in macros:
        keyed: dict[
            tuple[str, str | None, str],
            list[tuple[CompilationRequirements, CompilerFlagExample]],
        ] = {}
        for mapping in _feature_mappings_for_macro(callable_, macro, feature_index):
            for requirement in mapping.compilation_requirements(
                macro=macro,
                target=target,
            ):
                for example in requirement.compiler_flags:
                    style = _flag_selector_style(example.flags)
                    if style is None:
                        continue
                    keyed.setdefault(
                        (example.compiler, example.version, style), []
                    ).append((requirement, example))
        if not keyed:
            return (
                (),
                f"{mode or 'global'} branch {_availability_label(branch)} "
                f"({target}): {macro} has no complete compiler example",
                (),
            )
        options_by_macro[macro] = keyed

    common_keys = set.intersection(*(set(options_by_macro[macro]) for macro in macros))
    examples = []
    architecture_mins: list[str] = []
    combination_count = 0
    for key in sorted(
        common_keys, key=lambda item: tuple(str(value) for value in item)
    ):
        option_lists = [options_by_macro[macro][key] for macro in macros]
        for combination in product(*option_lists):
            combination_count += 1
            if combination_count > _FLAG_COMBINATION_LIMIT:
                return (
                    (),
                    f"{mode or 'global'} branch {_availability_label(branch)} "
                    f"({target}): compiler-context combinations exceed "
                    f"{_FLAG_COMBINATION_LIMIT}",
                    (),
                )
            combined = _combine_compiler_flag_examples(
                tuple(example for _, example in combination),
                availability=branch,
                mode=mode,
                target=target,
            )
            if combined is not None:
                examples.append(combined)
                architecture_min = _conjunctive_architecture_min(
                    (
                        callable_.compilation.architecture_min,
                        *(
                            requirement.architecture_min
                            for requirement, _ in combination
                        ),
                    )
                )
                if architecture_min is not None:
                    architecture_mins.append(architecture_min)
    if not examples:
        return (
            (),
            f"{mode or 'global'} branch {_availability_label(branch)} ({target}): "
            "no target-compatible compiler contexts can be combined",
            (),
        )
    return (
        _canonical_union((), examples),
        None,
        tuple(dict.fromkeys(architecture_mins)),
    )


def _conjunctive_architecture_min(values: Sequence[str | None]) -> str | None:
    """Combine minimum architectures required by one target/availability branch."""

    unique = tuple(dict.fromkeys(value for value in values if value))
    if not unique:
        return None
    parsed: list[tuple[int, int, str, str]] = []
    for value in unique:
        match = re.fullmatch(
            r"Armv(?P<major>\d+)(?:\.(?P<minor>\d+))?-(?P<profile>.+)",
            value,
        )
        if match is None:
            return " / ".join(unique)
        parsed.append(
            (
                int(match.group("major")),
                int(match.group("minor") or 0),
                match.group("profile"),
                value,
            )
        )
    if len({profile for _, _, profile, _ in parsed}) != 1:
        return " / ".join(unique)
    return max(parsed)[3]


def _flag_selector_style(flags: Sequence[str]) -> str | None:
    styles = {
        "march" if flag.startswith("-march=") else "mcpu"
        for flag in flags
        if flag.startswith(("-march=", "-mcpu="))
    }
    return styles.pop() if len(styles) == 1 else None


def _combine_compiler_flag_examples(
    examples: Sequence[CompilerFlagExample],
    *,
    availability: AvailabilityExpr,
    mode: str | None,
    target: str,
) -> CompilerFlagExample | None:
    selectors = [
        flag
        for example in examples
        for flag in example.flags
        if flag.startswith(("-march=", "-mcpu="))
    ]
    selector = _combine_target_selectors(selectors)
    if selector is None:
        return None
    other_flags = tuple(
        dict.fromkeys(
            flag
            for example in examples
            for flag in example.flags
            if not flag.startswith(("-march=", "-mcpu="))
        )
    )
    defaults = [example.default_enabled for example in examples]
    default_enabled = (
        False
        if False in defaults
        else True
        if defaults and all(value is True for value in defaults)
        else None
    )
    sources = _unique_sources(
        source for example in examples for source in example.provenance.sources
    )
    base_march = selector.split("=", 1)[1].split("+", 1)[0]
    if selector.startswith("-mcpu="):
        base_march = None
    return CompilerFlagExample(
        compiler=examples[0].compiler,
        version=examples[0].version,
        base_march=base_march,
        flags=(selector, *other_flags),
        default_enabled=default_enabled,
        notes=tuple(
            dict.fromkeys(note for example in examples for note in example.notes)
        ),
        provenance=Provenance(
            ProvenanceKind.DERIVED,
            sources,
            rule="combine-target-compatible-flags-for-one-availability-branch",
        ),
        availability=availability,
        mode=mode,
        target=target,
    )


def _combine_target_selectors(selectors: Sequence[str]) -> str | None:
    prefixes = {selector.split("=", 1)[0] for selector in selectors}
    if len(prefixes) != 1 or not selectors:
        return None
    prefix = prefixes.pop()
    parsed = [_split_target_selector(selector) for selector in selectors]
    if any(value is None for value in parsed):
        return None
    values = [value for value in parsed if value is not None]
    bases = [base for base, _ in values]
    if prefix == "-mcpu":
        if len(set(bases)) != 1:
            return None
        base = bases[0]
    else:
        base = _highest_compatible_march(bases)
        if base is None:
            return None
    extensions = tuple(
        dict.fromkeys(extension for _, items in values for extension in items)
    )
    suffix = "".join(f"+{extension}" for extension in extensions)
    return f"{prefix}={base}{suffix}"


def _split_target_selector(value: str) -> tuple[str, tuple[str, ...]] | None:
    if "=" not in value:
        return None
    _, payload = value.split("=", 1)
    parts = payload.split("+")
    if not parts[0]:
        return None
    return parts[0], tuple(part for part in parts[1:] if part)


def _highest_compatible_march(values: Sequence[str]) -> str | None:
    parsed = []
    for value in values:
        match = re.fullmatch(
            r"armv(?P<major>\d+)(?:\.(?P<minor>\d+))?-(?P<profile>.+)",
            value,
        )
        if match is None:
            return value if len(set(values)) == 1 else None
        parsed.append(
            (
                int(match.group("major")),
                int(match.group("minor") or 0),
                match.group("profile"),
                value,
            )
        )
    if len({profile for _, _, profile, _ in parsed}) != 1:
        return None
    return max(parsed)[3]


def _availability_label(expression: AvailabilityExpr) -> str:
    if expression.op is AvailabilityOp.DEFINED:
        return f"defined({expression.key})"
    if expression.op is AvailabilityOp.COMPARE:
        return f"{expression.key} {expression.comparator} {expression.value}"
    if expression.op is AvailabilityOp.RAW:
        return expression.text or "raw"
    if expression.op is AvailabilityOp.ALWAYS:
        return "always"
    if expression.op is AvailabilityOp.NOT:
        return f"not ({_availability_label(expression.arguments[0])})"
    joiner = " and " if expression.op is AvailabilityOp.ALL else " or "
    return joiner.join(_availability_label(item) for item in expression.arguments)


def _merge_unresolved_reasons(*values: str | None) -> str | None:
    reasons = tuple(dict.fromkeys(value for value in values if value))
    return "; ".join(reasons) if reasons else None


def _is_superseded_adapter_reason(value: str | None) -> bool:
    if value is None:
        return False
    return any(
        phrase in value
        for phrase in (
            "generated Clang header does not provide a stable per-declaration",
            "official tabular source does not specify complete per-intrinsic feature",
        )
    )


@dataclass(frozen=True, slots=True)
class _NeonFeatureRule:
    """Exact feature facts derived from one pinned AdvSIMD section row."""

    macros: frozenset[str]
    target_features: frozenset[str]
    unresolved_reason: str | None = None


_NEON_SECTION_BASIC = "Basic intrinsics"
_NEON_SECTION_CRYPTO = "Crypto"
_NEON_SECTION_CRC = "CRC32"
_NEON_SECTION_QRDMX = "sqrdmlah intrinsics (From ARMv8.1-A)"
_NEON_SECTION_FP16_SCALAR = (
    "fp16 scalar intrinsics (available through <arm_fp16.h> from ARMv8.2-A)"
)
_NEON_SECTION_FP16_VECTOR = "fp16 vector intrinsics (from ARMv8.2-A)"
_NEON_SECTION_ALWAYS = (
    "Additional intrinsics added in ACLE 3.0 for data processing (Always available)"
)
_NEON_SECTION_DOTPROD = (
    "Dot Product intrinsics added for ARMv8.2-a and newer. Requires the +dotprod "
    "architecture extension."
)
_NEON_SECTION_ARMV84 = "Armv8.4-a intrinsics."
_NEON_SECTION_FP16_FML = "FP16 Armv8.4-a"
_NEON_SECTION_COMPLEX = "Complex operations from Armv8.3-a"
_NEON_SECTION_FRINT = "Floating-point rounding intrinsics from Armv8.5-A"
_NEON_SECTION_I8MM = "Matrix multiplication intrinsics from Armv8.6-A"
_NEON_SECTION_BF16 = "Bfloat16 intrinsics Requires the +bf16 architecture extension."
_NEON_SECTION_FP8 = "Modal 8-bit floating-point intrinsics"
_NEON_SECTION_FP8_MM = "Matrix multiplication intrinsics from Armv9.6-A"
_NEON_SECTION_F16F32DOT = (
    "Half-precision dot product to single-precision instructions from Armv9.7-A. "
    "Requires the +f16f32dot architecture extension."
)
_NEON_SECTION_F16F32MM = (
    "Half-precision matrix multiply accumulating to single-precision instruction "
    "from Armv9.7-A. Requires the +f16f32mm architecture extension."
)
_NEON_SECTION_F16MM = (
    "Non-widening half-precision matrix multiply instruction. Requires the +f16mm "
    "architecture extension."
)

_NEON_MACRO_TARGET_FEATURES: Mapping[str, frozenset[str]] = {
    "__ARM_NEON": frozenset(("neon",)),
    "__ARM_FEATURE_AES": frozenset(("aes",)),
    "__ARM_FEATURE_BF16": frozenset(("bf16",)),
    "__ARM_FEATURE_BF16_SCALAR_ARITHMETIC": frozenset(("bf16",)),
    "__ARM_FEATURE_BF16_VECTOR_ARITHMETIC": frozenset(("bf16",)),
    "__ARM_FEATURE_COMPLEX": frozenset(("v8.3a",)),
    "__ARM_FEATURE_CRC32": frozenset(("crc",)),
    "__ARM_FEATURE_DOTPROD": frozenset(("dotprod",)),
    "__ARM_FEATURE_F16F32DOT": frozenset(("f16f32dot",)),
    "__ARM_FEATURE_F16F32MM": frozenset(("f16f32mm",)),
    "__ARM_FEATURE_F16MM": frozenset(("f16mm",)),
    "__ARM_FEATURE_F8F16MM": frozenset(("f8f16mm",)),
    "__ARM_FEATURE_F8F32MM": frozenset(("f8f32mm",)),
    "__ARM_FEATURE_FAMINMAX": frozenset(("faminmax",)),
    "__ARM_FEATURE_FP16_FML": frozenset(("fp16fml",)),
    "__ARM_FEATURE_FP16_SCALAR_ARITHMETIC": frozenset(("fullfp16",)),
    "__ARM_FEATURE_FP16_VECTOR_ARITHMETIC": frozenset(("fullfp16",)),
    "__ARM_FEATURE_FP8": frozenset(("fp8",)),
    "__ARM_FEATURE_FP8DOT2": frozenset(("fp8dot2",)),
    "__ARM_FEATURE_FP8DOT4": frozenset(("fp8dot4",)),
    "__ARM_FEATURE_FP8FMA": frozenset(("fp8fma",)),
    "__ARM_FEATURE_FRINT": frozenset(("v8.5a",)),
    "__ARM_FEATURE_LUT": frozenset(("lut",)),
    "__ARM_FEATURE_MATMUL_INT8": frozenset(("i8mm",)),
    "__ARM_FEATURE_QRDMX": frozenset(("v8.1a",)),
    "__ARM_FEATURE_SHA2": frozenset(("sha2",)),
    "__ARM_FEATURE_SHA3": frozenset(("sha3",)),
    "__ARM_FEATURE_SHA512": frozenset(("sha3",)),
    "__ARM_FEATURE_SM3": frozenset(("sm4",)),
    "__ARM_FEATURE_SM4": frozenset(("sm4",)),
}

_NEON_FEATURE_EVIDENCE_ERRORS = frozenset(
    {
        "llvm.neon_target_features_ambiguous",
        "llvm.neon_target_features_conflict",
        "tabular.neon_feature_rule_unresolved",
    }
)


def _neon_feature_rule(callable_: ConcreteCallable) -> _NeonFeatureRule:
    """Map the exact pinned section and instruction identity to ACLE macros."""

    spellings = _callable_spellings(callable_)
    mnemonics = {
        item.mnemonic.upper() for item in callable_.instructions if item.mnemonic
    }
    section = callable_.semantics.summary
    has_neon_spelling = any(name.startswith("v") for name in spellings)
    macros: set[str] = set()
    if has_neon_spelling and section != _NEON_SECTION_FP16_SCALAR:
        macros.add("__ARM_NEON")
    target_features = (
        {"neon"}
        if has_neon_spelling and section != _NEON_SECTION_FP16_SCALAR
        else set()
    )
    unresolved_reason: str | None = None

    if section in {_NEON_SECTION_BASIC, _NEON_SECTION_ALWAYS}:
        if mnemonics & {"FAMAX", "FAMIN"}:
            macros.add("__ARM_FEATURE_FAMINMAX")
        if mnemonics & {"LUTI2", "LUTI4"}:
            macros.add("__ARM_FEATURE_LUT")
            if any("_bf16" in name for name in spellings):
                macros.add("__ARM_FEATURE_BF16")
    elif section == _NEON_SECTION_CRYPTO:
        if any(item.startswith("AES") for item in mnemonics) or any(
            name in {"vmull_p64", "vmull_high_p64"} for name in spellings
        ):
            macros.add("__ARM_FEATURE_AES")
        elif any(
            item.startswith("SHA1") or item.startswith("SHA256") for item in mnemonics
        ):
            macros.add("__ARM_FEATURE_SHA2")
    elif section == _NEON_SECTION_CRC:
        macros.add("__ARM_FEATURE_CRC32")
    elif section == _NEON_SECTION_QRDMX:
        macros.add("__ARM_FEATURE_QRDMX")
    elif section == _NEON_SECTION_FP16_SCALAR:
        macros.add("__ARM_FEATURE_FP16_SCALAR_ARITHMETIC")
    elif section == _NEON_SECTION_FP16_VECTOR:
        macros.add("__ARM_FEATURE_FP16_VECTOR_ARITHMETIC")
    elif section == _NEON_SECTION_DOTPROD:
        macros.add("__ARM_FEATURE_DOTPROD")
    elif section == _NEON_SECTION_ARMV84:
        if any(item.startswith("SHA512") for item in mnemonics):
            macros.add("__ARM_FEATURE_SHA512")
        elif mnemonics & {"BCAX", "EOR3", "RAX1", "XAR"}:
            macros.add("__ARM_FEATURE_SHA3")
        elif any(item.startswith("SM3") for item in mnemonics):
            macros.add("__ARM_FEATURE_SM3")
        elif any(item.startswith("SM4") for item in mnemonics):
            macros.add("__ARM_FEATURE_SM4")
        else:
            unresolved_reason = (
                "The pinned Armv8.4 section needs an exact SHA512, SHA3, SM3, or "
                "SM4 instruction identity."
            )
    elif section == _NEON_SECTION_FP16_FML:
        macros.add("__ARM_FEATURE_FP16_FML")
    elif section == _NEON_SECTION_COMPLEX:
        macros.add("__ARM_FEATURE_COMPLEX")
        if any("_f16" in name for name in spellings):
            target_features.add("fullfp16")
    elif section == _NEON_SECTION_FRINT:
        macros.add("__ARM_FEATURE_FRINT")
    elif section == _NEON_SECTION_I8MM:
        macros.add("__ARM_FEATURE_MATMUL_INT8")
    elif section == _NEON_SECTION_BF16:
        macros.add("__ARM_FEATURE_BF16")
        if any(name in {"vcvth_bf16_f32", "vcvtah_f32_bf16"} for name in spellings):
            macros.add("__ARM_FEATURE_BF16_SCALAR_ARITHMETIC")
        elif any(
            item.startswith(prefix)
            for item in mnemonics
            for prefix in ("BFCVTN", "BFDOT", "BFMMLA", "BFMLALB", "BFMLALT")
        ):
            macros.add("__ARM_FEATURE_BF16_VECTOR_ARITHMETIC")
    elif section == _NEON_SECTION_FP8:
        if "FDOT" in mnemonics and any("_f16_mf8" in name for name in spellings):
            macros.add("__ARM_FEATURE_FP8DOT2")
        elif "FDOT" in mnemonics and any("_f32_mf8" in name for name in spellings):
            macros.add("__ARM_FEATURE_FP8DOT4")
        elif any(
            item.startswith("FMLAL") or item.startswith("FMLALL") for item in mnemonics
        ):
            macros.add("__ARM_FEATURE_FP8FMA")
        elif "FDOT" in mnemonics:
            unresolved_reason = (
                "The pinned modal FP8 FDOT row needs an exact f16 or f32 public "
                "spelling."
            )
        else:
            macros.add("__ARM_FEATURE_FP8")
    elif section == _NEON_SECTION_FP8_MM:
        if any("_f16_mf8" in name for name in spellings):
            macros.add("__ARM_FEATURE_F8F16MM")
        elif any("_f32_mf8" in name for name in spellings):
            macros.add("__ARM_FEATURE_F8F32MM")
        else:
            unresolved_reason = (
                "The pinned Armv9.6 matrix section needs an exact f16 or f32 "
                "public spelling."
            )
    elif section == _NEON_SECTION_F16F32DOT:
        macros.add("__ARM_FEATURE_F16F32DOT")
    elif section == _NEON_SECTION_F16F32MM:
        macros.add("__ARM_FEATURE_F16F32MM")
    elif section == _NEON_SECTION_F16MM:
        macros.add("__ARM_FEATURE_F16MM")

    target_features.update(
        target_feature
        for macro in macros
        for target_feature in _NEON_MACRO_TARGET_FEATURES.get(macro, ())
    )
    return _NeonFeatureRule(
        macros=frozenset(macros),
        target_features=frozenset(target_features),
        unresolved_reason=unresolved_reason,
    )


def _apply_llvm_neon_target_features(
    callables: Sequence[ConcreteCallable],
    llvm_callables: Sequence[LLVMCallable],
    *,
    require_complete: bool = True,
) -> list[ConcreteCallable]:
    """Validate exact tabular Neon rules against pinned generated declarations."""

    candidates_by_spelling: dict[str, list[LLVMCallable]] = {}
    for item in llvm_callables:
        if item.family != "neon":
            continue
        for spelling in dict.fromkeys(name.spelling for name in item.names):
            candidates_by_spelling.setdefault(spelling, []).append(item)

    result: list[ConcreteCallable] = []
    for callable_ in callables:
        if "neon" not in callable_.families:
            result.append(callable_)
            continue
        rule = _neon_feature_rule(callable_)
        candidates: list[LLVMCallable] = []
        candidate_ids: set[int] = set()
        for spelling in _callable_spellings(callable_):
            for candidate in candidates_by_spelling.get(spelling, ()):
                if id(candidate) in candidate_ids:
                    continue
                candidates.append(candidate)
                candidate_ids.add(id(candidate))

        error_code: str | None = None
        error_message: str | None = None
        signature_drift_message: str | None = None
        selected: list[LLVMCallable] = []
        if candidates:
            signature_matches = [
                item
                for item in candidates
                if _llvm_neon_signature_key(item)
                == _model_neon_signature_key(callable_)
            ]
            if not signature_matches:
                selected = candidates
                signature_drift_message = (
                    f"Pinned LLVM exposes {len(candidates)} declarations for exact "
                    f"spelling(s) {', '.join(_callable_spellings(callable_))}, but "
                    "none has the exact Arm ACLE tabular signature; target-feature "
                    "evidence is accepted only because every same-spelling wrapper "
                    "records one identical non-empty feature set."
                )
            elif len(signature_matches) > 1:
                selected = signature_matches
                error_code = "llvm.neon_target_features_ambiguous"
                error_message = (
                    f"Pinned LLVM exposes {len(signature_matches)} declarations with "
                    "the same exact public spelling and tabular signature."
                )
            else:
                selected = signature_matches

        missing_exact_declaration = (
            error_code is None and not selected and require_complete
        )
        mismatch_diagnostics = [
            diagnostic
            for item in selected
            for diagnostic in item.diagnostics
            if diagnostic.code == "llvm.target_feature_mismatch"
        ]
        feature_sets = {item.target_features for item in selected}
        if error_code is None and mismatch_diagnostics:
            error_code = "llvm.neon_target_features_ambiguous"
            error_message = mismatch_diagnostics[0].message
        elif (
            error_code is None
            and selected
            and (len(feature_sets) != 1 or not next(iter(feature_sets), ()))
        ):
            rendered = ", ".join(
                "[" + ", ".join(features) + "]" for features in sorted(feature_sets)
            )
            error_code = "llvm.neon_target_features_ambiguous"
            error_message = (
                "Exact LLVM declaration candidates do not provide one non-empty "
                f"target feature set ({rendered or 'none'})."
            )
        elif error_code is None and selected:
            header_features = frozenset(next(iter(feature_sets)))
            if header_features != rule.target_features:
                error_code = "llvm.neon_target_features_conflict"
                error_message = (
                    "Pinned AdvSIMD section/instruction identity requires target "
                    f"features {sorted(rule.target_features)!r}, while the exact "
                    f"LLVM declaration records {sorted(header_features)!r}."
                )

        if error_code is None and rule.unresolved_reason:
            error_code = "tabular.neon_feature_rule_unresolved"
            error_message = rule.unresolved_reason

        if error_code is not None:
            assert error_message is not None
            result.append(
                _neon_feature_evidence_error(
                    callable_,
                    rule,
                    selected,
                    code=error_code,
                    message=error_message,
                )
            )
            continue

        evidence_sources = _unique_sources(
            (
                *callable_.semantics.provenance.sources,
                *(
                    _llvm_neon_source_ref(source)
                    for item in selected
                    for source in item.source_refs
                ),
            )
        )
        diagnostics = callable_.diagnostics
        if signature_drift_message:
            diagnostics = tuple(
                _unique_diagnostics(
                    (
                        *diagnostics,
                        Diagnostic(
                            code="llvm.neon_signature_drift",
                            message=signature_drift_message,
                            severity=DiagnosticSeverity.WARNING,
                            field="signature",
                            sources=evidence_sources,
                        ),
                    )
                )
            )
        if missing_exact_declaration:
            diagnostics = tuple(
                _unique_diagnostics(
                    (
                        *diagnostics,
                        Diagnostic(
                            code="llvm.neon_target_features_missing",
                            message=(
                                "The pinned LLVM Neon inventory has no exact "
                                "public-spelling declaration for this tabular "
                                "callable; the exact pinned AdvSIMD section and "
                                "instruction rule remains authoritative."
                            ),
                            severity=DiagnosticSeverity.WARNING,
                            field="compilation.feature_macros",
                            sources=evidence_sources,
                        ),
                    )
                )
            )
        validation_clause = (
            " and validate the exact public spelling against Clang target attributes"
            if selected
            else ""
        )
        result.append(
            normalize_callable(
                replace(
                    callable_,
                    compilation=replace(
                        callable_.compilation,
                        feature_macros=tuple(
                            sorted(
                                set(callable_.compilation.feature_macros)
                                | set(rule.macros)
                            )
                        ),
                    ),
                    diagnostics=diagnostics,
                    field_provenance=tuple(
                        dict.fromkeys(
                            (
                                *callable_.field_provenance,
                                FieldProvenance(
                                    "compilation.feature_macros",
                                    Provenance(
                                        ProvenanceKind.DERIVED,
                                        evidence_sources,
                                        rule=(
                                            "Match the exact pinned AdvSIMD section "
                                            "and instruction identity"
                                            f"{validation_clause}."
                                        ),
                                    ),
                                ),
                            )
                        )
                    ),
                )
            )
        )
    return result


def _model_neon_signature_key(
    callable_: ConcreteCallable,
) -> tuple[str, tuple[str, ...]]:
    return (
        normalize_c_type(callable_.signature.return_type),
        tuple(
            normalize_c_type(parameter.type_name)
            for parameter in callable_.signature.parameters
        ),
    )


def _llvm_neon_signature_key(
    callable_: LLVMCallable,
) -> tuple[str, tuple[str, ...]]:
    return (
        normalize_c_type(callable_.prototype.return_type),
        tuple(
            normalize_c_type(parameter.type)
            for parameter in callable_.prototype.parameters
        ),
    )


def _llvm_neon_source_ref(source: LLVMSourceRef) -> SourceRef:
    return SourceRef(
        id=f"llvm:{source.commit}:{source.header}:{source.line}:{source.sha256[:12]}",
        repository=source.repository,
        commit=source.commit,
        path=f"lib/clang/22/include/{source.header}",
        start_line=source.line,
        end_line=source.line,
        license_id=source.license,
        url=f"https://github.com/llvm/llvm-project/releases/tag/{source.release_tag}",
    )


def _neon_feature_evidence_error(
    callable_: ConcreteCallable,
    rule: _NeonFeatureRule,
    candidates: Sequence[LLVMCallable],
    *,
    code: str,
    message: str,
) -> ConcreteCallable:
    sources = _unique_sources(
        (
            *callable_.semantics.provenance.sources,
            *(
                _llvm_neon_source_ref(source)
                for candidate in candidates
                for source in candidate.source_refs
            ),
        )
    )
    return normalize_callable(
        replace(
            callable_,
            compilation=replace(
                callable_.compilation,
                feature_macros=tuple(
                    sorted(set(callable_.compilation.feature_macros) | set(rule.macros))
                ),
                compiler_flags=(),
                unresolved_reason=_merge_unresolved_reasons(
                    callable_.compilation.unresolved_reason,
                    f"Neon target-feature evidence is unresolved: {message}",
                ),
            ),
            diagnostics=tuple(
                _unique_diagnostics(
                    (
                        *callable_.diagnostics,
                        Diagnostic(
                            code=code,
                            message=message,
                            severity=DiagnosticSeverity.ERROR,
                            field="compilation.feature_macros",
                            sources=sources,
                        ),
                    )
                )
            ),
        )
    )


def _derived_family_macros(
    callable_: ConcreteCallable,
    *,
    infer_family_macros: bool = True,
) -> set[str]:
    families = set(callable_.families)
    if "neon" in families:
        return (
            set(_neon_feature_rule(callable_).macros) if infer_family_macros else set()
        )
    if not infer_family_macros:
        # Explicit availability is authoritative. Families can also be
        # classification inferred from a feature's implication graph, so
        # converting every classified family back into a global requirement
        # would incorrectly turn source-level OR branches into an AND.
        return set()
    result = set()
    family_macros = {
        "mve": "__ARM_FEATURE_MVE",
        "sve": "__ARM_FEATURE_SVE",
        "sve2": "__ARM_FEATURE_SVE2",
        "sve2.1": "__ARM_FEATURE_SVE2p1",
        "sve2.2": "__ARM_FEATURE_SVE2p2",
        "sve2.3": "__ARM_FEATURE_SVE2p3",
        "sme": "__ARM_FEATURE_SME",
        "sme2": "__ARM_FEATURE_SME2",
        "sme2.1": "__ARM_FEATURE_SME2p1",
        "sme2.2": "__ARM_FEATURE_SME2p2",
        "sme2.3": "__ARM_FEATURE_SME2p3",
    }
    for family in families:
        macro = family_macros.get(family)
        if macro:
            result.add(macro)
    return result


def _targets_for_callable(callable_: ConcreteCallable) -> tuple[str, ...]:
    states = set(callable_.compilation.execution_states)
    if states:
        targets = []
        if "AArch32" in states:
            targets.append("aarch32")
        if "AArch64" in states:
            targets.append("aarch64")
        if targets:
            return tuple(targets)
    families = set(callable_.families)
    if "mve" in families:
        return ("aarch32",)
    if "neon" in families:
        return ("aarch32", "aarch64")
    if any(family.startswith(("sve", "sme")) for family in families):
        return ("aarch64",)
    return ("aarch32", "aarch64")


def _callable_uses_floating_point(callable_: ConcreteCallable) -> bool:
    types = [callable_.signature.return_type]
    types.extend(parameter.type_name for parameter in callable_.signature.parameters)
    return any(
        re.search(r"(?:float|bfloat|fp16|fp32|fp64)", item, re.IGNORECASE)
        for item in types
    )


def _availability_macros(expression: AvailabilityExpr) -> set[str]:
    result: set[str] = set()
    if expression.key and expression.key.startswith("__ARM"):
        result.add(expression.key)
    if expression.text:
        result.update(_FEATURE_MACRO_RE.findall(expression.text))
    for child in expression.arguments:
        result.update(_availability_macros(child))
    return result


def _macros_from_availability_payload(payload: Mapping[str, object]) -> set[str]:
    return set(_FEATURE_MACRO_RE.findall(canonical_json(payload)))


def _patch_source(patch: Mapping[str, object]) -> SourceRef:
    provenance = patch.get("provenance")
    source_data = provenance.get("source") if isinstance(provenance, Mapping) else None
    if not isinstance(source_data, Mapping):
        raise ValueError("ACLE enrichment is missing source provenance")
    start = source_data.get("start_line")
    end = source_data.get("end_line")
    path = str(source_data.get("path") or "main/acle.md")
    return SourceRef(
        id=f"acle:{path}:{start or 1}-{end or start or 1}",
        repository=str(source_data.get("repository") or ACLE_REPOSITORY),
        commit=str(source_data.get("commit") or ACLE_REVISION),
        path=path,
        start_line=start if isinstance(start, int) else None,
        end_line=end if isinstance(end, int) else None,
        license_id=str(source_data.get("license") or ACLE_CONTENT_LICENSE),
        url=f"{ACLE_SOURCE_URL}/{path}",
    )


def _patch_family_matches(callable_: ConcreteCallable, value: object) -> bool:
    if not isinstance(value, Sequence) or isinstance(value, str):
        return True
    broad_families = {_family_root(family) for family in callable_.families}
    return any(
        isinstance(item, str) and _family_root(item) in broad_families for item in value
    )


def _callable_spellings(callable_: ConcreteCallable) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys((callable_.name, *(alias.name for alias in callable_.aliases)))
    )


def _deduplicate_callables(
    callables: Iterable[ConcreteCallable],
) -> list[ConcreteCallable]:
    by_id: dict[str, ConcreteCallable] = {}
    normalized_callables = sorted(
        (normalize_callable(callable_) for callable_ in callables),
        key=lambda callable_: (callable_.id, canonical_json(callable_)),
    )
    for normalized in normalized_callables:
        previous = by_id.get(normalized.id)
        if previous is None:
            by_id[normalized.id] = normalized
            continue
        if canonical_json(previous) == canonical_json(normalized):
            continue
        if _callable_identity_payload(previous) != _callable_identity_payload(
            normalized
        ):
            raise ValueError(f"canonical callable id collision: {normalized.id}")
        conflicts = _equivalent_fact_conflict_diagnostics(previous, normalized)
        merged = _merge_equivalent_declarations(previous, normalized)
        if conflicts:
            merged = normalize_callable(
                replace(
                    merged,
                    diagnostics=tuple(
                        _unique_diagnostics((*merged.diagnostics, *conflicts))
                    ),
                )
            )
        if merged.id != normalized.id:
            raise ValueError(
                "equivalent callable merge changed canonical identity: "
                f"{normalized.id} -> {merged.id}"
            )
        by_id[normalized.id] = merged
    return list(by_id.values())


def _equivalent_fact_conflict_diagnostics(
    left: ConcreteCallable,
    right: ConcreteCallable,
) -> tuple[Diagnostic, ...]:
    """Report conflicting resolved scalars before deterministic source merging."""

    sources = _unique_sources((*left.sources, *right.sources))
    diagnostics: list[Diagnostic] = []
    if (
        left.maturity is not Maturity.UNSPECIFIED
        and right.maturity is not Maturity.UNSPECIFIED
        and left.maturity is not right.maturity
    ):
        values = sorted((left.maturity.value, right.maturity.value))
        diagnostics.append(
            Diagnostic(
                code="pipeline.equivalent_fact_conflict",
                message=(
                    f"Equivalent declarations disagree on maturity ({values[0]} "
                    f"versus {values[1]}); deterministic source ordering selects "
                    "the displayed value."
                ),
                severity=DiagnosticSeverity.WARNING,
                field="maturity",
                sources=sources,
            )
        )
    for field in ("summary", "description", "operation", "result"):
        left_value = getattr(left.semantics, field)
        right_value = getattr(right.semantics, field)
        if left_value and right_value and left_value != right_value:
            diagnostics.append(
                Diagnostic(
                    code="pipeline.equivalent_fact_conflict",
                    message=(
                        f"Equivalent declarations disagree on semantics.{field}; "
                        "deterministic source ordering selects the displayed value."
                    ),
                    severity=DiagnosticSeverity.WARNING,
                    field=f"semantics.{field}",
                    sources=sources,
                )
            )
    return tuple(diagnostics)


def _callable_identity_payload(callable_: ConcreteCallable) -> str:
    """Return the unhashed stable-ID payload for collision-safe comparison."""

    normalized = normalize_callable(callable_)
    return canonical_json(
        {
            "families": normalized.families,
            "kind": normalized.kind,
            "name": normalized.name,
            "name_role": normalized.name_role,
            "name_availability": normalized.name_availability,
            "signature": signature_identity(normalized.signature),
            "availability": normalized.availability,
            "headers": normalized.headers,
        }
    )


def _families_from_callables(
    callables: Sequence[ConcreteCallable],
) -> tuple[Family, ...]:
    result = []
    for key in sorted({family for item in callables for family in item.families}):
        items = [item for item in callables if key in item.families]
        sources = _unique_sources(source for item in items for source in item.sources)
        maturity_values = {item.maturity for item in items}
        maturity = (
            maturity_values.pop() if len(maturity_values) == 1 else Maturity.UNSPECIFIED
        )
        result.append(
            Family(
                key=key,
                title=_FAMILY_TITLES.get(key, key.upper()),
                domains=(key.split(".", 1)[0],),
                headers=tuple(
                    sorted({header for item in items for header in item.headers})
                ),
                summary=f"{len(items):,} normalized source-backed callables.",
                maturity=maturity,
                taxonomy=tuple(
                    dict.fromkeys(path for item in items for path in item.taxonomy)
                ),
                provenance=Provenance(
                    ProvenanceKind.DERIVED,
                    sources,
                    rule="aggregate-canonical-callable-family",
                ),
                sources=sources,
            )
        )
    return tuple(result)


def _markdown_document_diagnostics(parsed: Mapping[str, object]) -> list[Diagnostic]:
    result = []
    for item in cast(Iterable[object], parsed.get("diagnostics", ())):
        if not isinstance(item, Mapping):
            continue
        source_data = item.get("source")
        sources = ()
        if isinstance(source_data, Mapping):
            source = _patch_source({"provenance": {"source": source_data}})
            sources = (source,)
        result.append(
            Diagnostic(
                code=str(item.get("code") or "acle.document"),
                message=str(item.get("message") or "ACLE document diagnostic."),
                severity=DiagnosticSeverity.WARNING,
                sources=sources,
            )
        )
    return result


def _flatten_performance(
    values: Sequence[PerformanceDataset | PerformanceRecord],
) -> tuple[PerformanceRecord, ...]:
    result = []
    for value in values:
        if isinstance(value, PerformanceDataset):
            result.extend(value.records)
        elif isinstance(value, PerformanceRecord):
            result.append(value)
        else:
            raise TypeError(f"unsupported performance data: {type(value).__name__}")
    return tuple(result)


def _unique_sources(values: Iterable[SourceRef]) -> tuple[SourceRef, ...]:
    by_id: dict[str, SourceRef] = {}
    for value in values:
        previous = by_id.setdefault(value.id, value)
        if previous != value:
            raise ValueError(f"source id collision: {value.id}")
    return tuple(by_id[key] for key in sorted(by_id))


def _unique_diagnostics(values: Iterable[Diagnostic]) -> list[Diagnostic]:
    by_key = {}
    for value in values:
        key = (value.code, value.message, value.severity, value.field)
        by_key.setdefault(key, value)
    return [
        by_key[key]
        for key in sorted(by_key, key=lambda item: tuple(str(v) for v in item))
    ]
