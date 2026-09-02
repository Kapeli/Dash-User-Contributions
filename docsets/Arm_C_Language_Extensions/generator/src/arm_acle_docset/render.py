"""Render canonical ACLE callables as static, Dash-friendly HTML pages."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
import shutil
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markdown_it import MarkdownIt
from markdown_it.token import Token
from markupsafe import Markup

from .model import (
    AvailabilityExpr,
    AvailabilityOp,
    CallableKind,
    ConcreteCallable,
    Constraint,
    Diagnostic,
    PerformanceMetric,
    PerformanceRecord,
    Provenance,
    SourceRef,
)
from .provenance import collect_callable_sources


_DEFAULT_TEMPLATE_DIRECTORY = Path(__file__).resolve().parents[2] / "templates"
_DEFAULT_PERFORMANCE_REASON = (
    "No public, source-pinned microarchitecture data is available for this "
    "callable. No latency, throughput, or execution-resource value is inferred."
)
_DEFAULT_FLAG_REASON = (
    "No pinned GCC or Clang flag example is available for this callable's "
    "architecture context. Consult the compiler documentation for the selected "
    "target CPU and toolchain version."
)
_STANDARD_PERFORMANCE_METRIC_NOTES = frozenset(
    {
        "Compiler scheduling model estimate; not measured hardware behavior.",
        "LLVM scheduling model estimate; not measured hardware behavior.",
        "LLVM scheduling model estimate, not measured hardware data.",
    }
)


@dataclass(frozen=True, slots=True)
class IndexEntry:
    """One Dash search-index entry for a rendered page."""

    name: str
    type: str
    path: str


@dataclass(frozen=True, slots=True)
class RenderedPage:
    """A rendered file and the search entries that resolve to it."""

    relative_path: str
    html: str
    index_entries: tuple[IndexEntry, ...]


class DashRenderer:
    """Render the canonical IR without network access or client-side JavaScript."""

    def __init__(self, template_directory: Path | str | None = None) -> None:
        self.template_directory = Path(
            template_directory or _DEFAULT_TEMPLATE_DIRECTORY
        )
        self.environment = Environment(
            loader=FileSystemLoader(self.template_directory),
            autoescape=True,
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.markdown = MarkdownIt(
            "commonmark",
            {"html": False, "linkify": False, "typographer": False},
        ).enable("table")

    def render_callable(self, callable_: ConcreteCallable) -> RenderedPage:
        """Render one concrete signature to one stable page."""

        relative_path = f"intrinsics/{callable_.slug}.html"
        index_entries = self._index_entries(callable_, relative_path)
        context = self._callable_context(callable_, index_entries)
        html = self.environment.get_template("intrinsic.html.j2").render(context)
        return RenderedPage(relative_path, html, index_entries)

    def render_index(
        self,
        callables: Iterable[ConcreteCallable],
        *,
        version: str | None = None,
        source_revision: str | None = None,
        catalog_diagnostics: Iterable[Diagnostic] = (),
    ) -> RenderedPage:
        """Render the offline landing and attribution page."""

        items = tuple(callables)
        family_counts = Counter(item.family for item in items)
        maturity_counts = Counter(_enum_text(item.maturity) for item in items)
        diagnostic_counts = Counter(
            _enum_text(diagnostic.severity)
            for item in items
            for diagnostic in item.diagnostics
        )
        diagnostic_counts.update(
            _enum_text(diagnostic.severity) for diagnostic in catalog_diagnostics
        )
        source_revisions = sorted(
            {
                source.commit
                for item in items
                for source in collect_callable_sources(item)
                if source.commit
            }
        )
        html = self.environment.get_template("landing.html.j2").render(
            title="Arm C Language Extensions",
            version=version or "Pinned source revision",
            source_revision=source_revision,
            source_revisions=source_revisions,
            callable_count=len(items),
            family_counts=sorted(
                family_counts.items(), key=lambda item: item[0].lower()
            ),
            maturity_counts=[
                {
                    "key": key,
                    "label": _display_enum(key),
                    "count": maturity_counts.get(key, 0),
                }
                for key in ("release", "beta", "alpha", "unspecified")
            ],
            diagnostic_counts=sorted(diagnostic_counts.items()),
        )
        entry = IndexEntry("Arm C Language Extensions", "Guide", "index.html")
        return RenderedPage("index.html", html, (entry,))

    def write_assets(self, documents_directory: Path | str) -> tuple[Path, ...]:
        """Copy static assets beneath a docset's ``Documents`` directory."""

        destination_directory = Path(documents_directory) / "assets"
        destination_directory.mkdir(parents=True, exist_ok=True)
        destination = destination_directory / "style.css"
        shutil.copyfile(self.template_directory / "style.css", destination)
        return (destination,)

    def render_to_directory(
        self,
        callables: Iterable[ConcreteCallable],
        documents_directory: Path | str,
        *,
        version: str | None = None,
        source_revision: str | None = None,
    ) -> tuple[RenderedPage, ...]:
        """Deterministically render a complete set of pages and local assets."""

        destination = Path(documents_directory)
        destination.mkdir(parents=True, exist_ok=True)
        items = tuple(sorted(callables, key=lambda item: (item.slug, item.id)))
        pages = [
            self.render_index(
                items,
                version=version,
                source_revision=source_revision,
            )
        ]
        pages.extend(self.render_callable(item) for item in items)

        seen_paths: set[str] = set()
        for page in pages:
            if page.relative_path in seen_paths:
                raise ValueError(f"duplicate rendered path: {page.relative_path}")
            seen_paths.add(page.relative_path)
            output = destination / page.relative_path
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(page.html, encoding="utf-8", newline="\n")
        self.write_assets(destination)
        return tuple(pages)

    def _callable_context(
        self,
        callable_: ConcreteCallable,
        index_entries: Sequence[IndexEntry],
    ) -> dict[str, object]:
        semantics = callable_.semantics
        parameters = _parameter_rows(callable_)
        instructions = _instruction_rows(callable_)
        sources = _source_rows(collect_callable_sources(callable_))
        families = _families(callable_)
        result = semantics.result
        if not result:
            if callable_.signature.return_type.strip() == "void":
                result = "This callable does not return a value."
            else:
                result = "No source-backed result description is available."

        return {
            "name": callable_.name,
            "page_description": semantics.summary
            or f"Reference for the {callable_.name} ACLE callable.",
            "is_type": callable_.kind is CallableKind.TYPE,
            "callable_kind": _display_enum(_enum_text(callable_.kind)),
            "family_label": " / ".join(families),
            "families": families,
            "maturity": _maturity_context(callable_.maturity),
            "signature": (
                callable_.signature.raw
                if callable_.kind is CallableKind.TYPE and callable_.signature.raw
                else callable_.signature.render(callable_.name)
            ),
            "dash_anchors": [
                {"name": _dash_anchor(entry.type, entry.name)}
                for entry in index_entries
            ],
            "diagnostics": [_diagnostic_row(item) for item in callable_.diagnostics],
            "compilation": _compilation_context(callable_),
            "parameters": parameters,
            "parameters_reason": (
                "This callable takes no parameters."
                if not callable_.signature.parameters
                else "No source-backed parameter information is available."
            ),
            "semantics": {
                "summary": semantics.summary,
                "description": self._render_markdown(semantics.description),
                "operation": semantics.operation,
                "notes": tuple(semantics.notes),
            },
            "state_access": [
                {
                    "state": item.state,
                    "mode": _display_enum(_enum_text(item.mode)),
                    "details": _format_provenance(item.provenance),
                }
                for item in callable_.state_access
            ],
            "result": result,
            "instructions": instructions,
            "instruction_disclaimer": _instruction_disclaimer(callable_),
            "instruction_reason": _instruction_reason(callable_),
            "performance": _performance_context(callable_.performance),
            "constraints": _constraints(callable_),
            "aliases": [
                {
                    "name": alias.name,
                    "role": _display_enum(_enum_text(alias.role)),
                    "availability": (
                        _format_availability(alias.availability)
                        if alias.availability is not None
                        else "Same as the concrete callable"
                    ),
                    "provenance": _format_provenance(alias.provenance),
                }
                for alias in callable_.aliases
            ],
            "related": tuple(callable_.related),
            "sources": sources,
            "provenance": _field_provenance_rows(callable_),
        }

    def _render_markdown(self, text: str | None) -> Markup:
        if not text:
            return Markup("")
        tokens = self.markdown.parse(text)
        for token in tokens:
            if token.type in {"heading_open", "heading_close"}:
                level = min(int(token.tag.removeprefix("h")) + 2, 6)
                token.tag = f"h{level}"
        tokens = _without_fragment_only_links(tokens)
        return Markup(self.markdown.renderer.render(tokens, self.markdown.options, {}))

    @staticmethod
    def _index_entries(
        callable_: ConcreteCallable,
        relative_path: str,
    ) -> tuple[IndexEntry, ...]:
        callable_type = _dash_type(callable_.kind)
        entries: list[IndexEntry] = [
            IndexEntry(callable_.name, callable_type, relative_path)
        ]
        entries.extend(
            IndexEntry(alias.name, callable_type, relative_path)
            for alias in callable_.aliases
        )
        entries.extend(
            IndexEntry(mapping.mnemonic, "Instruction", relative_path)
            for mapping in callable_.instructions
            if mapping.mnemonic
        )
        deduplicated: list[IndexEntry] = []
        seen: set[tuple[str, str, str]] = set()
        for entry in entries:
            key = (entry.name, entry.type, entry.path)
            if key not in seen:
                seen.add(key)
                deduplicated.append(entry)
        return tuple(deduplicated)


