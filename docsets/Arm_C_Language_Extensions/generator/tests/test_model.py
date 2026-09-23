from __future__ import annotations

import json
import unittest

from arm_acle_docset.model import (
    Alias,
    AvailabilityExpr,
    CallableKind,
    CompilationRequirements,
    CompilerFlagExample,
    ConcreteCallable,
    Constraint,
    ConstraintKind,
    Diagnostic,
    DiagnosticSeverity,
    Family,
    Maturity,
    ModeAvailability,
    NameRole,
    NumericRange,
    Parameter,
    PerformanceConfidence,
    PerformanceEvidenceKind,
    PerformanceMetric,
    PerformanceRecord,
    Provenance,
    ProvenanceKind,
    Signature,
    SourceRef,
    StateAccess,
    StateAccessMode,
)
from arm_acle_docset.normalize import (
    canonical_json,
    expand_lockstep_brackets,
    normalize_availability,
    normalize_callable,
    normalize_c_type,
    parse_availability_guard,
    stable_slug,
)
from arm_acle_docset.provenance import collect_callable_sources


def source_ref() -> SourceRef:
    return SourceRef(
        id="acle-main",
        repository="ARM-software/acle",
        commit="62d9cbd68abb6d18dd8f06980da7758d9dbe0560",
        path="main/acle.md",
        start_line=3482,
        end_line=3530,
        license_id="CC-BY-SA-4.0 AND Apache-Patent-License",
    )


def signature() -> Signature:
    return Signature(
        return_type="  uint32_t ",
        parameters=(Parameter("value", " const uint32_t * "),),
        attributes=("__arm_streaming",),
    )


