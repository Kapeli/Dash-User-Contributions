"""Adapters for the official Neon and MVE intrinsic TSV databases.

The upstream files use a ``.csv`` suffix but are tab-separated.  This module
keeps source facts verbatim and only derives facts that are defined by the
tabular format itself: C prototype components, MVE public spellings, and
classification paths.
"""

from __future__ import annotations

import csv
import re
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Literal

from .. import model as canonical

Family = Literal["neon", "mve"]
NameRole = Literal["typed", "overloaded"]
Namespace = Literal["prefixed", "unprefixed"]

_SPDX_LICENSE = "Apache-2.0"
_USER_NAMESPACE_CONDITION = "!defined(__ARM_MVE_PRESERVE_USER_NAMESPACE)"
_SIGNATURE_RE = re.compile(
    r"^(?P<return_type>.+?)\s+"
    r"(?P<name>(?:\[[^\]\r\n]+\]|[A-Za-z_][A-Za-z0-9_]*?)+)"
    r"\((?P<parameters>.*)\)$"
)
_PARAMETER_NAME_RE = re.compile(
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
    r"(?P<array>(?:\s*\[[^\]]*\])*)\s*$"
)
_BRACKET_RE = re.compile(r"\[([^\]]+)\]")


class TabularFormatError(ValueError):
    """Raised when an upstream TSV row violates the documented structure."""


@dataclass(frozen=True, slots=True)
class SourceRef:
    """A line-addressable reference to one Apache-2.0 upstream data file."""

    path: str
    line: int
    license: str = _SPDX_LICENSE


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """A non-fatal fact that must remain visible to downstream consumers."""

    code: str
    message: str
    source_ref: SourceRef


@dataclass(frozen=True, slots=True)
class Parameter:
    """A conservatively parsed C parameter."""

    raw: str
    type: str
    name: str | None


@dataclass(frozen=True, slots=True)
class Prototype:
    """The raw and parsed forms of an intrinsic declaration."""

    raw: str
    return_type: str
    name_pattern: str
    parameters: tuple[Parameter, ...]


@dataclass(frozen=True, slots=True)
class NameForm:
    """One concrete searchable spelling derived from an upstream name pattern."""

    spelling: str
    role: NameRole
    namespace: Namespace
    availability: str | None


@dataclass(frozen=True, slots=True)
class Section:
    """The nearest preceding ``<SECTION>`` row."""

    title: str
    description: str
    source_ref: SourceRef


@dataclass(frozen=True, slots=True)
class Classification:
    """One taxonomy path associated with an upstream name pattern."""

    path: tuple[str, ...]
    source_ref: SourceRef


@dataclass(frozen=True, slots=True)
class TabularIntrinsic:
    """A loss-minimizing record shared by the Neon and MVE adapters."""

    family: Family
    prototype: Prototype
    names: tuple[NameForm, ...]
    section: Section | None
    classifications: tuple[Classification, ...]
    argument_preparation: str
    instruction: str
    result: str
    supported_architectures: tuple[str, ...]
    supported_architectures_raw: str
    maturity: Literal["Unspecified"]
    features: tuple[str, ...]
    source_ref: SourceRef
    diagnostics: tuple[Diagnostic, ...]

    @property
    def name_pattern(self) -> str:
        return self.prototype.name_pattern

    def as_model_payload(self) -> Mapping[str, object]:
        """Return primitives for a small, explicit model integration boundary."""

        return asdict(self)


@dataclass(frozen=True, slots=True)
class TabularParseResult:
    """Parsed records plus diagnostics not owned by a single intrinsic."""

    intrinsics: tuple[TabularIntrinsic, ...]
    diagnostics: tuple[Diagnostic, ...]