def render_callable(callable_: ConcreteCallable) -> RenderedPage:
    """Convenience entrypoint using the bundled templates."""

    return DashRenderer().render_callable(callable_)


def _without_fragment_only_links(tokens: Sequence[Token]) -> list[Token]:
    """Remove broken local link wrappers while preserving their inline content."""

    filtered: list[Token] = []
    fragment_only_stack: list[bool] = []
    for token in tokens:
        if token.children is not None:
            token.children = _without_fragment_only_links(token.children)

        if token.type == "link_open":
            href = token.attrGet("href")
            is_fragment_only = isinstance(href, str) and href.startswith("#")
            fragment_only_stack.append(is_fragment_only)
            if is_fragment_only:
                continue
        elif token.type == "link_close":
            is_fragment_only = (
                fragment_only_stack.pop() if fragment_only_stack else False
            )
            if is_fragment_only:
                continue

        filtered.append(token)
    return filtered


def _enum_text(value: object) -> str:
    raw = getattr(value, "value", value)
    return str(raw)


def _display_enum(value: str) -> str:
    return value.replace("_", " ").strip().title()


def _maturity_context(value: object) -> dict[str, str]:
    key = _enum_text(value).lower()
    if key not in {"release", "beta", "alpha", "unspecified"}:
        key = "unspecified"
    return {"label": _display_enum(key), "css_class": key}