class CanonicalModelTests(unittest.TestCase):
    def test_lockstep_brackets_do_not_create_cartesian_product(self) -> None:
        self.assertEqual(
            expand_lockstep_brackets("svmla[_single]_za32[_s8]_vg4x2"),
            ("svmla_single_za32_s8_vg4x2", "svmla_za32_vg4x2"),
        )
        self.assertEqual(
            expand_lockstep_brackets("svld1_gather_[s32]offset[_u32]"),
            ("svld1_gather_s32offset_u32", "svld1_gather_offset"),
        )

    def test_malformed_bracket_pattern_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "malformed bracket pattern"):
            expand_lockstep_brackets("svadd[_s32")

    def test_type_normalization_is_conservative(self) -> None:
        self.assertEqual(
            normalize_c_type(" const uint32_t * restrict "), "const uint32_t* restrict"
        )
        self.assertEqual(
            normalize_c_type("svint32_t  (* fn) ( int )"), "svint32_t(* fn)(int)"
        )

    def test_callable_id_is_independent_of_parameter_names_and_condition_order(
        self,
    ) -> None:
        first = ConcreteCallable(
            family="sve2",
            name="svscale_n_bf16_z",
            signature=Signature("svbfloat16_t", (Parameter("op", "svbfloat16_t"),)),
            availability=AvailabilityExpr.all(
                AvailabilityExpr.defined("__ARM_FEATURE_SVE"),
                AvailabilityExpr.defined("__ARM_FEATURE_SVE_BFSCALE"),
            ),
        )
        second = ConcreteCallable(
            family="sve2",
            name="svscale_n_bf16_z",
            signature=Signature("svbfloat16_t", (Parameter("value", "svbfloat16_t"),)),
            availability=AvailabilityExpr.all(
                AvailabilityExpr.defined("__ARM_FEATURE_SVE_BFSCALE"),
                AvailabilityExpr.defined("__ARM_FEATURE_SVE"),
            ),
        )
        self.assertEqual(first.id, second.id)
        self.assertEqual(first.slug, second.slug)

    def test_callable_id_changes_with_concrete_signature(self) -> None:
        first = ConcreteCallable(
            family="mve",
            name="vaddq",
            signature=Signature("int32x4_t", (Parameter("a", "int32x4_t"),)),
        )
        second = ConcreteCallable(
            family="mve",
            name="vaddq",
            signature=Signature("uint32x4_t", (Parameter("a", "uint32x4_t"),)),
        )
        self.assertNotEqual(first.id, second.id)
        self.assertNotEqual(first.slug, second.slug)

    def test_callable_content_identity_includes_availability_and_headers(self) -> None:
        baseline = ConcreteCallable(
            family="general",
            name="__example",
            signature=Signature("void"),
            headers=("arm_acle.h",),
        )
        availability_variant = ConcreteCallable(
            family=baseline.family,
            name=baseline.name,
            signature=baseline.signature,
            availability=AvailabilityExpr.defined("__ARM_FEATURE_EXAMPLE"),
            headers=baseline.headers,
        )
        header_variant = ConcreteCallable(
            family=baseline.family,
            name=baseline.name,
            signature=baseline.signature,
            headers=("arm_neon.h",),
        )

        self.assertEqual(
            len(
                {
                    baseline.id,
                    availability_variant.id,
                    header_variant.id,
                }
            ),
            3,
        )
        self.assertEqual(
            len(
                {
                    baseline.slug,
                    availability_variant.slug,
                    header_variant.slug,
                }
            ),
            3,
        )

    def test_normalize_callable_deduplicates_aliases_and_collections(self) -> None:
        callable_ = ConcreteCallable(
            family=" sve ",
            name="svadd_s32_m",
            signature=signature(),
            aliases=(
                Alias("svadd_m", NameRole.OVERLOADED),
                Alias("svadd_m", NameRole.OVERLOADED),
                Alias("svadd_s32_m", NameRole.TYPED),
            ),
            headers=("arm_sve.h", "arm_sve.h"),
            related=("svsub_s32_m", "svsub_s32_m"),
            diagnostics=(
                Diagnostic("B", "warning", DiagnosticSeverity.WARNING),
                Diagnostic("A", "error", DiagnosticSeverity.ERROR),
            ),
        )
        normalized = normalize_callable(callable_)
        self.assertEqual(normalized.family, "sve")
        self.assertEqual([alias.name for alias in normalized.aliases], ["svadd_m"])
        self.assertEqual(normalized.headers, ("arm_sve.h",))
        self.assertEqual(normalized.related, ("svsub_s32_m",))
        self.assertEqual([item.code for item in normalized.diagnostics], ["A", "B"])

    def test_normalize_callable_deduplicates_compilation_availability(self) -> None:
        crc = AvailabilityExpr.defined("__ARM_FEATURE_CRC32")
        callable_ = ConcreteCallable(
            family="general",
            name="__crc32w",
            signature=Signature("uint32_t"),
            compilation=CompilationRequirements(
                availability=AvailabilityExpr.all(
                    crc,
                    AvailabilityExpr.all(crc, crc),
                )
            ),
        )

        normalized = normalize_callable(callable_)

        self.assertEqual(normalized.compilation.availability, crc)

    def test_always_is_an_identity_for_all_and_absorbs_any(self) -> None:
        crc = AvailabilityExpr.defined("__ARM_FEATURE_CRC32")

        self.assertEqual(
            normalize_availability(
                AvailabilityExpr.all(AvailabilityExpr.always(), crc)
            ),
            crc,
        )
        self.assertEqual(
            normalize_availability(
                AvailabilityExpr.any(AvailabilityExpr.always(), crc)
            ),
            AvailabilityExpr.always(),
        )

    def test_guard_parser_preserves_boolean_precedence(self) -> None:
        parsed, diagnostic = parse_availability_guard(
            "(__ARM_FEATURE_SVE2 && __ARM_FEATURE_FP8DOT2) || "
            "__ARM_FEATURE_SSVE_FP8DOT2"
        )

        self.assertIsNone(diagnostic)
        self.assertEqual(
            parsed,
            normalize_availability(
                AvailabilityExpr.any(
                    AvailabilityExpr.all(
                        AvailabilityExpr.defined("__ARM_FEATURE_SVE2"),
                        AvailabilityExpr.defined("__ARM_FEATURE_FP8DOT2"),
                    ),
                    AvailabilityExpr.defined("__ARM_FEATURE_SSVE_FP8DOT2"),
                )
            ),
        )

    def test_guard_parser_handles_parenthesized_alternatives(self) -> None:
        parsed, diagnostic = parse_availability_guard("FP8 && (SVE2 || SME2)")

        self.assertIsNone(diagnostic)
        self.assertEqual(
            parsed,
            normalize_availability(
                AvailabilityExpr.all(
                    AvailabilityExpr.defined("FP8"),
                    AvailabilityExpr.any(
                        AvailabilityExpr.defined("SVE2"),
                        AvailabilityExpr.defined("SME2"),
                    ),
                )
            ),
        )

    def test_guard_parser_supports_defined_not_comma_and_numeric_compare(
        self,
    ) -> None:
        parsed, diagnostic = parse_availability_guard(
            "defined(__ARM_FEATURE_SVE), !defined __ARM_BIG_ENDIAN, __ARM_ARCH == 9"
        )

        self.assertIsNone(diagnostic)
        self.assertEqual(parsed.op.value, "all")
        serialized = json.loads(canonical_json(parsed))
        self.assertIn(
            {
                "arguments": [],
                "comparator": "==",
                "key": "__ARM_ARCH",
                "op": "compare",
                "text": None,
                "value": 9,
            },
            serialized["arguments"],
        )

    def test_guard_parser_retains_invalid_expression_as_raw(self) -> None:
        source_text = "FP8 && (SVE2 ||) trailing"

        parsed, diagnostic = parse_availability_guard(source_text)

        self.assertEqual(parsed, AvailabilityExpr.raw(source_text))
        self.assertIsNotNone(diagnostic)
        self.assertIn("offset", diagnostic or "")

    def test_callable_identity_and_primary_are_family_order_independent(self) -> None:
        first = ConcreteCallable(
            family="sve2.1",
            families=("sve2.1", "sme2"),
            name="svclamp_f16",
            signature=Signature("svfloat16_t"),
        )
        second = ConcreteCallable(
            family="sme2",
            families=("sme2", "sve2.1"),
            name="svclamp_f16",
            signature=Signature("svfloat16_t"),
        )

        self.assertEqual(first.id, second.id)
        self.assertEqual(first.slug, second.slug)
        self.assertEqual(normalize_callable(first).family, "sme2")
        self.assertEqual(normalize_callable(second).family, "sme2")
        self.assertEqual(
            normalize_callable(first).families,
            normalize_callable(second).families,
        )

    def test_alias_normalization_preserves_condition_and_all_source_evidence(
        self,
    ) -> None:
        first_source = source_ref()
        second_source = SourceRef(
            id="acle-alias",
            repository=first_source.repository,
            commit=first_source.commit,
            path=first_source.path,
            start_line=3600,
            end_line=3601,
            license_id=first_source.license_id,
        )
        crc = AvailabilityExpr.defined("__ARM_FEATURE_CRC32")
        callable_ = ConcreteCallable(
            family="general",
            name="__crc32b",
            signature=Signature("uint32_t"),
            aliases=(
                Alias(
                    "__crc32b_alias",
                    availability=AvailabilityExpr.all(AvailabilityExpr.always(), crc),
                    provenance=Provenance(ProvenanceKind.EXPLICIT, (first_source,)),
                ),
                Alias(
                    "__crc32b_alias",
                    availability=crc,
                    provenance=Provenance(ProvenanceKind.EXPLICIT, (second_source,)),
                ),
            ),
        )

        normalized = normalize_callable(callable_)

        self.assertEqual(len(normalized.aliases), 1)
        self.assertEqual(normalized.aliases[0].availability, crc)
        self.assertEqual(
            set(normalized.aliases[0].provenance.sources),
            {first_source, second_source},
        )

    def test_alias_normalization_collapses_effective_inherited_condition(
        self,
    ) -> None:
        first_source = source_ref()
        second_source = SourceRef(
            id="acle-alias-main-condition",
            repository=first_source.repository,
            commit=first_source.commit,
            path=first_source.path,
            start_line=3600,
            end_line=3601,
            license_id=first_source.license_id,
        )
        conditional_source = SourceRef(
            id="acle-alias-distinct-condition",
            repository=first_source.repository,
            commit=first_source.commit,
            path=first_source.path,
            start_line=3610,
            end_line=3611,
            license_id=first_source.license_id,
        )
        callable_guard = AvailabilityExpr.defined("__ARM_FEATURE_SVE")
        compilation_guard = AvailabilityExpr.defined("__ARM_FEATURE_SVE2")
        alias_guard = AvailabilityExpr.defined("__ARM_FEATURE_ALIAS")
        callable_ = ConcreteCallable(
            family="sve2",
            name="svexample_s32",
            signature=Signature("svint32_t"),
            availability=callable_guard,
            compilation=CompilationRequirements(availability=compilation_guard),
            aliases=(
                Alias(
                    "svexample",
                    NameRole.OVERLOADED,
                    provenance=Provenance(
                        ProvenanceKind.EXPLICIT,
                        (first_source,),
                    ),
                ),
                Alias(
                    "svexample",
                    NameRole.OVERLOADED,
                    availability=AvailabilityExpr.all(
                        compilation_guard,
                        callable_guard,
                    ),
                    provenance=Provenance(
                        ProvenanceKind.EXPLICIT,
                        (second_source,),
                    ),
                ),
                Alias(
                    "svexample",
                    NameRole.OVERLOADED,
                    availability=alias_guard,
                    provenance=Provenance(
                        ProvenanceKind.EXPLICIT,
                        (conditional_source,),
                    ),
                ),
            ),
        )

        normalized = normalize_callable(callable_)

        self.assertEqual(len(normalized.aliases), 2)
        inherited_alias = next(
            alias for alias in normalized.aliases if alias.availability is None
        )
        conditional_alias = next(
            alias for alias in normalized.aliases if alias.availability is not None
        )
        self.assertEqual(
            set(inherited_alias.provenance.sources),
            {first_source, second_source},
        )
        self.assertEqual(conditional_alias.availability, alias_guard)
        self.assertEqual(
            conditional_alias.provenance.sources,
            (conditional_source,),
        )

    def test_compilation_requirements_are_target_and_compiler_scoped(self) -> None:
        evidence = Provenance(ProvenanceKind.EXPLICIT, sources=(source_ref(),))
        requirements = CompilationRequirements(
            architecture_min="Armv8-A",
            profiles=("A",),
            extensions=("crc",),
            feature_macros=("__ARM_FEATURE_CRC32",),
            headers=("arm_acle.h",),
            compiler_flags=(
                CompilerFlagExample(
                    compiler="clang",
                    version="22",
                    base_march="armv8-a",
                    flags=("-march=armv8-a+crc",),
                    default_enabled=False,
                    provenance=evidence,
                ),
            ),
            provenance=evidence,
        )
        callable_ = ConcreteCallable(
            family="general",
            name="__crc32b",
            signature=Signature(
                "uint32_t",
                (Parameter("acc", "uint32_t"), Parameter("value", "uint8_t")),
            ),
            compilation=requirements,
            headers=("arm_acle.h",),
        )
        data = json.loads(canonical_json(callable_))
        self.assertEqual(data["compilation"]["extensions"], ["crc"])
        self.assertEqual(
            data["compilation"]["compiler_flags"][0]["flags"],
            ["-march=armv8-a+crc"],
        )
        flag = data["compilation"]["compiler_flags"][0]
        self.assertFalse(flag["default_enabled"])
        self.assertEqual(flag["availability"]["op"], "always")
        self.assertIsNone(flag["mode"])
        self.assertIsNone(flag["target"])

    def test_compiler_flag_examples_can_be_scoped_to_guard_mode_and_target(
        self,
    ) -> None:
        crc = AvailabilityExpr.defined("__ARM_FEATURE_CRC32")
        flag = CompilerFlagExample(
            compiler="clang",
            flags=("-march=armv8-a+crc",),
            availability=AvailabilityExpr.all(AvailabilityExpr.always(), crc),
            mode="non-streaming",
            target="aarch64",
        )
        callable_ = ConcreteCallable(
            family="general",
            name="__crc32b",
            signature=Signature("uint32_t"),
            compilation=CompilationRequirements(compiler_flags=(flag,)),
        )

        normalized_flag = normalize_callable(callable_).compilation.compiler_flags[0]

        self.assertEqual(normalized_flag.availability, crc)
        self.assertEqual(normalized_flag.mode, "non-streaming")
        self.assertEqual(normalized_flag.target, "aarch64")

    def test_mode_specific_availability_and_execution_state_are_preserved(self) -> None:
        evidence = Provenance(ProvenanceKind.EXPLICIT, sources=(source_ref(),))
        requirements = CompilationRequirements(
            execution_states=("AArch64",),
            availability_by_mode=(
                ModeAvailability(
                    "non-streaming",
                    AvailabilityExpr.defined("__ARM_FEATURE_SVE2p1"),
                    evidence,
                ),
                ModeAvailability(
                    "streaming",
                    AvailabilityExpr.defined("__ARM_FEATURE_SME2"),
                    evidence,
                ),
            ),
            provenance=evidence,
        )
        data = json.loads(
            canonical_json(
                ConcreteCallable(
                    family="sme2",
                    name="svexample",
                    signature=Signature("void"),
                    compilation=requirements,
                )
            )
        )
        self.assertEqual(data["compilation"]["execution_states"], ["AArch64"])
        self.assertEqual(
            [item["mode"] for item in data["compilation"]["availability_by_mode"]],
            ["non-streaming", "streaming"],
        )

    def test_primary_name_can_have_namespace_specific_availability(self) -> None:
        name_availability = AvailabilityExpr.not_(
            AvailabilityExpr.defined("__ARM_MVE_PRESERVE_USER_NAMESPACE")
        )
        callable_ = ConcreteCallable(
            family="mve",
            name="vaddq_s32",
            name_role=NameRole.UNPREFIXED,
            name_availability=name_availability,
            signature=Signature("int32x4_t"),
            aliases=(Alias("__arm_vaddq_s32", NameRole.PREFIXED),),
        )
        data = json.loads(canonical_json(callable_))
        self.assertEqual(data["name_role"], "unprefixed")
        self.assertEqual(data["name_availability"]["op"], "not")
        self.assertEqual(data["aliases"][0]["name"], "__arm_vaddq_s32")

    def test_provenance_traversal_includes_mode_availability(self) -> None:
        evidence = Provenance(ProvenanceKind.EXPLICIT, (source_ref(),))
        callable_ = ConcreteCallable(
            family="sve2.1",
            name="svclamp_s32",
            signature=Signature("svint32_t"),
            compilation=CompilationRequirements(
                availability_by_mode=(
                    ModeAvailability(
                        "non_streaming",
                        AvailabilityExpr.defined("__ARM_FEATURE_SVE2p1"),
                        evidence,
                    ),
                )
            ),
        )

        self.assertEqual(collect_callable_sources(callable_), (source_ref(),))

    def test_provenance_traversal_rejects_conflicting_location_metadata(self) -> None:
        first = source_ref()
        conflicting = SourceRef(
            id="conflicting-license",
            repository=first.repository,
            commit=first.commit,
            path=first.path,
            start_line=first.start_line,
            end_line=first.end_line,
            license_id="Apache-2.0",
        )
        callable_ = ConcreteCallable(
            family="general",
            name="__probe",
            signature=Signature("void"),
            sources=(first,),
            aliases=(
                Alias(
                    "__probe_alias",
                    provenance=Provenance(
                        ProvenanceKind.EXPLICIT,
                        (conflicting,),
                    ),
                ),
            ),
        )

        with self.assertRaisesRegex(ValueError, "conflicting source metadata"):
            collect_callable_sources(callable_)

    def test_acle_new_and_agnostic_state_attributes_are_not_flattened(self) -> None:
        callable_ = ConcreteCallable(
            family="sme",
            name="svexample_za",
            signature=Signature("void"),
            state_access=(
                StateAccess("za", StateAccessMode.NEW),
                StateAccess("sme_za_state", StateAccessMode.AGNOSTIC),
            ),
        )
        state_access = json.loads(canonical_json(callable_))["state_access"]
        self.assertEqual(
            [(item["state"], item["mode"]) for item in state_access],
            [("za", "new"), ("sme_za_state", "agnostic")],
        )

    def test_performance_is_scoped_and_supports_intervals(self) -> None:
        evidence = Provenance(ProvenanceKind.EXPLICIT, sources=(source_ref(),))
        record = PerformanceRecord(
            microarchitecture="Example Core",
            cpu="example-cpu",
            instruction_form="ADD Z.ZZZ",
            latency=PerformanceMetric(
                NumericRange(2, 3), evidence, PerformanceConfidence.MEDIUM
            ),
            reciprocal_throughput=PerformanceMetric(
                NumericRange(0.5), evidence, PerformanceConfidence.MEDIUM
            ),
            uops=PerformanceMetric(
                NumericRange(1, unit="uops"), evidence, PerformanceConfidence.MEDIUM
            ),
            resources=("vector-pipe-0", "vector-pipe-1"),
            resources_provenance=evidence,
            evidence_kind=PerformanceEvidenceKind.MEASURED,
            provenance=evidence,
            confidence=PerformanceConfidence.MEDIUM,
        )
        callable_ = ConcreteCallable(
            family="sve",
            name="svadd_s32_m",
            signature=Signature("svint32_t", (Parameter("op1", "svint32_t"),)),
            performance=(record,),
        )
        serialized = json.loads(canonical_json(callable_))["performance"][0]
        self.assertEqual(serialized["microarchitecture"], "Example Core")
        self.assertEqual(serialized["latency"]["value"]["minimum"], 2)
        self.assertEqual(serialized["latency"]["value"]["maximum"], 3)
        self.assertEqual(serialized["evidence_kind"], "measured")

    def test_missing_performance_facts_are_explicitly_unresolved(self) -> None:
        record = PerformanceRecord(
            microarchitecture="Unknown Core",
            unresolved_reason="No redistributable performance source is available.",
        )
        self.assertFalse(record.latency.is_resolved)
        self.assertEqual(record.latency.provenance.kind, ProvenanceKind.UNRESOLVED)
        self.assertEqual(record.resources_provenance.kind, ProvenanceKind.UNRESOLVED)
        with self.assertRaisesRegex(ValueError, "missing performance value"):
            PerformanceMetric(value=None, provenance=Provenance())

    def test_non_finite_performance_values_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "must be finite"):
            NumericRange(float("nan"))
        with self.assertRaisesRegex(ValueError, "must be finite"):
            NumericRange(1, float("inf"))

    def test_semantic_constraints_and_maturity_survive_serialization(self) -> None:
        immediate = Constraint(
            ConstraintKind.RANGE,
            "The immediate must be in the range 0 to 15.",
            parameter="imm",
            value=(0, 15),
        )
        callable_ = ConcreteCallable(
            family="general",
            name="__example",
            signature=Signature(
                "void", (Parameter("imm", "unsigned int", (immediate,)),)
            ),
            kind=CallableKind.SUPPORT_FUNCTION,
            maturity=Maturity.ALPHA,
            sources=(source_ref(),),
        )
        data = json.loads(canonical_json(callable_))
        self.assertEqual(data["maturity"], "alpha")
        self.assertEqual(
            data["signature"]["parameters"][0]["constraints"][0]["value"],
            [0, 15],
        )
        self.assertTrue(data["id"].startswith("callable:general:example:"))

    def test_family_has_stable_identity(self) -> None:
        first = Family("SVE2.1", "SVE2.1", domains=("sve2",))
        second = Family("SVE2.1", "Localized title", domains=("sve2",))
        self.assertEqual(first.id, second.id)
        self.assertEqual(first.slug, "sve2-1")

    def test_slug_is_ascii_and_deterministic(self) -> None:
        self.assertEqual(stable_slug("__ARM_FEATURE_CRC32"), "arm-feature-crc32")
        self.assertEqual(stable_slug(""), "item")

    def test_source_ranges_are_validated(self) -> None:
        with self.assertRaisesRegex(ValueError, "must not precede"):
            SourceRef("x", "repo", "commit", "file", start_line=3, end_line=2)


if __name__ == "__main__":
    unittest.main()