def to_concrete_callables(
    records: Iterable[TabularIntrinsic],
    *,
    repository: str,
    commit: str,
    source_root: Path | None = None,
    source_url_base: str | None = None,
) -> tuple[canonical.ConcreteCallable, ...]:
    """Map tabular records into the canonical source-aware callable model."""

    merged: dict[str, canonical.ConcreteCallable] = {}
    for record in records:
        callable_ = _to_concrete_callable(
            record,
            repository=repository,
            commit=commit,
            source_root=source_root,
            source_url_base=source_url_base,
        )
        existing = merged.get(callable_.id)
        merged[callable_.id] = (
            callable_
            if existing is None
            else _merge_concrete_callables(existing, callable_)
        )
    return tuple(merged.values())


def to_catalog(
    results: Iterable[TabularParseResult],
    *,
    version: str,
    repository: str,
    commit: str,
    source_root: Path | None = None,
    source_url_base: str | None = None,
) -> canonical.Catalog:
    """Combine one or more tabular family results into a canonical catalog."""

    parsed_results = tuple(results)
    callables = to_concrete_callables(
        (record for result in parsed_results for record in result.intrinsics),
        repository=repository,
        commit=commit,
        source_root=source_root,
        source_url_base=source_url_base,
    )

    family_records: dict[Family, list[TabularIntrinsic]] = {}
    for result in parsed_results:
        for record in result.intrinsics:
            family_records.setdefault(record.family, []).append(record)

    families = tuple(
        _to_canonical_family(
            family,
            records,
            repository=repository,
            commit=commit,
            source_root=source_root,
            source_url_base=source_url_base,
        )
        for family, records in sorted(family_records.items())
    )
    global_diagnostics = tuple(
        _to_canonical_diagnostic(
            diagnostic,
            repository=repository,
            commit=commit,
            source_root=source_root,
            source_url_base=source_url_base,
        )
        for result in parsed_results
        for diagnostic in result.diagnostics
    )
    catalog_sources = _unique_canonical_sources(
        source for callable_ in callables for source in callable_.sources
    )
    return canonical.Catalog(
        version=version,
        source_commit=commit,
        families=families,
        callables=callables,
        provenance=canonical.Provenance(
            kind=canonical.ProvenanceKind.DERIVED,
            sources=_file_level_sources(catalog_sources),
            rule="arm-acle-tabular-adapter",
            note="Generated from the official Apache-2.0 Neon and MVE TSV databases.",
        ),
        diagnostics=global_diagnostics,
    )


def load_tabular_sources(
    definitions_path: Path,
    classifications_path: Path,
    *,
    family: Family,
    definitions_source: str | None = None,
    classifications_source: str | None = None,
) -> TabularParseResult:
    """Load and parse one official definition/classification TSV pair."""

    with (
        definitions_path.open(encoding="utf-8", newline="") as definitions,
        classifications_path.open(encoding="utf-8", newline="") as classifications,
    ):
        return parse_tabular_sources(
            definitions,
            classifications,
            family=family,
            definitions_source=definitions_source or str(definitions_path),
            classifications_source=(
                classifications_source or str(classifications_path)
            ),
        )