def _dash_type(kind: CallableKind) -> str:
    return {
        CallableKind.INTRINSIC: "Function",
        CallableKind.SUPPORT_FUNCTION: "Function",
        CallableKind.MACRO: "Macro",
        CallableKind.TYPE: "Type",
        CallableKind.MAPPING_ONLY: "Guide",
        CallableKind.NO_INTRINSIC: "Guide",
    }.get(kind, "Function")


def _dash_anchor(entry_type: str, name: str) -> str:
    encoded_name = quote(name, safe="._-")
    return f"//apple_ref/cpp/{entry_type}/{encoded_name}"


def _families(callable_: ConcreteCallable) -> tuple[str, ...]:
    values = list(callable_.families)
    for path in callable_.taxonomy:
        if path:
            values.append(" › ".join(path))
    return _deduplicate_text(values)


def _format_availability(expression: AvailabilityExpr | None) -> str:
    if expression is None:
        return "Not resolved from the pinned sources."
    op = expression.op
    if op is AvailabilityOp.ALWAYS:
        return "Always available when the documented header and target are valid"
    if op is AvailabilityOp.DEFINED:
        return f"defined({expression.key})"
    if op is AvailabilityOp.COMPARE:
        return f"{expression.key} {expression.comparator} {expression.value}"
    if op is AvailabilityOp.RAW:
        return expression.text or "Unresolved raw condition"
    if op is AvailabilityOp.PROFILE:
        return f"profile in {_format_value(expression.value)}"
    if op is AvailabilityOp.EXECUTION_STATE:
        return f"execution state is {_format_value(expression.value)}"
    if op is AvailabilityOp.ARCHITECTURE_MIN:
        return f"architecture >= {_format_value(expression.value)}"
    if op is AvailabilityOp.CALLING_CONTEXT:
        return f"calling context is {_format_value(expression.value)}"
    if op is AvailabilityOp.NOT:
        return f"not ({_format_availability(expression.arguments[0])})"
    if op in {AvailabilityOp.ALL, AvailabilityOp.ANY}:
        joiner = " and " if op is AvailabilityOp.ALL else " or "
        return joiner.join(
            f"({_format_availability(argument)})" for argument in expression.arguments
        )
    return expression.text or "Not resolved from the pinned sources."


