"""Parse callable metadata from the Arm ACLE Markdown specification.

The ACLE main specification is intentionally human-authored Markdown rather
than a callable database.  This adapter therefore builds a small structural
tree first and only then extracts facts from bounded section contexts.  It
expands only source-declared variant lists whose suffixes and signature type
changes can be proved mechanically; all other variant prose stays unresolved.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Iterator, Sequence
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

from ..model import AvailabilityExpr, AvailabilityOp, ComparisonOperator
from ..normalize import parse_availability_guard

ACLE_REPOSITORY = "ARM-software/acle"
ACLE_MARKDOWN_LICENSE = "CC-BY-SA-4.0 AND Apache-Patent-License"

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
_FENCE_RE = re.compile(r"^\s*(?P<fence>`{3,}|~{3,})\s*(?P<info>[^`]*)$")
_CALLABLE_NAME_RE = re.compile(
    r"(?P<name>(?:__arm_|__|sv)[A-Za-z0-9_]*(?:\[[^\]\n]+\][A-Za-z0-9_]*)*)\s*\("
)
_BRACKET_SEGMENT_RE = re.compile(r"\[([^\]]+)\]")
_ATTRIBUTE_RE = re.compile(
    r"__arm_(?:agnostic|in|inout|locally_streaming|new|out|preserves|"
    r"streaming|streaming_compatible)\b(?:\s*\([^)]*\))?"
)
_ATTRIBUTE_NAMES = {
    "__attribute__",
    "__arm_agnostic",
    "__arm_in",
    "__arm_inout",
    "__arm_locally_streaming",
    "__arm_new",
    "__arm_out",
    "__arm_preserves",
    "__arm_streaming",
    "__arm_streaming_compatible",
}
_STATE_ATTRIBUTE_RE = re.compile(
    r"__arm_(?P<mode>in|inout|new|out|preserves)\s*\((?P<states>[^)]*)\)"
)
_MACRO_RE = re.compile(r"\b__ARM(?:_FEATURE)?_[A-Za-z0-9_]+\b|\b__ARM_FP\b")
_ARCH_RE = re.compile(r"\bArmv(?P<version>\d+(?:\.\d+)?)(?:-(?P<profile>[AMR]))?\b")
_EXECUTION_STATE_RE = re.compile(r"\bAArch(?:32|64)\b")
_FEAT_RE = re.compile(r"\bFEAT_[A-Za-z0-9_]+\b")
_HEADER_RE = re.compile(r"<(?P<header>arm_[a-z0-9_]+\.h)>")
_MATURITY_RE = re.compile(
    r"(?:"
    r"\[\*\*(Release|Beta|Alpha)\*\*\s+(?:quality level|state)\]\([^)]*\)"
    r"|\[\*\*(Release|Beta|Alpha)\*\*\]\([^)]*\)\s+(?:quality level|state)"
    r"|\*\*(Release|Beta|Alpha)\*\*\s+(?:quality level|state)"
    r")",
    re.IGNORECASE,
)
_VARIANT_PROSE_RE = re.compile(
    r"\b(?:"
    r"variants?\s+(?:(?:are|is)\s+)?(?:also\s+)?available"
    r"|variants?\s+for\b.+?\b(?:are|is)\s+(?:also\s+)?available"
    r"|available\s+variants?\s+are"
    r"|also\s+for(?=\s+_[A-Za-z0-9_]+)"
    r"|and similarly for"
    r"|replac(?:e|ing) .+? with"
    r"|the same (?:prototype|intrinsic).+?for"
    r")\b",
    re.IGNORECASE,
)
_SIMPLE_VARIANT_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:"
    r"_[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*"
    r"|(?:bf|mf|[bcsuf])(?:8|16|32|64)"
    r")(?![A-Za-z0-9_])"
)
_VARIANT_SUFFIX_FRAGMENT_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?P<suffix>"
    r"_[A-Za-z0-9]+(?:\[[A-Za-z0-9_]+\]|_[A-Za-z0-9]+)*"
    r"|(?:bf|mf|[bcsuf])(?:8|16|32|64)"
    r")(?![A-Za-z0-9_])"
)
_REPLACEMENT_VARIANT_RE = re.compile(
    r"\breplac(?:e|ing)\s+`?(?P<old>_[A-Za-z0-9_]+)`?\s+with\s+"
    r"`?(?P<new>_[A-Za-z0-9_]+)`?",
    re.IGNORECASE,
)
_TYPE_ATOM_RE = re.compile(
    r"(?<![A-Za-z0-9])(?P<atom>(?:bf|mf|[bcsuf])(?:8|16|32|64))"
    r"(?![A-Za-z0-9])"
)
_TUPLE_SUFFIX_RE = re.compile(r"_x(?P<count>2|4)$")
_TYPE_ROOTS = {
    **{f"s{bits}": f"int{bits}" for bits in (8, 16, 32, 64)},
    **{f"u{bits}": f"uint{bits}" for bits in (8, 16, 32, 64)},
    **{f"f{bits}": f"float{bits}" for bits in (16, 32, 64)},
    "bf16": "bfloat16",
    "mf8": "mfloat8",
}
_C_TYPE_ATOM_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?P<sv>sv)?"
    r"(?P<root>bfloat|mfloat|float|uint|int)(?P<bits>8|16|32|64)"
    r"(?P<vector>x\d+)?_t\b"
)
_FIXED_SCALAR_PARAMETER_RE = re.compile(
    r"^(?:imm(?:_idx)?|index|offset|vnum|lane|slice|tile|shift|rotation|"
    r"pattern|prfop|fpm)$",
    re.IGNORECASE,
)
_REQUIREMENT_CUE_RE = re.compile(
    r"\b(?:available|availability|defined|only if|only when|provided|"
    r"requires?|introduced in|execution state|target|header file|includ(?:e|ed|ing))\b",
    re.IGNORECASE,
)
_EXAMPLE_HEADING_RE = re.compile(r"\bexamples?\b", re.IGNORECASE)


@dataclass(slots=True)
class _TextBlock:
    lines: list[str]
    start_line: int
    end_line: int

    @property
    def text(self) -> str:
        return "\n".join(self.lines).strip()


@dataclass(slots=True)
class _CodeBlock:
    lines: list[str]
    info: str
    start_line: int
    end_line: int


_Block = _TextBlock | _CodeBlock


@dataclass(slots=True)
class _Section:
    title: str
    level: int
    start_line: int
    end_line: int
    parent: _Section | None = None
    blocks: list[_Block] = field(default_factory=list)
    children: list[_Section] = field(default_factory=list)

    def ancestors(self, *, include_self: bool = True) -> list[_Section]:
        result: list[_Section] = []
        current: _Section | None = self if include_self else self.parent
        while current is not None:
            result.append(current)
            current = current.parent
        result.reverse()
        return result


def parse_acle_markdown_file(
    path: str | Path,
    *,
    source_commit: str,
    source_path: str = "main/acle.md",
) -> dict[str, Any]:
    """Parse an ACLE Markdown file and return records plus diagnostics."""

    markdown = Path(path).read_text(encoding="utf-8")
    return parse_acle_markdown(
        markdown,
        source_commit=source_commit,
        source_path=source_path,
    )


def parse_acle_markdown(
    markdown: str,
    *,
    source_commit: str,
    source_path: str = "main/acle.md",
) -> dict[str, Any]:
    """Parse supported callable facts from ACLE Markdown.

    The returned mapping deliberately stays adapter-local.  ``to_ir_records``
    is the single conversion boundary used by the generator's canonical IR.
    """

    root = _parse_markdown_tree(markdown)
    default_maturity = _document_default_maturity(root)
    named_semantics = _collect_named_semantics(root)
    records: list[dict[str, Any]] = []
    document_diagnostics: list[dict[str, Any]] = []

    for section in _walk_sections(root):
        if section is root or _is_example_section(section):
            continue
        code_blocks = [
            block for block in section.blocks if isinstance(block, _CodeBlock)
        ]
        if not code_blocks:
            continue

        first_code_index = next(
            index
            for index, block in enumerate(section.blocks)
            if isinstance(block, _CodeBlock)
        )
        section_intro = [
            block
            for block in section.blocks[:first_code_index]
            if isinstance(block, _TextBlock)
        ]

        for block in code_blocks:
            if block.info and block.info.lower() not in {"c", "cpp", "c++", ""}:
                continue
            following_text = _following_text_blocks(section.blocks, block)
            declarations = _extract_declarations(block)
            if not declarations:
                continue

            for declaration in declarations:
                context_blocks: list[_TextBlock] = [*section_intro, *following_text]
                record = _record_from_declaration(
                    declaration,
                    section=section,
                    context_blocks=context_blocks,
                    default_maturity=default_maturity,
                    named_semantics=named_semantics,
                    source_commit=source_commit,
                    source_path=source_path,
                )
                records.append(record)
                records.extend(
                    _expand_source_declared_variants(
                        record,
                        declaration=declaration,
                    )
                )

    records, duplicate_diagnostics = _deduplicate_records(records)
    document_diagnostics.extend(duplicate_diagnostics)
    enrichments = _parse_instruction_mapping_enrichments(
        root,
        default_maturity=default_maturity,
        source_commit=source_commit,
        source_path=source_path,
    )
    return {
        "records": records,
        "enrichments": enrichments,
        "diagnostics": document_diagnostics,
        "source": {
            "repository": ACLE_REPOSITORY,
            "commit": source_commit,
            "path": source_path,
            "license": ACLE_MARKDOWN_LICENSE,
        },
    }


def to_ir_records(
    parsed_or_markdown: dict[str, Any] | str,
    *,
    source_commit: str | None = None,
    source_path: str = "main/acle.md",
    families: Iterable[str] = ("general",),
) -> list[Any]:
    """Convert explicit Markdown declarations to canonical callables.

    The default deliberately converts only general ACLE declarations.  SVE
    and SME declaration identity comes from the pinned LLVM inventory; use
    :func:`to_enrichment_records` to merge Markdown semantics and metadata
    into those callables.  Callers may opt additional families in when they
    need standalone source comparison records.
    """

    if isinstance(parsed_or_markdown, str):
        if not source_commit:
            raise ValueError("source_commit is required when parsing Markdown text")
        parsed = parse_acle_markdown(
            parsed_or_markdown,
            source_commit=source_commit,
            source_path=source_path,
        )
    else:
        parsed = parsed_or_markdown

    payloads = parsed.get("records")
    if not isinstance(payloads, list):
        raise TypeError("parsed ACLE Markdown must contain a records list")
    included = set(families)
    records = []
    for payload in payloads:
        blocker = _canonical_signature_blocker(payload)
        if blocker:
            diagnostic = {
                "code": "canonical_signature_unresolved",
                "message": blocker,
                "source": payload["provenance"]["source"],
            }
            if diagnostic not in parsed.setdefault("diagnostics", []):
                parsed["diagnostics"].append(diagnostic)
            continue
        payload_families = payload["family"]
        selected = [family for family in payload_families if family in included]
        for family in selected:
            records.append(_payload_to_concrete_callable(payload, family=family))
    return records


def to_enrichment_records(
    parsed_or_markdown: dict[str, Any] | str,
    *,
    source_commit: str | None = None,
    source_path: str = "main/acle.md",
) -> list[dict[str, Any]]:
    """Return name-matchable metadata patches for the declaration inventory."""

    if isinstance(parsed_or_markdown, str):
        if not source_commit:
            raise ValueError("source_commit is required when parsing Markdown text")
        parsed = parse_acle_markdown(
            parsed_or_markdown,
            source_commit=source_commit,
            source_path=source_path,
        )
    else:
        parsed = parsed_or_markdown

    patches: list[dict[str, Any]] = list(parsed.get("enrichments", []))
    for payload in parsed.get("records", []):
        if payload["family"] == ["general"]:
            continue
        names = [payload["names"]["explicit"], *payload["names"]["overloaded"]]
        patch = {
            "match": {"names": names, "base_names": []},
            "family": payload["family"],
            "header": payload["header"],
            "availability": payload["availability"],
            "maturity": payload["maturity"],
            "semantics": payload["semantics"],
            "instructions": payload["instructions"],
            "state": payload["state"],
            "taxonomy_path": payload["taxonomy_path"],
            "source_signature": payload["signature"],
            "provenance": payload["provenance"],
            "diagnostics": payload["diagnostics"],
        }
        if payload.get("variant_group") is not None:
            patch["variant_group"] = payload["variant_group"]
        patches.append(patch)
    return patches


def _parse_markdown_tree(markdown: str) -> _Section:
    lines = markdown.splitlines()
    root = _Section(title="", level=0, start_line=1, end_line=max(1, len(lines)))
    stack: list[_Section] = [root]
    text_lines: list[str] = []
    text_start = 1

    def flush_text(end_line: int) -> None:
        nonlocal text_lines, text_start
        if text_lines and any(line.strip() for line in text_lines):
            stack[-1].blocks.append(
                _TextBlock(text_lines, text_start, max(text_start, end_line))
            )
        text_lines = []

    index = 0
    while index < len(lines):
        line = lines[index]
        line_number = index + 1
        fence_match = _FENCE_RE.match(_strip_blockquote_prefix(line))
        if fence_match:
            flush_text(line_number - 1)
            fence = fence_match.group("fence")
            info_text = fence_match.group("info").strip()
            info = info_text.split(maxsplit=1)[0] if info_text else ""
            code_lines: list[str] = []
            start_line = line_number
            index += 1
            while index < len(lines):
                candidate = _strip_blockquote_prefix(lines[index])
                if re.match(
                    rf"^\s*{re.escape(fence[0])}{{{len(fence)},}}\s*$", candidate
                ):
                    break
                code_lines.append(candidate)
                index += 1
            end_line = min(len(lines), index + 1)
            stack[-1].blocks.append(
                _CodeBlock(code_lines, info.lower(), start_line, end_line)
            )
            index += 1
            text_start = index + 1
            continue

        heading_match = _HEADING_RE.match(line)
        if heading_match:
            flush_text(line_number - 1)
            level = len(heading_match.group(1))
            while stack[-1].level >= level:
                stack[-1].end_line = line_number - 1
                stack.pop()
            section = _Section(
                title=_plain_heading(heading_match.group(2)),
                level=level,
                start_line=line_number,
                end_line=max(line_number, len(lines)),
                parent=stack[-1],
            )
            stack[-1].children.append(section)
            stack.append(section)
            index += 1
            text_start = index + 1
            continue

        if not text_lines:
            text_start = line_number
        text_lines.append(line)
        index += 1

    flush_text(len(lines))
    while len(stack) > 1:
        stack[-1].end_line = len(lines)
        stack.pop()
    return root


def _walk_sections(root: _Section) -> Iterator[_Section]:
    yield root
    for child in root.children:
        yield from _walk_sections(child)


def _strip_blockquote_prefix(line: str) -> str:
    stripped = line
    while re.match(r"^\s*>\s?", stripped):
        stripped = re.sub(r"^\s*>\s?", "", stripped, count=1)
    return stripped


def _plain_heading(title: str) -> str:
    title = re.sub(r"<[^>]+>", "", title)
    title = re.sub(r"[`*_]", "", title)
    return re.sub(r"\s+", " ", title).strip()


def _document_default_maturity(root: _Section) -> tuple[str, int | None]:
    for section in _walk_sections(root):
        if section.title.lower() != "support levels":
            continue
        text = _blocks_text(
            block for block in section.blocks if isinstance(block, _TextBlock)
        )
        match = re.search(
            r"All content in this document is at the \*\*(Release|Beta|Alpha)\*\* "
            r"quality level",
            text,
            re.IGNORECASE,
        )
        if match:
            return match.group(1).lower(), section.start_line
    return "unspecified", None


def _explicit_section_maturity(section: _Section) -> tuple[str, int] | None:
    if section.title.lower() == "support levels":
        return None
    intro = _section_intro_blocks(section)
    for block in intro:
        match = _MATURITY_RE.search(block.text)
        if match:
            level = next(group for group in match.groups() if group is not None)
            return level.lower(), block.start_line
    return None


def _resolved_maturity(
    section: _Section,
    default: tuple[str, int | None],
) -> dict[str, Any]:
    level, line = default
    status = "inherited" if line is not None else "unresolved"
    for ancestor in section.ancestors():
        explicit = _explicit_section_maturity(ancestor)
        if explicit is not None:
            level, line = explicit
            status = "explicit" if ancestor is section else "inherited"
    return {
        "support_level": level,
        "status": status,
        "source_line": line,
    }


def _section_intro_blocks(section: _Section) -> list[_TextBlock]:
    result: list[_TextBlock] = []
    for block in section.blocks:
        if isinstance(block, _CodeBlock):
            break
        if isinstance(block, _TextBlock):
            result.append(block)
    return result


def _following_text_blocks(
    blocks: Sequence[_Block], code: _CodeBlock
) -> list[_TextBlock]:
    result: list[_TextBlock] = []
    found = False
    for block in blocks:
        if block is code:
            found = True
            continue
        if not found:
            continue
        if isinstance(block, _CodeBlock):
            break
        result.append(block)
    return result


def _section_wide_requirement_blocks(section: _Section) -> list[_TextBlock]:
    """Select late prose that explicitly scopes requirements to the section."""

    result: list[_TextBlock] = []
    scope_cue = re.compile(
        r"\b(?:these intrinsics|intrinsics in this section|to access (?:these|the) intrinsics)\b",
        re.IGNORECASE,
    )
    for block in section.blocks:
        if not isinstance(block, _TextBlock):
            continue
        selected = [
            sentence
            for sentence in _sentences(block.text)
            if scope_cue.search(sentence) and _REQUIREMENT_CUE_RE.search(sentence)
        ]
        if selected:
            result.append(_TextBlock(selected, block.start_line, block.end_line))
    return result


def _is_example_section(section: _Section) -> bool:
    return any(_EXAMPLE_HEADING_RE.search(item.title) for item in section.ancestors())


def _extract_declarations(block: _CodeBlock) -> list[dict[str, Any]]:
    declarations: list[dict[str, Any]] = []
    pending_comments: list[tuple[int, str]] = []
    shared_variant_comments: list[tuple[int, str]] = []
    statement_lines: list[tuple[int, str]] = []
    in_block_comment = False

    def flush_statement() -> None:
        nonlocal statement_lines, pending_comments, shared_variant_comments
        if not statement_lines:
            return
        raw = "\n".join(line for _, line in statement_lines).strip()
        line_start = statement_lines[0][0]
        line_end = statement_lines[-1][0]
        statement_lines = []
        parsed = _parse_declaration(raw)
        if parsed is None:
            pending_comments = []
            shared_variant_comments = []
            return
        parsed["line_start"] = line_start
        parsed["line_end"] = line_end
        leading_comments = pending_comments or shared_variant_comments
        parsed["leading_comments"] = list(leading_comments)
        declarations.append(parsed)
        if pending_comments:
            shared_variant_comments = (
                list(pending_comments)
                if any(
                    _VARIANT_PROSE_RE.search(_normalize_space(text.lstrip("/ ")))
                    for _, text in pending_comments
                )
                else []
            )
        pending_comments = []

    for offset, original in enumerate(block.lines, start=block.start_line + 1):
        stripped = original.strip()
        if in_block_comment:
            pending_comments.append((offset, stripped))
            if "*/" in stripped:
                in_block_comment = False
            continue
        if stripped.startswith("/*"):
            pending_comments.append((offset, stripped))
            if "*/" not in stripped:
                in_block_comment = True
            continue
        if stripped.startswith("//"):
            pending_comments.append((offset, stripped[2:].strip()))
            continue
        if not stripped or stripped.startswith("#"):
            if statement_lines:
                statement_lines.append((offset, original))
            elif not pending_comments:
                shared_variant_comments = []
            continue
        statement_lines.append((offset, original))
        if ";" in _remove_c_comments(original):
            flush_statement()

    flush_statement()
    return declarations


def _parse_declaration(raw: str) -> dict[str, Any] | None:
    normalized = _normalize_space(raw)
    if not normalized.endswith(";"):
        return None
    if (
        "{" in normalized
        or "}" in normalized
        or normalized.startswith(("typedef ", "enum "))
    ):
        return None
    code = _normalize_space(_remove_c_comments(normalized))
    matches = list(_CALLABLE_NAME_RE.finditer(code))
    if not matches:
        return None

    match = next(
        (item for item in matches if item.group("name") not in _ATTRIBUTE_NAMES),
        None,
    )
    if match is None:
        return None
    name = match.group("name")
    prefix = code[: match.start("name")].strip()
    if not prefix or prefix.startswith(("return ", "case ")) or "=" in prefix:
        return None
    if "(" in prefix or ")" in prefix:
        return None

    open_paren = code.find("(", match.start("name"))
    close_paren = _matching_paren(code, open_paren)
    if close_paren is None:
        return None
    suffix = code[close_paren + 1 :].rstrip(";").strip()
    attributes = _ATTRIBUTE_RE.findall(code)
    return_type = _ATTRIBUTE_RE.sub("", prefix).strip()
    if not return_type:
        return None

    parameters_raw = code[open_paren + 1 : close_paren].strip()
    parameters = [_parse_parameter(item) for item in _split_parameters(parameters_raw)]
    return {
        "name_pattern": name,
        "raw": normalized,
        "return_type": return_type,
        "parameters": parameters,
        "attributes": attributes,
        "suffix": suffix,
    }


def _matching_paren(text: str, open_index: int) -> int | None:
    depth = 0
    in_string = False
    escaped = False
    for index in range(open_index, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index
    return None


def _split_parameters(parameters: str) -> list[str]:
    if not parameters or parameters == "void":
        return []
    result: list[str] = []
    start = 0
    depth = 0
    for index, char in enumerate(parameters):
        if char in "([":
            depth += 1
        elif char in ")]":
            depth -= 1
        elif char == "," and depth == 0:
            result.append(parameters[start:index].strip())
            start = index + 1
    result.append(parameters[start:].strip())
    return [item for item in result if item]


def _parse_parameter(raw: str) -> dict[str, Any]:
    cleaned = _normalize_space(_remove_c_comments(raw))
    constraint = "constant_expression" if "/*constant*/" in raw else None
    if cleaned == "...":
        return {"name": None, "type": "...", "constraints": []}
    match = re.search(r"\b([A-Za-z_]\w*)\s*(?:\[[^]]*\])?$", cleaned)
    candidate_is_type = False
    if match:
        candidate = match.group(1)
        prefix_words = cleaned[: match.start(1)].strip().split()
        type_words = {
            "_Bool",
            "char",
            "const",
            "double",
            "float",
            "int",
            "long",
            "short",
            "signed",
            "unsigned",
            "void",
            "volatile",
        }
        candidate_is_type = (
            not prefix_words
            or candidate in type_words
            and all(word in type_words for word in prefix_words)
            or candidate.endswith("_t")
            and all(
                word in {"const", "volatile", "signed", "unsigned"}
                for word in prefix_words
            )
        )
    if match and not candidate_is_type:
        name = match.group(1)
        parameter_type = (cleaned[: match.start(1)] + cleaned[match.end(1) :]).strip()
    else:
        name = None
        parameter_type = cleaned
    constraints = []
    if constraint:
        constraints.append({"kind": constraint, "raw": "/*constant*/"})
    return {"name": name, "type": parameter_type, "constraints": constraints}


def _canonical_signature_blocker(payload: dict[str, Any]) -> str | None:
    signature = payload.get("signature")
    if not isinstance(signature, dict):
        return "The Markdown record has no structured signature."
    if not str(signature.get("return_type", "")).strip():
        return "The Markdown declaration has no parseable return type."
    for index, parameter in enumerate(signature.get("parameters", []), start=1):
        if not str(parameter.get("type", "")).strip():
            return (
                f"Parameter {index} of {payload['names']['explicit']} has no "
                "parseable type; no placeholder type was invented."
            )
    return None


def _remove_c_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    return re.sub(r"//.*?(?=\n|$)", " ", text)


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _record_from_declaration(
    declaration: dict[str, Any],
    *,
    section: _Section,
    context_blocks: Sequence[_TextBlock],
    default_maturity: tuple[str, int | None],
    named_semantics: dict[str, str],
    source_commit: str,
    source_path: str,
) -> dict[str, Any]:
    path = [item.title for item in section.ancestors() if item.title]
    families = _families_from_path(path)
    name_pattern = declaration["name_pattern"]
    explicit_name, overloaded_name = _expand_lockstep_name(name_pattern)
    signature_raw = declaration["raw"].replace(name_pattern, explicit_name, 1)
    ancestor_intro_blocks: list[_TextBlock] = []
    for ancestor in section.ancestors(include_self=False):
        ancestor_intro_blocks.extend(_section_intro_blocks(ancestor))
    all_requirement_blocks = [
        *ancestor_intro_blocks,
        *_section_wide_requirement_blocks(section),
        *context_blocks,
    ]
    comments = declaration["leading_comments"]
    comment_blocks = [
        _TextBlock([text], line, line) for line, text in comments if text.strip()
    ]
    requirement_comment_blocks = _requirement_comment_blocks(comments)
    requirements = _extract_requirements(
        [*all_requirement_blocks, *requirement_comment_blocks],
        families=families,
        attributes=declaration["attributes"],
    )
    variant_hints = _variant_hints([*context_blocks, *comment_blocks])
    variant_group = _expected_variant_group(
        exemplar_name=explicit_name,
        exemplar_return_type=declaration["return_type"],
        source_path=source_path,
        declaration_line=declaration["line_start"],
        comments=comments,
        variant_hints=variant_hints,
    )
    diagnostics = [
        {
            "code": "unexpanded_variant_prose",
            "line": hint["line"],
            "message": hint["raw"],
            "severity": "error",
        }
        for hint in variant_hints
    ]
    diagnostics.extend(requirements.pop("diagnostics"))
    semantics = named_semantics.get(explicit_name)
    if semantics is None and overloaded_name:
        semantics = named_semantics.get(overloaded_name)
    if semantics is None:
        semantics = _semantic_context(context_blocks)

    state = _state_access(declaration["attributes"])
    instructions = _instruction_relations(section, context_blocks)
    kind = _callable_kind(section, declaration)
    line_start = declaration["line_start"]
    line_end = declaration["line_end"]
    source = {
        "repository": ACLE_REPOSITORY,
        "commit": source_commit,
        "path": source_path,
        "start_line": line_start,
        "end_line": line_end,
        "license": ACLE_MARKDOWN_LICENSE,
    }
    return {
        "kind": kind,
        "family": families,
        "names": {
            "pattern": name_pattern,
            "explicit": explicit_name,
            "overloaded": [overloaded_name] if overloaded_name else [],
        },
        "signature": {
            "raw": signature_raw,
            "return_type": declaration["return_type"],
            "parameters": declaration["parameters"],
            "attributes": declaration["attributes"],
            "is_concrete": True,
        },
        "header": requirements.pop("headers"),
        "availability": requirements,
        "maturity": _resolved_maturity(section, default_maturity),
        "semantics": semantics,
        "instructions": instructions,
        "state": state,
        "variant_origin": "unresolved"
        if variant_hints
        else ("expanded_from_pattern" if overloaded_name else "explicit"),
        "variant_hints": variant_hints,
        "variant_group": variant_group,
        "taxonomy_path": path,
        "provenance": {
            "source": source,
            "fields": {
                "signature": "explicit",
                "names": "expanded" if overloaded_name else "explicit",
                "maturity": _resolved_maturity(section, default_maturity)["status"],
                "availability": "inherited_or_explicit",
                "semantics": "explicit" if semantics else "unresolved",
            },
        },
        "diagnostics": diagnostics,
    }


def _expand_source_declared_variants(
    exemplar: dict[str, Any],
    *,
    declaration: dict[str, Any],
) -> list[dict[str, Any]]:
    """Expand one fully understood, unconditional suffix list.

    ACLE uses a compact notation in which one declaration is followed by a
    list of additional type suffixes. The expansion here is deliberately
    narrow: the declaration must contain at most one lockstep bracket segment,
    the name and every listed suffix must contain exactly one element-type
    atom, and all non-type suffix structure must match the exemplar. The whole
    list is rejected if any part falls outside that grammar.
    """

    hints = exemplar["variant_hints"]
    if not hints:
        return []

    comment_hints = _variant_hints(
        [
            _TextBlock([text], line, line)
            for line, text in declaration["leading_comments"]
            if text.strip()
        ]
    )
    if comment_hints != hints:
        return []

    suffixes = _simple_declared_variant_suffixes(declaration["leading_comments"])
    if suffixes is None:
        return []

    expanded: list[dict[str, Any]] = []
    for suffix in suffixes:
        variant = _expanded_variant_record(exemplar, suffix=suffix)
        if variant is None:
            return []
        if variant["names"]["explicit"] == exemplar["names"]["explicit"]:
            continue
        if all(
            item["names"]["explicit"] != variant["names"]["explicit"]
            for item in expanded
        ):
            expanded.append(variant)

    if not expanded:
        return []

    exemplar["variant_origin"] = (
        "expanded_from_pattern" if exemplar["names"]["overloaded"] else "explicit"
    )
    exemplar["variant_group"] = None
    exemplar["diagnostics"] = [
        item
        for item in exemplar["diagnostics"]
        if item["code"] != "unexpanded_variant_prose"
    ]
    variant_source_start = min(
        [
            exemplar["provenance"]["source"]["start_line"],
            *(line for line, _ in declaration["leading_comments"]),
        ]
    )
    for variant in expanded:
        variant["provenance"]["source"]["start_line"] = variant_source_start
        variant["diagnostics"] = [
            item
            for item in variant["diagnostics"]
            if item["code"] != "unexpanded_variant_prose"
        ]
    return expanded


def _simple_declared_variant_suffixes(
    comments: Sequence[tuple[int, str]],
) -> list[str] | None:
    """Return an exhaustively parsed simple suffix list, or None."""

    normalized_lines = [
        _normalize_space(text.lstrip("/ "))
        for _, text in comments
        if _normalize_space(text.lstrip("/ "))
    ]
    cue_indices = [
        index
        for index, line in enumerate(normalized_lines)
        if _VARIANT_PROSE_RE.search(line)
    ]
    if len(cue_indices) != 1:
        return None

    cue_index = cue_indices[0]
    cue = _VARIANT_PROSE_RE.search(normalized_lines[cue_index])
    assert cue is not None
    tail_parts = [normalized_lines[cue_index][cue.end() :]]
    tail_parts.extend(normalized_lines[cue_index + 1 :])
    tail = " ".join(tail_parts).strip()
    if not tail or re.search(r"\b(?:if|when|unless|only)\b|__ARM", tail, re.IGNORECASE):
        return None
    if any(character in tail for character in "[]`()"):
        return None

    matches = list(_SIMPLE_VARIANT_TOKEN_RE.finditer(tail))
    if not matches:
        return None
    residual = _SIMPLE_VARIANT_TOKEN_RE.sub(" ", tail)
    residual = re.sub(r"\b(?:for|and|or|also)\b", " ", residual, flags=re.IGNORECASE)
    if re.sub(r"[\s,:;.]+", "", residual):
        return None

    suffixes: list[str] = []
    for match in matches:
        suffix = match.group(0)
        if not suffix.startswith("_"):
            suffix = f"_{suffix}"
        if suffix not in suffixes:
            suffixes.append(suffix)
    return suffixes


def _expected_variant_group(
    *,
    exemplar_name: str,
    exemplar_return_type: str,
    source_path: str,
    declaration_line: int,
    comments: Sequence[tuple[int, str]],
    variant_hints: Sequence[dict[str, Any]],
) -> dict[str, Any] | None:
    """Describe source-declared names that require inventory reconciliation.

    This interface never supplies a signature. ``exhaustive`` is true only
    when every suffix, separator, condition, and source cue was consumed and
    every suffix mapped to one unambiguous explicit spelling. A failed parse
    deliberately exposes no partial expected-name list.
    """

    if not variant_hints:
        return None

    comment_hints = _variant_hints(
        [_TextBlock([text], line, line) for line, text in comments if text.strip()]
    )
    if comment_hints == list(variant_hints):
        source_lines = comments
    else:
        source_lines = [(int(hint["line"]), str(hint["raw"])) for hint in variant_hints]

    expected, exhaustive = _parse_expected_variant_names(
        exemplar_name,
        source_lines,
        preferred_type_atoms=_c_type_name_atoms(exemplar_return_type),
    )
    if not exhaustive:
        expected = []
    first_hint_line = min(int(hint["line"]) for hint in variant_hints)
    return {
        "group_id": (
            f"acle:{source_path}:{first_hint_line}:{declaration_line}:{exemplar_name}"
        ),
        "exemplar_name": exemplar_name,
        "expected_variants": expected,
        "exhaustive": exhaustive,
    }


def _parse_expected_variant_names(
    exemplar_name: str,
    source_lines: Sequence[tuple[int, str]],
    *,
    preferred_type_atoms: frozenset[str] = frozenset(),
) -> tuple[list[dict[str, Any]], bool]:
    normalized_lines = [
        (line, _normalize_space(text.lstrip("/ ")))
        for line, text in source_lines
        if _normalize_space(text.lstrip("/ "))
    ]
    cue_locations = [
        (index, match)
        for index, (_, text) in enumerate(normalized_lines)
        if (match := _VARIANT_PROSE_RE.search(text)) is not None
    ]
    if len(cue_locations) != 1:
        orthogonal, orthogonal_ok = _parse_orthogonal_replacement_variants(
            exemplar_name,
            normalized_lines,
            cue_locations,
            preferred_type_atoms=preferred_type_atoms,
        )
        if orthogonal_ok:
            return orthogonal, True
        if not _continued_variant_cues_are_safe(normalized_lines, cue_locations):
            return [], False

    cue_index, cue = cue_locations[0]
    cue_line, cue_text = normalized_lines[cue_index]
    replacement = _REPLACEMENT_VARIANT_RE.search(cue_text)
    if replacement is not None:
        return _parse_replacement_variant(
            exemplar_name,
            cue_line=cue_line,
            cue_text=cue_text,
            cue_index=cue_index,
            source_lines=normalized_lines,
            replacement=replacement,
        )

    embedded_suffixes = list(_VARIANT_SUFFIX_FRAGMENT_RE.finditer(cue.group(0)))
    remainder = cue_text[cue.end() :]
    if len(embedded_suffixes) > 1 and re.search(
        r"\b(?:if|when|unless|only)\b|__ARM", remainder, re.IGNORECASE
    ):
        return [], False

    chunks: list[tuple[int, str]] = []
    if embedded_suffixes:
        embedded = " ".join(match.group("suffix") for match in embedded_suffixes)
        chunks.append((cue_line, f"{embedded} {remainder}".strip()))
    else:
        chunks.append((cue_line, remainder))
    chunks.extend(normalized_lines[cue_index + 1 :])

    text_parts: list[str] = []
    line_offsets: list[tuple[int, int]] = []
    sme_broadened_lines: set[int] = set()
    length = 0
    for line, text in chunks:
        text, sme_broadened = _expand_sme_variant_tag(text)
        if sme_broadened:
            sme_broadened_lines.add(line)
        if text_parts:
            text_parts.append("\n")
            length += 1
        line_offsets.append((length, line))
        text_parts.append(text)
        length += len(text)
    tail = "".join(text_parts)
    tail = re.sub(
        r"(?<![A-Za-z0-9_])\[(_[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*)\]",
        r"\1",
        tail,
    )
    tail = re.sub(r"(?<![A-Za-z0-9_])za(?=\d+\[)", "_za", tail)
    suffix_matches = list(_VARIANT_SUFFIX_FRAGMENT_RE.finditer(tail))
    if not suffix_matches:
        return [], False
    if not _variant_separator_is_consumed(tail[: suffix_matches[0].start()]):
        return [], False

    expected: list[dict[str, Any]] = []
    seen_names: dict[str, dict[str, Any]] = {}
    for index, match in enumerate(suffix_matches):
        gap_end = (
            suffix_matches[index + 1].start()
            if index + 1 < len(suffix_matches)
            else len(tail)
        )
        availability, residual, condition_ok = _variant_gap_availability(
            tail[match.end() : gap_end]
        )
        if not condition_ok or not _variant_separator_is_consumed(residual):
            return [], False

        suffix = match.group("suffix")
        explicit_name = _derive_variant_explicit_name(
            exemplar_name,
            suffix,
            preferred_type_atoms=preferred_type_atoms,
        )
        if explicit_name is None:
            return [], False
        if explicit_name == exemplar_name:
            continue
        line = max(
            source_line
            for offset, source_line in line_offsets
            if offset <= match.start()
        )
        duplicate = seen_names.get(explicit_name)
        if duplicate is not None:
            if duplicate["availability"] != availability:
                return [], False
            duplicate["line"] = max(int(duplicate["line"]), line)
            continue
        item = {
            "explicit_name": explicit_name,
            "suffix": suffix,
            "line": line,
            "availability": availability,
        }
        if line in sme_broadened_lines:
            item["availability_merge"] = "broaden_sme"
        expected.append(item)
        seen_names[explicit_name] = item
    return expected, bool(expected)


def _expand_sme_variant_tag(value: str) -> tuple[str, bool]:
    """Turn one ACLE ``[SME]`` list tag into per-variant conditions."""

    tag = re.search(r"\s*\[SME\]\s*$", value, re.IGNORECASE)
    if tag is None:
        return value, False
    body = value[: tag.start()]
    matches = list(_VARIANT_SUFFIX_FRAGMENT_RE.finditer(body))
    if not matches:
        return value, False
    parts: list[str] = []
    cursor = 0
    for match in matches:
        parts.append(body[cursor : match.end()])
        parts.append(" if __ARM_FEATURE_SME")
        cursor = match.end()
    parts.append(body[cursor:])
    return "".join(parts), True


def _continued_variant_cues_are_safe(
    source_lines: Sequence[tuple[int, str]],
    cue_locations: Sequence[tuple[int, re.Match[str]]],
) -> bool:
    if len(cue_locations) < 2:
        return False
    later_indices = {index for index, _ in cue_locations[1:]}
    return all(
        index not in later_indices
        or re.match(r"^(?:and\s+)?also\s+for\b", text, re.IGNORECASE) is not None
        for index, (_, text) in enumerate(source_lines)
    )


def _parse_orthogonal_replacement_variants(
    exemplar_name: str,
    source_lines: Sequence[tuple[int, str]],
    cue_locations: Sequence[tuple[int, re.Match[str]]],
    *,
    preferred_type_atoms: frozenset[str],
) -> tuple[list[dict[str, Any]], bool]:
    """Expand one exact name replacement across independent type variants."""

    if len(cue_locations) < 2 or len(cue_locations) != len(source_lines):
        return [], False
    replacements = [
        (index, match)
        for index, (_, text) in enumerate(source_lines)
        if (match := _REPLACEMENT_VARIANT_RE.search(text)) is not None
    ]
    if len(replacements) != 1:
        return [], False

    replacement_index, replacement_match = replacements[0]
    replacement_items, replacement_ok = _parse_expected_variant_names(
        exemplar_name,
        (source_lines[replacement_index],),
        preferred_type_atoms=preferred_type_atoms,
    )
    if not replacement_ok or len(replacement_items) != 1:
        return [], False

    type_items: list[dict[str, Any]] = []
    for index, source_line in enumerate(source_lines):
        if index == replacement_index:
            continue
        parsed, exhaustive = _parse_expected_variant_names(
            exemplar_name,
            (source_line,),
            preferred_type_atoms=preferred_type_atoms,
        )
        if not exhaustive:
            return [], False
        type_items.extend(parsed)
    if not type_items:
        return [], False

    result = [*type_items, *replacement_items]
    old_fragment = replacement_match.group("old")
    new_fragment = replacement_match.group("new")
    replacement_item = replacement_items[0]
    for item in type_items:
        combined_name = _replace_variant_explicit_fragment(
            str(item["explicit_name"]),
            old_fragment=old_fragment,
            new_fragment=new_fragment,
        )
        if combined_name is None:
            return [], False
        result.append(
            {
                "explicit_name": combined_name,
                "suffix": f"{item['suffix']} {new_fragment}",
                "line": max(int(item["line"]), int(replacement_item["line"])),
                "availability": _combine_variant_availability(
                    cast(dict[str, Any], item["availability"]),
                    cast(dict[str, Any], replacement_item["availability"]),
                ),
            }
        )

    names = [str(item["explicit_name"]) for item in result]
    return (result, len(names) == len(set(names)))


def _combine_variant_availability(
    left: dict[str, Any],
    right: dict[str, Any],
) -> dict[str, Any]:
    if left.get("op") == "always":
        return right
    if right.get("op") == "always" or left == right:
        return left
    return {"op": "all", "args": [left, right]}


def _parse_replacement_variant(
    exemplar_name: str,
    *,
    cue_line: int,
    cue_text: str,
    cue_index: int,
    source_lines: Sequence[tuple[int, str]],
    replacement: re.Match[str],
) -> tuple[list[dict[str, Any]], bool]:
    if any(text for _, text in source_lines[cue_index + 1 :]):
        return [], False
    prefix = cue_text[: replacement.start()]
    suffix = cue_text[replacement.end() :]
    if re.sub(r"[\s,:;.`*-]+", "", prefix):
        return [], False
    if not re.fullmatch(
        r"\s*(?:gives?|yields?)\s+(?:the\s+)?(?:associated|corresponding)\s+"
        r"[A-Za-z -]+\s+forms?\.?\s*",
        suffix,
        re.IGNORECASE,
    ):
        return [], False

    old_fragment = replacement.group("old")
    new_fragment = replacement.group("new")
    explicit_name = _replace_variant_explicit_fragment(
        exemplar_name,
        old_fragment=old_fragment,
        new_fragment=new_fragment,
    )
    if explicit_name is None or explicit_name == exemplar_name:
        return [], False
    return (
        [
            {
                "explicit_name": explicit_name,
                "suffix": new_fragment,
                "line": cue_line,
                "availability": {"op": "always"},
            }
        ],
        True,
    )


def _variant_gap_availability(
    value: str,
) -> tuple[dict[str, Any], str, bool]:
    normalized = _normalize_space(value)
    candidate = re.sub(r"^[,;:]\s*", "", normalized)
    outer_condition = re.match(
        r"^\(\s*(?:only\s+)?(?:if|when)\s+",
        candidate,
        re.IGNORECASE,
    )
    if outer_condition is not None:
        close_index = _matching_paren(candidate, 0)
        if close_index is None:
            return {"op": "always"}, value, False
        expression = candidate[outer_condition.end() : close_index]
        residual = candidate[close_index + 1 :]
        return _parsed_variant_availability(expression, residual)

    condition = re.match(
        r"^(?:only\s+)?(?:if|when)\s+",
        candidate,
        re.IGNORECASE,
    )
    if condition is None:
        return {"op": "always"}, value, True

    condition_tail = candidate[condition.end() :].strip()
    if condition_tail.startswith("("):
        close_index = _matching_paren(condition_tail, 0)
        if close_index is None:
            return {"op": "always"}, value, False
        expression = condition_tail[1:close_index]
        residual = condition_tail[close_index + 1 :]
        return _parsed_variant_availability(expression, residual)

    connector = re.search(
        r"\s+(?:and|or)(?:\s+also)?\s*[,;:.]?\s*$",
        condition_tail,
        re.IGNORECASE,
    )
    if connector is None:
        expression = condition_tail.rstrip(" ,;:.")
        residual = ""
    else:
        expression = condition_tail[: connector.start()].rstrip(" ,;:.")
        residual = condition_tail[connector.start() :]
    return _parsed_variant_availability(expression, residual)


def _parsed_variant_availability(
    expression: str,
    residual: str,
) -> tuple[dict[str, Any], str, bool]:
    expression = expression.replace("`", "").strip()
    if not expression:
        return {"op": "always"}, residual, False
    parsed, diagnostic = parse_availability_guard(expression)
    if diagnostic is not None:
        return {"op": "raw", "text": expression}, residual, False
    return _availability_payload(parsed), residual, True


def _variant_separator_is_consumed(value: str) -> bool:
    residual = re.sub(
        r"\(?\s*(?:with\s+)?(?:the\s+)?same\s+(?:prototype|intrinsic)\s*\)?",
        " ",
        value,
        flags=re.IGNORECASE,
    )
    residual = re.sub(
        r"\b(?:and|or|also|for|similarly)\b",
        " ",
        residual,
        flags=re.IGNORECASE,
    )
    return not re.sub(r"[\s,:;.`*\-()]+", "", residual)


def _derive_variant_explicit_name(
    exemplar_name: str,
    suffix: str,
    *,
    preferred_type_atoms: frozenset[str] = frozenset(),
) -> str | None:
    fragment = suffix if suffix.startswith("_") else f"_{suffix}"
    if fragment.count("[") != fragment.count("]"):
        return None
    explicit_fragment, _ = _expand_lockstep_name(fragment)
    if "[" in explicit_fragment or "]" in explicit_fragment:
        return None
    fragment_components = [item for item in explicit_fragment.split("_") if item]
    exemplar_components = exemplar_name.split("_")
    if not fragment_components or len(fragment_components) > len(exemplar_components):
        return None

    candidates: list[tuple[tuple[int, int], int]] = []
    width = len(fragment_components)
    for start in range(len(exemplar_components) - width + 1):
        existing = exemplar_components[start : start + width]
        if all(
            _variant_name_components_are_compatible(old, new)
            for old, new in zip(existing, fragment_components, strict=True)
        ):
            candidates.append(
                (
                    (
                        sum(
                            old == new
                            for old, new in zip(
                                existing,
                                fragment_components,
                                strict=True,
                            )
                        ),
                        sum(old in preferred_type_atoms for old in existing),
                    ),
                    start,
                )
            )
    if not candidates:
        return None
    best_score = max(score for score, _ in candidates)
    best_starts = [start for score, start in candidates if score == best_score]
    if len(best_starts) != 1:
        return None
    start = best_starts[0]
    return "_".join(
        [
            *exemplar_components[:start],
            *fragment_components,
            *exemplar_components[start + width :],
        ]
    )


def _c_type_name_atoms(type_name: str) -> frozenset[str]:
    prefixes = {
        "int": "s",
        "uint": "u",
        "float": "f",
        "bfloat": "bf",
        "mfloat": "mf",
    }
    return frozenset(
        f"{prefixes[match.group('root')]}{match.group('bits')}"
        for match in _C_TYPE_ATOM_RE.finditer(type_name)
    )


def _variant_name_components_are_compatible(old: str, new: str) -> bool:
    if old == new:
        return True
    if re.fullmatch(r"(?:bf|mf|[bcsuf])(?:8|16|32|64)", old) and re.fullmatch(
        r"(?:bf|mf|[bcsuf])(?:8|16|32|64)", new
    ):
        return True
    if re.fullmatch(r"x\d+", old) and re.fullmatch(r"x\d+", new):
        return True
    return bool(re.fullmatch(r"za\d+", old) and re.fullmatch(r"za\d+", new))


def _replace_variant_explicit_fragment(
    exemplar_name: str,
    *,
    old_fragment: str,
    new_fragment: str,
) -> str | None:
    old_components = [item for item in old_fragment.split("_") if item]
    new_components = [item for item in new_fragment.split("_") if item]
    exemplar_components = exemplar_name.split("_")
    if not old_components or len(old_components) != len(new_components):
        return None
    width = len(old_components)
    candidates = [
        start
        for start in range(len(exemplar_components) - width + 1)
        if exemplar_components[start : start + width] == old_components
    ]
    if len(candidates) != 1:
        return None
    start = candidates[0]
    return "_".join(
        [
            *exemplar_components[:start],
            *new_components,
            *exemplar_components[start + width :],
        ]
    )


def _expanded_variant_record(
    exemplar: dict[str, Any],
    *,
    suffix: str,
) -> dict[str, Any] | None:
    pattern = exemplar["names"]["pattern"]
    segments = list(_BRACKET_SEGMENT_RE.finditer(pattern))
    new_atoms = list(_TYPE_ATOM_RE.finditer(suffix))
    if len(new_atoms) != 1:
        return None
    new_atom = new_atoms[0].group("atom")

    if len(segments) == 1:
        segment = segments[0]
        old_suffix = segment.group(1)
        old_atoms = list(_TYPE_ATOM_RE.finditer(old_suffix))
        if len(old_atoms) != 1:
            return None
        old_atom = old_atoms[0].group("atom")
        if suffix == f"_{new_atom}":
            new_suffix = (
                old_suffix[: old_atoms[0].start()]
                + new_atom
                + old_suffix[old_atoms[0].end() :]
            )
        else:
            old_shape = _TYPE_ATOM_RE.sub("{type}", old_suffix)
            new_shape = _TYPE_ATOM_RE.sub("{type}", suffix)
            if old_shape != new_shape:
                return None
            new_suffix = suffix
        new_pattern = (
            pattern[: segment.start(1)] + new_suffix + pattern[segment.end(1) :]
        )
        old_tuple_context = old_suffix
        new_tuple_context = new_suffix
    elif not segments:
        old_atoms = list(_TYPE_ATOM_RE.finditer(pattern))
        if len(old_atoms) != 1:
            return None
        old_atom = old_atoms[0].group("atom")
        if suffix == f"_{new_atom}":
            new_pattern = (
                pattern[: old_atoms[0].start()]
                + new_atom
                + pattern[old_atoms[0].end() :]
            )
        else:
            expected_old_suffix = suffix.replace(new_atom, old_atom, 1)
            if pattern.count(expected_old_suffix) != 1:
                return None
            new_pattern = pattern.replace(expected_old_suffix, suffix, 1)
        old_tuple_context = pattern
        new_tuple_context = new_pattern
    else:
        return None

    if not _signature_supports_lockstep_variant(
        exemplar["signature"],
        old_atom=old_atom,
        new_atom=new_atom,
    ):
        return None

    explicit_name, overloaded_name = _expand_lockstep_name(new_pattern)
    variant = deepcopy(exemplar)
    old_explicit = exemplar["names"]["explicit"]
    variant["names"] = {
        "pattern": new_pattern,
        "explicit": explicit_name,
        "overloaded": [overloaded_name] if overloaded_name else [],
    }
    variant["variant_origin"] = "expanded_from_variant_list"
    variant["variant_group"] = None
    variant["provenance"]["fields"]["names"] = "expanded"
    variant["provenance"]["fields"]["signature"] = "expanded"

    old_tuple = _suffix_tuple_count(old_tuple_context)
    new_tuple = _suffix_tuple_count(new_tuple_context)
    signature = variant["signature"]
    signature["return_type"] = _rewrite_signature_type(
        signature["return_type"],
        old_atom=old_atom,
        new_atom=new_atom,
        old_tuple=old_tuple,
        new_tuple=new_tuple,
    )
    for parameter in signature["parameters"]:
        parameter["type"] = _rewrite_signature_type(
            parameter["type"],
            old_atom=old_atom,
            new_atom=new_atom,
            old_tuple=old_tuple,
            new_tuple=new_tuple,
        )
    raw = signature["raw"].replace(old_explicit, explicit_name, 1)
    signature["raw"] = _rewrite_signature_type(
        raw,
        old_atom=old_atom,
        new_atom=new_atom,
        old_tuple=old_tuple,
        new_tuple=new_tuple,
    )
    return variant


def _signature_supports_lockstep_variant(
    signature: dict[str, Any],
    *,
    old_atom: str,
    new_atom: str,
) -> bool:
    """Return whether every data-bearing type follows one type atom.

    Widening and narrowing declarations often list a result suffix while their
    operands follow a different, implicit width relationship. Those shapes
    require an inventory-backed signature rather than textual substitution.
    """

    def name_only_class(atom: str) -> str | None:
        if atom.startswith("c"):
            return "count"
        if atom.startswith("b") and not atom.startswith("bf"):
            return "predicate"
        return None

    old_name_only_class = name_only_class(old_atom)
    new_name_only_class = name_only_class(new_atom)
    if old_name_only_class is not None or new_name_only_class is not None:
        return (
            old_name_only_class is not None
            and old_name_only_class == new_name_only_class
        )
    if old_atom not in _TYPE_ROOTS or new_atom not in _TYPE_ROOTS:
        return False

    saw_old_atom = False

    def type_is_supported(
        type_name: str,
        *,
        parameter_name: str | None,
        is_return: bool,
    ) -> bool:
        nonlocal saw_old_atom
        for match in _C_TYPE_ATOM_RE.finditer(type_name):
            root = match.group("root")
            prefix = {
                "int": "s",
                "uint": "u",
                "float": "f",
                "bfloat": "bf",
                "mfloat": "mf",
            }[root]
            atom = f"{prefix}{match.group('bits')}"
            if atom == old_atom:
                saw_old_atom = True
                continue
            data_bearing = bool(
                is_return
                or match.group("sv")
                or match.group("vector")
                or "*" in type_name
            )
            source_fixed_index = bool(
                parameter_name and "indice" in parameter_name.lower() and atom == "u8"
            )
            source_fixed_scalar = bool(
                parameter_name
                and not data_bearing
                and _FIXED_SCALAR_PARAMETER_RE.fullmatch(parameter_name)
            )
            if not source_fixed_index and not source_fixed_scalar:
                return False
        return True

    if not type_is_supported(
        signature["return_type"],
        parameter_name=None,
        is_return=True,
    ):
        return False
    for parameter in signature["parameters"]:
        if not type_is_supported(
            parameter["type"],
            parameter_name=parameter["name"],
            is_return=False,
        ):
            return False
    return saw_old_atom


def _suffix_tuple_count(suffix: str) -> int | None:
    match = _TUPLE_SUFFIX_RE.search(suffix)
    return int(match.group("count")) if match else None


def _rewrite_signature_type(
    text: str,
    *,
    old_atom: str,
    new_atom: str,
    old_tuple: int | None,
    new_tuple: int | None,
) -> str:
    old_root = _TYPE_ROOTS.get(old_atom)
    new_root = _TYPE_ROOTS.get(new_atom)
    if old_root is None or new_root is None:
        return text

    old_bits_match = re.search(r"\d+$", old_atom)
    new_bits_match = re.search(r"\d+$", new_atom)
    assert old_bits_match is not None and new_bits_match is not None
    old_bits = int(old_bits_match.group(0))
    new_bits = int(new_bits_match.group(0))
    type_re = re.compile(
        rf"(?<![A-Za-z0-9_])(?P<sv>sv)?{re.escape(old_root)}"
        rf"(?P<vector>x(?P<count>\d+))?_t\b"
    )

    def replacement(match: re.Match[str]) -> str:
        sv_prefix = match.group("sv") or ""
        count_text = match.group("count")
        count = int(count_text) if count_text else None
        if sv_prefix and count == old_tuple and new_tuple is not None:
            count = new_tuple
        elif not sv_prefix and count is not None:
            total_bits = count * old_bits
            if total_bits % new_bits != 0:
                return match.group(0)
            count = total_bits // new_bits
        vector = f"x{count}" if count is not None else ""
        return f"{sv_prefix}{new_root}{vector}_t"

    return type_re.sub(replacement, text)


def _requirement_comment_blocks(
    comments: Sequence[tuple[int, str]],
) -> list[_TextBlock]:
    """Keep the pre-variant declaration guard separate from variant conditions.

    The pinned ACLE source places declaration-wide guards before a variant-list
    introduction. The entire remaining comment suffix belongs to that list,
    including wrapped entries that start with prose such as ``and also``.
    """

    result: list[_TextBlock] = []
    for line, text in comments:
        normalized = _normalize_space(text.lstrip("/ "))
        if not normalized:
            continue
        if _VARIANT_PROSE_RE.search(normalized):
            break
        result.append(_TextBlock([text], line, line))
    return result


def _expand_lockstep_name(pattern: str) -> tuple[str, str | None]:
    if "[" not in pattern:
        return pattern, None
    explicit = _BRACKET_SEGMENT_RE.sub(lambda match: match.group(1), pattern)
    overloaded = _BRACKET_SEGMENT_RE.sub("", pattern)
    overloaded = re.sub(r"__+", "_", overloaded)
    return explicit, overloaded


def _families_from_path(path: Sequence[str]) -> list[str]:
    joined = " / ".join(path)
    matches: list[tuple[int, str]] = []
    for prefix in ("SVE", "SME"):
        for match in re.finditer(
            rf"\b{prefix}2(?:[._]([123]))?\b|\b{prefix}\b", joined
        ):
            token = match.group(0).lower().replace("_", ".")
            matches.append((match.start(), token))
    if not matches:
        return ["general"]
    result: list[str] = []
    for _, family in sorted(matches):
        if family not in result:
            result.append(family)
    # A versioned family is more precise than its unversioned ancestor.
    for base in ("sve", "sme"):
        if any(item.startswith(base + "2") for item in result):
            result = [item for item in result if item != base]
    return result


def _extract_requirements(
    blocks: Sequence[_TextBlock],
    *,
    families: Sequence[str],
    attributes: Sequence[str],
) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    raw: list[dict[str, Any]] = []
    by_mode: dict[str, list[dict[str, Any]]] = {}
    headers: list[dict[str, Any]] = []
    architecture: list[dict[str, Any]] = []
    execution_states: list[str] = []
    features: list[str] = []
    extensions: list[str] = []
    diagnostics: list[dict[str, Any]] = []

    for block in blocks:
        for sentence in _sentences(block.text):
            headers_in_sentence = _HEADER_RE.findall(sentence)
            for header in headers_in_sentence:
                _append_unique(headers, {"name": header, "status": "explicit"})
            for match in _ARCH_RE.finditer(sentence):
                item = {
                    "op": "architecture_min",
                    "version": match.group("version"),
                }
                if match.group("profile"):
                    item["profile"] = match.group("profile")
                _append_unique(architecture, item)
            for state in _EXECUTION_STATE_RE.findall(sentence):
                if state not in execution_states:
                    execution_states.append(state)
            for feature in _FEAT_RE.findall(sentence):
                if feature not in features:
                    features.append(feature)
            for extension in re.findall(
                r"\b([A-Z][A-Z0-9_.+-]{2,}) extensions?\b", sentence
            ):
                if extension not in extensions:
                    extensions.append(extension)

            mode = _calling_mode(sentence)
            macros = _MACRO_RE.findall(sentence)
            if macros and _REQUIREMENT_CUE_RE.search(sentence):
                expression, diagnostic = _macro_expression(sentence, macros)
                if diagnostic:
                    diagnostics.append(
                        {
                            "code": "acle.availability_expression_unparsed",
                            "line": block.start_line,
                            "message": diagnostic,
                        }
                    )
                if mode:
                    by_mode.setdefault(mode, []).append(expression)
                else:
                    nodes.append(expression)
                raw.append(
                    {"line": block.start_line, "text": _normalize_space(sentence)}
                )
            elif mode == "streaming" and re.search(
                r"appropriate SME feature macro", sentence, re.IGNORECASE
            ):
                inherited_macros = sorted(
                    macro
                    for node in nodes
                    for macro in _requirement_macros_from_payload(node)
                    if macro.startswith("__ARM_FEATURE_SME")
                )
                if inherited_macros:
                    by_mode.setdefault(mode, []).append(
                        _combine_requirements(
                            [
                                {"op": "defined", "macro": macro}
                                for macro in inherited_macros
                            ]
                        )
                    )
                    raw.append(
                        {
                            "line": block.start_line,
                            "text": _normalize_space(sentence),
                        }
                    )
            elif mode == "streaming_compatible" and re.search(
                r"called from both non-streaming code and streaming code",
                sentence,
                re.IGNORECASE,
            ):
                inherited_modes = [
                    _combine_requirements(by_mode[required_mode])
                    for required_mode in ("non_streaming", "streaming")
                    if required_mode in by_mode
                ]
                if len(inherited_modes) == 2:
                    by_mode.setdefault(mode, []).append(
                        {"op": "all", "args": inherited_modes}
                    )
                    raw.append(
                        {
                            "line": block.start_line,
                            "text": _normalize_space(sentence),
                        }
                    )
            elif _REQUIREMENT_CUE_RE.search(sentence) and (
                _ARCH_RE.search(sentence) or _EXECUTION_STATE_RE.search(sentence)
            ):
                raw.append(
                    {"line": block.start_line, "text": _normalize_space(sentence)}
                )

    for attribute in attributes:
        if attribute.startswith("__arm_streaming_compatible"):
            nodes.append({"op": "calling_context", "values": ["streaming_compatible"]})
        elif attribute.startswith("__arm_streaming"):
            nodes.append({"op": "calling_context", "values": ["streaming"]})
        elif attribute.startswith("__arm_locally_streaming"):
            nodes.append({"op": "calling_context", "values": ["locally_streaming"]})

    if not headers:
        defaults = {
            "general": "arm_acle.h",
            "sve": "arm_sve.h",
            "sve2": "arm_sve.h",
            "sve2.1": "arm_sve.h",
            "sve2.2": "arm_sve.h",
            "sve2.3": "arm_sve.h",
            "sme": "arm_sme.h",
            "sme2": "arm_sme.h",
            "sme2.1": "arm_sme.h",
            "sme2.2": "arm_sme.h",
            "sme2.3": "arm_sme.h",
        }
        for family in families:
            if family in defaults:
                _append_unique(headers, {"name": defaults[family], "status": "derived"})

    expression = _combine_requirements(nodes)
    return {
        "headers": headers,
        "expression": expression,
        "by_mode": {
            mode: _combine_requirements(mode_nodes)
            for mode, mode_nodes in sorted(by_mode.items())
        },
        "minimum_architecture": architecture,
        "execution_states": execution_states,
        "features": features,
        "extensions": extensions,
        "raw": raw,
        "diagnostics": diagnostics,
    }


def _sentences(text: str) -> Iterator[str]:
    for paragraph in re.split(r"\n\s*\n", text):
        paragraph = _normalize_space(paragraph)
        if not paragraph:
            continue
        yield from (item for item in re.split(r"(?<=[.!?])\s+", paragraph) if item)


def _macro_expression(
    sentence: str,
    macros: Sequence[str],
) -> tuple[dict[str, Any], str | None]:
    """Parse one source condition without flattening mixed boolean operators."""

    macro_matches = list(_MACRO_RE.finditer(sentence))
    if not macro_matches:
        diagnostic = "The requirement sentence contains no parseable feature macro."
        return {"op": "raw", "text": _normalize_space(sentence)}, diagnostic

    code_candidate = _code_like_macro_span(sentence, macro_matches)
    if code_candidate:
        expression, diagnostic = parse_availability_guard(code_candidate)
        if diagnostic is None:
            return _availability_payload(expression), None

    atom_texts: list[str] = []
    connectors: list[tuple[str, bool]] = []
    for index, match in enumerate(macro_matches):
        if index:
            between = sentence[macro_matches[index - 1].end() : match.start()]
            connector, clause_boundary, connector_diagnostic = _prose_boolean_connector(
                between
            )
            if connector_diagnostic:
                return (
                    {"op": "raw", "text": _normalize_space(sentence)},
                    connector_diagnostic,
                )
            connectors.append((connector, clause_boundary))
        following_end = (
            macro_matches[index + 1].start()
            if index + 1 < len(macro_matches)
            else len(sentence)
        )
        following = sentence[match.end() : following_end]
        macro = match.group(0)
        if re.search(r"^\s*!=\s*0|\bnon-zero\b", following, re.IGNORECASE):
            atom_texts.append(f"{macro} != 0")
        elif re.search(r"^\s*==\s*1|\bdefined to\s+1\b", following, re.IGNORECASE):
            atom_texts.append(f"{macro} == 1")
        else:
            atom_texts.append(macro)

    expression, diagnostic = _parse_prose_boolean_expression(atom_texts, connectors)
    if diagnostic is not None:
        return (
            {"op": "raw", "text": _normalize_space(sentence)},
            f"Could not preserve availability expression: {diagnostic}",
        )
    return _availability_payload(expression), None


def _code_like_macro_span(
    sentence: str,
    macro_matches: Sequence[re.Match[str]],
) -> str | None:
    unquoted = sentence.replace("`", "")
    first_macro = macro_matches[0].group(0)
    last_macro = macro_matches[-1].group(0)
    start = unquoted.find(first_macro)
    end = unquoted.rfind(last_macro) + len(last_macro)
    if start < 0 or end <= start:
        return None
    while start > 0 and unquoted[start - 1] in " (!":
        start -= 1
    comparison = re.match(r"\s*(?:==|!=)\s*\d+", unquoted[end:])
    if comparison:
        end += comparison.end()
    while end < len(unquoted) and unquoted[end] in " )":
        end += 1
    candidate = unquoted[start:end].strip()
    return candidate if re.search(r"&&|\|\||[|!,()]", candidate) else None


def _prose_boolean_connector(value: str) -> tuple[str, bool, str | None]:
    if re.search(r"\band\s*/\s*or\b", value, re.IGNORECASE):
        return (
            "",
            False,
            (
                "The source uses the ambiguous prose connector 'and/or': "
                f"{_normalize_space(value)!r}."
            ),
        )
    has_or = bool(re.search(r"\|\||(?<!\|)\|(?!\|)|\bor\b", value, re.IGNORECASE))
    has_and = bool(re.search(r"&&|\band\b", value, re.IGNORECASE))
    if has_or and has_and:
        return (
            "",
            False,
            (
                "A macro connector contains both AND and OR without source-backed "
                f"grouping: {_normalize_space(value)!r}."
            ),
        )
    clause_boundary = "," in value
    if has_or:
        return "||", clause_boundary, None
    if has_and or clause_boundary:
        return "&&", clause_boundary, None
    return (
        "",
        False,
        (
            "No source-backed boolean connector was found between adjacent macros: "
            f"{_normalize_space(value)!r}."
        ),
    )


def _parse_prose_boolean_expression(
    atom_texts: Sequence[str],
    connectors: Sequence[tuple[str, bool]],
) -> tuple[AvailabilityExpr, str | None]:
    atoms: list[AvailabilityExpr] = []
    for atom_text in atom_texts:
        atom, diagnostic = parse_availability_guard(atom_text)
        if diagnostic is not None:
            return AvailabilityExpr.raw(" ".join(atom_texts)), diagnostic
        atoms.append(atom)

    clauses: list[list[AvailabilityExpr]] = [[atoms[0]]]
    clause_connectors: list[list[str]] = [[]]
    outer_connectors: list[str] = []
    for connector_index, (operator, boundary) in enumerate(connectors):
        if boundary:
            outer_connectors.append(operator)
            clauses.append([atoms[connector_index + 1]])
            clause_connectors.append([])
        else:
            clause_connectors[-1].append(operator)
            clauses[-1].append(atoms[connector_index + 1])

    clause_values: list[AvailabilityExpr] = []
    for clause_atoms, operators in zip(clauses, clause_connectors, strict=True):
        clause, diagnostic = _combine_prose_operands(clause_atoms, operators)
        if diagnostic is not None:
            return AvailabilityExpr.raw(" ".join(atom_texts)), diagnostic
        clause_values.append(clause)
    return _combine_prose_operands(clause_values, outer_connectors)


def _combine_prose_operands(
    operands: Sequence[AvailabilityExpr],
    operators: Sequence[str],
) -> tuple[AvailabilityExpr, str | None]:
    if len(operands) == 1:
        return operands[0], None
    unique_operators = set(operators)
    if len(unique_operators) != 1:
        return AvailabilityExpr.raw("mixed prose boolean expression"), (
            "Mixed prose boolean operators lack a source-backed clause boundary."
        )
    operator = next(iter(unique_operators))
    if operator == "&&":
        return AvailabilityExpr.all(*operands), None
    if operator == "||":
        return AvailabilityExpr.any(*operands), None
    return AvailabilityExpr.raw("unknown prose boolean operator"), (
        f"Unknown prose boolean operator: {operator!r}."
    )


def _availability_payload(expression: AvailabilityExpr) -> dict[str, Any]:
    if expression.op in {AvailabilityOp.ALL, AvailabilityOp.ANY, AvailabilityOp.NOT}:
        return {
            "op": expression.op.value,
            "args": [_availability_payload(item) for item in expression.arguments],
        }
    if expression.op is AvailabilityOp.DEFINED:
        return {"op": "defined", "macro": expression.key}
    if expression.op is AvailabilityOp.COMPARE:
        return {
            "op": "compare",
            "macro": expression.key,
            "comparator": cast(ComparisonOperator, expression.comparator).value,
            "value": expression.value,
        }
    if expression.op is AvailabilityOp.RAW:
        return {"op": "raw", "text": expression.text}
    return {"op": expression.op.value}


def _calling_mode(sentence: str) -> str | None:
    lowered = sentence.lower()
    if "streaming-compatible" in lowered:
        return "streaming_compatible"
    if "non-streaming" in lowered:
        return "non_streaming"
    if "streaming code" in lowered or "streaming mode" in lowered:
        return "streaming"
    return None


def _combine_requirements(nodes: Sequence[dict[str, Any]]) -> dict[str, Any]:
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for node in nodes:
        key = json.dumps(node, sort_keys=True)
        if key not in seen:
            seen.add(key)
            unique.append(node)
    if not unique:
        return {"op": "always"}
    if len(unique) == 1:
        return unique[0]
    return {"op": "all", "args": unique}


def _variant_hints(blocks: Sequence[_TextBlock]) -> list[dict[str, Any]]:
    hints: list[dict[str, Any]] = []
    for block in blocks:
        for offset, line in enumerate(block.lines):
            normalized = _normalize_space(line.lstrip("/ "))
            if normalized and _VARIANT_PROSE_RE.search(normalized):
                hints.append({"line": block.start_line + offset, "raw": normalized})
    return hints


def _state_access(attributes: Sequence[str]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for attribute in attributes:
        match = _STATE_ATTRIBUTE_RE.search(attribute)
        if match:
            states = re.findall(r'"([^"]+)"', match.group("states"))
            for state in states:
                _append_unique(result, {"state": state, "mode": match.group("mode")})
        elif attribute.startswith("__arm_agnostic"):
            _append_unique(result, {"state": "sme_za_state", "mode": "agnostic"})
    return result


def _instruction_relations(
    section: _Section,
    context_blocks: Sequence[_TextBlock],
) -> list[dict[str, Any]]:
    title = section.title
    result: list[dict[str, Any]] = []
    if not re.search(
        r"\b(?:intrinsics?|functions?|prototypes?|semantics?)\b", title, re.IGNORECASE
    ):
        heading_prefix = re.split(r"\s*\(", title, maxsplit=1)[0]
        tokens = [token.strip() for token in heading_prefix.split(",")]
        if tokens and all(re.fullmatch(r"[A-Z][A-Z0-9.]*", token) for token in tokens):
            result.append(
                {
                    "relation": "group",
                    "mnemonics": tokens,
                    "heading": title,
                    "guaranteed_emission": False,
                }
            )

    text = _blocks_text(context_blocks)
    generate_match = re.search(
        r"\bGenerates? (?:an? )?(?P<mnemonic>[A-Z][A-Z0-9]+)\b(?P<tail>[^.]*\.)",
        text,
    )
    if generate_match:
        tail = generate_match.group("tail")
        relation = (
            "semantic_equivalent"
            if re.search(r"\bequivalent\b|\bor nothing\b", tail)
            else "direct_access"
        )
        item = {
            "relation": relation,
            "mnemonics": [generate_match.group("mnemonic")],
            "raw": _normalize_space(generate_match.group(0)),
            "guaranteed_emission": False,
        }
        if item not in result:
            result.append(item)
    return result


def _callable_kind(section: _Section, declaration: dict[str, Any]) -> str:
    comments = " ".join(text for _, text in declaration["leading_comments"])
    path = " / ".join(item.title for item in section.ancestors())
    if re.search(r"external linkage", comments, re.IGNORECASE):
        return "support_function"
    if "Streaming-compatible versions of standard routines" in path:
        return "support_function"
    if declaration["name_pattern"].startswith("__arm_") and re.search(
        r"\bPSTATE functions\b", path, re.IGNORECASE
    ):
        return "support_function"
    return "intrinsic"


def _semantic_context(blocks: Sequence[_TextBlock]) -> str | None:
    text = _blocks_text(blocks)
    return text or None


def _collect_named_semantics(root: _Section) -> dict[str, str]:
    result: dict[str, str] = {}
    marker = re.compile(r"\*\*`(?P<name>[A-Za-z_]\w*)\(\)`\*\*")
    for section in _walk_sections(root):
        if section.title.lower() != "semantics":
            continue
        text = _blocks_text(
            block for block in section.blocks if isinstance(block, _TextBlock)
        )
        matches = list(marker.finditer(text))
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            semantics = text[match.end() : end].strip()
            if semantics:
                result[match.group("name")] = semantics
    return result


def _parse_instruction_mapping_enrichments(
    root: _Section,
    *,
    default_maturity: tuple[str, int | None],
    source_commit: str,
    source_path: str,
) -> list[dict[str, Any]]:
    """Parse signature-less SVE instruction-to-family mapping table rows."""

    enrichments: list[dict[str, Any]] = []
    link_name = re.compile(r"\[`(?P<name>sv[A-Za-z0-9_]+)`\]\(")
    for section in _walk_sections(root):
        path = [item.title for item in section.ancestors() if item.title]
        if "Mapping of SVE instructions to intrinsics" not in path:
            continue
        for block in section.blocks:
            if not isinstance(block, _TextBlock):
                continue
            for offset, line in enumerate(block.lines):
                if not line.lstrip().startswith("|"):
                    continue
                columns = [item.strip() for item in line.strip().strip("|").split("|")]
                if len(columns) != 2 or columns[0].startswith(("**", "--")):
                    continue
                names = list(dict.fromkeys(link_name.findall(columns[1])))
                if not names:
                    continue
                instruction_text = re.sub(r"[`*_]", "", columns[0]).strip()
                mnemonic_match = re.match(
                    r"(?P<mnemonic>[A-Z][A-Z0-9.]*)", instruction_text
                )
                if mnemonic_match is None:
                    continue
                mnemonic = mnemonic_match.group("mnemonic")
                relation = (
                    "optimizer_candidate"
                    if "optimization" in columns[1].lower()
                    else "group"
                )
                source_line = block.start_line + offset
                for name in names:
                    enrichments.append(
                        {
                            "match": {"names": [], "base_names": [name]},
                            # The mapping table has no ISA column. The pinned
                            # LLVM TableGen guard adapter supplies the family.
                            "family": ["sve"],
                            "header": [{"name": "arm_sve.h", "status": "derived"}],
                            "availability": {
                                "expression": {"op": "always"},
                                "by_mode": {},
                                "minimum_architecture": [],
                                "execution_states": ["AArch64"],
                                "features": [],
                                "extensions": [],
                                "raw": [],
                            },
                            "maturity": _resolved_maturity(section, default_maturity),
                            "semantics": None,
                            "instructions": [
                                {
                                    "relation": relation,
                                    "mnemonics": [mnemonic],
                                    "form": instruction_text,
                                    "guaranteed_emission": False,
                                }
                            ],
                            "state": [],
                            "taxonomy_path": path,
                            "source_signature": None,
                            "provenance": {
                                "source": {
                                    "repository": ACLE_REPOSITORY,
                                    "commit": source_commit,
                                    "path": source_path,
                                    "start_line": source_line,
                                    "end_line": source_line,
                                    "license": ACLE_MARKDOWN_LICENSE,
                                },
                                "fields": {
                                    "signature": "unresolved",
                                    "instructions": "explicit",
                                    "maturity": _resolved_maturity(
                                        section, default_maturity
                                    )["status"],
                                },
                            },
                            "diagnostics": [
                                {
                                    "code": "signature_missing_use_declaration_inventory",
                                    "line": source_line,
                                    "message": (
                                        "The ACLE mapping table names an intrinsic family "
                                        "but does not provide a callable signature."
                                    ),
                                }
                            ],
                        }
                    )
    return enrichments


def _payload_to_concrete_callable(payload: dict[str, Any], *, family: str) -> Any:
    """Build one canonical model callable from an explicit source declaration."""

    from ..model import (
        Alias,
        AvailabilityExpr,
        AvailabilityOp,
        CallableKind,
        ComparisonOperator,
        CompilationRequirements,
        ConcreteCallable,
        Constraint,
        ConstraintKind,
        Diagnostic,
        DiagnosticSeverity,
        FieldProvenance,
        InstructionMapping,
        InstructionRelationKind,
        Maturity,
        ModeAvailability,
        NameRole,
        Parameter,
        Provenance,
        ProvenanceKind,
        Semantics,
        Signature,
        SourceRef,
        StateAccess,
        StateAccessMode,
    )

    del AvailabilityExpr, AvailabilityOp, ComparisonOperator  # Used by helper imports.
    source_data = payload["provenance"]["source"]
    source = SourceRef(
        id=(
            f"acle:{source_data['path']}:"
            f"{source_data['start_line']}-{source_data['end_line']}"
        ),
        repository=source_data["repository"],
        commit=source_data["commit"],
        path=source_data["path"],
        start_line=source_data["start_line"],
        end_line=source_data["end_line"],
        license_id=source_data["license"],
        url=(
            f"https://github.com/{source_data['repository']}/blob/"
            f"{source_data['commit']}/{source_data['path']}"
        ),
    )
    explicit = Provenance(ProvenanceKind.EXPLICIT, (source,))
    expanded = Provenance(
        ProvenanceKind.EXPANDED,
        (source,),
        rule="ACLE lockstep bracket expansion",
    )
    variant_expanded = Provenance(
        ProvenanceKind.EXPANDED,
        (source,),
        rule="ACLE source-declared variant list expansion",
    )
    names_provenance = (
        variant_expanded
        if payload["variant_origin"] == "expanded_from_variant_list"
        else (expanded if payload["names"]["overloaded"] else explicit)
    )
    signature_provenance = (
        variant_expanded
        if payload["provenance"]["fields"]["signature"] == "expanded"
        else explicit
    )
    availability = _availability_to_model(payload["availability"]["expression"])
    parameters = []
    for parameter_payload in payload["signature"]["parameters"]:
        constraints = tuple(
            Constraint(
                kind=ConstraintKind(item["kind"]),
                text=item["raw"],
                parameter=parameter_payload["name"],
                provenance=signature_provenance,
            )
            for item in parameter_payload["constraints"]
        )
        parameters.append(
            Parameter(
                name=parameter_payload["name"],
                type_name=parameter_payload["type"],
                constraints=constraints,
            )
        )
    signature = Signature(
        return_type=payload["signature"]["return_type"],
        parameters=tuple(parameters),
        attributes=tuple(payload["signature"]["attributes"]),
        raw=payload["signature"]["raw"],
    )
    aliases = tuple(
        Alias(
            name=name,
            role=NameRole.OVERLOADED,
            availability=availability,
            provenance=names_provenance,
        )
        for name in payload["names"]["overloaded"]
    )
    instructions = tuple(
        InstructionMapping(
            relation=InstructionRelationKind(item["relation"]),
            mnemonic=mnemonic,
            form=item.get("form") or item.get("heading") or item.get("raw"),
            guaranteed_emission=item.get("guaranteed_emission", False),
            provenance=explicit,
        )
        for item in payload["instructions"]
        for mnemonic in item.get("mnemonics", [None])
    )
    states = tuple(
        StateAccess(
            state=item["state"],
            mode=StateAccessMode(item["mode"]),
            provenance=explicit,
        )
        for item in payload["state"]
    )
    headers = tuple(item["name"] for item in payload["header"])
    feature_macros = tuple(
        sorted(_requirement_macros_from_payload(payload["availability"]["expression"]))
    )
    mode_availability = tuple(
        ModeAvailability(
            mode=mode,
            availability=_availability_to_model(expression),
            provenance=explicit,
        )
        for mode, expression in sorted(payload["availability"]["by_mode"].items())
    )
    architecture_min, profiles = _compilation_architecture(payload["availability"])
    compilation = CompilationRequirements(
        architecture_min=architecture_min,
        profiles=profiles,
        extensions=tuple(payload["availability"]["extensions"]),
        feature_macros=feature_macros,
        headers=headers,
        execution_states=tuple(payload["availability"]["execution_states"]),
        availability=availability,
        availability_by_mode=mode_availability,
        provenance=explicit,
    )
    maturity = Maturity(payload["maturity"]["support_level"])
    semantics_text = payload["semantics"]
    semantics = Semantics(
        description=semantics_text,
        provenance=(
            explicit
            if semantics_text
            else Provenance.unresolved("No prose was associated with this declaration.")
        ),
    )
    diagnostics = tuple(
        Diagnostic(
            code=item["code"],
            message=item["message"],
            severity=DiagnosticSeverity(item.get("severity", "warning")),
            sources=(source,),
        )
        for item in payload["diagnostics"]
    )
    field_provenance = (
        FieldProvenance("signature", signature_provenance),
        FieldProvenance("names", names_provenance),
        FieldProvenance(
            "maturity",
            Provenance(
                ProvenanceKind(payload["maturity"]["status"]),
                (source,),
            ),
        ),
        FieldProvenance("availability", explicit),
        FieldProvenance(
            "semantics",
            explicit
            if semantics_text
            else Provenance.unresolved("No associated prose."),
        ),
    )
    return ConcreteCallable(
        family=family,
        name=payload["names"]["explicit"],
        signature=signature,
        kind=CallableKind(payload["kind"]),
        name_role=NameRole.TYPED,
        aliases=aliases,
        availability=availability,
        maturity=maturity,
        semantics=semantics,
        instructions=instructions,
        state_access=states,
        compilation=compilation,
        headers=headers,
        taxonomy=(tuple(payload["taxonomy_path"]),),
        sources=(source,),
        field_provenance=field_provenance,
        diagnostics=diagnostics,
    )


def _availability_to_model(node: dict[str, Any]) -> Any:
    from ..model import AvailabilityExpr, AvailabilityOp, ComparisonOperator

    op = AvailabilityOp(node["op"])
    if op in {AvailabilityOp.ALL, AvailabilityOp.ANY, AvailabilityOp.NOT}:
        return AvailabilityExpr(
            op,
            arguments=tuple(
                _availability_to_model(child) for child in node.get("args", [])
            ),
        )
    if op is AvailabilityOp.DEFINED:
        return AvailabilityExpr(op, key=node["macro"])
    if op is AvailabilityOp.COMPARE:
        return AvailabilityExpr(
            op,
            key=node["macro"],
            comparator=ComparisonOperator(node["comparator"]),
            value=node["value"],
        )
    if op in {
        AvailabilityOp.CALLING_CONTEXT,
        AvailabilityOp.EXECUTION_STATE,
        AvailabilityOp.PROFILE,
        AvailabilityOp.ARCHITECTURE_MIN,
    }:
        return AvailabilityExpr(
            op,
            key=node.get("key"),
            value=tuple(node.get("values", [])) or node.get("value"),
        )
    if op is AvailabilityOp.RAW:
        return AvailabilityExpr.raw(node["text"])
    return AvailabilityExpr(op)


def _requirement_macros_from_payload(node: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    macro = node.get("macro")
    if macro:
        result.add(macro)
    for child in node.get("args", []):
        result.update(_requirement_macros_from_payload(child))
    return result


def _compilation_architecture(
    availability: dict[str, Any],
) -> tuple[str | None, tuple[str, ...]]:
    candidates = availability["minimum_architecture"]
    if not candidates:
        return None, ()

    def version_key(item: dict[str, Any]) -> tuple[int, ...]:
        return tuple(int(part) for part in item["version"].split("."))

    selected = max(candidates, key=version_key)
    profile = selected.get("profile")
    label = f"Armv{selected['version']}" + (f"-{profile}" if profile else "")
    profiles = tuple(
        dict.fromkeys(item["profile"] for item in candidates if item.get("profile"))
    )
    return label, profiles


def _blocks_text(blocks: Iterable[_TextBlock]) -> str:
    return "\n\n".join(block.text for block in blocks if block.text).strip()


def _append_unique(items: list[Any], value: Any) -> None:
    if value not in items:
        items.append(value)


def _deduplicate_records(
    records: Sequence[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    result: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    seen: dict[tuple[str, str, str], dict[str, Any]] = {}
    for record in records:
        key = (
            ",".join(record["family"]),
            record["names"]["explicit"],
            record["signature"]["raw"],
        )
        if key in seen:
            diagnostics.append(
                {
                    "code": "duplicate_markdown_declaration",
                    "message": record["names"]["explicit"],
                    "first_line": seen[key]["provenance"]["source"]["start_line"],
                    "duplicate_line": record["provenance"]["source"]["start_line"],
                }
            )
            continue
        seen[key] = record
        result.append(record)
    return result, diagnostics