def parse_tabular_sources(
    definitions: Iterable[str],
    classifications: Iterable[str],
    *,
    family: Family,
    definitions_source: str,
    classifications_source: str,
) -> TabularParseResult:
    """Parse official TSV iterables without inferring maturity or features."""

    if family not in ("neon", "mve"):
        raise ValueError(f"unsupported tabular family: {family!r}")

    classification_map, classification_diagnostics = _parse_classifications(
        classifications,
        source=classifications_source,
    )
    records: list[TabularIntrinsic] = []
    global_diagnostics: list[Diagnostic] = list(classification_diagnostics)
    current_section: Section | None = None
    saw_header = False

    for line, row in _rows(definitions, source=definitions_source):
        marker = row[0]
        source_ref = SourceRef(definitions_source, line)
        if marker == "<COMMENT>":
            continue
        if marker == "<HEADER>":
            _validate_header(row, source_ref)
            saw_header = True
            continue
        if marker == "<SECTION>":
            current_section = _parse_section(row, source_ref)
            continue
        if marker.startswith("<"):
            global_diagnostics.append(
                Diagnostic(
                    code="tabular.unknown_directive",
                    message=f"Ignored unsupported directive {marker!r}.",
                    source_ref=source_ref,
                )
            )
            continue
        if len(row) != 5:
            raise TabularFormatError(
                f"{definitions_source}:{line}: expected 5 definition columns, "
                f"found {len(row)}"
            )

        prototype = parse_prototype(row[0], source_ref=source_ref)
        classifications_for_name = tuple(
            classification_map.get(prototype.name_pattern, ())
        )
        diagnostics = [
            Diagnostic(
                code="tabular.maturity_unspecified",
                message="The tabular source does not specify per-intrinsic maturity.",
                source_ref=source_ref,
            ),
            Diagnostic(
                code="tabular.features_unspecified",
                message="The tabular source does not specify per-intrinsic features.",
                source_ref=source_ref,
            ),
        ]
        if current_section is None:
            diagnostics.append(
                Diagnostic(
                    code="tabular.section_missing",
                    message="No preceding <SECTION> row applies to this intrinsic.",
                    source_ref=source_ref,
                )
            )
        if not classifications_for_name:
            diagnostics.append(
                Diagnostic(
                    code="tabular.classification_missing",
                    message=(
                        "No classification row matches the exact upstream name "
                        f"pattern {prototype.name_pattern!r}."
                    ),
                    source_ref=source_ref,
                )
            )

        architectures_raw = row[4].strip()
        architectures = tuple(
            part.strip() for part in architectures_raw.split("/") if part.strip()
        )
        records.append(
            TabularIntrinsic(
                family=family,
                prototype=prototype,
                names=expand_name_forms(prototype.name_pattern, family=family),
                section=current_section,
                classifications=classifications_for_name,
                argument_preparation=row[1].strip(),
                instruction=row[2].strip(),
                result=row[3].strip(),
                supported_architectures=architectures,
                supported_architectures_raw=architectures_raw,
                maturity="Unspecified",
                features=(),
                source_ref=source_ref,
                diagnostics=tuple(diagnostics),
            )
        )

    if not saw_header:
        source_ref = SourceRef(definitions_source, 1)
        global_diagnostics.append(
            Diagnostic(
                code="tabular.header_missing",
                message="The definition source does not contain a <HEADER> row.",
                source_ref=source_ref,
            )
        )

    return TabularParseResult(tuple(records), tuple(global_diagnostics))


def parse_prototype(raw: str, *, source_ref: SourceRef) -> Prototype:
    """Parse the declaration shape while retaining every source character."""

    signature = raw.strip()
    match = _SIGNATURE_RE.fullmatch(signature)
    if match is None:
        raise TabularFormatError(
            f"{source_ref.path}:{source_ref.line}: cannot parse intrinsic signature "
            f"{signature!r}"
        )

    parameter_text = match.group("parameters").strip()
    parameters = tuple(
        _parse_parameter(parameter)
        for parameter in _split_parameters(parameter_text)
        if parameter.strip() and parameter.strip() != "void"
    )
    return Prototype(
        raw=signature,
        return_type=match.group("return_type").strip(),
        name_pattern=match.group("name"),
        parameters=parameters,
    )


def expand_name_forms(name_pattern: str, *, family: Family) -> tuple[NameForm, ...]:
    """Expand only the public-name rules explicitly encoded by the source."""

    if family == "neon":
        if "[" in name_pattern or "]" in name_pattern:
            raise TabularFormatError(
                f"Neon name patterns must be concrete, found {name_pattern!r}"
            )
        return (
            NameForm(
                spelling=name_pattern,
                role="typed",
                namespace="unprefixed",
                availability=None,
            ),
        )

    prefix = "[__arm_]"
    has_optional_prefix = name_pattern.startswith(prefix)
    polymorphic_pattern = (
        name_pattern[len(prefix) :] if has_optional_prefix else name_pattern
    )
    bracket_groups = tuple(_BRACKET_RE.findall(polymorphic_pattern))
    typed = _BRACKET_RE.sub(lambda match: match.group(1), polymorphic_pattern)
    overloaded = _BRACKET_RE.sub("", polymorphic_pattern)

    namespaces: tuple[tuple[Namespace, str, str | None], ...]
    if has_optional_prefix:
        namespaces = (
            ("prefixed", "__arm_", None),
            ("unprefixed", "", _USER_NAMESPACE_CONDITION),
        )
    else:
        namespaces = (("unprefixed", "", None),)

    forms: list[NameForm] = []
    for namespace, namespace_prefix, availability in namespaces:
        forms.append(
            NameForm(
                spelling=f"{namespace_prefix}{typed}",
                role="typed",
                namespace=namespace,
                availability=availability,
            )
        )
        if bracket_groups and overloaded != typed:
            forms.append(
                NameForm(
                    spelling=f"{namespace_prefix}{overloaded}",
                    role="overloaded",
                    namespace=namespace,
                    availability=availability,
                )
            )

    return tuple(forms)