def _format_value(value: object) -> str:
    if isinstance(value, tuple):
        return ", ".join(str(item) for item in value)
    return str(value) if value is not None else "unspecified"


def _compilation_context(callable_: ConcreteCallable) -> dict[str, object]:
    compilation = callable_.compilation
    headers = _deduplicate_text((*callable_.headers, *compilation.headers))
    callable_availability = _format_availability(callable_.availability)
    compilation_availability = _format_availability(compilation.availability)
    availability = callable_availability
    if (
        callable_availability != compilation_availability
        and compilation.availability.op is not AvailabilityOp.ALWAYS
    ):
        availability = f"({callable_availability}) and ({compilation_availability})"

    flags = []
    for flag in compilation.compiler_flags:
        context_parts = []
        if flag.base_march:
            context_parts.append(f"base: {flag.base_march}")
        if flag.version:
            context_parts.append(f"version: {flag.version}")
        context_parts.extend(flag.notes)
        flags.append(
            {
                "compiler": flag.compiler,
                "flags": " ".join(flag.flags) or "No flags recorded",
                "context": "; ".join(context_parts) or "No context recorded",
                "target": flag.target or "Target not recorded",
                "mode": (
                    _display_enum(flag.mode)
                    if flag.mode is not None
                    else "All applicable calling modes"
                ),
                "availability": _format_availability(flag.availability),
                "is_default": _optional_bool(flag.default_enabled),
                "source": _format_provenance(flag.provenance),
            }
        )
    mode_availability = []
    for item in getattr(compilation, "availability_by_mode", ()):
        mode_availability.append(
            {
                "mode": _display_enum(_enum_text(item.mode)),
                "availability": _format_availability(item.availability),
                "source": _format_provenance(item.provenance),
            }
        )
    return {
        "headers": headers,
        "architecture_min": compilation.architecture_min,
        "profiles": tuple(compilation.profiles),
        "extensions": tuple(compilation.extensions),
        "feature_macros": tuple(compilation.feature_macros),
        "execution_states": tuple(getattr(compilation, "execution_states", ())),
        "availability": availability,
        "mode_availability": mode_availability,
        "flags": flags,
        "unresolved_reason": compilation.unresolved_reason,
        "missing_flags_reason": compilation.unresolved_reason or _DEFAULT_FLAG_REASON,
    }


def _parameter_rows(callable_: ConcreteCallable) -> list[dict[str, str]]:
    documentation = {
        parameter.name: parameter.description
        for parameter in callable_.semantics.parameters
    }
    rows = []
    for index, parameter in enumerate(callable_.signature.parameters):
        name = parameter.name or f"argument {index + 1}"
        constraints = "; ".join(
            _constraint_text(item) for item in parameter.constraints
        )
        rows.append(
            {
                "name": name,
                "type": parameter.type_name,
                "description": documentation.get(
                    parameter.name or "",
                    "No source-backed parameter description is available.",
                ),
                "constraints": constraints or "No additional constraint recorded",
            }
        )
    return rows


def _instruction_rows(callable_: ConcreteCallable) -> list[dict[str, str]]:
    rows = []
    for mapping in callable_.instructions:
        form_parts = []
        if mapping.sequence_index is not None:
            form_parts.append(f"Sequence step {mapping.sequence_index + 1}")
        if mapping.form:
            form_parts.append(mapping.form)
        rows.append(
            {
                "relation": _display_enum(_enum_text(mapping.relation)),
                "instruction_set": mapping.instruction_set,
                "mnemonic": mapping.mnemonic or "Not specified",
                "form": " · ".join(form_parts) or "Not specified",
                "argument_mapping": mapping.argument_mapping or "Not specified",
                "result_mapping": mapping.result_mapping or "Not specified",
                "emission": (
                    "Guaranteed by the cited relation"
                    if mapping.guaranteed_emission
                    else "Not guaranteed"
                ),
                "evidence": _format_provenance(mapping.provenance),
            }
        )
    return rows


