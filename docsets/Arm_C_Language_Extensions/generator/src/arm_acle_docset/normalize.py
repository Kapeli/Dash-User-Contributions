"""Deterministic normalization and serialization for the canonical IR."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import fields, is_dataclass, replace
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping

from .model import (
    Alias,
    AvailabilityExpr,
    AvailabilityOp,
    ComparisonOperator,
    ConcreteCallable,
    ModeAvailability,
    Provenance,
    ProvenanceKind,
    Signature,
    SourceRef,
)


_BRACKET_GROUP = re.compile(r"\[([^\[\]]*)\]")
_WHITESPACE = re.compile(r"\s+")
_SLUG_SEPARATOR = re.compile(r"[^a-z0-9]+")


class _AvailabilityGuardSyntaxError(ValueError):
    def __init__(self, message: str, offset: int) -> None:
        super().__init__(message)
        self.offset = offset


class _AvailabilityGuardParser:
    """Strict recursive-descent parser for source guard expressions."""

    def __init__(self, text: str) -> None:
        self._tokens = _tokenize_availability_guard(text)
        self._index = 0

    def parse(self) -> AvailabilityExpr:
        expression = self._parse_or()
        token = self._peek()
        if token[0] != "EOF":
            self._fail(f"unexpected token {token[1]!r}", token)
        return expression

    def _parse_or(self) -> AvailabilityExpr:
        expressions = [self._parse_and()]
        while self._peek()[0] == "OR":
            self._advance()
            expressions.append(self._parse_and())
        return AvailabilityExpr.any(*expressions)

    def _parse_and(self) -> AvailabilityExpr:
        expressions = [self._parse_unary()]
        while self._peek()[0] in {"AND", "COMMA"}:
            self._advance()
            expressions.append(self._parse_unary())
        return AvailabilityExpr.all(*expressions)

    def _parse_unary(self) -> AvailabilityExpr:
        if self._peek()[0] == "NOT":
            self._advance()
            return AvailabilityExpr.not_(self._parse_unary())
        return self._parse_primary()

    def _parse_primary(self) -> AvailabilityExpr:
        token = self._peek()
        if token[0] == "LPAREN":
            self._advance()
            expression = self._parse_or()
            self._expect("RPAREN", "expected ')' to close availability group")
            return expression
        if token[0] != "IDENT":
            self._fail("expected a macro name or parenthesized expression", token)

        identifier = self._advance()[1]
        if identifier == "defined":
            return self._parse_defined()

        comparator_token = self._peek()
        if comparator_token[0] not in {"EQ", "NE"}:
            return AvailabilityExpr.defined(identifier)
        self._advance()
        number = self._expect("NUMBER", "expected a numeric comparison value")
        comparator = (
            ComparisonOperator.EQUAL
            if comparator_token[0] == "EQ"
            else ComparisonOperator.NOT_EQUAL
        )
        base = 16 if number[1].lower().startswith("0x") else 10
        return AvailabilityExpr(
            AvailabilityOp.COMPARE,
            key=identifier,
            comparator=comparator,
            value=int(number[1], base),
        )

    def _parse_defined(self) -> AvailabilityExpr:
        if self._peek()[0] == "LPAREN":
            self._advance()
            macro = self._expect("IDENT", "expected a macro name after 'defined('")
            self._expect("RPAREN", "expected ')' after defined macro")
        else:
            macro = self._expect("IDENT", "expected a macro name after 'defined'")
        return AvailabilityExpr.defined(macro[1])

    def _peek(self) -> tuple[str, str, int]:
        return self._tokens[self._index]

    def _advance(self) -> tuple[str, str, int]:
        token = self._peek()
        self._index += 1
        return token

    def _expect(
        self,
        kind: str,
        message: str,
    ) -> tuple[str, str, int]:
        token = self._peek()
        if token[0] != kind:
            self._fail(message, token)
        return self._advance()

    @staticmethod
    def _fail(message: str, token: tuple[str, str, int]) -> None:
        raise _AvailabilityGuardSyntaxError(message, token[2])


def _tokenize_availability_guard(text: str) -> tuple[tuple[str, str, int], ...]:
    tokens: list[tuple[str, str, int]] = []
    offset = 0
    while offset < len(text):
        character = text[offset]
        if character.isspace():
            offset += 1
            continue

        operators = (
            ("&&", "AND"),
            ("||", "OR"),
            ("==", "EQ"),
            ("!=", "NE"),
        )
        matched_operator = next(
            (
                (spelling, kind)
                for spelling, kind in operators
                if text.startswith(spelling, offset)
            ),
            None,
        )
        if matched_operator is not None:
            spelling, kind = matched_operator
            tokens.append((kind, spelling, offset))
            offset += len(spelling)
            continue

        punctuation = {
            "!": "NOT",
            "|": "OR",
            ",": "COMMA",
            "(": "LPAREN",
            ")": "RPAREN",
        }
        if character in punctuation:
            tokens.append((punctuation[character], character, offset))
            offset += 1
            continue

        identifier = re.match(r"[A-Za-z_][A-Za-z0-9_.+-]*", text[offset:])
        if identifier is not None:
            spelling = identifier.group(0)
            tokens.append(("IDENT", spelling, offset))
            offset += len(spelling)
            continue

        number = re.match(r"(?:0[xX][0-9A-Fa-f]+|[0-9]+)", text[offset:])
        if number is not None:
            spelling = number.group(0)
            tokens.append(("NUMBER", spelling, offset))
            offset += len(spelling)
            continue

        raise _AvailabilityGuardSyntaxError(
            f"unsupported character {character!r}",
            offset,
        )

    tokens.append(("EOF", "", len(text)))
    return tuple(tokens)


def normalize_whitespace(value: str) -> str:
    """Collapse source formatting whitespace without changing word order."""

    return _WHITESPACE.sub(" ", value).strip()


def normalize_calling_mode(value: str) -> str:
    """Return one stable key for an ACLE calling or execution mode."""

    return re.sub(r"[\s-]+", "_", normalize_whitespace(value).lower()).strip("_")


def normalize_c_type(value: str) -> str:
    """Return a conservative canonical spelling for a C type.

    This intentionally does not rewrite typedefs or reorder qualifiers. Those
    transformations would erase distinctions that adapters need to preserve.
    """

    normalized = normalize_whitespace(value)
    normalized = re.sub(r"\s*,\s*", ", ", normalized)
    normalized = re.sub(r"\s*\*\s*", "*", normalized)
    normalized = re.sub(
        r"\*+(?=[A-Za-z_])", lambda match: f"{match.group(0)} ", normalized
    )
    normalized = re.sub(r"\s+([)\]])", r"\1", normalized)
    normalized = re.sub(r"([(\[])\s+", r"\1", normalized)
    normalized = re.sub(r"\s+\(", "(", normalized)
    return normalized


def normalize_signature(signature: Signature) -> Signature:
    """Normalize type and attribute spelling while preserving parameter names."""

    parameters = tuple(
        replace(parameter, type_name=normalize_c_type(parameter.type_name))
        for parameter in signature.parameters
    )
    attributes = tuple(
        sorted({normalize_whitespace(attribute) for attribute in signature.attributes})
    )
    raw = normalize_whitespace(signature.raw) if signature.raw else None
    return replace(
        signature,
        return_type=normalize_c_type(signature.return_type),
        parameters=parameters,
        attributes=attributes,
        raw=raw,
    )


def signature_identity(signature: Signature) -> dict[str, Any]:
    """Return the signature facts that identify one concrete callable."""

    normalized = normalize_signature(signature)
    return {
        "return_type": normalized.return_type,
        "parameters": [parameter.type_name for parameter in normalized.parameters],
        "attributes": list(normalized.attributes),
    }


def normalize_availability(expression: AvailabilityExpr) -> AvailabilityExpr:
    """Canonicalize commutative availability trees for stable identity."""

    if expression.op not in {AvailabilityOp.ALL, AvailabilityOp.ANY}:
        if expression.op is AvailabilityOp.NOT:
            return AvailabilityExpr.not_(
                normalize_availability(expression.arguments[0])
            )
        return expression

    children: list[AvailabilityExpr] = []
    for child in expression.arguments:
        normalized_child = normalize_availability(child)
        if normalized_child.op is expression.op:
            children.extend(normalized_child.arguments)
        else:
            children.append(normalized_child)

    if expression.op is AvailabilityOp.ALL:
        children = [
            child for child in children if child.op is not AvailabilityOp.ALWAYS
        ]
        if not children:
            return AvailabilityExpr.always()
    elif any(child.op is AvailabilityOp.ALWAYS for child in children):
        return AvailabilityExpr.always()

    by_identity = {canonical_json(child): child for child in children}
    ordered = tuple(by_identity[key] for key in sorted(by_identity))
    if len(ordered) == 1:
        return ordered[0]
    return AvailabilityExpr(expression.op, arguments=ordered)


def parse_availability_guard(text: str) -> tuple[AvailabilityExpr, str | None]:
    """Parse a source guard without weakening malformed expressions.

    Empty input means that no guard was supplied. Any non-empty expression that
    cannot be consumed completely is retained verbatim as ``RAW`` and paired
    with a diagnostic suitable for an adapter diagnostic or unresolved note.
    """

    if not isinstance(text, str):
        raise TypeError("availability guard must be a string")
    if not text.strip():
        return AvailabilityExpr.always(), None

    try:
        parsed = _AvailabilityGuardParser(text).parse()
    except _AvailabilityGuardSyntaxError as error:
        diagnostic = (
            f"Could not parse availability guard at offset {error.offset}: {error}."
        )
        return AvailabilityExpr.raw(text), diagnostic
    return normalize_availability(parsed), None


def expand_lockstep_brackets(pattern: str) -> tuple[str, ...]:
    """Expand ACLE bracket groups as full and overloaded spellings.

    ACLE brackets move in lockstep: all groups are retained for the explicit
    spelling or all groups are removed for the overloaded spelling. They do not
    describe a Cartesian product.
    """

    if "[" not in pattern and "]" not in pattern:
        return (pattern,)

    matches = tuple(_BRACKET_GROUP.finditer(pattern))
    consumed = _BRACKET_GROUP.sub("", pattern)
    if not matches or "[" in consumed or "]" in consumed:
        raise ValueError(f"malformed bracket pattern: {pattern!r}")

    full = _BRACKET_GROUP.sub(lambda match: match.group(1), pattern)
    overloaded = _BRACKET_GROUP.sub("", pattern)
    return tuple(dict.fromkeys((full, overloaded)))


def normalize_aliases(
    aliases: Iterable[Alias],
    primary_name: str,
    inherited_availability: AvailabilityExpr,
) -> tuple[Alias, ...]:
    """Normalize alias conditions against inherited callable availability."""

    normalized_inherited = normalize_availability(inherited_availability)
    unique: dict[str, Alias] = {}
    for alias in aliases:
        if alias.name == primary_name:
            continue
        normalized_availability = (
            normalize_availability(alias.availability)
            if alias.availability is not None
            else None
        )
        if normalized_availability == normalized_inherited:
            normalized_availability = None
        normalized_alias = replace(alias, availability=normalized_availability)
        identity = canonical_json(
            {
                "name": normalized_alias.name,
                "role": normalized_alias.role,
                "availability": normalized_availability,
            }
        )
        previous = unique.get(identity)
        if previous is None:
            unique[identity] = normalized_alias
        else:
            unique[identity] = replace(
                previous,
                provenance=_merge_equivalent_provenance(
                    previous.provenance,
                    normalized_alias.provenance,
                    rule="merge-equivalent-alias-provenance",
                    note=(
                        "Equivalent alias facts were present at multiple "
                        "source locations."
                    ),
                ),
            )
    return tuple(unique[key] for key in sorted(unique))


def _merge_equivalent_provenance(
    left: Provenance,
    right: Provenance,
    *,
    rule: str,
    note: str,
) -> Provenance:
    if left == right:
        return left
    sources = _unique_source_refs((*left.sources, *right.sources))
    if left.kind is right.kind and left.rule == right.rule and left.note == right.note:
        return replace(left, sources=sources)
    return Provenance(
        ProvenanceKind.DERIVED,
        sources,
        rule=rule,
        note=note,
    )


def _unique_source_refs(sources: Iterable[SourceRef]) -> tuple[SourceRef, ...]:
    unique: dict[str, SourceRef] = {}
    for source in sources:
        key = canonical_json(source)
        unique.setdefault(key, source)
    return tuple(unique[key] for key in sorted(unique))


def normalize_families(primary: str, families: Iterable[str]) -> tuple[str, ...]:
    """Return precise, stable family memberships for one callable."""

    normalized = {
        normalize_whitespace(family) for family in (primary, *tuple(families))
    }
    for base in ("sve", "sme"):
        if any(family.startswith(f"{base}2") for family in normalized):
            normalized.discard(base)
    return tuple(sorted(normalized))


def normalize_mode_availability(
    values: Iterable[ModeAvailability],
) -> tuple[ModeAvailability, ...]:
    """Normalize one condition per mode without losing equivalent evidence."""

    unique: dict[str, ModeAvailability] = {}
    for value in values:
        normalized = replace(
            value,
            mode=normalize_calling_mode(value.mode),
            availability=normalize_availability(value.availability),
        )
        previous = unique.get(normalized.mode)
        if previous is None:
            unique[normalized.mode] = normalized
        elif previous.availability != normalized.availability:
            raise ValueError(
                "conflicting availability conditions for normalized calling "
                f"mode {normalized.mode!r}"
            )
        else:
            unique[normalized.mode] = replace(
                previous,
                provenance=_merge_equivalent_provenance(
                    previous.provenance,
                    normalized.provenance,
                    rule="merge-equivalent-mode-availability-provenance",
                    note=(
                        "Equivalent calling-mode availability facts were present "
                        "at multiple source locations."
                    ),
                ),
            )
    return tuple(unique[key] for key in sorted(unique))


def normalize_callable(callable_: ConcreteCallable) -> ConcreteCallable:
    """Normalize identity-bearing callable fields and deterministic collections."""

    normalized_signature = normalize_signature(callable_.signature)
    normalized_availability = normalize_availability(callable_.availability)
    normalized_name_availability = (
        normalize_availability(callable_.name_availability)
        if callable_.name_availability is not None
        else None
    )
    normalized_compilation = replace(
        callable_.compilation,
        availability=normalize_availability(callable_.compilation.availability),
        availability_by_mode=normalize_mode_availability(
            callable_.compilation.availability_by_mode
        ),
        compiler_flags=tuple(
            replace(
                flag,
                availability=normalize_availability(flag.availability),
            )
            for flag in callable_.compilation.compiler_flags
        ),
    )
    inherited_alias_availability = normalize_availability(
        AvailabilityExpr.all(
            normalized_availability,
            normalized_compilation.availability,
        )
    )
    aliases = normalize_aliases(
        callable_.aliases,
        callable_.name,
        inherited_alias_availability,
    )
    headers = tuple(sorted(set(callable_.headers)))
    related = tuple(sorted(set(callable_.related)))
    sources = tuple(sorted(callable_.sources, key=lambda source: source.id))
    provenance = tuple(sorted(callable_.field_provenance, key=lambda item: item.field))
    diagnostics = tuple(
        sorted(
            callable_.diagnostics,
            key=lambda diagnostic: (
                diagnostic.severity.value,
                diagnostic.code,
                diagnostic.field or "",
                diagnostic.message,
            ),
        )
    )
    families = normalize_families(callable_.family, callable_.families)
    primary_family = families[0]
    return replace(
        callable_,
        family=primary_family,
        families=families,
        name=normalize_whitespace(callable_.name),
        signature=normalized_signature,
        aliases=aliases,
        availability=normalized_availability,
        name_availability=normalized_name_availability,
        compilation=normalized_compilation,
        headers=headers,
        related=related,
        sources=sources,
        field_provenance=provenance,
        diagnostics=diagnostics,
    )


def stable_slug(value: str) -> str:
    """Create a deterministic, filesystem-safe ASCII slug."""

    ascii_value = (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
    slug = _SLUG_SEPARATOR.sub("-", ascii_value).strip("-")
    return slug or "item"


def stable_family_id(key: str) -> str:
    normalized = normalize_whitespace(key).lower()
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]
    return f"family:{stable_slug(normalized)}:{digest}"


def stable_callable_id(callable_: ConcreteCallable) -> str:
    """Return deterministic content identity, not a persistent enrichment key.

    Availability, spelling scope, and headers distinguish genuine callable
    variants, so enriching any of those identity facts intentionally changes
    the ID rather than collapsing distinct declarations onto one page.
    """

    families = normalize_families(callable_.family, callable_.families)
    identity = {
        "families": [family.lower() for family in families],
        "kind": callable_.kind.value,
        "name": normalize_whitespace(callable_.name),
        "name_role": callable_.name_role.value,
        "name_availability": (
            canonical_data(normalize_availability(callable_.name_availability))
            if callable_.name_availability is not None
            else None
        ),
        "signature": signature_identity(callable_.signature),
        "availability": canonical_data(normalize_availability(callable_.availability)),
        "headers": sorted(set(callable_.headers)),
    }
    digest = hashlib.sha256(canonical_json(identity).encode("utf-8")).hexdigest()[:16]
    return f"callable:{stable_slug(families[0])}:{stable_slug(callable_.name)}:{digest}"


def stable_callable_slug(callable_: ConcreteCallable) -> str:
    digest = stable_callable_id(callable_).rsplit(":", 1)[-1][:12]
    return f"{stable_slug(callable_.name)}-{digest}"


def canonical_data(value: Any) -> Any:
    """Convert model objects to JSON-compatible data with stable key ordering."""

    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {
            model_field.name: canonical_data(getattr(value, model_field.name))
            for model_field in fields(value)
        }
    if isinstance(value, Mapping):
        return {
            str(key): canonical_data(value[key])
            for key in sorted(value, key=lambda item: str(item))
        }
    if isinstance(value, (tuple, list)):
        return [canonical_data(item) for item in value]
    if isinstance(value, (set, frozenset)):
        converted = [canonical_data(item) for item in value]
        return sorted(converted, key=canonical_json)
    if isinstance(value, Path):
        return str(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"unsupported canonical JSON value: {type(value).__name__}")


def canonical_json(value: Any, *, indent: int | None = None) -> str:
    """Serialize a value deterministically without depending on object hashes."""

    separators = None if indent is not None else (",", ":")
    return json.dumps(
        canonical_data(value),
        allow_nan=False,
        ensure_ascii=False,
        indent=indent,
        separators=separators,
        sort_keys=True,
    )