def _to_concrete_callable(
    record: TabularIntrinsic,
    *,
    repository: str,
    commit: str,
    source_root: Path | None,
    source_url_base: str | None,
) -> canonical.ConcreteCallable:
    definition_source = _to_canonical_source(
        record.source_ref,
        repository=repository,
        commit=commit,
        source_root=source_root,
        source_url_base=source_url_base,
    )
    section_source = (
        _to_canonical_source(
            record.section.source_ref,
            repository=repository,
            commit=commit,
            source_root=source_root,
            source_url_base=source_url_base,
        )
        if record.section is not None
        else None
    )
    classification_sources = tuple(
        _to_canonical_source(
            classification.source_ref,
            repository=repository,
            commit=commit,
            source_root=source_root,
            source_url_base=source_url_base,
        )
        for classification in record.classifications
    )
    sources = _unique_canonical_sources(
        source
        for source in (definition_source, section_source, *classification_sources)
        if source is not None
    )
    explicit = canonical.Provenance(
        kind=canonical.ProvenanceKind.EXPLICIT,
        sources=(definition_source,),
    )
    name_provenance = canonical.Provenance(
        kind=(
            canonical.ProvenanceKind.EXPLICIT
            if record.family == "neon"
            else canonical.ProvenanceKind.EXPANDED
        ),
        sources=(definition_source,),
        rule=None if record.family == "neon" else "mve-bracket-and-namespace-expansion",
    )

    primary = next(
        (
            form
            for form in record.names
            if form.role == "typed" and form.namespace == "unprefixed"
        ),
        record.names[0],
    )
    aliases = tuple(
        canonical.Alias(
            name=form.spelling,
            role=_to_canonical_name_role(form),
            availability=_to_name_availability(form.availability),
            provenance=name_provenance,
        )
        for form in record.names
        if form != primary
    )
    signature = canonical.Signature(
        return_type=record.prototype.return_type,
        parameters=tuple(
            canonical.Parameter(name=parameter.name, type_name=parameter.type)
            for parameter in record.prototype.parameters
        ),
        raw=record.prototype.raw,
    )
    availability = (
        canonical.AvailabilityExpr.raw(record.supported_architectures_raw)
        if record.supported_architectures_raw
        else canonical.AvailabilityExpr.always()
    )
    semantics_sources = tuple(
        source for source in (definition_source, section_source) if source is not None
    )
    semantics = canonical.Semantics(
        summary=record.section.title if record.section is not None else None,
        description=(
            record.section.description
            if record.section is not None and record.section.description
            else None
        ),
        operation=record.argument_preparation or None,
        result=record.result or None,
        notes=(
            f"Supported architectures (verbatim): {record.supported_architectures_raw}",
        ),
        provenance=canonical.Provenance(
            kind=canonical.ProvenanceKind.EXPLICIT,
            sources=semantics_sources,
            note="Section context is inherited from the nearest preceding <SECTION> row.",
        ),
    )
    instructions = _to_instruction_mappings(
        record,
        provenance=explicit,
    )
    header = "arm_neon.h" if record.family == "neon" else "arm_mve.h"
    execution_states = tuple(
        state
        for marker, state in (("A32", "AArch32"), ("A64", "AArch64"))
        if marker in record.supported_architectures
    )
    unresolved_compilation = canonical.Provenance(
        kind=canonical.ProvenanceKind.UNRESOLVED,
        sources=(definition_source,),
        note=(
            "Architecture labels are explicit, but the tabular source does not provide "
            "complete per-intrinsic feature requirements."
        ),
    )
    diagnostics = tuple(
        _to_canonical_diagnostic(
            diagnostic,
            repository=repository,
            commit=commit,
            source_root=source_root,
            source_url_base=source_url_base,
        )
        for diagnostic in record.diagnostics
    )
    taxonomy_provenance = canonical.Provenance(
        kind=(
            canonical.ProvenanceKind.EXPLICIT
            if classification_sources
            else canonical.ProvenanceKind.UNRESOLVED
        ),
        sources=classification_sources,
    )
    return canonical.ConcreteCallable(
        family=record.family,
        name=primary.spelling,
        name_role=canonical.NameRole.TYPED,
        name_availability=_to_name_availability(primary.availability),
        signature=signature,
        aliases=aliases,
        availability=availability,
        maturity=canonical.Maturity.UNSPECIFIED,
        semantics=semantics,
        instructions=instructions,
        compilation=canonical.CompilationRequirements(
            headers=(header,),
            execution_states=execution_states,
            availability=availability,
            provenance=unresolved_compilation,
            unresolved_reason=(
                "The official tabular source does not specify complete per-intrinsic "
                "feature requirements."
            ),
        ),
        headers=(header,),
        taxonomy=tuple(
            classification.path for classification in record.classifications
        ),
        sources=sources,
        field_provenance=(
            canonical.FieldProvenance("name", name_provenance),
            canonical.FieldProvenance("signature", explicit),
            canonical.FieldProvenance("aliases", name_provenance),
            canonical.FieldProvenance("availability", explicit),
            canonical.FieldProvenance(
                "maturity",
                canonical.Provenance(
                    kind=canonical.ProvenanceKind.UNRESOLVED,
                    sources=(definition_source,),
                    note="No per-intrinsic maturity field exists in the tabular source.",
                ),
            ),
            canonical.FieldProvenance(
                "semantics",
                semantics.provenance,
            ),
            canonical.FieldProvenance("instructions", explicit),
            canonical.FieldProvenance(
                "compilation",
                unresolved_compilation,
            ),
            canonical.FieldProvenance(
                "headers",
                canonical.Provenance(
                    kind=canonical.ProvenanceKind.DERIVED,
                    sources=(definition_source,),
                    rule="tabular-family-header",
                ),
            ),
            canonical.FieldProvenance("taxonomy", taxonomy_provenance),
        ),
        diagnostics=diagnostics,
    )