def _instruction_disclaimer(callable_: ConcreteCallable) -> str | None:
    if not callable_.instructions:
        return None
    qualifiers = []
    if len(callable_.instructions) > 1:
        qualifiers.append(
            "Multiple mappings are listed; their order does not imply a fixed "
            "one-to-one emitted instruction sequence unless a source says so."
        )
    if any(not mapping.guaranteed_emission for mapping in callable_.instructions):
        qualifiers.append(
            "At least one mapping is semantic, grouped, optional, or optimizer-dependent. "
            "The compiler may emit a different equivalent sequence."
        )
    return " ".join(qualifiers) or None


def _instruction_reason(callable_: ConcreteCallable) -> str:
    matching = [
        diagnostic.message
        for diagnostic in callable_.diagnostics
        if "instruction" in f"{diagnostic.code} {diagnostic.field or ''}".lower()
    ]
    if matching:
        return " ".join(matching)
    return (
        "No reliable instruction mapping is present in the pinned sources. "
        "The converter does not infer a lowering from the callable name."
    )


def _performance_context(records: Sequence[PerformanceRecord]) -> dict[str, object]:
    rows: list[dict[str, str]] = []
    reasons: list[str] = []
    if not records:
        reasons.append(_DEFAULT_PERFORMANCE_REASON)
    for record in records:
        has_data = any(
            metric.is_resolved
            for metric in (record.latency, record.reciprocal_throughput, record.uops)
        ) or bool(record.resources)
        if not has_data:
            reasons.append(
                record.unresolved_reason
                or f"{record.microarchitecture}: {_DEFAULT_PERFORMANCE_REASON}"
            )
            continue

        source_note_parts = [
            f"evidence: {_display_enum(_enum_text(record.evidence_kind))}",
            *_performance_provenance(record),
        ]
        source_note_parts.extend(record.notes)
        if record.unresolved_reason:
            reasons.append(f"{record.microarchitecture}: {record.unresolved_reason}")
        rows.append(
            {
                "microarchitecture": record.microarchitecture,
                "cpu_form": " · ".join(
                    part for part in (record.cpu, record.instruction_form) if part
                )
                or "Not specified",
                "latency": _format_metric(record.latency),
                "throughput": _format_metric(record.reciprocal_throughput),
                "resources": _format_resources(record),
                "confidence": _display_enum(_enum_text(record.confidence)),
                "confidence_class": _enum_text(record.confidence),
                "source_summary": _performance_source_summary(record),
                "source_note": "; ".join(part for part in source_note_parts if part),
            }
        )
    return {"rows": rows, "reasons": _deduplicate_text(reasons)}


def _format_metric(metric: PerformanceMetric) -> str:
    if not metric.is_resolved or metric.value is None:
        reason = (
            metric.provenance.note
            or ("; ".join(metric.notes) if metric.notes else None)
            or "not reported by the pinned performance source"
        )
        return f"Unavailable — {reason}"
    value = metric.value
    number = (
        str(value.minimum)
        if value.maximum is None or value.maximum == value.minimum
        else f"{value.minimum}–{value.maximum}"
    )
    display_notes = tuple(
        note for note in metric.notes if note not in _STANDARD_PERFORMANCE_METRIC_NOTES
    )
    notes = f" ({'; '.join(display_notes)})" if display_notes else ""
    return f"{number} {value.unit}{notes}"


def _performance_source_summary(record: PerformanceRecord) -> str:
    if record.evidence_kind.value == "compiler_model":
        return "LLVM scheduling-model estimate; not measured hardware data."
    return f"{_display_enum(_enum_text(record.evidence_kind))} evidence."


