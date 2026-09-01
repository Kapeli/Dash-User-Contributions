"""Canonical, source-aware model for the Arm ACLE docset generator.

The model deliberately distinguishes a missing fact from a known empty value.
Adapters should attach provenance to facts they derive and use ``UNRESOLVED``
when an upstream source does not provide enough information.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Any, Iterable


class _StringEnum(str, Enum):
    """String-valued enum with useful JSON and display behaviour."""

    def __str__(self) -> str:
        return self.value


class Maturity(_StringEnum):
    RELEASE = "release"
    BETA = "beta"
    ALPHA = "alpha"
    UNSPECIFIED = "unspecified"


class ProvenanceKind(_StringEnum):
    EXPLICIT = "explicit"
    INHERITED = "inherited"
    EXPANDED = "expanded"
    DERIVED = "derived"
    MANUAL_OVERRIDE = "manual_override"
    UNRESOLVED = "unresolved"


class DiagnosticSeverity(_StringEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class CallableKind(_StringEnum):
    INTRINSIC = "intrinsic"
    SUPPORT_FUNCTION = "support_function"
    MACRO = "macro"
    TYPE = "type"
    MAPPING_ONLY = "mapping_only"
    NO_INTRINSIC = "no_intrinsic"


class NameRole(_StringEnum):
    TYPED = "typed"
    OVERLOADED = "overloaded"
    PREFIXED = "prefixed"
    UNPREFIXED = "unprefixed"
    ALTERNATE = "alternate"


class AvailabilityOp(_StringEnum):
    ALWAYS = "always"
    ALL = "all"
    ANY = "any"
    NOT = "not"
    DEFINED = "defined"
    COMPARE = "compare"
    PROFILE = "profile"
    EXECUTION_STATE = "execution_state"
    ARCHITECTURE_MIN = "architecture_min"
    CALLING_CONTEXT = "calling_context"
    RAW = "raw"


class ComparisonOperator(_StringEnum):
    EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER_OR_EQUAL = ">="
    BITWISE_AND = "&"


class ConstraintKind(_StringEnum):
    CONSTANT_EXPRESSION = "constant_expression"
    RANGE = "range"
    ENUM_SET = "enum_set"
    ALIGNMENT = "alignment"
    PREDICATE_SHAPE = "predicate_shape"
    STATE = "state"
    RAW = "raw"


class InstructionRelationKind(_StringEnum):
    SEMANTIC_EQUIVALENT = "semantic_equivalent"
    DIRECT_ACCESS = "direct_access"
    GROUP = "group"
    IMPLICIT_AUXILIARY = "implicit_auxiliary"
    OPTIMIZER_CANDIDATE = "optimizer_candidate"
    MAY_LOWER = "may_lower"
    NO_GUARANTEE = "no_guarantee"
    NONE = "none"
    UNKNOWN = "unknown"


class StateAccessMode(_StringEnum):
    IN = "in"
    OUT = "out"
    INOUT = "inout"
    NEW = "new"
    AGNOSTIC = "agnostic"
    PRESERVES = "preserves"
    SIDE_EFFECT = "side_effect"


class PerformanceConfidence(_StringEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNRESOLVED = "unresolved"


class PerformanceEvidenceKind(_StringEnum):
    OFFICIAL = "official"
    MEASURED = "measured"
    COMPILER_MODEL = "compiler_model"
    DERIVED = "derived"
    UNKNOWN = "unknown"


def _as_tuple(value: Iterable[Any] | None) -> tuple[Any, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple):
        return value
    return tuple(value)


def _require_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


@dataclass(frozen=True, slots=True)
class SourceRef:
    """A stable reference to an upstream source location."""

    id: str
    repository: str
    commit: str
    path: str
    start_line: int | None = None
    end_line: int | None = None
    license_id: str | None = None
    url: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.id, "SourceRef.id")
        _require_text(self.repository, "SourceRef.repository")
        _require_text(self.commit, "SourceRef.commit")
        _require_text(self.path, "SourceRef.path")
        if self.start_line is not None and self.start_line < 1:
            raise ValueError("SourceRef.start_line must be positive")
        if self.end_line is not None and self.end_line < 1:
            raise ValueError("SourceRef.end_line must be positive")
        if (
            self.start_line is not None
            and self.end_line is not None
            and self.end_line < self.start_line
        ):
            raise ValueError("SourceRef.end_line must not precede start_line")


@dataclass(frozen=True, slots=True)
class Provenance:
    kind: ProvenanceKind = ProvenanceKind.EXPLICIT
    sources: tuple[SourceRef, ...] = ()
    rule: str | None = None
    note: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "sources", _as_tuple(self.sources))

    @classmethod
    def unresolved(cls, note: str | None = None) -> Provenance:
        return cls(kind=ProvenanceKind.UNRESOLVED, note=note)


@dataclass(frozen=True, slots=True)
class FieldProvenance:
    field: str
    provenance: Provenance

    def __post_init__(self) -> None:
        _require_text(self.field, "FieldProvenance.field")


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    message: str
    severity: DiagnosticSeverity = DiagnosticSeverity.WARNING
    field: str | None = None
    sources: tuple[SourceRef, ...] = ()

    def __post_init__(self) -> None:
        _require_text(self.code, "Diagnostic.code")
        _require_text(self.message, "Diagnostic.message")
        object.__setattr__(self, "sources", _as_tuple(self.sources))


@dataclass(frozen=True, slots=True)
class AvailabilityExpr:
    """Boolean availability expression that preserves source conditions."""

    op: AvailabilityOp
    arguments: tuple[AvailabilityExpr, ...] = ()
    key: str | None = None
    value: str | int | tuple[str, ...] | None = None
    comparator: ComparisonOperator | None = None
    text: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "arguments", _as_tuple(self.arguments))
        if isinstance(self.value, list):
            object.__setattr__(self, "value", tuple(self.value))

        if self.op in {AvailabilityOp.ALL, AvailabilityOp.ANY}:
            if not self.arguments:
                raise ValueError(f"{self.op.value} requires at least one argument")
        elif self.op is AvailabilityOp.NOT:
            if len(self.arguments) != 1:
                raise ValueError("not requires exactly one argument")
        elif self.arguments:
            raise ValueError(f"{self.op.value} does not accept child arguments")

        if self.op is AvailabilityOp.DEFINED and not self.key:
            raise ValueError("defined requires a macro name in key")
        if self.op is AvailabilityOp.COMPARE:
            if not self.key or self.comparator is None or self.value is None:
                raise ValueError("compare requires key, comparator, and value")
        if self.op is AvailabilityOp.RAW and not self.text:
            raise ValueError("raw requires text")

    @classmethod
    def always(cls) -> AvailabilityExpr:
        return cls(AvailabilityOp.ALWAYS)

    @classmethod
    def defined(cls, macro: str) -> AvailabilityExpr:
        return cls(AvailabilityOp.DEFINED, key=macro)

    @classmethod
    def all(cls, *expressions: AvailabilityExpr) -> AvailabilityExpr:
        if not expressions:
            return cls.always()
        if len(expressions) == 1:
            return expressions[0]
        return cls(AvailabilityOp.ALL, arguments=expressions)

    @classmethod
    def any(cls, *expressions: AvailabilityExpr) -> AvailabilityExpr:
        if not expressions:
            raise ValueError("any requires at least one expression")
        if len(expressions) == 1:
            return expressions[0]
        return cls(AvailabilityOp.ANY, arguments=expressions)

    @classmethod
    def not_(cls, expression: AvailabilityExpr) -> AvailabilityExpr:
        return cls(AvailabilityOp.NOT, arguments=(expression,))

    @classmethod
    def raw(cls, text: str) -> AvailabilityExpr:
        return cls(AvailabilityOp.RAW, text=text)


@dataclass(frozen=True, slots=True)
class Constraint:
    kind: ConstraintKind
    text: str
    parameter: str | None = None
    value: Any = None
    provenance: Provenance = field(default_factory=Provenance)

    def __post_init__(self) -> None:
        _require_text(self.text, "Constraint.text")


@dataclass(frozen=True, slots=True)
class Parameter:
    name: str | None
    type_name: str
    constraints: tuple[Constraint, ...] = ()

    def __post_init__(self) -> None:
        _require_text(self.type_name, "Parameter.type_name")
        object.__setattr__(self, "constraints", _as_tuple(self.constraints))


@dataclass(frozen=True, slots=True)
class Signature:
    return_type: str
    parameters: tuple[Parameter, ...] = ()
    attributes: tuple[str, ...] = ()
    raw: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.return_type, "Signature.return_type")
        object.__setattr__(self, "parameters", _as_tuple(self.parameters))
        object.__setattr__(self, "attributes", _as_tuple(self.attributes))

    def render(self, name: str) -> str:
        rendered_parameters = ", ".join(
            f"{parameter.type_name} {parameter.name}".rstrip()
            if parameter.name
            else parameter.type_name
            for parameter in self.parameters
        )
        attributes = " ".join(self.attributes)
        prefix = f"{attributes} " if attributes else ""
        return f"{prefix}{self.return_type} {name}({rendered_parameters})"


@dataclass(frozen=True, slots=True)
class Alias:
    name: str
    role: NameRole = NameRole.ALTERNATE
    availability: AvailabilityExpr | None = None
    provenance: Provenance = field(default_factory=Provenance)

    def __post_init__(self) -> None:
        _require_text(self.name, "Alias.name")


@dataclass(frozen=True, slots=True)
class ParameterDocumentation:
    name: str
    description: str
    provenance: Provenance = field(default_factory=Provenance)

    def __post_init__(self) -> None:
        _require_text(self.name, "ParameterDocumentation.name")
        _require_text(self.description, "ParameterDocumentation.description")


@dataclass(frozen=True, slots=True)
class Semantics:
    summary: str | None = None
    description: str | None = None
    operation: str | None = None
    result: str | None = None
    parameters: tuple[ParameterDocumentation, ...] = ()
    constraints: tuple[Constraint, ...] = ()
    notes: tuple[str, ...] = ()
    provenance: Provenance = field(default_factory=Provenance.unresolved)

    def __post_init__(self) -> None:
        object.__setattr__(self, "parameters", _as_tuple(self.parameters))
        object.__setattr__(self, "constraints", _as_tuple(self.constraints))
        object.__setattr__(self, "notes", _as_tuple(self.notes))


@dataclass(frozen=True, slots=True)
class InstructionMapping:
    relation: InstructionRelationKind
    mnemonic: str | None = None
    instruction_set: str | None = None
    form: str | None = None
    argument_mapping: str | None = None
    result_mapping: str | None = None
    sequence_index: int | None = None
    guaranteed_emission: bool = False
    provenance: Provenance = field(default_factory=Provenance)

    def __post_init__(self) -> None:
        if self.sequence_index is not None and self.sequence_index < 0:
            raise ValueError("InstructionMapping.sequence_index must not be negative")


@dataclass(frozen=True, slots=True)
class StateAccess:
    state: str
    mode: StateAccessMode
    provenance: Provenance = field(default_factory=Provenance)

    def __post_init__(self) -> None:
        _require_text(self.state, "StateAccess.state")


@dataclass(frozen=True, slots=True)
class CompilerFlagExample:
    """Compiler-specific example; never a universal compilation prescription."""

    compiler: str
    version: str | None = None
    base_march: str | None = None
    flags: tuple[str, ...] = ()
    default_enabled: bool | None = None
    notes: tuple[str, ...] = ()
    provenance: Provenance = field(default_factory=Provenance)
    availability: AvailabilityExpr = field(default_factory=AvailabilityExpr.always)
    mode: str | None = None
    target: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.compiler, "CompilerFlagExample.compiler")
        if self.mode is not None:
            _require_text(self.mode, "CompilerFlagExample.mode")
        if self.target is not None:
            _require_text(self.target, "CompilerFlagExample.target")
        object.__setattr__(self, "flags", _as_tuple(self.flags))
        object.__setattr__(self, "notes", _as_tuple(self.notes))


@dataclass(frozen=True, slots=True)
class ModeAvailability:
    """Availability scoped to an ACLE calling or execution mode."""

    mode: str
    availability: AvailabilityExpr
    provenance: Provenance = field(default_factory=Provenance)

    def __post_init__(self) -> None:
        _require_text(self.mode, "ModeAvailability.mode")


@dataclass(frozen=True, slots=True)
class CompilationRequirements:
    architecture_min: str | None = None
    profiles: tuple[str, ...] = ()
    extensions: tuple[str, ...] = ()
    feature_macros: tuple[str, ...] = ()
    headers: tuple[str, ...] = ()
    execution_states: tuple[str, ...] = ()
    compiler_flags: tuple[CompilerFlagExample, ...] = ()
    availability: AvailabilityExpr = field(default_factory=AvailabilityExpr.always)
    availability_by_mode: tuple[ModeAvailability, ...] = ()
    provenance: Provenance = field(default_factory=Provenance.unresolved)
    unresolved_reason: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "profiles", _as_tuple(self.profiles))
        object.__setattr__(self, "extensions", _as_tuple(self.extensions))
        object.__setattr__(self, "feature_macros", _as_tuple(self.feature_macros))
        object.__setattr__(self, "headers", _as_tuple(self.headers))
        object.__setattr__(self, "execution_states", _as_tuple(self.execution_states))
        object.__setattr__(self, "compiler_flags", _as_tuple(self.compiler_flags))
        object.__setattr__(
            self,
            "availability_by_mode",
            _as_tuple(self.availability_by_mode),
        )

    @property
    def is_resolved(self) -> bool:
        return self.provenance.kind is not ProvenanceKind.UNRESOLVED


@dataclass(frozen=True, slots=True)
class NumericRange:
    minimum: int | float
    maximum: int | float | None = None
    unit: str = "cycles"

    def __post_init__(self) -> None:
        if isinstance(self.minimum, bool) or not isinstance(self.minimum, (int, float)):
            raise TypeError("NumericRange.minimum must be numeric")
        if not math.isfinite(self.minimum):
            raise ValueError("NumericRange.minimum must be finite")
        if self.minimum < 0:
            raise ValueError("NumericRange.minimum must not be negative")
        if self.maximum is not None:
            if isinstance(self.maximum, bool) or not isinstance(
                self.maximum, (int, float)
            ):
                raise TypeError("NumericRange.maximum must be numeric")
            if not math.isfinite(self.maximum):
                raise ValueError("NumericRange.maximum must be finite")
            if self.maximum < self.minimum:
                raise ValueError("NumericRange.maximum must not be less than minimum")
        _require_text(self.unit, "NumericRange.unit")

    @property
    def upper(self) -> int | float:
        return self.minimum if self.maximum is None else self.maximum


@dataclass(frozen=True, slots=True)
class PerformanceMetric:
    value: NumericRange | None = None
    provenance: Provenance = field(default_factory=Provenance.unresolved)
    confidence: PerformanceConfidence = PerformanceConfidence.UNRESOLVED
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "notes", _as_tuple(self.notes))
        if self.value is None and self.provenance.kind is not ProvenanceKind.UNRESOLVED:
            raise ValueError(
                "a missing performance value must have unresolved provenance"
            )
        if (
            self.value is None
            and self.confidence is not PerformanceConfidence.UNRESOLVED
        ):
            raise ValueError(
                "a missing performance value must have unresolved confidence"
            )

    @property
    def is_resolved(self) -> bool:
        return self.value is not None


@dataclass(frozen=True, slots=True)
class PerformanceRecord:
    """Performance data scoped to one microarchitecture and instruction form."""

    microarchitecture: str
    cpu: str | None = None
    instruction_form: str | None = None
    latency: PerformanceMetric = field(default_factory=PerformanceMetric)
    reciprocal_throughput: PerformanceMetric = field(default_factory=PerformanceMetric)
    uops: PerformanceMetric = field(default_factory=PerformanceMetric)
    resources: tuple[str, ...] = ()
    resources_provenance: Provenance = field(default_factory=Provenance.unresolved)
    evidence_kind: PerformanceEvidenceKind = PerformanceEvidenceKind.UNKNOWN
    provenance: Provenance = field(default_factory=Provenance.unresolved)
    confidence: PerformanceConfidence = PerformanceConfidence.UNRESOLVED
    notes: tuple[str, ...] = ()
    unresolved_reason: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.microarchitecture, "PerformanceRecord.microarchitecture")
        object.__setattr__(self, "resources", _as_tuple(self.resources))
        object.__setattr__(self, "notes", _as_tuple(self.notes))
        if (
            not self.resources
            and self.resources_provenance.kind is not ProvenanceKind.UNRESOLVED
        ):
            raise ValueError("missing resources must have unresolved provenance")


@dataclass(frozen=True, slots=True)
class ConcreteCallable:
    """One concrete callable signature rendered as one Dash page."""

    family: str
    name: str
    signature: Signature
    families: tuple[str, ...] = ()
    kind: CallableKind = CallableKind.INTRINSIC
    name_role: NameRole = NameRole.TYPED
    name_availability: AvailabilityExpr | None = None
    aliases: tuple[Alias, ...] = ()
    availability: AvailabilityExpr = field(default_factory=AvailabilityExpr.always)
    maturity: Maturity = Maturity.UNSPECIFIED
    semantics: Semantics = field(default_factory=Semantics)
    instructions: tuple[InstructionMapping, ...] = ()
    state_access: tuple[StateAccess, ...] = ()
    compilation: CompilationRequirements = field(
        default_factory=CompilationRequirements
    )
    performance: tuple[PerformanceRecord, ...] = ()
    headers: tuple[str, ...] = ()
    taxonomy: tuple[tuple[str, ...], ...] = ()
    related: tuple[str, ...] = ()
    sources: tuple[SourceRef, ...] = ()
    field_provenance: tuple[FieldProvenance, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()
    id: str = field(init=False)
    slug: str = field(init=False)

    def __post_init__(self) -> None:
        _require_text(self.family, "ConcreteCallable.family")
        _require_text(self.name, "ConcreteCallable.name")
        object.__setattr__(
            self,
            "families",
            _as_tuple(self.families) or (self.family,),
        )
        for family in self.families:
            _require_text(family, "ConcreteCallable.families")
        object.__setattr__(self, "aliases", _as_tuple(self.aliases))
        object.__setattr__(self, "instructions", _as_tuple(self.instructions))
        object.__setattr__(self, "state_access", _as_tuple(self.state_access))
        object.__setattr__(self, "performance", _as_tuple(self.performance))
        object.__setattr__(self, "headers", _as_tuple(self.headers))
        object.__setattr__(
            self,
            "taxonomy",
            tuple(tuple(path) for path in self.taxonomy),
        )
        object.__setattr__(self, "related", _as_tuple(self.related))
        object.__setattr__(self, "sources", _as_tuple(self.sources))
        object.__setattr__(self, "field_provenance", _as_tuple(self.field_provenance))
        object.__setattr__(self, "diagnostics", _as_tuple(self.diagnostics))

        from .normalize import stable_callable_id, stable_callable_slug

        object.__setattr__(self, "id", stable_callable_id(self))
        object.__setattr__(self, "slug", stable_callable_slug(self))


@dataclass(frozen=True, slots=True)
class Family:
    key: str
    title: str
    domains: tuple[str, ...] = ()
    headers: tuple[str, ...] = ()
    summary: str | None = None
    description: str | None = None
    maturity: Maturity = Maturity.UNSPECIFIED
    availability: AvailabilityExpr = field(default_factory=AvailabilityExpr.always)
    taxonomy: tuple[tuple[str, ...], ...] = ()
    provenance: Provenance = field(default_factory=Provenance)
    sources: tuple[SourceRef, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()
    id: str = field(init=False)
    slug: str = field(init=False)

    def __post_init__(self) -> None:
        _require_text(self.key, "Family.key")
        _require_text(self.title, "Family.title")
        object.__setattr__(self, "domains", _as_tuple(self.domains))
        object.__setattr__(self, "headers", _as_tuple(self.headers))
        object.__setattr__(
            self,
            "taxonomy",
            tuple(tuple(path) for path in self.taxonomy),
        )
        object.__setattr__(self, "sources", _as_tuple(self.sources))
        object.__setattr__(self, "diagnostics", _as_tuple(self.diagnostics))

        from .normalize import stable_family_id, stable_slug

        object.__setattr__(self, "id", stable_family_id(self.key))
        object.__setattr__(self, "slug", stable_slug(self.key))


@dataclass(frozen=True, slots=True)
class Catalog:
    version: str
    source_commit: str
    families: tuple[Family, ...] = ()
    callables: tuple[ConcreteCallable, ...] = ()
    provenance: Provenance = field(default_factory=Provenance)
    diagnostics: tuple[Diagnostic, ...] = ()

    def __post_init__(self) -> None:
        _require_text(self.version, "Catalog.version")
        _require_text(self.source_commit, "Catalog.source_commit")
        object.__setattr__(self, "families", _as_tuple(self.families))
        object.__setattr__(self, "callables", _as_tuple(self.callables))
        object.__setattr__(self, "diagnostics", _as_tuple(self.diagnostics))