def _merge_concrete_callables(
    left: canonical.ConcreteCallable,
    right: canonical.ConcreteCallable,
) -> canonical.ConcreteCallable:
    """Merge upstream rows that describe alternatives for one callable identity."""

    if left.id != right.id:
        raise ValueError("cannot merge different canonical callable identities")

    aliases: dict[
        tuple[str, canonical.NameRole, canonical.AvailabilityExpr | None],
        canonical.Alias,
    ] = {}
    for alias in (*left.aliases, *right.aliases):
        key = (alias.name, alias.role, alias.availability)
        existing = aliases.get(key)
        aliases[key] = (
            alias
            if existing is None
            else replace(
                existing,
                provenance=_merge_provenance(
                    existing.provenance,
                    alias.provenance,
                ),
            )
        )

    semantics = canonical.Semantics(
        summary=_merge_optional_text(left.semantics.summary, right.semantics.summary),
        description=_merge_optional_text(
            left.semantics.description,
            right.semantics.description,
        ),
        operation=_merge_optional_text(
            left.semantics.operation,
            right.semantics.operation,
            separator="\n",
        ),
        result=_merge_optional_text(
            left.semantics.result,
            right.semantics.result,
            separator="\n",
        ),
        parameters=tuple(
            dict.fromkeys((*left.semantics.parameters, *right.semantics.parameters))
        ),
        constraints=tuple(
            dict.fromkeys((*left.semantics.constraints, *right.semantics.constraints))
        ),
        notes=tuple(dict.fromkeys((*left.semantics.notes, *right.semantics.notes))),
        provenance=_merge_provenance(
            left.semantics.provenance,
            right.semantics.provenance,
        ),
    )
    compilation = replace(
        left.compilation,
        provenance=_merge_provenance(
            left.compilation.provenance,
            right.compilation.provenance,
        ),
    )
    field_provenance: dict[str, canonical.Provenance] = {}
    for item in (*left.field_provenance, *right.field_provenance):
        existing = field_provenance.get(item.field)
        field_provenance[item.field] = (
            item.provenance
            if existing is None
            else _merge_provenance(existing, item.provenance)
        )

    merged = replace(
        left,
        aliases=tuple(aliases.values()),
        semantics=semantics,
        instructions=tuple(dict.fromkeys((*left.instructions, *right.instructions))),
        compilation=compilation,
        taxonomy=tuple(dict.fromkeys((*left.taxonomy, *right.taxonomy))),
        sources=_unique_canonical_sources((*left.sources, *right.sources)),
        field_provenance=tuple(
            canonical.FieldProvenance(field, provenance)
            for field, provenance in field_provenance.items()
        ),
        diagnostics=tuple(dict.fromkeys((*left.diagnostics, *right.diagnostics))),
    )
    if merged.id != left.id:
        raise AssertionError(
            "merging non-identity fields changed the callable identity"
        )
    return merged