def _format_resources(record: PerformanceRecord) -> str:
    parts = [f"µops: {_format_metric(record.uops)}"]
    if record.resources:
        parts.append(f"resources: {', '.join(record.resources)}")
    else:
        reason = (
            record.resources_provenance.note
            or "not reported by the pinned performance source"
        )
        parts.append(f"resources: unavailable — {reason}")
    return "; ".join(parts)


def _constraints(callable_: ConcreteCallable) -> tuple[str, ...]:
    values = [_constraint_text(item) for item in callable_.semantics.constraints]
    for parameter in callable_.signature.parameters:
        values.extend(
            f"{parameter.name}: {_constraint_text(item)}"
            if parameter.name
            else _constraint_text(item)
            for item in parameter.constraints
        )
    return _deduplicate_text(values)


def _constraint_text(constraint: Constraint) -> str:
    prefix = (
        f"{_display_enum(_enum_text(constraint.kind))}: " if constraint.kind else ""
    )
    return f"{prefix}{constraint.text}"


def _diagnostic_row(diagnostic: Diagnostic) -> dict[str, str]:
    severity = _enum_text(diagnostic.severity).lower()
    return {
        "code": diagnostic.code,
        "message": diagnostic.message,
        "severity": severity,
        "severity_label": _display_enum(severity),
    }


def _source_rows(sources: Sequence[SourceRef]) -> list[dict[str, str | None]]:
    rows = []
    for source in sources:
        line_range = ""
        if source.start_line is not None:
            line_range = f":{source.start_line}"
            if source.end_line is not None and source.end_line != source.start_line:
                line_range += f"-{source.end_line}"
        rows.append(
            {
                "label": f"{source.repository} · {source.id}",
                "revision": source.commit,
                "location": f"{source.path}{line_range}",
                "license": source.license_id or "Not specified (release-blocking)",
                "url": _source_url(source),
            }
        )
    return rows


def _source_url(source: SourceRef) -> str | None:
    if source.url:
        return source.url
    repository = source.repository.removeprefix("https://github.com/").removesuffix(
        ".git"
    )
    if repository.count("/") != 1:
        return None
    url = f"https://github.com/{repository}/blob/{source.commit}/{source.path}"
    if source.start_line is not None:
        url += f"#L{source.start_line}"
        if source.end_line is not None and source.end_line != source.start_line:
            url += f"-L{source.end_line}"
    return url


def _field_provenance_rows(callable_: ConcreteCallable) -> list[dict[str, str]]:
    rows = []
    for item in callable_.field_provenance:
        provenance = item.provenance
        evidence = []
        if provenance.rule:
            evidence.append(f"rule: {provenance.rule}")
        if provenance.note:
            evidence.append(provenance.note)
        evidence.extend(_source_short(source) for source in provenance.sources)
        rows.append(
            {
                "field": item.field,
                "method": _display_enum(_enum_text(provenance.kind)),
                "evidence": "; ".join(evidence) or "No additional detail recorded",
            }
        )
    return rows


def _format_provenance(provenance: Provenance) -> str:
    parts = [_display_enum(_enum_text(provenance.kind))]
    if provenance.rule:
        parts.append(f"rule: {provenance.rule}")
    if provenance.note:
        parts.append(provenance.note)
    parts.extend(_source_short(source) for source in provenance.sources)
    return "; ".join(parts)


def _performance_provenance(record: PerformanceRecord) -> tuple[str, ...]:
    values = []
    for provenance in (
        record.provenance,
        record.latency.provenance,
        record.reciprocal_throughput.provenance,
        record.uops.provenance,
        record.resources_provenance,
    ):
        if (
            _enum_text(provenance.kind) != "unresolved"
            or provenance.sources
            or provenance.rule
            or provenance.note
        ):
            values.append(_format_provenance(provenance))
    return _deduplicate_text(values)


def _source_short(source: SourceRef) -> str:
    lines = ""
    if source.start_line is not None:
        lines = f":{source.start_line}"
        if source.end_line is not None and source.end_line != source.start_line:
            lines += f"-{source.end_line}"
    return f"{source.path}{lines}@{source.commit}"


def _optional_bool(value: bool | None) -> str:
    if value is None:
        return "Not established"
    return "Yes" if value else "No"


def _deduplicate_text(values: Iterable[str]) -> tuple[str, ...]:
    result = []
    seen = set()
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return tuple(result)
