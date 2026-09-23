"""Statically cross-check a canonical catalog against pinned GCC test samples.

The GCC inputs are build-time validation evidence only.  They are downloaded
into the source cache, checked by :mod:`arm_acle_docset.sources.manifest`, and
never copied into the generated docset or archive.  GCC testsuite files remain
licensed under GPL-3.0-or-later with the GCC Runtime Library Exception where
applicable; this module contains only the independently-authored validation
rules below.

This module does not invoke GCC, compile the samples, or validate generated
code.  It only inspects active source text in a small, pinned GCC testsuite
sample.  Comments and ``#if 0`` regions are excluded, and paired explicit and
overloaded spellings must occur in one related TEST construct or function
group.  The rules then validate a stronger property than simple name presence:
both spellings must resolve uniquely to the same canonical callable, and the
overloaded spelling must retain its name role.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Mapping, Sequence

from ..model import Catalog, ConcreteCallable, NameRole
from .manifest import GCC_COMMIT


GCC_REPOSITORY = "gcc-mirror/gcc"


@dataclass(frozen=True, slots=True)
class GCCValidationSample:
    """One independently selected relation demonstrated by a GCC test."""

    sample_id: str
    family: str
    source_path: str
    explicit_name: str
    overloaded_name: str | None = None


@dataclass(frozen=True, slots=True)
class GCCValidationResult:
    """One successful static sample cross-check and its canonical callable."""

    sample: GCCValidationSample
    source_lines: tuple[int, ...]
    callable_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class GCCValidationReport:
    """Summary returned after every configured static sample check passes."""

    repository: str
    commit: str
    results: tuple[GCCValidationResult, ...]

    @property
    def validated_count(self) -> int:
        return len(self.results)


@dataclass(frozen=True, slots=True)
class GCCValidationIssue:
    """A stable diagnostic emitted by the validation gate."""

    code: str
    sample_id: str
    message: str


class GCCValidationError(RuntimeError):
    """Raised when a pinned GCC sample and the canonical catalog disagree."""

    def __init__(self, issues: Sequence[GCCValidationIssue]) -> None:
        self.issues = tuple(issues)
        detail = "\n".join(f"- [{issue.code}] {issue.message}" for issue in self.issues)
        super().__init__(f"GCC static sample cross-check failed:\n{detail}")


@dataclass(frozen=True, slots=True)
class _SourceRegion:
    """One active, related source construct represented by original spans."""

    label: str
    spans: tuple[tuple[int, int], ...]


_GCC_TEST_ROOT = "gcc/testsuite/gcc.target"

GCC_VALIDATION_SAMPLES: tuple[GCCValidationSample, ...] = (
    GCCValidationSample(
        sample_id="neon-vaddh-f16",
        family="neon",
        source_path=f"{_GCC_TEST_ROOT}/aarch64/advsimd-intrinsics/vaddh_f16_1.c",
        explicit_name="vaddh_f16",
    ),
    GCCValidationSample(
        sample_id="mve-vaddq-s32",
        family="mve",
        source_path=f"{_GCC_TEST_ROOT}/arm/mve/intrinsics/vaddq_s32.c",
        explicit_name="vaddq_s32",
        overloaded_name="vaddq",
    ),
    GCCValidationSample(
        sample_id="sve-add-vector-s32-m",
        family="sve",
        source_path=f"{_GCC_TEST_ROOT}/aarch64/sve/acle/asm/add_s32.c",
        explicit_name="svadd_s32_m",
        overloaded_name="svadd_m",
    ),
    GCCValidationSample(
        sample_id="sve-add-scalar-s32-m",
        family="sve",
        source_path=f"{_GCC_TEST_ROOT}/aarch64/sve/acle/asm/add_s32.c",
        explicit_name="svadd_n_s32_m",
        overloaded_name="svadd_m",
    ),
    GCCValidationSample(
        sample_id="sme-mopa-s8-za32",
        family="sme",
        source_path=f"{_GCC_TEST_ROOT}/aarch64/sme/acle-asm/mopa_za32.c",
        explicit_name="svmopa_za32_s8_m",
        overloaded_name="svmopa_za32_m",
    ),
    GCCValidationSample(
        sample_id="sme-mopa-f32-za32",
        family="sme",
        source_path=f"{_GCC_TEST_ROOT}/aarch64/sme/acle-asm/mopa_za32.c",
        explicit_name="svmopa_za32_f32_m",
        overloaded_name="svmopa_za32_m",
    ),
)


def validate_catalog_against_gcc(
    catalog: Catalog,
    source_paths: Mapping[str, Path],
    *,
    samples: Sequence[GCCValidationSample] = GCC_VALIDATION_SAMPLES,
) -> GCCValidationReport:
    """Statically cross-check pinned spellings and canonical alias relations.

    ``source_paths`` uses the same manifest-relative keys yielded by
    :func:`arm_acle_docset.sources.manifest.resolved_source_snapshot`.

    No compiler is run.  A sample is evidence only when its identifiers occur
    in active code and, for an explicit/overloaded pair, in one related TEST
    macro invocation or function group.
    """

    texts: dict[str, str] = {}
    results: list[GCCValidationResult] = []
    issues: list[GCCValidationIssue] = []

    for sample in samples:
        source = source_paths.get(sample.source_path)
        if source is None:
            issues.append(
                GCCValidationIssue(
                    code="gcc.source_missing",
                    sample_id=sample.sample_id,
                    message=(
                        f"sample {sample.sample_id!r} requires {sample.source_path}; "
                        "fetch or provide the complete pinned source manifest"
                    ),
                )
            )
            continue

        try:
            if sample.source_path not in texts:
                texts[sample.source_path] = Path(source).read_text(encoding="utf-8")
            text = texts[sample.source_path]
        except (OSError, UnicodeError) as error:
            issues.append(
                GCCValidationIssue(
                    code="gcc.source_unreadable",
                    sample_id=sample.sample_id,
                    message=f"cannot read {source}: {error}",
                )
            )
            continue

        expected_names = (sample.explicit_name,) + (
            (sample.overloaded_name,) if sample.overloaded_name is not None else ()
        )
        sanitized = _sanitize_active_c_source(text)
        source_lines = _sample_source_lines(sanitized, expected_names)
        if source_lines is None:
            missing_names = tuple(
                name
                for name in expected_names
                if _identifier_offset(sanitized, name) is None
            )
            if missing_names:
                missing = ", ".join(repr(name) for name in missing_names)
                issues.append(
                    GCCValidationIssue(
                        code="gcc.sample_identifier_missing",
                        sample_id=sample.sample_id,
                        message=(
                            f"pinned sample {sample.source_path} no longer contains "
                            f"active identifier(s) {missing}; comments and #if 0 "
                            "regions do not count. Inspect the source pin and rule"
                        ),
                    )
                )
            else:
                issues.append(
                    GCCValidationIssue(
                        code="gcc.sample_relation_missing",
                        sample_id=sample.sample_id,
                        message=(
                            f"pinned sample {sample.source_path} contains the requested "
                            "identifiers, but not in one related active TEST construct "
                            "or function group; unrelated test cases do not establish "
                            "an explicit/overloaded relation"
                        ),
                    )
                )
            continue

        matches = tuple(
            callable_
            for callable_ in catalog.callables
            if sample.family in callable_.families
            and _has_non_overloaded_name(callable_, sample.explicit_name)
            and (
                sample.overloaded_name is None
                or _has_overloaded_name(callable_, sample.overloaded_name)
            )
        )
        if not matches:
            issues.append(_catalog_issue(catalog, sample))
            continue
        if len(matches) != 1:
            candidates = sorted(
                f"{callable_.id}:{callable_.signature.render(callable_.name)}"
                for callable_ in matches
            )
            issues.append(
                GCCValidationIssue(
                    code="gcc.catalog_relation_ambiguous",
                    sample_id=sample.sample_id,
                    message=(
                        f"static sample {sample.sample_id!r} resolves to "
                        f"{len(matches)} canonical callables, expected exactly one; "
                        f"candidates={candidates}"
                    ),
                )
            )
            continue

        results.append(
            GCCValidationResult(
                sample=sample,
                source_lines=source_lines,
                callable_ids=(matches[0].id,),
            )
        )

    if issues:
        raise GCCValidationError(issues)
    return GCCValidationReport(
        repository=GCC_REPOSITORY,
        commit=GCC_COMMIT,
        results=tuple(results),
    )


def required_gcc_source_paths(
    samples: Sequence[GCCValidationSample] = GCC_VALIDATION_SAMPLES,
) -> tuple[str, ...]:
    """Return the deterministic set of manifest paths needed for validation."""

    return tuple(sorted({sample.source_path for sample in samples}))


def _sample_source_lines(
    text: str,
    names: tuple[str, ...],
) -> tuple[int, ...] | None:
    for region in _source_regions(text):
        offsets = tuple(_identifier_in_region(text, name, region) for name in names)
        if all(offset is not None for offset in offsets):
            return tuple(
                text.count("\n", 0, offset) + 1
                for offset in offsets
                if offset is not None
            )
    return None


def _identifier_offset(text: str, name: str) -> int | None:
    match = re.search(_identifier_pattern(name), text)
    return None if match is None else match.start()


def _identifier_in_region(
    text: str,
    name: str,
    region: _SourceRegion,
) -> int | None:
    pattern = re.compile(_identifier_pattern(name))
    for start, end in region.spans:
        match = pattern.search(text, start, end)
        if match is not None:
            return match.start()
    return None


def _identifier_pattern(name: str) -> str:
    return rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])"


def _source_regions(text: str) -> tuple[_SourceRegion, ...]:
    regions: list[_SourceRegion] = []

    for match in re.finditer(r"(?m)^\s*#\s*define\b[^\n]*", text):
        regions.append(
            _SourceRegion("preprocessor definition", ((match.start(), match.end()),))
        )

    macro_pattern = re.compile(r"\b(?P<name>(?:TEST|CHECK)_[A-Z0-9_]+)\s*\(")
    for match in macro_pattern.finditer(text):
        opening = text.find("(", match.start(), match.end())
        closing = _matching_delimiter(text, opening, "(", ")")
        if closing is not None:
            regions.append(
                _SourceRegion(
                    f"macro {match.group('name')}",
                    ((match.start(), closing + 1),),
                )
            )

    functions: list[tuple[str, tuple[int, int]]] = []
    function_pattern = re.compile(
        r"\b(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*"
        r"\([^(){};]*\)\s*\{",
        re.MULTILINE,
    )
    control_words = {"if", "for", "while", "switch"}
    for match in function_pattern.finditer(text):
        name = match.group("name")
        if name in control_words:
            continue
        opening = text.find("{", match.start(), match.end())
        closing = _matching_delimiter(text, opening, "{", "}")
        if closing is None:
            continue
        span = (match.start(), closing + 1)
        functions.append((name, span))
        regions.append(_SourceRegion(f"function {name}", (span,)))

    function_groups: dict[str, list[tuple[int, int]]] = {}
    for name, span in functions:
        stem = re.sub(r"\d+$", "", name)
        function_groups.setdefault(stem, []).append(span)
    for stem, spans in sorted(function_groups.items()):
        if len(spans) > 1:
            regions.append(
                _SourceRegion(f"related functions {stem}*", tuple(sorted(spans)))
            )

    return tuple(
        sorted(
            regions,
            key=lambda region: (
                min(start for start, _ in region.spans),
                len(region.spans),
                region.label,
            ),
        )
    )


def _matching_delimiter(
    text: str,
    opening: int,
    open_character: str,
    close_character: str,
) -> int | None:
    if opening < 0 or opening >= len(text) or text[opening] != open_character:
        return None
    depth = 0
    for offset in range(opening, len(text)):
        character = text[offset]
        if character == open_character:
            depth += 1
        elif character == close_character:
            depth -= 1
            if depth == 0:
                return offset
    return None


def _sanitize_active_c_source(text: str) -> str:
    """Mask comments, literals, and complete ``#if 0`` blocks in place."""

    active_text = _mask_if_zero_blocks(text)
    characters = list(active_text)
    index = 0
    state: str | None = None
    while index < len(characters):
        character = characters[index]
        following = characters[index + 1] if index + 1 < len(characters) else ""
        if state is None:
            if character == "/" and following == "*":
                characters[index] = characters[index + 1] = " "
                state = "block_comment"
                index += 2
                continue
            if character == "/" and following == "/":
                characters[index] = characters[index + 1] = " "
                state = "line_comment"
                index += 2
                continue
            if character in {'"', "'"}:
                state = "string" if character == '"' else "character"
                characters[index] = " "
                index += 1
                continue
        elif state == "block_comment":
            if character == "*" and following == "/":
                characters[index] = characters[index + 1] = " "
                state = None
                index += 2
                continue
            if character != "\n":
                characters[index] = " "
        elif state == "line_comment":
            if character == "\n":
                state = None
            else:
                characters[index] = " "
        else:
            quote = '"' if state == "string" else "'"
            if character == "\\":
                characters[index] = " "
                if index + 1 < len(characters):
                    if characters[index + 1] != "\n":
                        characters[index + 1] = " "
                    index += 2
                    continue
            if character == quote:
                state = None
            if character != "\n":
                characters[index] = " "
        index += 1
    return "".join(characters)