def _merge_provenance(
    left: canonical.Provenance,
    right: canonical.Provenance,
) -> canonical.Provenance:
    kind = left.kind if left.kind is right.kind else canonical.ProvenanceKind.DERIVED
    return canonical.Provenance(
        kind=kind,
        sources=_unique_canonical_sources((*left.sources, *right.sources)),
        rule=_merge_optional_text(left.rule, right.rule, separator="; "),
        note=_merge_optional_text(left.note, right.note),
    )


def _merge_optional_text(
    left: str | None,
    right: str | None,
    *,
    separator: str = "\n\n",
) -> str | None:
    values = tuple(dict.fromkeys(value for value in (left, right) if value))
    return separator.join(values) if values else None


def _to_instruction_mappings(
    record: TabularIntrinsic,
    *,
    provenance: canonical.Provenance,
) -> tuple[canonical.InstructionMapping, ...]:
    forms = tuple(
        part.strip() for part in record.instruction.split(";") if part.strip()
    )
    mappings: list[canonical.InstructionMapping] = []
    for index, form in enumerate(forms):
        mnemonic_match = re.match(r"[A-Za-z0-9_.]+", form)
        mappings.append(
            canonical.InstructionMapping(
                relation=canonical.InstructionRelationKind.DIRECT_ACCESS,
                mnemonic=mnemonic_match.group(0)
                if mnemonic_match is not None
                else None,
                instruction_set="Advanced SIMD" if record.family == "neon" else "MVE",
                form=form,
                argument_mapping=record.argument_preparation if index == 0 else None,
                result_mapping=record.result if index == len(forms) - 1 else None,
                sequence_index=index,
                guaranteed_emission=False,
                provenance=provenance,
            )
        )
    return tuple(mappings)


