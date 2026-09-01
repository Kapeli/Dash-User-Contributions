from dataclasses import replace
from pathlib import Path

import pytest

from arm_acle_docset.model import (
    Alias,
    AvailabilityExpr,
    Catalog,
    CompilationRequirements,
    CompilerFlagExample,
    ConcreteCallable,
    Diagnostic,
    DiagnosticSeverity,
    InstructionMapping,
    InstructionRelationKind,
    Maturity,
    ModeAvailability,
    NameRole,
    Parameter,
    PerformanceRecord,
    Provenance,
    ProvenanceKind,
    Signature,
    SourceRef,
    Semantics,
)
from arm_acle_docset.normalize import canonical_json
from arm_acle_docset.pipeline import (
    ACLE_REPOSITORY,
    _apply_markdown_enrichments,
    _apply_llvm_neon_target_features,
    _apply_llvm_target_guards,
    _attach_feature_flags,
    _attach_performance,
    _deduplicate_callables,
    _derived_family_macros,
    _merge_compilation,
    _merge_markdown_declarations,
    _target_guard_concrete_names,
    _target_guard_macro_index,
    _translate_target_guard,
    _variant_enrichment_patch,
    _variant_signature_mappings,
    _rewrite_variant_signature,
    build_catalog,
    completeness_report,
)
from arm_acle_docset.sources.llvm import (
    LLVMCallable,
    LLVMName,
    LLVMParameter,
    LLVMPrototype,
    LLVMSourceRef,
    parse_sve_target_guards,
)
from arm_acle_docset.sources.feature_flags import (
    DEFAULT_FEATURE_FLAG_MANIFEST,
    index_feature_flags_by_macro,
)


FIXTURES = Path(__file__).parent / "fixtures"


def _source_paths() -> dict[str, Path]:
    return {
        "acle/main/acle.md": FIXTURES / "acle" / "general_crc.md",
        "acle/tools/intrinsic_db/advsimd.csv": (FIXTURES / "tabular" / "advsimd.tsv"),
        "acle/tools/intrinsic_db/advsimd_classification.csv": (
            FIXTURES / "tabular" / "advsimd_classification.tsv"
        ),
        "acle/tools/intrinsic_db/mve.csv": FIXTURES / "tabular" / "mve.tsv",
        "acle/tools/intrinsic_db/mve_classification.csv": (
            FIXTURES / "tabular" / "mve_classification.tsv"
        ),
    }


def test_build_catalog_merges_every_declaration_source() -> None:
    catalog = build_catalog(
        _source_paths(), FIXTURES / "llvm", llvm_expected_hashes=None
    )

    families = {callable_.family for callable_ in catalog.callables}
    assert {"general", "mve", "neon", "sme", "sve"} <= families
    assert "__attribute__" not in {callable_.name for callable_ in catalog.callables}
    assert len({callable_.id for callable_ in catalog.callables}) == len(
        catalog.callables
    )
    assert len({source.id for source in catalog.provenance.sources}) == len(
        catalog.provenance.sources
    )