def _mask_if_zero_blocks(text: str) -> str:
    lines = text.splitlines(keepends=True)
    masked: list[str] = []
    disabled_depth = 0
    directive_pattern = re.compile(
        r"^\s*#\s*(?P<directive>if|ifdef|ifndef|endif)\b(?P<body>.*)$"
    )
    zero_pattern = re.compile(r"^\s*(?:0|\(\s*0\s*\))\s*(?:(?://|/\*).*)?$")
    for line in lines:
        match = directive_pattern.match(line.rstrip("\r\n"))
        if match is not None:
            directive = match.group("directive")
            if disabled_depth:
                if directive in {"if", "ifdef", "ifndef"}:
                    disabled_depth += 1
                elif directive == "endif":
                    disabled_depth -= 1
                masked.append(_mask_line(line))
                continue
            if directive == "if" and zero_pattern.fullmatch(match.group("body")):
                disabled_depth = 1
                masked.append(_mask_line(line))
                continue
        masked.append(line if not disabled_depth else _mask_line(line))
    return "".join(masked)


def _mask_line(line: str) -> str:
    return "".join(
        "\n" if character == "\n" else "\r" if character == "\r" else " "
        for character in line
    )


def _name_roles(callable_: ConcreteCallable, name: str) -> tuple[NameRole, ...]:
    roles: list[NameRole] = []
    if callable_.name == name:
        roles.append(callable_.name_role)
    roles.extend(alias.role for alias in callable_.aliases if alias.name == name)
    return tuple(roles)