def _to_canonical_family(
    family: Family,
    records: Iterable[TabularIntrinsic],
    *,
    repository: str,
    commit: str,
    source_root: Path | None,
    source_url_base: str | None,
) -> canonical.Family:
    materialized_records = tuple(records)
    header = "arm_neon.h" if family == "neon" else "arm_mve.h"
    title = "Advanced SIMD (Neon)" if family == "neon" else "M-profile Vector Extension"
    sources = _file_level_sources(
        _unique_canonical_sources(
            source
            for record in materialized_records
            for source in (
                _to_canonical_source(
                    record.source_ref,
                    repository=repository,
                    commit=commit,
                    source_root=source_root,
                    source_url_base=source_url_base,
                ),
                *(
                    _to_canonical_source(
                        classification.source_ref,
                        repository=repository,
                        commit=commit,
                        source_root=source_root,
                        source_url_base=source_url_base,
                    )
                    for classification in record.classifications
                ),
            )
        )
    )
    taxonomy = tuple(
        dict.fromkeys(
            classification.path
            for record in materialized_records
            for classification in record.classifications
        )
    )
    return canonical.Family(
        key=family,
        title=title,
        domains=(family,),
        headers=(header,),
        summary=f"Official ACLE tabular intrinsic definitions for {title}.",
        maturity=canonical.Maturity.UNSPECIFIED,
        taxonomy=taxonomy,
        provenance=canonical.Provenance(
            kind=canonical.ProvenanceKind.DERIVED,
            sources=sources,
            rule="arm-acle-tabular-adapter",
        ),
        sources=sources,
    )


def _to_canonical_name_role(form: NameForm) -> canonical.NameRole:
    if form.role == "overloaded":
        return canonical.NameRole.OVERLOADED
    if form.namespace == "prefixed":
        return canonical.NameRole.PREFIXED
    return canonical.NameRole.UNPREFIXED


def _to_name_availability(value: str | None) -> canonical.AvailabilityExpr | None:
    if value is None:
        return None
    if value == _USER_NAMESPACE_CONDITION:
        return canonical.AvailabilityExpr.not_(
            canonical.AvailabilityExpr.defined("__ARM_MVE_PRESERVE_USER_NAMESPACE")
        )
    return canonical.AvailabilityExpr.raw(value)


def _to_canonical_diagnostic(
    diagnostic: Diagnostic,
    *,
    repository: str,
    commit: str,
    source_root: Path | None,
    source_url_base: str | None,
) -> canonical.Diagnostic:
    return canonical.Diagnostic(
        code=diagnostic.code,
        message=diagnostic.message,
        severity=canonical.DiagnosticSeverity.WARNING,
        sources=(
            _to_canonical_source(
                diagnostic.source_ref,
                repository=repository,
                commit=commit,
                source_root=source_root,
                source_url_base=source_url_base,
            ),
        ),
    )


def _to_canonical_source(
    source: SourceRef,
    *,
    repository: str,
    commit: str,
    source_root: Path | None,
    source_url_base: str | None,
) -> canonical.SourceRef:
    path = _source_path(source.path, source_root=source_root)
    base = source_url_base or f"https://github.com/{repository}/blob/{commit}"
    url = f"{base.rstrip('/')}/{path}#L{source.line}"
    return canonical.SourceRef(
        id=f"{repository}@{commit}:{path}:{source.line}",
        repository=repository,
        commit=commit,
        path=path,
        start_line=source.line,
        end_line=source.line,
        license_id=source.license,
        url=url,
    )


def _source_path(value: str, *, source_root: Path | None) -> str:
    path = Path(value)
    if source_root is not None:
        try:
            return path.resolve().relative_to(source_root.resolve()).as_posix()
        except ValueError:
            pass
    return path.as_posix()


def _unique_canonical_sources(
    sources: Iterable[canonical.SourceRef],
) -> tuple[canonical.SourceRef, ...]:
    unique: dict[str, canonical.SourceRef] = {}
    for source in sources:
        unique.setdefault(source.id, source)
    return tuple(unique.values())


def _file_level_sources(
    sources: Iterable[canonical.SourceRef],
) -> tuple[canonical.SourceRef, ...]:
    unique: dict[tuple[str, str, str], canonical.SourceRef] = {}
    for source in sources:
        key = (source.repository, source.commit, source.path)
        unique.setdefault(
            key,
            canonical.SourceRef(
                id=f"{source.repository}@{source.commit}:{source.path}",
                repository=source.repository,
                commit=source.commit,
                path=source.path,
                license_id=source.license_id,
                url=source.url.rsplit("#L", 1)[0] if source.url else None,
            ),
        )
    return tuple(unique.values())


