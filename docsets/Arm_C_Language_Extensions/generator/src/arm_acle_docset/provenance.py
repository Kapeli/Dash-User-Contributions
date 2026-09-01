"""Shared provenance traversal for catalog validation and rendering."""

from __future__ import annotations

from .model import ConcreteCallable, SourceRef


def collect_callable_sources(callable_: ConcreteCallable) -> tuple[SourceRef, ...]:
    """Collect every source reference that can appear on a callable page."""

    sources: list[SourceRef] = list(callable_.sources)
    provenances = [
        callable_.semantics.provenance,
        callable_.compilation.provenance,
        *(item.provenance for item in callable_.field_provenance),
        *(item.provenance for item in callable_.aliases),
        *(item.provenance for item in callable_.instructions),
        *(item.provenance for item in callable_.state_access),
        *(item.provenance for item in callable_.semantics.constraints),
        *(item.provenance for item in callable_.semantics.parameters),
        *(item.provenance for item in callable_.compilation.compiler_flags),
        *(item.provenance for item in callable_.compilation.availability_by_mode),
    ]
    for parameter in callable_.signature.parameters:
        provenances.extend(item.provenance for item in parameter.constraints)
    for record in callable_.performance:
        provenances.extend(
            (
                record.provenance,
                record.resources_provenance,
                record.latency.provenance,
                record.reciprocal_throughput.provenance,
                record.uops.provenance,
            )
        )
    for provenance in provenances:
        sources.extend(provenance.sources)
    for diagnostic in callable_.diagnostics:
        sources.extend(diagnostic.sources)

    deduplicated: list[SourceRef] = []
    seen: dict[tuple[object, ...], SourceRef] = {}
    for source in sources:
        key = (
            source.repository,
            source.commit,
            source.path,
            source.start_line,
            source.end_line,
        )
        previous = seen.get(key)
        if previous is None:
            seen[key] = source
            deduplicated.append(source)
            continue
        if previous.license_id != source.license_id or previous.url != source.url:
            raise ValueError(
                "conflicting source metadata for "
                f"{source.repository}@{source.commit}:{source.path}:"
                f"{source.start_line}-{source.end_line}"
            )
    return tuple(deduplicated)


__all__ = ["collect_callable_sources"]