def _has_non_overloaded_name(callable_: ConcreteCallable, name: str) -> bool:
    return any(role is not NameRole.OVERLOADED for role in _name_roles(callable_, name))


def _has_overloaded_name(callable_: ConcreteCallable, name: str) -> bool:
    return NameRole.OVERLOADED in _name_roles(callable_, name)


def _catalog_issue(catalog: Catalog, sample: GCCValidationSample) -> GCCValidationIssue:
    family_callables = tuple(
        callable_
        for callable_ in catalog.callables
        if sample.family in callable_.families
    )
    explicit_count = sum(
        _has_non_overloaded_name(callable_, sample.explicit_name)
        for callable_ in family_callables
    )
    if sample.overloaded_name is None:
        expected = f"non-overloaded name {sample.explicit_name!r}"
        counts = (
            f"family matches={len(family_callables)}, name matches={explicit_count}"
        )
    else:
        overloaded_count = sum(
            _has_overloaded_name(callable_, sample.overloaded_name)
            for callable_ in family_callables
        )
        expected = (
            f"explicit name {sample.explicit_name!r} and overloaded alias "
            f"{sample.overloaded_name!r} on one callable"
        )
        counts = (
            f"family matches={len(family_callables)}, explicit matches={explicit_count}, "
            f"overloaded matches={overloaded_count}"
        )
    return GCCValidationIssue(
        code="gcc.catalog_relation_missing",
        sample_id=sample.sample_id,
        message=(
            f"The pinned GCC {GCC_COMMIT[:12]} static sample contains {expected} "
            f"in family {sample.family!r}, but the canonical catalog does not; "
            f"{counts}. "
            "Inspect the declaration adapter and canonical alias merge."
        ),
    )


__all__ = [
    "GCC_REPOSITORY",
    "GCC_VALIDATION_SAMPLES",
    "GCCValidationError",
    "GCCValidationIssue",
    "GCCValidationReport",
    "GCCValidationResult",
    "GCCValidationSample",
    "required_gcc_source_paths",
    "validate_catalog_against_gcc",
]