def _parse_classifications(
    classifications: Iterable[str],
    *,
    source: str,
) -> tuple[dict[str, list[Classification]], tuple[Diagnostic, ...]]:
    result: dict[str, list[Classification]] = {}
    diagnostics: list[Diagnostic] = []
    for line, row in _rows(classifications, source=source):
        marker = row[0]
        source_ref = SourceRef(source, line)
        if marker == "<COMMENT>" or marker == "<HEADER>":
            continue
        if marker.startswith("<"):
            diagnostics.append(
                Diagnostic(
                    code="tabular.classification_unknown_directive",
                    message=f"Ignored unsupported classification directive {marker!r}.",
                    source_ref=source_ref,
                )
            )
            continue
        if len(row) != 2:
            raise TabularFormatError(
                f"{source}:{line}: expected 2 classification columns, found {len(row)}"
            )
        path = tuple(part.strip() for part in row[1].split("|") if part.strip())
        if not path:
            diagnostics.append(
                Diagnostic(
                    code="tabular.classification_empty",
                    message=f"Ignored empty classification for {marker!r}.",
                    source_ref=source_ref,
                )
            )
            continue
        result.setdefault(marker, []).append(Classification(path, source_ref))
    return result, tuple(diagnostics)


def _rows(lines: Iterable[str], *, source: str) -> Iterator[tuple[int, list[str]]]:
    reader = csv.reader(lines, delimiter="\t", strict=True)
    try:
        for row in reader:
            if not row or all(not cell.strip() for cell in row):
                continue
            yield reader.line_num, row
    except csv.Error as error:
        raise TabularFormatError(f"{source}:{reader.line_num}: {error}") from error


def _validate_header(row: list[str], source_ref: SourceRef) -> None:
    if len(row) != 6:
        raise TabularFormatError(
            f"{source_ref.path}:{source_ref.line}: expected <HEADER> plus 5 columns, "
            f"found {len(row)} fields"
        )
    normalized = tuple(field.strip().lower() for field in row[1:])
    if normalized[0] != "intrinsic" or normalized[-1] != "supported architectures":
        raise TabularFormatError(
            f"{source_ref.path}:{source_ref.line}: unsupported definition header {row[1:]!r}"
        )


def _parse_section(row: list[str], source_ref: SourceRef) -> Section:
    if len(row) not in (2, 3):
        raise TabularFormatError(
            f"{source_ref.path}:{source_ref.line}: expected a section title and optional "
            f"description, found {len(row) - 1} values"
        )
    return Section(
        title=row[1].strip(),
        description=row[2].strip() if len(row) == 3 else "",
        source_ref=source_ref,
    )


def _split_parameters(parameters: str) -> Iterator[str]:
    if not parameters:
        return
    start = 0
    nesting = 0
    for index, character in enumerate(parameters):
        if character in "([":
            nesting += 1
        elif character in ")]":
            nesting -= 1
        elif character == "," and nesting == 0:
            yield parameters[start:index].strip()
            start = index + 1
    if nesting != 0:
        raise TabularFormatError(f"unbalanced parameter list {parameters!r}")
    yield parameters[start:].strip()


def _parse_parameter(raw: str) -> Parameter:
    parameter = raw.strip()
    match = _PARAMETER_NAME_RE.search(parameter)
    if match is None:
        return Parameter(raw=parameter, type=parameter, name=None)
    type_prefix = parameter[: match.start()].rstrip()
    if not type_prefix:
        return Parameter(raw=parameter, type=parameter, name=None)
    array_suffix = match.group("array").replace(" ", "")
    parameter_type = f"{type_prefix}{array_suffix}" if array_suffix else type_prefix
    return Parameter(raw=parameter, type=parameter_type, name=match.group("name"))


__all__ = [
    "Classification",
    "Diagnostic",
    "NameForm",
    "Parameter",
    "Prototype",
    "Section",
    "SourceRef",
    "TabularFormatError",
    "TabularIntrinsic",
    "TabularParseResult",
    "expand_name_forms",
    "load_tabular_sources",
    "parse_prototype",
    "parse_tabular_sources",
    "to_catalog",
    "to_concrete_callables",
]