def test_build_catalog_validates_exact_neon_header_target_features(
    tmp_path: Path,
) -> None:
    definitions = tmp_path / "advsimd.tsv"
    definitions.write_text(
        "\n".join(
            (
                "<HEADER>\tIntrinsic\tArgument preparation\tAArch64 Instruction\t"
                "Result\tSupported architectures",
                "<SECTION>\tBasic intrinsics\tThe intrinsics in this section are "
                "guarded by the macro ``__ARM_NEON``.",
                "int32x4_t vaddq_s32(int32x4_t a, int32x4_t b)\t"
                "a -> Vn.4S;b -> Vm.4S\tADD Vd.4S,Vn.4S,Vm.4S\t"
                "Vd.4S -> result\tA64",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    source_paths = _source_paths()
    source_paths["acle/tools/intrinsic_db/advsimd.csv"] = definitions

    catalog = build_catalog(
        source_paths,
        FIXTURES / "llvm",
        llvm_expected_hashes=None,
    )
    callable_ = next(
        item
        for item in catalog.callables
        if item.name == "vaddq_s32" and "neon" in item.families
    )

    assert callable_.compilation.feature_macros == ("__ARM_NEON",)
    assert any(
        item.field == "compilation.feature_macros"
        and item.provenance.rule
        and "Clang target attributes" in item.provenance.rule
        for item in callable_.field_provenance
    )
    assert not any(
        item.code
        in {
            "llvm.neon_target_features_ambiguous",
            "llvm.neon_target_features_conflict",
        }
        for item in callable_.diagnostics
    )


def test_build_catalog_fails_closed_on_neon_header_feature_conflict(
    tmp_path: Path,
) -> None:
    definitions = tmp_path / "advsimd.tsv"
    definitions.write_text(
        "\n".join(
            (
                "<HEADER>\tIntrinsic\tArgument preparation\tAArch64 Instruction\t"
                "Result\tSupported architectures",
                "<SECTION>\tFP16 Armv8.4-a",
                "int32x4_t vaddq_s32(int32x4_t a, int32x4_t b)\t"
                "a -> Vn.4S;b -> Vm.4S\tFMLAL Vd.4S,Vn.4H,Vm.4H\t"
                "Vd.4S -> result\tA64",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    source_paths = _source_paths()
    source_paths["acle/tools/intrinsic_db/advsimd.csv"] = definitions

    catalog = build_catalog(
        source_paths,
        FIXTURES / "llvm",
        llvm_expected_hashes=None,
    )
    callable_ = next(
        item
        for item in catalog.callables
        if item.name == "vaddq_s32" and "neon" in item.families
    )
    diagnostic = next(
        item
        for item in callable_.diagnostics
        if item.code == "llvm.neon_target_features_conflict"
    )

    assert diagnostic.severity.value == "error"
    assert diagnostic.field == "compilation.feature_macros"
    assert callable_.compilation.compiler_flags == ()
    assert "target-feature evidence is unresolved" in (
        callable_.compilation.unresolved_reason or ""
    )
    assert completeness_report(catalog).release_blockers >= 1


def test_neon_header_multiple_feature_sets_are_not_unioned() -> None:
    source = LLVMSourceRef(
        repository="llvm/llvm-project",
        commit="llvm-commit",
        release_tag="llvmorg-test",
        header="arm_neon.h",
        line=10,
        sha256="a" * 64,
    )
    prototype = LLVMPrototype(
        raw="int8x8_t vprobe_s8(int8x8_t value)",
        return_type="int8x8_t",
        parameters=(LLVMParameter("int8x8_t value", "int8x8_t", "value"),),
    )
    name = LLVMName(
        spelling="vprobe_s8",
        role="explicit",
        namespace="default",
        availability=None,
        source_ref=source,
    )
    llvm_callables = (
        LLVMCallable(
            family="neon",
            builtin="probe_neon",
            prototype=prototype,
            names=(name,),
            source_refs=(source,),
            target_features=("neon",),
        ),
        LLVMCallable(
            family="neon",
            builtin="probe_sha3",
            prototype=prototype,
            names=(name,),
            source_refs=(source,),
            target_features=("neon", "sha3"),
        ),
    )
    callable_ = ConcreteCallable(
        family="neon",
        name="vprobe_s8",
        signature=Signature(
            "int8x8_t",
            (Parameter("value", "int8x8_t"),),
        ),
        semantics=Semantics(summary="Basic intrinsics"),
    )

    validated = _apply_llvm_neon_target_features((callable_,), llvm_callables)[0]
    diagnostic = next(
        item
        for item in validated.diagnostics
        if item.code == "llvm.neon_target_features_ambiguous"
    )
    attached = _attach_feature_flags(
        validated,
        index_feature_flags_by_macro(DEFAULT_FEATURE_FLAG_MANIFEST),
    )

    assert diagnostic.severity.value == "error"
    assert attached.compilation.compiler_flags == ()
    assert attached.compilation.feature_macros == ("__ARM_NEON",)


def test_neon_header_missing_exact_candidate_uses_source_rule() -> None:
    callable_ = ConcreteCallable(
        family="neon",
        name="vmissing_s8",
        signature=Signature("int8x8_t"),
        semantics=Semantics(summary="Basic intrinsics"),
    )

    validated = _apply_llvm_neon_target_features((callable_,), ())[0]
    diagnostic = next(
        item
        for item in validated.diagnostics
        if item.code == "llvm.neon_target_features_missing"
    )
    attached = _attach_feature_flags(
        validated,
        index_feature_flags_by_macro(DEFAULT_FEATURE_FLAG_MANIFEST),
    )

    assert diagnostic.severity.value == "warning"
    assert attached.compilation.feature_macros == ("__ARM_NEON",)
    assert attached.compilation.compiler_flags
    assert not attached.compilation.unresolved_reason
    assert "no exact public-spelling declaration" in diagnostic.message


def _complex_variant_patch(
    expected_variants: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "match": {
            "names": ["svqshrun_n_u16_s32_x2"],
            "base_names": [],
        },
        "family": ["sve2"],
        "header": [{"name": "arm_sve.h", "status": "explicit"}],
        "availability": {
            "expression": {"op": "defined", "macro": "__ARM_FEATURE_SVE2"},
            "by_mode": {},
            "extensions": [],
            "execution_states": ["AArch64"],
        },
        "maturity": {"support_level": "release"},
        "semantics": "Saturating narrowing variant semantics.",
        "instructions": [],
        "state": [],
        "taxonomy_path": ["SVE2", "Narrowing"],
        "source_signature": {
            "return_type": "svuint16_t",
            "parameters": [
                {"type": "svuint16_t"},
                {"type": "svint32x2_t"},
            ],
            "attributes": [],
        },
        "provenance": {
            "source": {
                "repository": "ARM-software/acle",
                "commit": "acle-commit",
                "path": "main/acle.md",
                "start_line": 20,
                "end_line": 21,
                "license": "CC-BY-SA-4.0",
            }
        },
        "diagnostics": [
            {
                "code": "unexpanded_variant_prose",
                "message": "Variant for _u8[_s16_x2] is also available.",
                "severity": "error",
            }
        ],
        "variant_group": {
            "group_id": "acle:main/acle.md:20:21:svqshrun_n_u16_s32_x2",
            "exemplar_name": "svqshrun_n_u16_s32_x2",
            "expected_variants": expected_variants,
            "exhaustive": True,
        },
    }


def _llvm_variant_source(line: int) -> SourceRef:
    return SourceRef(
        id=f"llvm-variant-{line}",
        repository="llvm/llvm-project",
        commit="llvm-commit",
        path="lib/clang/22/include/arm_sve.h",
        start_line=line,
        end_line=line,
        license_id="Apache-2.0 WITH LLVM-exception",
    )


def test_sme_tag_broadens_global_and_streaming_variant_availability() -> None:
    patch = {
        "availability": {
            "expression": {
                "op": "any",
                "args": [
                    {"op": "defined", "macro": "__ARM_FEATURE_SVE2p1"},
                    {"op": "defined", "macro": "__ARM_FEATURE_SME2"},
                ],
            },
            "by_mode": {
                "non_streaming": {
                    "op": "defined",
                    "macro": "__ARM_FEATURE_SVE2p1",
                },
                "streaming": {
                    "op": "defined",
                    "macro": "__ARM_FEATURE_SME2",
                },
                "streaming_compatible": {
                    "op": "all",
                    "args": [
                        {"op": "defined", "macro": "__ARM_FEATURE_SVE2p1"},
                        {"op": "defined", "macro": "__ARM_FEATURE_SME2"},
                    ],
                },
            },
        },
        "diagnostics": (),
    }
    variant = {
        "explicit_name": "svpsel_lane_b16",
        "availability": {"op": "defined", "macro": "__ARM_FEATURE_SME"},
        "availability_merge": "broaden_sme",
    }

    result = _variant_enrichment_patch(patch, variant)
    availability = result["availability"]
    assert isinstance(availability, dict)

    expression = availability["expression"]
    assert isinstance(expression, dict)
    assert expression["args"][-1] == {
        "op": "defined",
        "macro": "__ARM_FEATURE_SME",
    }
    assert availability["by_mode"]["non_streaming"] == {
        "op": "defined",
        "macro": "__ARM_FEATURE_SVE2p1",
    }
    assert availability["by_mode"]["streaming"] == {
        "op": "defined",
        "macro": "__ARM_FEATURE_SME",
    }
    assert availability["by_mode"]["streaming_compatible"] == {
        "op": "all",
        "args": [
            {"op": "defined", "macro": "__ARM_FEATURE_SVE2p1"},
            {"op": "defined", "macro": "__ARM_FEATURE_SME"},
        ],
    }


def test_complex_variant_group_reconciles_header_inventory_atomically() -> None:
    exemplar = ConcreteCallable(
        family="sve",
        name="svqshrun_n_u16_s32_x2",
        signature=Signature(
            "svuint16_t",
            (
                Parameter("zda", "svuint16_t"),
                Parameter("zn", "svint32x2_t"),
            ),
        ),
        headers=("arm_sve.h",),
        sources=(_llvm_variant_source(100),),
        diagnostics=(
            Diagnostic(
                code="unexpanded_variant_prose",
                message="Variant list needs inventory reconciliation.",
                severity=DiagnosticSeverity.ERROR,
            ),
        ),
    )
    header_signature = Signature(
        "svuint8_t",
        (
            Parameter("zda", "svuint8_t"),
            Parameter("zn", "svint16x2_t"),
        ),
        raw=("svuint8_t svqshrun_n_u8_s16_x2(svuint8_t zda, svint16x2_t zn)"),
    )
    variant = ConcreteCallable(
        family="sme",
        name="svqshrun_n_u8_s16_x2",
        signature=header_signature,
        headers=("arm_sve.h",),
        sources=(_llvm_variant_source(101),),
    )
    patch = _complex_variant_patch(
        [
            {
                "explicit_name": "svqshrun_n_u8_s16_x2",
                "suffix": "_u8[_s16_x2]",
                "line": 20,
                "availability": {
                    "op": "defined",
                    "macro": "__ARM_FEATURE_SVE2p1",
                },
            }
        ]
    )

    reconciled = _apply_markdown_enrichments((exemplar, variant), (patch,))
    by_name = {item.name: item for item in reconciled}
    enriched_variant = by_name["svqshrun_n_u8_s16_x2"]

    assert enriched_variant.signature == header_signature
    assert enriched_variant.family == "sve2"
    assert enriched_variant.semantics.description == (
        "Saturating narrowing variant semantics."
    )
    assert enriched_variant.availability == AvailabilityExpr.all(
        AvailabilityExpr.defined("__ARM_FEATURE_SVE2"),
        AvailabilityExpr.defined("__ARM_FEATURE_SVE2p1"),
    )
    assert {
        source.start_line
        for source in enriched_variant.sources
        if source.repository == "ARM-software/acle"
    } == {20}
    assert not any(
        item.code == "unexpanded_variant_prose"
        for item in by_name["svqshrun_n_u16_s32_x2"].diagnostics
    )


def test_complex_variant_group_does_not_apply_a_partial_inventory_match() -> None:
    exemplar = ConcreteCallable(
        family="sve",
        name="svqshrun_n_u16_s32_x2",
        signature=Signature(
            "svuint16_t",
            (
                Parameter("zda", "svuint16_t"),
                Parameter("zn", "svint32x2_t"),
            ),
        ),
        headers=("arm_sve.h",),
        sources=(_llvm_variant_source(110),),
    )
    first_variant = ConcreteCallable(
        family="sve",
        name="svqshrun_n_u8_s16_x2",
        signature=Signature("svuint8_t"),
        headers=("arm_sve.h",),
        sources=(_llvm_variant_source(111),),
    )
    patch = _complex_variant_patch(
        [
            {
                "explicit_name": "svqshrun_n_u8_s16_x2",
                "suffix": "_u8[_s16_x2]",
                "line": 20,
                "availability": {"op": "always"},
            },
            {
                "explicit_name": "svqshrun_n_u8_s16_x3_lane",
                "suffix": "_u8[_s16_x3_lane]",
                "line": 20,
                "availability": {"op": "always"},
            },
        ]
    )

    reconciled = _apply_markdown_enrichments(
        (exemplar, first_variant),
        (patch,),
    )
    by_name = {item.name: item for item in reconciled}

    assert by_name["svqshrun_n_u8_s16_x2"].semantics.description is None
    exemplar_diagnostics = by_name["svqshrun_n_u16_s32_x2"].diagnostics
    assert any(
        item.code == "unexpanded_variant_prose"
        and item.severity is DiagnosticSeverity.ERROR
        for item in exemplar_diagnostics
    )
    assert any(
        item.code == "acle.variant_inventory_reconciliation_failed"
        and item.severity is DiagnosticSeverity.ERROR
        for item in exemplar_diagnostics
    )


def test_complex_variant_group_derives_missing_source_declared_signature() -> None:
    source = SourceRef(
        id="acle-variant-source",
        repository=ACLE_REPOSITORY,
        commit="acle-commit",
        path="main/acle.md",
        start_line=19,
        end_line=21,
        license_id="CC-BY-SA-4.0",
    )
    exemplar = ConcreteCallable(
        family="sve",
        name="svqshrun_n_u16_s32_x2",
        signature=Signature(
            "svuint16_t",
            (
                Parameter("zda", "svuint16_t"),
                Parameter("zn", "svint32x2_t"),
            ),
        ),
        aliases=(Alias("svqshrun_n", NameRole.OVERLOADED),),
        headers=("arm_sve.h",),
        sources=(source,),
        diagnostics=(
            Diagnostic(
                code="unexpanded_variant_prose",
                message="Variant list needs inventory reconciliation.",
                severity=DiagnosticSeverity.ERROR,
            ),
        ),
    )
    patch = _complex_variant_patch(
        [
            {
                "explicit_name": "svqshrun_n_u8_s16_x2",
                "suffix": "_u8[_s16_x2]",
                "line": 20,
                "availability": {
                    "op": "defined",
                    "macro": "__ARM_FEATURE_SVE2p3",
                },
            }
        ]
    )
    decoy = replace(
        exemplar,
        sources=(replace(source, id="acle-variant-decoy", start_line=5, end_line=5),),
        diagnostics=(),
    )
    sme_branch = replace(
        exemplar,
        family="sme",
        families=("sme",),
    )

    reconciled = _apply_markdown_enrichments(
        (decoy, exemplar, sme_branch),
        (patch,),
    )
    by_name = {item.name: item for item in reconciled}
    derived = by_name["svqshrun_n_u8_s16_x2"]

    assert derived.signature.return_type == "svuint8_t"
    assert [item.type_name for item in derived.signature.parameters] == [
        "svuint8_t",
        "svint16x2_t",
    ]
    assert derived.availability == AvailabilityExpr.all(
        AvailabilityExpr.defined("__ARM_FEATURE_SVE2"),
        AvailabilityExpr.defined("__ARM_FEATURE_SVE2p3"),
    )
    assert {item.repository for item in derived.sources} == {ACLE_REPOSITORY}
    assert any(family.startswith("sve") for family in derived.families)
    assert any(family.startswith("sme") for family in derived.families)
    resolved_exemplar = next(
        item
        for item in reconciled
        if item.name == "svqshrun_n_u16_s32_x2"
        and any(source.start_line == 19 for source in item.sources)
    )
    assert not any(
        item.code
        in {
            "unexpanded_variant_prose",
            "acle.variant_inventory_reconciliation_failed",
        }
        for item in resolved_exemplar.diagnostics
    )


def test_variant_signature_rewrite_scopes_tuple_shape_to_element_type() -> None:
    old_name = "svluti6_lane_s16_x4_s16_x2_u8_x2"
    new_name = "svluti6_lane_s16_x4_s16_x2_u8_x3"
    mappings = _variant_signature_mappings(old_name, new_name)

    assert mappings is not None
    atom_mapping, shape_mapping = mappings
    rewritten = _rewrite_variant_signature(
        Signature(
            "svint16x4_t",
            (
                Parameter("table", "svint16x2_t"),
                Parameter("indices", "svuint8x2_t"),
                Parameter("imm_idx", "uint64_t"),
            ),
        ),
        old_name=old_name,
        new_name=new_name,
        atom_mapping=atom_mapping,
        shape_mapping=shape_mapping,
    )

    assert rewritten is not None
    assert [item.type_name for item in rewritten.parameters] == [
        "svint16x2_t",
        "svuint8x3_t",
        "uint64_t",
    ]


def test_complex_variant_group_uses_source_calling_mode_over_header_mode() -> None:
    exemplar = ConcreteCallable(
        family="sve",
        name="svqshrun_n_u16_s32_x2",
        signature=Signature(
            "svuint16_t",
            (
                Parameter("zda", "svuint16_t"),
                Parameter("zn", "svint32x2_t"),
            ),
        ),
        headers=("arm_sve.h",),
        sources=(_llvm_variant_source(120),),
    )
    streaming_variant = ConcreteCallable(
        family="sve",
        name="svqshrun_n_u8_s16_x2",
        signature=Signature("svuint8_t", attributes=("__arm_streaming",)),
        headers=("arm_sve.h",),
        sources=(_llvm_variant_source(121),),
    )
    patch = _complex_variant_patch(
        [
            {
                "explicit_name": "svqshrun_n_u8_s16_x2",
                "suffix": "_u8[_s16_x2]",
                "line": 20,
                "availability": {"op": "always"},
            }
        ]
    )

    reconciled = _apply_markdown_enrichments(
        (exemplar, streaming_variant),
        (patch,),
    )

    by_name = {item.name: item for item in reconciled}

    assert not any(
        item.code == "acle.variant_inventory_reconciliation_failed"
        for item in by_name["svqshrun_n_u16_s32_x2"].diagnostics
    )
    assert by_name["svqshrun_n_u8_s16_x2"].signature.attributes == ()


def test_complex_variant_group_accepts_header_without_calling_mode_annotation() -> None:
    exemplar = ConcreteCallable(
        family="sme",
        name="svqshrun_n_u16_s32_x2",
        signature=Signature(
            "svuint16_t",
            (
                Parameter("zda", "svuint16_t"),
                Parameter("zn", "svint32x2_t"),
            ),
            attributes=("__arm_streaming",),
        ),
        headers=("arm_sme.h",),
        sources=(_llvm_variant_source(130),),
        diagnostics=(
            Diagnostic(
                code="unexpanded_variant_prose",
                message="Variant list needs inventory reconciliation.",
                severity=DiagnosticSeverity.ERROR,
            ),
        ),
    )
    variant = ConcreteCallable(
        family="sme",
        name="svqshrun_n_u8_s16_x2",
        signature=Signature("svuint8_t"),
        headers=("arm_sme.h",),
        sources=(_llvm_variant_source(131),),
    )
    patch = _complex_variant_patch(
        [
            {
                "explicit_name": "svqshrun_n_u8_s16_x2",
                "suffix": "_u8[_s16_x2]",
                "line": 20,
                "availability": {"op": "always"},
            }
        ]
    )
    patch["family"] = ["sme2"]
    patch["header"] = [{"name": "arm_sme.h", "status": "explicit"}]
    source_signature = patch["source_signature"]
    assert isinstance(source_signature, dict)
    source_signature["attributes"] = ["__arm_streaming"]

    reconciled = _apply_markdown_enrichments((exemplar, variant), (patch,))
    by_name = {item.name: item for item in reconciled}

    assert not any(
        item.code == "acle.variant_inventory_reconciliation_failed"
        for item in by_name["svqshrun_n_u16_s32_x2"].diagnostics
    )
    assert by_name["svqshrun_n_u8_s16_x2"].signature.attributes == ("__arm_streaming",)
    assert by_name["svqshrun_n_u8_s16_x2"].semantics.description == (
        "Saturating narrowing variant semantics."
    )


def test_neon_header_uniform_spelling_features_survive_signature_drift() -> None:
    source = LLVMSourceRef(
        repository="llvm/llvm-project",
        commit="llvm-commit",
        release_tag="llvmorg-test",
        header="arm_neon.h",
        line=10,
        sha256="a" * 64,
    )
    candidate = LLVMCallable(
        family="neon",
        builtin="probe",
        prototype=LLVMPrototype(
            raw="int8x8_t vprobe_s8(uint8x8_t value)",
            return_type="int8x8_t",
            parameters=(LLVMParameter("uint8x8_t value", "uint8x8_t", "value"),),
        ),
        names=(
            LLVMName(
                spelling="vprobe_s8",
                role="explicit",
                namespace="default",
                availability=None,
                source_ref=source,
            ),
        ),
        source_refs=(source,),
        target_features=("neon",),
    )
    callable_ = ConcreteCallable(
        family="neon",
        name="vprobe_s8",
        signature=Signature(
            "int8x8_t",
            (Parameter("value", "int8x8_t"),),
        ),
        semantics=Semantics(summary="Basic intrinsics"),
    )

    validated = _apply_llvm_neon_target_features((callable_,), (candidate,))[0]
    diagnostic = next(
        item
        for item in validated.diagnostics
        if item.code == "llvm.neon_signature_drift"
    )
    attached = _attach_feature_flags(
        validated,
        index_feature_flags_by_macro(DEFAULT_FEATURE_FLAG_MANIFEST),
    )

    assert diagnostic.severity is DiagnosticSeverity.WARNING
    assert "none has the exact Arm ACLE tabular signature" in diagnostic.message
    assert attached.compilation.feature_macros == ("__ARM_NEON",)
    assert attached.compilation.compiler_flags


def test_crc_pipeline_preserves_feature_gate_and_compiler_flag_examples() -> None:
    catalog = build_catalog(
        _source_paths(), FIXTURES / "llvm", llvm_expected_hashes=None
    )
    crc = next(
        callable_ for callable_ in catalog.callables if callable_.name == "__crc32b"
    )

    assert "__ARM_FEATURE_CRC32" in crc.compilation.feature_macros
    assert "__ARM_NEON" not in crc.compilation.feature_macros
    assert crc.family == "general"
    assert crc.maturity.value == "release"
    assert "arm_acle.h" in crc.compilation.headers
    assert "arm_neon.h" not in crc.compilation.headers
    assert all(mapping.instruction_set is None for mapping in crc.instructions)
    assert "checksum" in (crc.semantics.description or "").lower()
    assert any(
        "+crc" in flag
        for example in crc.compilation.compiler_flags
        for flag in example.flags
    )
    assert all(
        not source.path.startswith("/")
        for callable_ in catalog.callables
        for source in callable_.sources
    )
    neon = next(
        callable_ for callable_ in catalog.callables if callable_.name == "vadd_s8"
    )
    assert any(
        source.path == "tools/intrinsic_db/advsimd.csv"
        and source.url
        == (
            "https://github.com/ARM-software/acle/blob/"
            f"{source.commit}/tools/intrinsic_db/advsimd.csv#L4"
        )
        for source in neon.sources
    )
    assert any(
        source.path == "tools/intrinsic_db/advsimd_classification.csv"
        and source.url
        == (
            "https://github.com/ARM-software/acle/blob/"
            f"{source.commit}/tools/intrinsic_db/advsimd_classification.csv#L2"
        )
        for source in neon.sources
    )
    assert str(FIXTURES.resolve()) not in canonical_json(catalog)
    assert {
        source.license_id
        for example in crc.compilation.compiler_flags
        for source in example.provenance.sources
        if source.repository == "gcc.gnu.org/onlinedocs"
    } == {"GFDL-1.3-invariants-or-later"}


def test_fixture_catalog_has_no_release_blocker() -> None:
    report = completeness_report(
        build_catalog(_source_paths(), FIXTURES / "llvm", llvm_expected_hashes=None)
    )

    assert report.callables > 0
    assert report.release_blockers == 0


def test_signature_matched_enrichment_does_not_cross_contaminate_overloads() -> None:
    f16 = ConcreteCallable(
        family="sve",
        name="svclamp_f16",
        signature=Signature(
            "svfloat16_t",
            (
                Parameter(None, "svfloat16_t"),
                Parameter(None, "svfloat16_t"),
                Parameter(None, "svfloat16_t"),
            ),
        ),
        aliases=(Alias("svclamp", NameRole.OVERLOADED),),
    )
    bf16 = ConcreteCallable(
        family="sve",
        name="svclamp_bf16",
        signature=Signature(
            "svbfloat16_t",
            (
                Parameter(None, "svbfloat16_t"),
                Parameter(None, "svbfloat16_t"),
                Parameter(None, "svbfloat16_t"),
            ),
        ),
        aliases=(Alias("svclamp", NameRole.OVERLOADED),),
    )
    patch = {
        "match": {"names": ["svclamp_f16", "svclamp"], "base_names": []},
        "family": ["sve2.1", "sme2"],
        "header": [{"name": "arm_sve.h"}, {"name": "arm_sme.h"}],
        "availability": {
            "expression": {"op": "always"},
            "by_mode": {},
            "execution_states": ["AArch64"],
            "extensions": [],
        },
        "maturity": {"support_level": "beta"},
        "semantics": "Floating-point clamp.",
        "instructions": [],
        "state": [],
        "taxonomy_path": ["SVE2.1 and SME2", "FCLAMP"],
        "source_signature": {
            "return_type": "svfloat16_t",
            "parameters": [
                {"name": "op", "type": "svfloat16_t"},
                {"name": "minimum", "type": "svfloat16_t"},
                {"name": "maximum", "type": "svfloat16_t"},
            ],
            "attributes": [],
        },
        "provenance": {
            "source": {
                "path": "main/acle.md",
                "start_line": 13480,
                "end_line": 13480,
            }
        },
        "diagnostics": [],
    }

    enriched = _apply_markdown_enrichments((f16, bf16), (patch,))
    enriched_f16 = next(item for item in enriched if item.name == "svclamp_f16")
    enriched_bf16 = next(item for item in enriched if item.name == "svclamp_bf16")

    assert enriched_f16.semantics.description == "Floating-point clamp."
    assert enriched_f16.families == ("sme2", "sve2.1")
    assert enriched_bf16.semantics.description is None
    assert enriched_bf16.families == ("sve",)


def test_multi_family_mode_requirements_remain_alternatives() -> None:
    source_paths = _source_paths()
    source_paths["acle/main/acle.md"] = FIXTURES / "acle" / "sve_sme.md"
    catalog = build_catalog(source_paths, FIXTURES / "llvm", llvm_expected_hashes=None)
    clamp = next(
        callable_ for callable_ in catalog.callables if callable_.name == "svclamp_s32"
    )

    assert clamp.families == ("sme2", "sve2.1")
    expected_global = AvailabilityExpr.any(
        AvailabilityExpr.defined("__ARM_FEATURE_SME2"),
        AvailabilityExpr.defined("__ARM_FEATURE_SVE2p1"),
    )
    assert clamp.availability == expected_global
    assert clamp.compilation.availability == expected_global
    assert set(clamp.compilation.feature_macros) >= {
        "__ARM_FEATURE_SME2",
        "__ARM_FEATURE_SVE2p1",
    }
    assert "__ARM_FEATURE_SME" not in clamp.compilation.feature_macros
    assert "__ARM_FEATURE_SVE" not in clamp.compilation.feature_macros
    assert {
        mode.mode: mode.availability for mode in clamp.compilation.availability_by_mode
    } == {
        "non_streaming": AvailabilityExpr.defined("__ARM_FEATURE_SVE2p1"),
        "streaming": AvailabilityExpr.defined("__ARM_FEATURE_SME2"),
    }
    non_streaming_flags = [
        example
        for example in clamp.compilation.compiler_flags
        if example.mode == "non_streaming"
    ]
    streaming_flags = [
        example
        for example in clamp.compilation.compiler_flags
        if example.mode == "streaming"
    ]
    global_flags = [
        example for example in clamp.compilation.compiler_flags if example.mode is None
    ]
    assert not global_flags
    assert non_streaming_flags
    assert streaming_flags
    assert {example.mode for example in clamp.compilation.compiler_flags} == {
        "non_streaming",
        "streaming",
    }
    assert all(example.target == "aarch64" for example in non_streaming_flags)
    assert any(
        "+sve2p1" in flag for example in non_streaming_flags for flag in example.flags
    )
    assert any("+sme2" in flag for example in streaming_flags for flag in example.flags)
    assert not any(
        "+sme2" in flag for example in non_streaming_flags for flag in example.flags
    )
    assert not any(
        "+sve2p1" in flag for example in streaming_flags for flag in example.flags
    )
    assert set((clamp.compilation.architecture_min or "").split(" / ")) == {
        "Armv9.3-A",
        "Armv9.4-A",
    }


def test_acle_mode_availability_overrides_llvm_guard_fallback() -> None:
    llvm_source = SourceRef(
        "llvm-td",
        "llvm/llvm-project",
        "llvm-commit",
        "clang/include/clang/Basic/arm_sve.td",
        10,
        10,
    )
    acle_source = SourceRef(
        "acle-spec",
        "ARM-software/acle",
        "acle-commit",
        "main/acle.md",
        20,
        22,
    )
    llvm_gate = AvailabilityExpr.any(
        AvailabilityExpr.defined("__ARM_FEATURE_SME2"),
        AvailabilityExpr.defined("__ARM_FEATURE_SVE2p1"),
    )
    left = CompilationRequirements(
        availability_by_mode=(
            ModeAvailability(
                "Non Streaming",
                llvm_gate,
                Provenance(ProvenanceKind.EXPLICIT, (llvm_source,)),
            ),
            ModeAvailability(
                "streaming",
                llvm_gate,
                Provenance(ProvenanceKind.EXPLICIT, (llvm_source,)),
            ),
        )
    )
    right = CompilationRequirements(
        availability_by_mode=(
            ModeAvailability(
                "non-streaming",
                AvailabilityExpr.defined("__ARM_FEATURE_SVE2p1"),
                Provenance(ProvenanceKind.EXPLICIT, (acle_source,)),
            ),
            ModeAvailability(
                "streaming",
                AvailabilityExpr.defined("__ARM_FEATURE_SME2"),
                Provenance(ProvenanceKind.EXPLICIT, (acle_source,)),
            ),
            ModeAvailability(
                "streaming-compatible",
                AvailabilityExpr.all(
                    AvailabilityExpr.defined("__ARM_FEATURE_SME2"),
                    AvailabilityExpr.defined("__ARM_FEATURE_SVE2p1"),
                ),
                Provenance(ProvenanceKind.EXPLICIT, (acle_source,)),
            ),
        )
    )

    merged = _merge_compilation(
        left,
        right,
        prefer_right_mode_availability=True,
    )

    assert {item.mode: item.availability for item in merged.availability_by_mode} == {
        "non_streaming": AvailabilityExpr.defined("__ARM_FEATURE_SVE2p1"),
        "streaming": AvailabilityExpr.defined("__ARM_FEATURE_SME2"),
        "streaming_compatible": AvailabilityExpr.all(
            AvailabilityExpr.defined("__ARM_FEATURE_SME2"),
            AvailabilityExpr.defined("__ARM_FEATURE_SVE2p1"),
        ),
    }
    assert all(
        item.provenance.sources == (acle_source,)
        for item in merged.availability_by_mode
    )


def test_equal_authority_mode_conflicts_fail_closed() -> None:
    left = CompilationRequirements(
        availability_by_mode=(
            ModeAvailability(
                "streaming",
                AvailabilityExpr.defined("__ARM_FEATURE_SME"),
            ),
        )
    )
    right = CompilationRequirements(
        availability_by_mode=(
            ModeAvailability(
                "Streaming",
                AvailabilityExpr.defined("__ARM_FEATURE_SME2"),
            ),
        )
    )

    with pytest.raises(ValueError, match="conflicting availability conditions"):
        _merge_compilation(left, right)


def test_explicit_feature_or_is_not_tightened_by_classified_families() -> None:
    availability = AvailabilityExpr.any(
        AvailabilityExpr.defined("__ARM_FEATURE_SME"),
        AvailabilityExpr.defined("__ARM_FEATURE_SVE2p1"),
    )
    callable_ = ConcreteCallable(
        family="sme",
        families=("sme", "sve2", "sve2.1"),
        name="svclamp_s32",
        signature=Signature("svint32_t"),
        availability=availability,
        compilation=CompilationRequirements(
            feature_macros=("__ARM_FEATURE_SME", "__ARM_FEATURE_SVE2p1"),
            availability=availability,
            execution_states=("AArch64",),
        ),
    )

    attached = _attach_feature_flags(
        callable_,
        index_feature_flags_by_macro(DEFAULT_FEATURE_FLAG_MANIFEST),
    )

    assert attached.availability == availability
    assert attached.compilation.availability == availability
    assert set(attached.compilation.feature_macros) == {
        "__ARM_FEATURE_SME",
        "__ARM_FEATURE_SVE2p1",
    }
    sme_examples = [
        example
        for example in attached.compilation.compiler_flags
        if _branch_macros(example.availability) == {"__ARM_FEATURE_SME"}
    ]
    assert sme_examples
    assert all(
        "+sve2" not in flag for example in sme_examples for flag in example.flags
    )


def test_exact_manifest_macro_gates_are_preserved() -> None:
    feature_index = index_feature_flags_by_macro(DEFAULT_FEATURE_FLAG_MANIFEST)
    mve = ConcreteCallable(
        family="mve",
        name="vabdq_f32",
        signature=Signature("float32x4_t", (Parameter("a", "float32x4_t"),)),
        compilation=CompilationRequirements(
            feature_macros=("__ARM_FEATURE_MVE",),
            availability=AvailabilityExpr.defined("__ARM_FEATURE_MVE"),
            execution_states=("AArch32",),
        ),
    )
    cde = ConcreteCallable(
        family="general",
        name="__arm_cx1",
        signature=Signature("uint32_t", (Parameter("coproc", "uint32_t"),)),
        compilation=CompilationRequirements(
            feature_macros=("__ARM_FEATURE_CDE_COPROC",),
            availability=AvailabilityExpr.defined("__ARM_FEATURE_CDE_COPROC"),
            execution_states=("AArch32",),
        ),
    )

    attached_mve = _attach_feature_flags(mve, feature_index)
    attached_cde = _attach_feature_flags(cde, feature_index)

    assert attached_mve.availability == AvailabilityExpr.raw(
        "(__ARM_FEATURE_MVE & 0x3) == 0x3"
    )
    assert attached_mve.compilation.compiler_flags
    assert any(
        "+mve.fp" in flag
        for example in attached_mve.compilation.compiler_flags
        for flag in example.flags
    )
    assert attached_cde.availability == AvailabilityExpr.raw(
        "(__ARM_FEATURE_CDE_COPROC & (1u << N)) != 0"
    )
    assert not attached_cde.compilation.compiler_flags
    assert "raw condition" in (attached_cde.compilation.unresolved_reason or "")


def test_performance_matching_checks_every_callable_family() -> None:
    callable_ = ConcreteCallable(
        family="sme",
        families=("sme", "sve"),
        name="svadd_s32_x",
        signature=Signature(
            "svint32_t",
            (
                Parameter("pg", "svbool_t"),
                Parameter("op1", "svint32_t"),
                Parameter("op2", "svint32_t"),
            ),
        ),
    )
    sve_record = PerformanceRecord(
        microarchitecture="Neoverse N2",
        cpu="neoverse-n2",
        instruction_form="ADD Zdn.S, Pg/M, Zdn.S, Zm.S",
    )

    attached = _attach_performance(callable_, (sve_record,))

    assert attached.performance == (sve_record,)


def test_sve2_mapping_reclassifies_svaddlb_and_uses_sve2_flags() -> None:
    callable_ = ConcreteCallable(
        family="sve",
        name="svaddlb_s16",
        signature=Signature(
            "svint16_t",
            (Parameter(None, "svint8_t"), Parameter(None, "svint8_t")),
        ),
        aliases=(Alias("svaddlb", NameRole.OVERLOADED),),
    )
    patch = {
        "match": {"names": [], "base_names": ["svaddlb"]},
        "family": ["sve2"],
        "header": [{"name": "arm_sve.h"}],
        "availability": {
            "expression": {"op": "always"},
            "by_mode": {},
            "execution_states": ["AArch64"],
            "extensions": [],
        },
        "maturity": {"support_level": "release"},
        "semantics": None,
        "instructions": [
            {
                "relation": "group",
                "mnemonics": ["SADDLB"],
                "form": "SADDLB",
            }
        ],
        "state": [],
        "taxonomy_path": ["Mapping of SVE instructions to intrinsics"],
        "source_signature": None,
        "provenance": {
            "source": {
                "path": "main/acle.md",
                "start_line": 9154,
                "end_line": 9154,
            }
        },
        "diagnostics": [],
    }
    enriched = _apply_markdown_enrichments((callable_,), (patch,))[0]
    attached = _attach_feature_flags(
        enriched,
        index_feature_flags_by_macro(DEFAULT_FEATURE_FLAG_MANIFEST),
    )

    assert attached.family == "sve2"
    assert attached.families == ("sve2",)
    assert "__ARM_FEATURE_SVE2" in attached.compilation.feature_macros
    assert "__ARM_FEATURE_SVE" not in attached.compilation.feature_macros
    assert "sve2" in attached.compilation.extensions
    assert any(
        "+sve2" in flag
        for example in attached.compilation.compiler_flags
        for flag in example.flags
    )


def test_neon_vaddq_u32_has_complete_target_scoped_requirements() -> None:
    callable_ = ConcreteCallable(
        family="neon",
        name="vaddq_u32",
        signature=Signature(
            "uint32x4_t",
            (Parameter("a", "uint32x4_t"), Parameter("b", "uint32x4_t")),
        ),
        headers=("arm_neon.h",),
    )

    attached = _attach_feature_flags(
        callable_,
        index_feature_flags_by_macro(DEFAULT_FEATURE_FLAG_MANIFEST),
    )

    assert attached.compilation.feature_macros == ("__ARM_NEON",)
    assert attached.compilation.architecture_min == "Armv7-A / Armv8-A"
    assert attached.compilation.unresolved_reason is None
    assert any(
        "-mfloat-abi=softfp" in example.flags
        for example in attached.compilation.compiler_flags
    )
    assert any(
        "armv8-a" in flag
        for example in attached.compilation.compiler_flags
        for flag in example.flags
    )


def test_neon_dot_product_examples_satisfy_every_feature_in_branch() -> None:
    callable_ = ConcreteCallable(
        family="neon",
        name="vdotq_s32",
        signature=Signature("int32x4_t"),
        semantics=replace(
            ConcreteCallable(
                family="neon",
                name="placeholder",
                signature=Signature("void"),
            ).semantics,
            summary=(
                "Dot Product intrinsics added for ARMv8.2-a and newer. Requires the "
                "+dotprod architecture extension."
            ),
        ),
    )

    attached = _attach_feature_flags(
        callable_,
        index_feature_flags_by_macro(DEFAULT_FEATURE_FLAG_MANIFEST),
    )

    march_examples = [
        example
        for example in attached.compilation.compiler_flags
        if any(flag.startswith("-march=") for flag in example.flags)
    ]
    assert march_examples
    assert all(
        not (len(example.flags) == 1 and example.flags[0] == "-march=armv8-a+simd")
        for example in march_examples
    )
    assert any(
        "+dotprod" in flag and "+simd" in flag
        for example in march_examples
        for flag in example.flags
        if flag.startswith("-march=")
    )
    assert attached.compilation.architecture_min == "Armv8.2-A"
    assert all(example.target in {"aarch32", "aarch64"} for example in march_examples)
    assert all(
        _branch_macros(example.availability) >= {"__ARM_NEON", "__ARM_FEATURE_DOTPROD"}
        for example in march_examples
    )


def test_neon_absolute_minmax_instructions_require_faminmax() -> None:
    feature_index = index_feature_flags_by_macro(DEFAULT_FEATURE_FLAG_MANIFEST)

    for mnemonic, name in (("FAMAX", "vamaxq_f32"), ("FAMIN", "vaminq_f32")):
        callable_ = ConcreteCallable(
            family="neon",
            name=name,
            signature=Signature("float32x4_t"),
            compilation=CompilationRequirements(execution_states=("AArch64",)),
            semantics=Semantics(summary="Basic intrinsics"),
            instructions=(
                InstructionMapping(
                    InstructionRelationKind.SEMANTIC_EQUIVALENT,
                    mnemonic=mnemonic,
                ),
            ),
        )

        attached = _attach_feature_flags(callable_, feature_index)
        march_examples = [
            example
            for example in attached.compilation.compiler_flags
            if any(flag.startswith("-march=") for flag in example.flags)
        ]

        assert set(attached.compilation.feature_macros) == {
            "__ARM_NEON",
            "__ARM_FEATURE_FAMINMAX",
        }
        assert attached.compilation.architecture_min == "Armv9.2-A"
        assert attached.compilation.unresolved_reason is None
        assert march_examples
        assert all(example.target == "aarch64" for example in march_examples)
        assert all(
            _branch_macros(example.availability)
            >= {"__ARM_NEON", "__ARM_FEATURE_FAMINMAX"}
            for example in march_examples
        )
        assert any(
            "+faminmax" in flag and "+simd" in flag
            for example in march_examples
            for flag in example.flags
            if flag.startswith("-march=")
        )


@pytest.mark.parametrize(
    (
        "name",
        "section",
        "mnemonic",
        "required_macro",
        "forbidden_macro",
        "required_flag",
    ),
    (
        (
            "vfmlalq_low_f16",
            "FP16 Armv8.4-a",
            "FMLAL",
            "__ARM_FEATURE_FP16_FML",
            "__ARM_FEATURE_FP16_VECTOR_ARITHMETIC",
            "+fp16fml",
        ),
        (
            "vbcaxq_u8",
            "Armv8.4-a intrinsics.",
            "BCAX",
            "__ARM_FEATURE_SHA3",
            "__ARM_FEATURE_SHA512",
            "+sha3",
        ),
        (
            "vmull_p8",
            "Basic intrinsics",
            "PMULL",
            "__ARM_NEON",
            "__ARM_FEATURE_AES",
            "+simd",
        ),
        (
            "vmull_p64",
            "Crypto",
            "PMULL",
            "__ARM_FEATURE_AES",
            "__ARM_FEATURE_SHA2",
            "+aes",
        ),
        (
            "vusdot_s32",
            "Matrix multiplication intrinsics from Armv8.6-A",
            "USDOT",
            "__ARM_FEATURE_MATMUL_INT8",
            "__ARM_FEATURE_DOTPROD",
            "+i8mm",
        ),
        (
            "vsudot_lane_s32",
            "Matrix multiplication intrinsics from Armv8.6-A",
            "SUDOT",
            "__ARM_FEATURE_MATMUL_INT8",
            "__ARM_FEATURE_DOTPROD",
            "+i8mm",
        ),
    ),
)
def test_neon_exact_source_rules_select_feature_flags(
    name: str,
    section: str,
    mnemonic: str,
    required_macro: str,
    forbidden_macro: str,
    required_flag: str,
) -> None:
    callable_ = ConcreteCallable(
        family="neon",
        name=name,
        signature=Signature("int32x4_t"),
        compilation=CompilationRequirements(execution_states=("AArch64",)),
        semantics=Semantics(summary=section),
        instructions=(
            InstructionMapping(
                InstructionRelationKind.DIRECT_ACCESS,
                mnemonic=mnemonic,
            ),
        ),
    )

    attached = _attach_feature_flags(
        callable_,
        index_feature_flags_by_macro(DEFAULT_FEATURE_FLAG_MANIFEST),
    )

    assert required_macro in attached.compilation.feature_macros
    assert forbidden_macro not in attached.compilation.feature_macros
    assert any(
        required_flag in flag
        for example in attached.compilation.compiler_flags
        for flag in example.flags
    )


def test_neon_bf16_scalar_does_not_claim_vector_arithmetic() -> None:
    callable_ = ConcreteCallable(
        family="neon",
        name="vcvth_bf16_f32",
        signature=Signature("bfloat16_t"),
        compilation=CompilationRequirements(execution_states=("AArch64",)),
        semantics=Semantics(
            summary="Bfloat16 intrinsics Requires the +bf16 architecture extension."
        ),
        instructions=(
            InstructionMapping(
                InstructionRelationKind.DIRECT_ACCESS,
                mnemonic="BFCVT",
            ),
        ),
    )

    attached = _attach_feature_flags(
        callable_,
        index_feature_flags_by_macro(DEFAULT_FEATURE_FLAG_MANIFEST),
    )

    assert set(attached.compilation.feature_macros) == {
        "__ARM_NEON",
        "__ARM_FEATURE_BF16",
        "__ARM_FEATURE_BF16_SCALAR_ARITHMETIC",
    }
    assert "__ARM_FEATURE_BF16_VECTOR_ARITHMETIC" not in (
        attached.compilation.feature_macros
    )
    assert attached.compilation.compiler_flags == ()
    assert "BF16_SCALAR_ARITHMETIC" in (attached.compilation.unresolved_reason or "")


@pytest.mark.parametrize(
    ("name", "section", "mnemonic", "expected"),
    (
        (
            "__crc32b",
            "CRC32",
            "CRC32B",
            {"__ARM_FEATURE_CRC32"},
        ),
        (
            "vaddh_f16",
            "fp16 scalar intrinsics (available through <arm_fp16.h> from ARMv8.2-A)",
            "FADD",
            {"__ARM_FEATURE_FP16_SCALAR_ARITHMETIC"},
        ),
        (
            "vadd_f16",
            "fp16 vector intrinsics (from ARMv8.2-A)",
            "FADD",
            {"__ARM_NEON", "__ARM_FEATURE_FP16_VECTOR_ARITHMETIC"},
        ),
        (
            "vdot_s32",
            "Dot Product intrinsics added for ARMv8.2-a and newer. Requires the "
            "+dotprod architecture extension.",
            "SDOT",
            {"__ARM_NEON", "__ARM_FEATURE_DOTPROD"},
        ),
        (
            "vsha1cq_u32",
            "Crypto",
            "SHA1C",
            {"__ARM_NEON", "__ARM_FEATURE_SHA2"},
        ),
        (
            "vsha512hq_u64",
            "Armv8.4-a intrinsics.",
            "SHA512H",
            {"__ARM_NEON", "__ARM_FEATURE_SHA512"},
        ),
        (
            "vsm3ss1q_u32",
            "Armv8.4-a intrinsics.",
            "SM3SS1",
            {"__ARM_NEON", "__ARM_FEATURE_SM3"},
        ),
        (
            "vsm4eq_u32",
            "Armv8.4-a intrinsics.",
            "SM4E",
            {"__ARM_NEON", "__ARM_FEATURE_SM4"},
        ),
        (
            "vluti2q_u8",
            "Basic intrinsics",
            "LUTI2",
            {"__ARM_NEON", "__ARM_FEATURE_LUT"},
        ),
        (
            "vcvt_mf8_f32_fpm",
            "Modal 8-bit floating-point intrinsics",
            "FCVTN",
            {"__ARM_NEON", "__ARM_FEATURE_FP8"},
        ),
        (
            "vmlalbq_f16_mf8_fpm",
            "Modal 8-bit floating-point intrinsics",
            "FMLALB",
            {"__ARM_NEON", "__ARM_FEATURE_FP8FMA"},
        ),
    ),
)
def test_neon_section_rules_cover_pinned_feature_families(
    name: str,
    section: str,
    mnemonic: str,
    expected: set[str],
) -> None:
    callable_ = ConcreteCallable(
        family="neon",
        name=name,
        signature=Signature("void"),
        semantics=Semantics(summary=section),
        instructions=(
            InstructionMapping(
                InstructionRelationKind.DIRECT_ACCESS,
                mnemonic=mnemonic,
            ),
        ),
    )

    assert _derived_family_macros(callable_) == expected


def test_name_availability_is_not_promoted_to_an_isa_requirement() -> None:
    callable_ = ConcreteCallable(
        family="mve",
        name="vaddq_u32",
        signature=Signature("uint32x4_t"),
        name_availability=AvailabilityExpr.not_(
            AvailabilityExpr.defined("__ARM_MVE_PRESERVE_USER_NAMESPACE")
        ),
    )

    attached = _attach_feature_flags(
        callable_,
        index_feature_flags_by_macro(DEFAULT_FEATURE_FLAG_MANIFEST),
    )

    assert "__ARM_MVE_PRESERVE_USER_NAMESPACE" not in (
        attached.compilation.feature_macros
    )
    assert attached.name_availability == callable_.name_availability


def test_tabular_target_scope_does_not_block_source_backed_feature_flags() -> None:
    cases = (
        ("neon", "vaddq_s32", "A32/A64", "__ARM_NEON", "+simd"),
        ("mve", "vaddq_s32", "MVE/NEON", "__ARM_FEATURE_MVE", "+mve"),
    )
    for family, name, raw_scope, macro, required_flag in cases:
        callable_ = ConcreteCallable(
            family=family,
            name=name,
            signature=Signature("int32x4_t"),
            availability=AvailabilityExpr.raw(raw_scope),
            compilation=CompilationRequirements(feature_macros=(macro,)),
        )

        attached = _attach_feature_flags(
            callable_,
            index_feature_flags_by_macro(DEFAULT_FEATURE_FLAG_MANIFEST),
        )

        assert raw_scope in canonical_json(attached.availability)
        assert macro in canonical_json(attached.availability)
        assert attached.compilation.compiler_flags
        assert any(
            required_flag in flag
            for example in attached.compilation.compiler_flags
            for flag in example.flags
        )


def test_missing_feature_mapping_remains_visible_when_flags_exist() -> None:
    evidence = Provenance(
        ProvenanceKind.EXPLICIT,
        (SourceRef("manual", "example/repo", "commit", "flags.md"),),
    )
    callable_ = ConcreteCallable(
        family="general",
        name="__partial_feature",
        signature=Signature("void"),
        compilation=CompilationRequirements(
            feature_macros=("__ARM_FEATURE_NOT_PINNED",),
            compiler_flags=(
                CompilerFlagExample(
                    compiler="Example compiler",
                    flags=("-march=example",),
                    provenance=evidence,
                ),
            ),
            provenance=evidence,
        ),
    )

    attached = _attach_feature_flags(callable_, {})

    assert not attached.compilation.compiler_flags
    assert attached.compilation.unresolved_reason is not None
    assert "Partial feature-to-compiler mapping" in (
        attached.compilation.unresolved_reason
    )


def test_cde_and_mve_declarations_with_same_signature_remain_separate() -> None:
    signature = Signature("float16x8_t", (Parameter("value", "uint8x16_t"),))
    mve = ConcreteCallable(
        family="mve",
        name="__arm_vreinterpretq_f16_u8",
        signature=signature,
        aliases=(Alias("vreinterpretq_f16_u8", NameRole.UNPREFIXED),),
    )
    cde_gate = AvailabilityExpr.defined("__ARM_FEATURE_CDE")
    cde = ConcreteCallable(
        family="general",
        name="__arm_vreinterpretq_f16_u8",
        signature=signature,
        availability=cde_gate,
        compilation=CompilationRequirements(availability=cde_gate),
    )

    merged, diagnostics = _merge_markdown_declarations((mve,), (cde,))

    assert len(merged) == 2
    assert diagnostics
    mve_result = next(item for item in merged if item.family == "mve")
    cde_result = next(item for item in merged if item.family == "general")
    assert mve_result.availability == AvailabilityExpr.always()
    assert "__ARM_FEATURE_CDE" not in mve_result.compilation.feature_macros
    assert cde_result.availability == cde_gate


def test_alias_only_enrichment_does_not_promote_global_availability() -> None:
    callable_ = ConcreteCallable(
        family="mve",
        name="__arm_vreinterpretq_f16_u8",
        signature=Signature("float16x8_t", (Parameter(None, "uint8x16_t"),)),
        aliases=(Alias("vreinterpretq_f16_u8", NameRole.UNPREFIXED),),
    )
    patch = {
        "match": {"names": ["vreinterpretq_f16_u8"], "base_names": []},
        "family": ["mve"],
        "availability": {
            "expression": {"op": "defined", "macro": "__ARM_FEATURE_CDE"},
            "by_mode": {},
            "execution_states": [],
            "extensions": [],
        },
        "maturity": {"support_level": "release"},
        "source_signature": {
            "return_type": "float16x8_t",
            "parameters": [{"type": "uint8x16_t"}],
            "attributes": [],
        },
        "provenance": {"source": {"path": "main/acle.md", "start_line": 1}},
    }

    enriched = _apply_markdown_enrichments((callable_,), (patch,))[0]

    assert enriched.availability == AvailabilityExpr.always()
    assert enriched.compilation.availability == AvailabilityExpr.always()
    assert enriched.aliases[0].availability == AvailabilityExpr.defined(
        "__ARM_FEATURE_CDE"
    )


def test_crc_reclassification_removes_neon_family_membership() -> None:
    signature = Signature("uint32_t", (Parameter("acc", "uint32_t"),))
    neon = ConcreteCallable(family="neon", name="__crc32b", signature=signature)
    general = ConcreteCallable(family="general", name="__crc32b", signature=signature)

    merged, diagnostics = _merge_markdown_declarations((neon,), (general,))

    assert diagnostics == []
    assert len(merged) == 1
    assert merged[0].family == "general"
    assert merged[0].families == ("general",)


def test_tablegen_guards_reclassify_complete_representative_set() -> None:
    guards = parse_sve_target_guards(
        """
let SVETargetGuard = "sve2|sme" in {
def SVADCLB : SInst<"svadclb[_{d}]", "dddd", "UiUl", MergeNone>;
defm SVADDLB : SInstWideDSPLong<"svaddlb", "sil", "builtin">;
def SVADDHNB : SInst<"svaddhnb[_{d}]", "hdd", "sil", MergeNone>;
}
let SVETargetGuard = "sve-aes", SMETargetGuard = "ssve-aes" in {
def SVAESD : SInst<"svaesd[_{d}]", "ddd", "Uc", MergeNone>;
}
"""
    )
    callables = tuple(
        ConcreteCallable(
            family="sve",
            name=name,
            signature=Signature("svuint32_t"),
        )
        for name in ("svadclb_u32", "svaddhnb_u16", "svaesd_u8", "svaddlb_s16")
    )

    classified = _apply_llvm_target_guards(
        callables,
        guards,
        DEFAULT_FEATURE_FLAG_MANIFEST,
    )
    by_name = {item.name: item for item in classified}

    for name in ("svadclb_u32", "svaddhnb_u16", "svaddlb_s16"):
        assert "sve" not in by_name[name].families
        assert "sve2" in by_name[name].families
        assert "__ARM_FEATURE_SVE2" in by_name[name].compilation.feature_macros
    aes = by_name["svaesd_u8"]
    assert "sve" not in aes.families
    assert "sve2" in aes.families
    assert "__ARM_FEATURE_SVE2_AES" in aes.compilation.feature_macros
    assert any(source.path.endswith("arm_sve.td") for source in aes.sources)


def test_tablegen_guards_do_not_attach_to_acle_only_declarations() -> None:
    guards = parse_sve_target_guards(
        """
let SVETargetGuard = "sve-b16b16", SMETargetGuard = InvalidMode in {
def SVBFMMLA : SInst<"svmmla[_bf16]", "dddd", "b", MergeNone>;
}
"""
    )
    source = SourceRef(
        id="acle-only-svmmla",
        repository=ACLE_REPOSITORY,
        commit="acle-commit",
        path="main/acle.md",
        start_line=1,
        end_line=1,
        license_id="CC-BY-SA-4.0",
    )
    callable_ = ConcreteCallable(
        family="sve",
        name="svmmla_bf16",
        signature=Signature("svbfloat16_t"),
        availability=AvailabilityExpr.defined("__ARM_FEATURE_SVE_B16MM"),
        headers=("arm_sve.h",),
        sources=(source,),
    )

    classified = _apply_llvm_target_guards(
        (callable_,),
        guards,
        DEFAULT_FEATURE_FLAG_MANIFEST,
    )[0]

    assert classified == callable_
    assert not any(
        item.code == "llvm.target_guard_ambiguous" for item in classified.diagnostics
    )


def test_target_guard_aliases_do_not_expand_compound_features() -> None:
    index = _target_guard_macro_index(DEFAULT_FEATURE_FLAG_MANIFEST)

    assert index["sve"] == ("__ARM_FEATURE_SVE",)
    assert index["sve-bf16"] == ("__ARM_FEATURE_SVE_BF16",)
    assert index["bf16"] == ("__ARM_FEATURE_SVE_BF16",)
    assert index["i8mm"] == ("__ARM_FEATURE_SVE_MATMUL_INT8",)
    assert index["faminmax"] == ("__ARM_FEATURE_FAMINMAX",)
    assert index["sve-b16b16"] == ("__ARM_FEATURE_SVE_B16B16",)
    assert "__ARM_FEATURE_SVE" not in index["bf16"]
    assert "__ARM_FEATURE_SVE" not in index["i8mm"]

    expression, unknown = _translate_target_guard(
        AvailabilityExpr.all(
            AvailabilityExpr.defined("sme2"),
            AvailabilityExpr.defined("sve-b16b16"),
        ),
        index,
    )
    assert unknown == set()
    assert _branch_macros(expression) == {
        "__ARM_FEATURE_SME2",
        "__ARM_FEATURE_SVE_B16B16",
    }


def test_explicit_target_tokens_override_key_derived_aliases() -> None:
    index = _target_guard_macro_index(DEFAULT_FEATURE_FLAG_MANIFEST)
    expression, unknown = _translate_target_guard(
        AvailabilityExpr.all(
            AvailabilityExpr.defined("sve-aes2"),
            AvailabilityExpr.defined("ssve-aes"),
        ),
        index,
    )

    assert unknown == set()
    assert _branch_macros(expression) == {
        "__ARM_FEATURE_SVE_AES2",
        "__ARM_FEATURE_SSVE_AES",
    }
    assert "__ARM_FEATURE_SVE2_AES" not in _branch_macros(expression)


def test_target_guard_matcher_expands_allowlisted_multiclass_shapes() -> None:
    guards = parse_sve_target_guards(
        """
defm ZPZ : SInstZPZ<"svabs", "i", "intrinsic">;
defm ZPZZ : SInstZPZZ<"svadd", "i", "m", "x">;
defm ZPZZZ : SInstZPZZZ<"svmla", "i", "m", "x">;
defm ZPZXZ : SInstZPZxZ<"svqshl", "i", "dPdx", "dPdK", "m", "x">;
defm WIDE : SInstWideDSPAcc<"svabalb", "i", "intrinsic">;
defm CVTMXZ : SInstCvtMXZ<"svcvt_s32[_f16]", "ddPO", "dPO", "i", "intrinsic">;
defm CVTMX : SInstCvtMX<"svcvtlt_f32[_f16]", "ddPh", "dPh", "f", "intrinsic">;
"""
    )
    by_record = {guard.record_name: guard for guard in guards}

    assert _target_guard_concrete_names(by_record["ZPZ"]) == (
        "svabs_s32_m",
        "svabs_s32_x",
        "svabs_s32_z",
    )
    for record, base in (("ZPZZ", "svadd"), ("ZPZZZ", "svmla"), ("ZPZXZ", "svqshl")):
        assert set(_target_guard_concrete_names(by_record[record])) == {
            f"{base}_s32_m",
            f"{base}_s32_x",
            f"{base}_s32_z",
            f"{base}_n_s32_m",
            f"{base}_n_s32_x",
            f"{base}_n_s32_z",
        }
    assert set(_target_guard_concrete_names(by_record["WIDE"])) == {
        "svabalb_s32",
        "svabalb_n_s32",
    }
    assert _target_guard_concrete_names(by_record["CVTMXZ"]) == (
        "svcvt_s32_f16_m",
        "svcvt_s32_f16_x",
        "svcvt_s32_f16_z",
    )
    assert _target_guard_concrete_names(by_record["CVTMX"]) == (
        "svcvtlt_f32_f16_m",
        "svcvtlt_f32_f16_x",
    )


def test_target_guard_matcher_expands_correlated_numeric_placeholders() -> None:
    guards = parse_sve_target_guards(
        """
def SVDOT : SInst<"svdot[_{0}]", "ddqq", "i", MergeNone>;
def SVDOT_X2 : SInst<"svdot[_{d}_{2}]", "ddhh", "i", MergeNone>;
def SVQRSHRN_X4 : SInst<"svqrshrn[_n]_{0}[_{d}_x4]", "q4i", "i", MergeNone>;
def SVQRSHRN_X2 : SInst<"svqrshrn[_n]_{0}[_{d}_x2]", "h2i", "i", MergeNone>;
def SVQRSHRUN_X4 : SInst<"svqrshrun[_n]_{0}[_{d}_x4]", "b4i", "i", MergeNone>;
def SVQRSHRUN_X2 : SInst<"svqrshrun[_n]_{0}[_{d}_x2]", "e2i", "i", MergeNone>;
def SVLD1 : MInst<"svld1[_{2}]", "dPc", "i", [IsLoad], MemEltTyDefault>;
def SVLD1_GATHER : MInst<"svld1_gather_[{3}]offset[_{d}]", "dPcx", "lUld", [IsLoad], MemEltTyDefault>;
"""
    )
    by_record = {guard.record_name: guard for guard in guards}

    expected = {
        "SVDOT": {"svdot_s32"},
        "SVDOT_X2": {"svdot_s32_s16"},
        "SVQRSHRN_X4": {"svqrshrn_n_s8_s32_x4"},
        "SVQRSHRN_X2": {"svqrshrn_n_s16_s32_x2"},
        "SVQRSHRUN_X4": {"svqrshrun_n_u8_s32_x4"},
        "SVQRSHRUN_X2": {"svqrshrun_n_u16_s32_x2"},
        "SVLD1": {"svld1_s32"},
        "SVLD1_GATHER": {
            "svld1_gather_s64offset_s64",
            "svld1_gather_s64offset_u64",
            "svld1_gather_s64offset_f64",
        },
    }
    assert {
        name: set(_target_guard_concrete_names(by_record[name])) for name in expected
    } == expected


def test_same_guard_opaque_defm_is_shared_without_guessing_identity() -> None:
    guards = parse_sve_target_guards(
        """
let SVETargetGuard = "sve2|sme" in {
defm OPAQUE_S : UnknownMulticlass<"svopaque", "signed-layout", "other">;
defm OPAQUE_U : UnknownMulticlass<"svopaque", "unsigned-layout", "other">;
}
"""
    )
    callable_ = ConcreteCallable(
        family="sve",
        name="svopaque_s32",
        signature=Signature("svint32_t"),
    )

    classified = _apply_llvm_target_guards(
        (callable_,),
        guards,
        DEFAULT_FEATURE_FLAG_MANIFEST,
    )[0]

    assert "__ARM_FEATURE_SVE2" in classified.compilation.feature_macros
    assert not any(
        diagnostic.code == "llvm.target_guard_ambiguous"
        for diagnostic in classified.diagnostics
    )


def test_ambiguous_target_guard_blocks_release_and_disables_family_fallback() -> None:
    guards = parse_sve_target_guards(
        """
let SVETargetGuard = "sve2" in {
defm OPAQUE_BASE : UnknownMulticlass<"svambiguous", "base-layout">;
}
let SVETargetGuard = "sve-b16b16" in {
defm OPAQUE_BF16 : UnknownMulticlass<"svambiguous", "bf16-layout">;
}
"""
    )
    callable_ = ConcreteCallable(
        family="sve",
        name="svambiguous_f16",
        signature=Signature("svfloat16_t"),
        headers=("arm_sve.h",),
    )

    guarded = _apply_llvm_target_guards(
        (callable_,),
        guards,
        DEFAULT_FEATURE_FLAG_MANIFEST,
    )[0]
    attached = _attach_feature_flags(
        guarded,
        index_feature_flags_by_macro(DEFAULT_FEATURE_FLAG_MANIFEST),
    )
    diagnostic = next(
        item
        for item in attached.diagnostics
        if item.code == "llvm.target_guard_ambiguous"
    )

    assert diagnostic.severity.value == "error"
    assert diagnostic.field == "compilation.compiler_flags"
    assert attached.compilation.feature_macros == ()
    assert attached.compilation.compiler_flags == ()
    assert "LLVM target guard is unresolved" in (
        attached.compilation.unresolved_reason or ""
    )
    assert (
        completeness_report(
            Catalog(
                version="test",
                source_commit="test",
                callables=(attached,),
            )
        ).release_blockers
        == 1
    )


def test_multiclass_guards_keep_svmax_b16b16_separate_from_baseline_f16() -> None:
    guards = parse_sve_target_guards(
        """
defm SVMAX_F : SInstZPZZ<"svmax", "hfd", "m", "x">;
let SVETargetGuard = "sve-b16b16", SMETargetGuard = "sme2,sve-b16b16" in {
defm SVMAX_BF : SInstZPZZ<"svmax", "b", "m", "x">;
}
"""
    )
    callables = tuple(
        ConcreteCallable(
            family="sve",
            name=f"svmax_{type_name}_{policy}",
            signature=Signature(return_type),
        )
        for type_name, return_type in (
            ("f16", "svfloat16_t"),
            ("bf16", "svbfloat16_t"),
        )
        for policy in ("m", "x", "z")
    )

    classified = _apply_llvm_target_guards(
        callables,
        guards,
        DEFAULT_FEATURE_FLAG_MANIFEST,
    )
    by_name = {item.name: item for item in classified}

    for policy in ("m", "x", "z"):
        baseline = by_name[f"svmax_f16_{policy}"]
        assert "__ARM_FEATURE_SVE_B16B16" not in baseline.compilation.feature_macros
        assert {source.start_line for source in baseline.sources} == {2}

        b16b16 = by_name[f"svmax_bf16_{policy}"]
        assert "__ARM_FEATURE_SVE_B16B16" in b16b16.compilation.feature_macros
        assert "__ARM_FEATURE_SVE" not in b16b16.compilation.feature_macros
        assert {source.start_line for source in b16b16.sources} == {4}


def test_streaming_only_multivector_guards_replace_sve_family_defaults() -> None:
    guards = parse_sve_target_guards(
        """
let SVETargetGuard = InvalidMode, SMETargetGuard = "sme2" in {
defm MAX_MULTI_X2 : MinMaxIntr<"max", "", "x2", "222">;
}
let SVETargetGuard = InvalidMode, SMETargetGuard = "sme2,sve-b16b16" in {
defm SVBFMAX : BfSingleMultiVector<"max">;
}
"""
    )
    callables = (
        ConcreteCallable(
            family="sve",
            name="svmax_f16_x2",
            signature=Signature(
                "svfloat16x2_t",
                (Parameter(None, "svfloat16x2_t"),) * 2,
            ),
            headers=("arm_sve.h",),
        ),
        ConcreteCallable(
            family="sve",
            name="svmax_bf16_x2",
            signature=Signature(
                "svbfloat16x2_t",
                (Parameter(None, "svbfloat16x2_t"),) * 2,
            ),
            headers=("arm_sve.h",),
        ),
    )

    classified = _apply_llvm_target_guards(
        callables,
        guards,
        DEFAULT_FEATURE_FLAG_MANIFEST,
    )
    classified = tuple(
        _attach_feature_flags(
            item,
            index_feature_flags_by_macro(DEFAULT_FEATURE_FLAG_MANIFEST),
        )
        for item in classified
    )
    by_name = {item.name: item for item in classified}

    baseline = by_name["svmax_f16_x2"]
    assert baseline.families == ("sme2",)
    assert baseline.signature.attributes == ("__arm_streaming",)
    assert baseline.compilation.feature_macros == ("__ARM_FEATURE_SME2",)
    assert len(baseline.compilation.compiler_flags) == 4
    assert {example.mode for example in baseline.compilation.compiler_flags} == {
        "streaming"
    }
    assert not any(
        diagnostic.code == "llvm.target_guard_ambiguous"
        for diagnostic in baseline.diagnostics
    )
    assert "sve" not in {
        token
        for example in baseline.compilation.compiler_flags
        for selector in example.flags
        if selector.startswith(("-march=", "-mcpu="))
        for token in selector.split("+")[1:]
    }

    b16b16 = by_name["svmax_bf16_x2"]
    assert b16b16.families == ("sme2",)
    assert b16b16.signature.attributes == ("__arm_streaming",)
    assert set(b16b16.compilation.feature_macros) == {
        "__ARM_FEATURE_SME2",
        "__ARM_FEATURE_SVE_B16B16",
    }
    assert len(b16b16.compilation.compiler_flags) == 8
    assert {example.mode for example in b16b16.compilation.compiler_flags} == {
        "streaming"
    }
    assert "__ARM_FEATURE_SVE" not in b16b16.compilation.feature_macros
    assert not any(
        diagnostic.code == "llvm.target_guard_ambiguous"
        for diagnostic in b16b16.diagnostics
    )
    assert "sve" not in {
        token
        for example in b16b16.compilation.compiler_flags
        for selector in example.flags
        if selector.startswith(("-march=", "-mcpu="))
        for token in selector.split("+")[1:]
    }


def test_early_streaming_guard_enables_exact_markdown_signature_merge() -> None:
    header_source = SourceRef(
        "llvm-header",
        "llvm/llvm-project",
        "llvm-commit",
        "lib/clang/22/include/arm_sve.h",
        10,
        10,
    )
    markdown_source = SourceRef(
        "acle-markdown",
        "ARM-software/acle",
        "acle-commit",
        "main/acle.md",
        20,
        21,
    )
    header = ConcreteCallable(
        family="sve",
        name="svmax_f16_x2",
        signature=Signature(
            "svfloat16x2_t",
            (Parameter(None, "svfloat16x2_t"),) * 2,
        ),
        headers=("arm_sve.h",),
        sources=(header_source,),
    )
    specification = ConcreteCallable(
        family="sme2",
        name="svmax_f16_x2",
        signature=Signature(
            "svfloat16x2_t",
            (
                Parameter("zdn", "svfloat16x2_t"),
                Parameter("zm", "svfloat16x2_t"),
            ),
            attributes=("__arm_streaming",),
            raw=(
                "svfloat16x2_t svmax_f16_x2(svfloat16x2_t zdn, "
                "svfloat16x2_t zm) __arm_streaming;"
            ),
        ),
        headers=("arm_sme.h",),
        sources=(markdown_source,),
    )
    guards = parse_sve_target_guards(
        """
let SVETargetGuard = InvalidMode, SMETargetGuard = "sme2" in {
defm MAX_MULTI_X2 : MinMaxIntr<"max", "", "x2", "222">;
}
"""
    )

    guarded = _apply_llvm_target_guards(
        (header,),
        guards,
        DEFAULT_FEATURE_FLAG_MANIFEST,
    )
    merged, diagnostics = _merge_markdown_declarations(
        guarded,
        (specification,),
    )

    assert diagnostics == []
    assert len(merged) == 1
    assert merged[0].signature == specification.signature
    assert merged[0].headers == ("arm_sme.h", "arm_sve.h")
    assert {source.id for source in merged[0].sources} >= {
        "llvm-header",
        "acle-markdown",
    }

    twice_guarded = _apply_llvm_target_guards(
        merged,
        guards,
        DEFAULT_FEATURE_FLAG_MANIFEST,
    )
    assert len(twice_guarded[0].compilation.availability_by_mode) == 1
    assert twice_guarded[0].compilation.availability_by_mode[0].mode == "streaming"
    assert len({source.id for source in twice_guarded[0].sources}) == len(
        twice_guarded[0].sources
    )

    attached = _attach_feature_flags(
        twice_guarded[0],
        index_feature_flags_by_macro(DEFAULT_FEATURE_FLAG_MANIFEST),
    )
    assert attached.families == ("sme2",)
    assert attached.compilation.feature_macros == ("__ARM_FEATURE_SME2",)
    assert {example.mode for example in attached.compilation.compiler_flags} <= {
        None,
        "streaming",
    }


def test_markdown_attributes_enrich_unannotated_header_signature() -> None:
    header_source = SourceRef(
        "llvm-header",
        "llvm/llvm-project",
        "llvm-commit",
        "lib/clang/22/include/arm_sme.h",
        10,
        10,
    )
    markdown_source = SourceRef(
        "acle-markdown",
        "ARM-software/acle",
        "acle-commit",
        "main/acle.md",
        20,
        22,
    )
    header = ConcreteCallable(
        family="sme",
        name="svmopa_za32_f32_m",
        signature=Signature(
            "void",
            (
                Parameter(None, "uint64_t"),
                Parameter(None, "svbool_t"),
                Parameter(None, "svbool_t"),
                Parameter(None, "svfloat32_t"),
                Parameter(None, "svfloat32_t"),
            ),
        ),
        headers=("arm_sme.h",),
        sources=(header_source,),
    )
    specification = ConcreteCallable(
        family="sme",
        name="svmopa_za32_f32_m",
        signature=Signature(
            "void",
            (
                Parameter("tile", "uint64_t"),
                Parameter("pn", "svbool_t"),
                Parameter("pm", "svbool_t"),
                Parameter("zn", "svfloat32_t"),
                Parameter("zm", "svfloat32_t"),
            ),
            attributes=("__arm_streaming", '__arm_inout("za")'),
            raw=(
                "void svmopa_za32_f32_m(uint64_t tile, svbool_t pn, "
                "svbool_t pm, svfloat32_t zn, svfloat32_t zm) "
                '__arm_streaming __arm_inout("za");'
            ),
        ),
        headers=("arm_sme.h",),
        sources=(markdown_source,),
    )

    merged, diagnostics = _merge_markdown_declarations(
        (header,),
        (specification,),
    )

    assert diagnostics == []
    assert len(merged) == 1
    assert merged[0].signature.raw == specification.signature.raw
    assert set(merged[0].signature.attributes) == {
        "__arm_streaming",
        '__arm_inout("za")',
    }
    assert tuple(parameter.name for parameter in merged[0].signature.parameters) == (
        "tile",
        "pn",
        "pm",
        "zn",
        "zm",
    )
    assert {source.id for source in merged[0].sources} == {
        "llvm-header",
        "acle-markdown",
    }


def test_markdown_attribute_enrichment_refuses_ambiguous_header_matches() -> None:
    header_source = SourceRef(
        "llvm-header",
        "llvm/llvm-project",
        "llvm-commit",
        "lib/clang/22/include/arm_sme.h",
        10,
        10,
    )
    declaration = ConcreteCallable(
        family="sme",
        name="svambiguous_s32",
        signature=Signature("void", (Parameter(None, "int32_t"),)),
        sources=(header_source,),
    )
    specification = ConcreteCallable(
        family="sme",
        name="svambiguous_s32",
        signature=Signature(
            "void",
            (Parameter("value", "int32_t"),),
            attributes=("__arm_streaming",),
        ),
    )

    merged, diagnostics = _merge_markdown_declarations(
        (declaration, declaration),
        (specification,),
    )

    assert len(merged) == 3
    assert [item.code for item in diagnostics] == [
        "pipeline.llvm_acle_signature_ambiguous"
    ]


def test_markdown_attribute_enrichment_does_not_collapse_sve_dual_mode() -> None:
    declaration = ConcreteCallable(
        family="sme",
        families=("sme", "sve"),
        name="svcvt_f32_s32_x2",
        signature=Signature(
            "svfloat32x2_t",
            (Parameter(None, "svint32x2_t"),),
        ),
        compilation=CompilationRequirements(
            availability_by_mode=(
                ModeAvailability(
                    "non_streaming",
                    AvailabilityExpr.defined("__ARM_FEATURE_SVE"),
                ),
                ModeAvailability(
                    "streaming",
                    AvailabilityExpr.defined("__ARM_FEATURE_SME"),
                ),
            ),
        ),
        sources=(
            SourceRef(
                "llvm-sve-header",
                "llvm/llvm-project",
                "llvm-commit",
                "lib/clang/22/include/arm_sve.h",
                10,
                10,
            ),
        ),
    )
    specification = ConcreteCallable(
        family="sme2",
        name="svcvt_f32_s32_x2",
        signature=Signature(
            "svfloat32x2_t",
            (Parameter("zn", "svint32x2_t"),),
            attributes=("__arm_streaming",),
        ),
    )

    merged, diagnostics = _merge_markdown_declarations(
        (declaration,),
        (specification,),
    )

    assert len(merged) == 2
    assert merged[0].signature.attributes == ()
    assert merged[1].signature.attributes == ("__arm_streaming",)
    assert [item.code for item in diagnostics] == ["pipeline.llvm_acle_signature_drift"]


def test_tablegen_guard_identity_keeps_svclamp_types_and_shapes_separate() -> None:
    guards = parse_sve_target_guards(
        """
let SVETargetGuard = "sve2p1|sme2", SMETargetGuard = "sve2p1|sme2" in {
def SVFCLAMP : SInst<"svclamp[_{d}]", "dddd", "hfd", MergeNone>;
}
let SVETargetGuard = "sve-i8mm", SMETargetGuard = "sme2" in {
def SVSCLAMP_I8 : SInst<"svclamp[_{d}]", "dddd", "c", MergeNone>;
}
let SVETargetGuard = "sve-b16b16", SMETargetGuard = "sme2,sve-b16b16" in {
def SVFCLAMP_BF : SInst<"svclamp[_{d}]", "dddd", "b", MergeNone>;
}
let SVETargetGuard = InvalidMode, SMETargetGuard = "sme2" in {
def SVFCLAMP_X2 : SInst<"svclamp[_single_{d}_x2]", "22dd", "hfd", MergeNone>;
}
let SVETargetGuard = InvalidMode,
    SMETargetGuard = "sme2,sve-b16b16"in {
def SVBFCLAMP_X2 : SInst<"svclamp[_single_{d}_x2]", "22dd", "b", MergeNone>;
}
"""
    )
    callables = tuple(
        ConcreteCallable(
            family=family,
            name=name,
            signature=Signature(return_type),
            aliases=(Alias("svclamp", NameRole.OVERLOADED),),
            compilation=CompilationRequirements(
                provenance=Provenance.unresolved(
                    "Feature requirements must be merged from Arm ACLE."
                ),
                unresolved_reason=(
                    "The generated Clang header does not provide a stable "
                    "per-declaration ACLE availability expression."
                ),
            ),
        )
        for family, name, return_type in (
            ("sve", "svclamp_f16", "svfloat16_t"),
            ("sve", "svclamp_bf16", "svbfloat16_t"),
            ("sme2", "svclamp_single_f16_x2", "svfloat16x2_t"),
        )
    )

    classified = _apply_llvm_target_guards(
        callables,
        guards,
        DEFAULT_FEATURE_FLAG_MANIFEST,
    )
    classified = tuple(
        _attach_feature_flags(
            item,
            index_feature_flags_by_macro(DEFAULT_FEATURE_FLAG_MANIFEST),
        )
        for item in classified
    )
    by_name = {item.name: item for item in classified}

    f16 = by_name["svclamp_f16"]
    assert {"sme2", "sve2.1"} <= set(f16.families)
    assert "sve" not in f16.families
    assert {item.mode for item in f16.compilation.availability_by_mode} == {
        "non_streaming",
        "streaming",
    }
    assert "__arm_streaming" not in f16.signature.attributes
    assert set(f16.compilation.feature_macros) >= {
        "__ARM_FEATURE_SME2",
        "__ARM_FEATURE_SVE2p1",
    }
    assert not {
        "__ARM_FEATURE_SVE_B16B16",
        "__ARM_FEATURE_SVE_BF16",
        "__ARM_FEATURE_SVE_MATMUL_INT8",
    } & set(f16.compilation.feature_macros)
    assert {source.start_line for source in f16.sources} == {3}
    assert f16.compilation.unresolved_reason is None

    bf16 = by_name["svclamp_bf16"]
    assert "__ARM_FEATURE_SVE_B16B16" in bf16.compilation.feature_macros
    assert "__ARM_FEATURE_SVE2p1" not in bf16.compilation.feature_macros
    assert {source.start_line for source in bf16.sources} == {9}
    assert bf16.compilation.unresolved_reason is None

    f16_x2 = by_name["svclamp_single_f16_x2"]
    assert f16_x2.compilation.feature_macros == ("__ARM_FEATURE_SME2",)
    assert "__ARM_FEATURE_SVE_B16B16" not in f16_x2.compilation.feature_macros
    assert {source.start_line for source in f16_x2.sources} == {12}
    assert f16_x2.compilation.unresolved_reason is None


def test_duplicate_callable_identity_merges_sources_without_losing_signatures() -> None:
    first_source = SourceRef("one", "example/repo", "commit", "one.h", 1, 1)
    second_source = SourceRef("two", "example/repo", "commit", "two.h", 2, 2)
    first = ConcreteCallable(
        family="sme2",
        families=("sme2", "sve2.1"),
        name="svclamp_f16",
        signature=Signature(
            "svfloat16_t",
            (Parameter(None, "svfloat16_t"),) * 3,
        ),
        availability=AvailabilityExpr.any(
            AvailabilityExpr.defined("__ARM_FEATURE_SME2"),
            AvailabilityExpr.defined("__ARM_FEATURE_SVE2p1"),
        ),
        headers=("arm_sme.h", "arm_sve.h"),
        sources=(first_source,),
    )
    duplicate = replace(first, sources=(second_source,))

    merged = _deduplicate_callables((first, duplicate))

    assert len(merged) == 1
    assert merged[0].id == first.id
    assert merged[0].signature == first.signature
    assert {source.id for source in merged[0].sources} == {"one", "two"}

    different_signature = replace(
        first,
        signature=Signature("svfloat32_t", (Parameter(None, "svfloat32_t"),) * 3),
    )
    assert len(_deduplicate_callables((first, different_signature))) == 2


def test_duplicate_callable_conflicts_are_visible_and_order_independent() -> None:
    first_source = SourceRef("one", "example/repo", "commit", "one.h", 1, 1)
    second_source = SourceRef("two", "example/repo", "commit", "two.h", 2, 2)
    first = ConcreteCallable(
        family="sve",
        name="svexample_s32",
        signature=Signature("svint32_t"),
        maturity=Maturity.BETA,
        semantics=Semantics(summary="First resolved summary."),
        sources=(first_source,),
    )
    second = replace(
        first,
        maturity=Maturity.RELEASE,
        semantics=Semantics(summary="Second resolved summary."),
        sources=(second_source,),
    )

    forward = _deduplicate_callables((first, second))
    reverse = _deduplicate_callables((second, first))

    assert canonical_json(forward) == canonical_json(reverse)
    assert len(forward) == 1
    conflicts = [
        item
        for item in forward[0].diagnostics
        if item.code == "pipeline.equivalent_fact_conflict"
    ]
    assert {item.field for item in conflicts} == {"maturity", "semantics.summary"}
    assert all(
        {source.id for source in item.sources} == {"one", "two"} for item in conflicts
    )


def _branch_macros(expression: AvailabilityExpr) -> set[str]:
    result = {expression.key} if expression.key else set()
    for child in expression.arguments:
        result.update(_branch_macros(child))
    return result


def test_missing_source_license_is_a_release_blocker() -> None:
    catalog = build_catalog(
        _source_paths(), FIXTURES / "llvm", llvm_expected_hashes=None
    )
    callable_ = catalog.callables[0]
    unlicensed = SourceRef(
        id="unlicensed-source",
        repository="example/source",
        commit="0123456789abcdef",
        path="reference.md",
    )
    updated_callable = replace(callable_, sources=(*callable_.sources, unlicensed))
    updated_catalog = replace(
        catalog, callables=(updated_callable, *catalog.callables[1:])
    )

    assert completeness_report(updated_catalog).release_blockers == 1
