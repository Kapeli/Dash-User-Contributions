from __future__ import annotations

from io import StringIO
from pathlib import Path

import pytest
from arm_acle_docset.model import (
    AvailabilityOp,
    Maturity,
    NameRole,
    ProvenanceKind,
)
from arm_acle_docset.sources.tabular import (
    SourceRef,
    TabularFormatError,
    expand_name_forms,
    load_tabular_sources,
    parse_prototype,
    parse_tabular_sources,
    to_catalog,
    to_concrete_callables,
)

FIXTURES = Path(__file__).parent / "fixtures" / "tabular"


def test_neon_preserves_source_facts_and_uses_only_explicit_names() -> None:
    result = load_tabular_sources(
        FIXTURES / "advsimd.tsv",
        FIXTURES / "advsimd_classification.tsv",
        family="neon",
    )

    intrinsic = result.intrinsics[0]
    assert intrinsic.name_pattern == "vadd_s8"
    assert [(name.spelling, name.role) for name in intrinsic.names] == [
        ("vadd_s8", "typed")
    ]
    assert intrinsic.prototype.return_type == "int8x8_t"
    assert [
        (parameter.type, parameter.name) for parameter in intrinsic.prototype.parameters
    ] == [
        ("int8x8_t", "a"),
        ("int8x8_t", "b"),
    ]
    assert intrinsic.section is not None
    assert intrinsic.section.title == "Basic intrinsics"
    assert intrinsic.section.description.endswith("``__ARM_NEON``.")
    assert intrinsic.argument_preparation == "a -> Vn.8B;b -> Vm.8B"
    assert intrinsic.instruction == "ADD Vd.8B,Vn.8B,Vm.8B"
    assert intrinsic.result == "Vd.8B -> result"
    assert intrinsic.supported_architectures == ("v7", "A32", "A64")
    assert [classification.path for classification in intrinsic.classifications] == [
        ("Vector arithmetic", "Add", "Addition")
    ]


def test_tabular_records_do_not_guess_maturity_or_features() -> None:
    result = load_tabular_sources(
        FIXTURES / "advsimd.tsv",
        FIXTURES / "advsimd_classification.tsv",
        family="neon",
    )

    intrinsic = result.intrinsics[0]
    assert intrinsic.maturity == "Unspecified"
    assert intrinsic.features == ()
    assert {diagnostic.code for diagnostic in intrinsic.diagnostics} == {
        "tabular.features_unspecified",
        "tabular.maturity_unspecified",
    }


def test_duplicate_classification_rows_are_preserved_with_provenance() -> None:
    result = load_tabular_sources(
        FIXTURES / "advsimd.tsv",
        FIXTURES / "advsimd_classification.tsv",
        family="neon",
    )

    intrinsic = result.intrinsics[1]
    assert [classification.path for classification in intrinsic.classifications] == [
        ("Vector arithmetic", "Add", "Addition"),
        ("By element width", "8-bit"),
    ]
    assert [
        classification.source_ref.line for classification in intrinsic.classifications
    ] == [
        3,
        4,
    ]
    assert intrinsic.source_ref.line == 5
    assert intrinsic.section is not None
    assert intrinsic.section.source_ref.line == 3


def test_mve_expands_namespace_and_polymorphic_axes_independently() -> None:
    result = load_tabular_sources(
        FIXTURES / "mve.tsv",
        FIXTURES / "mve_classification.tsv",
        family="mve",
    )

    forms = result.intrinsics[0].names
    assert [(form.spelling, form.role, form.namespace) for form in forms] == [
        ("__arm_vaddq_s32", "typed", "prefixed"),
        ("__arm_vaddq", "overloaded", "prefixed"),
        ("vaddq_s32", "typed", "unprefixed"),
        ("vaddq", "overloaded", "unprefixed"),
    ]
    assert [form.availability for form in forms] == [
        None,
        None,
        "!defined(__ARM_MVE_PRESERVE_USER_NAMESPACE)",
        "!defined(__ARM_MVE_PRESERVE_USER_NAMESPACE)",
    ]


def test_mve_removes_all_polymorphic_brackets_in_lockstep() -> None:
    forms = expand_name_forms("[__arm_]vddupq[_n]_u8", family="mve")

    assert {form.spelling for form in forms} == {
        "__arm_vddupq_n_u8",
        "__arm_vddupq_u8",
        "vddupq_n_u8",
        "vddupq_u8",
    }
    assert "vddupq_n" not in {form.spelling for form in forms}


def test_one_overloaded_name_can_map_to_multiple_signatures() -> None:
    result = load_tabular_sources(
        FIXTURES / "mve.tsv",
        FIXTURES / "mve_classification.tsv",
        family="mve",
    )

    aliases = [
        intrinsic
        for intrinsic in result.intrinsics
        if any(name.spelling == "vaddq" for name in intrinsic.names)
    ]
    assert len(aliases) == 2
    assert {intrinsic.prototype.return_type for intrinsic in aliases} == {
        "int32x4_t",
        "uint32x4_t",
    }


def test_prototype_parser_preserves_pointer_and_const_parameters() -> None:
    prototype = parse_prototype(
        "uint8x16_t [__arm_]vddupq[_wb]_u8(uint32_t *a, const int imm)",
        source_ref=SourceRef("mve.csv", 21),
    )

    assert prototype.name_pattern == "[__arm_]vddupq[_wb]_u8"
    assert [
        (parameter.raw, parameter.type, parameter.name)
        for parameter in prototype.parameters
    ] == [
        ("uint32_t *a", "uint32_t *", "a"),
        ("const int imm", "const int", "imm"),
    ]


def test_missing_classification_and_section_are_diagnostics() -> None:
    definitions = StringIO(
        "<HEADER>\tIntrinsic\tArgument preparation\tInstruction\tResult\tSupported architectures\n"
        "int32x4_t [__arm_]vfoo[_s32](int32x4_t a)\ta -> Qn\tVFOO Qd, Qn\tQd -> result\tMVE\n"
    )

    result = parse_tabular_sources(
        definitions,
        StringIO(""),
        family="mve",
        definitions_source="mve.csv",
        classifications_source="mve_classification.csv",
    )

    assert {diagnostic.code for diagnostic in result.intrinsics[0].diagnostics} == {
        "tabular.classification_missing",
        "tabular.features_unspecified",
        "tabular.maturity_unspecified",
        "tabular.section_missing",
    }


def test_wrong_definition_column_count_is_rejected() -> None:
    definitions = StringIO(
        "<HEADER>\tIntrinsic\tArgument preparation\tInstruction\tResult\tSupported architectures\n"
        "int32x4_t [__arm_]vfoo[_s32](int32x4_t a)\ta -> Qn\tVFOO Qd, Qn\tMVE\n"
    )

    with pytest.raises(TabularFormatError, match="expected 5 definition columns"):
        parse_tabular_sources(
            definitions,
            StringIO(""),
            family="mve",
            definitions_source="mve.csv",
            classifications_source="mve_classification.csv",
        )


def test_canonical_bridge_preserves_tabular_content_and_provenance() -> None:
    result = load_tabular_sources(
        FIXTURES / "mve.tsv",
        FIXTURES / "mve_classification.tsv",
        family="mve",
    )

    callable_ = to_concrete_callables(
        result.intrinsics,
        repository="ARM-software/acle",
        commit="0123456789abcdef",
        source_root=FIXTURES,
    )[0]

    assert callable_.name == "vaddq_s32"
    assert callable_.name_role is NameRole.TYPED
    assert callable_.name_availability is not None
    assert callable_.name_availability.op is AvailabilityOp.NOT
    assert callable_.name_availability.arguments[0].op is AvailabilityOp.DEFINED
    assert callable_.name_availability.arguments[0].key == (
        "__ARM_MVE_PRESERVE_USER_NAMESPACE"
    )
    assert [(alias.name, alias.role) for alias in callable_.aliases] == [
        ("__arm_vaddq_s32", NameRole.PREFIXED),
        ("__arm_vaddq", NameRole.OVERLOADED),
        ("vaddq", NameRole.OVERLOADED),
    ]
    assert callable_.signature.render(callable_.name) == (
        "int32x4_t vaddq_s32(int32x4_t a, int32x4_t b)"
    )
    assert callable_.semantics.summary == "Vector arithmetic"
    assert callable_.semantics.description == (
        "MVE definitions; this prose is retained but not interpreted as feature metadata."
    )
    assert callable_.semantics.operation == "a -> Qn;b -> Qm"
    assert callable_.semantics.result == "Qd -> result"
    assert callable_.instructions[0].form == "VADD.I32 Qd, Qn, Qm"
    assert callable_.instructions[0].argument_mapping == "a -> Qn;b -> Qm"
    assert callable_.instructions[0].result_mapping == "Qd -> result"
    assert callable_.taxonomy == (("Vector arithmetic", "Add", "Addition"),)
    assert callable_.headers == ("arm_mve.h",)
    assert callable_.maturity is Maturity.UNSPECIFIED
    assert {source.path for source in callable_.sources} == {
        "mve.tsv",
        "mve_classification.tsv",
    }
    assert all(source.license_id == "Apache-2.0" for source in callable_.sources)
    assert {diagnostic.code for diagnostic in callable_.diagnostics} == {
        "tabular.features_unspecified",
        "tabular.maturity_unspecified",
    }
    provenance = {
        field.field: field.provenance.kind for field in callable_.field_provenance
    }
    assert provenance["name"] is ProvenanceKind.EXPANDED
    assert provenance["signature"] is ProvenanceKind.EXPLICIT
    assert provenance["maturity"] is ProvenanceKind.UNRESOLVED
    assert provenance["compilation"] is ProvenanceKind.UNRESOLVED


def test_catalog_bridge_combines_neon_and_mve_families() -> None:
    neon = load_tabular_sources(
        FIXTURES / "advsimd.tsv",
        FIXTURES / "advsimd_classification.tsv",
        family="neon",
    )
    mve = load_tabular_sources(
        FIXTURES / "mve.tsv",
        FIXTURES / "mve_classification.tsv",
        family="mve",
    )

    catalog = to_catalog(
        (neon, mve),
        version="fixture",
        repository="ARM-software/acle",
        commit="0123456789abcdef",
        source_root=FIXTURES,
    )

    assert len(catalog.callables) == 5
    assert sum(len(callable_.aliases) for callable_ in catalog.callables) == 9
    assert [(family.key, family.headers) for family in catalog.families] == [
        ("mve", ("arm_mve.h",)),
        ("neon", ("arm_neon.h",)),
    ]
    assert catalog.provenance.kind is ProvenanceKind.DERIVED
    assert {source.path for source in catalog.provenance.sources} == {
        "advsimd.tsv",
        "advsimd_classification.tsv",
        "mve.tsv",
        "mve_classification.tsv",
    }


def test_canonical_bridge_merges_alternative_rows_for_one_callable() -> None:
    definitions = StringIO(
        "<HEADER>\tIntrinsic\tArgument preparation\tInstruction\tResult\tSupported architectures\n"
        "<SECTION>\tShift left\tImmediate-dependent instruction selection.\n"
        "int16x8_t vshll_n_s8(int8x8_t a, __builtin_constant_p(n))\t"
        "a -> Vn.8B;0 <= n <= 7\tSSHLL Vd.8H,Vn.8B,#n\tVd.8H -> result\tA64\n"
        "int16x8_t vshll_n_s8(int8x8_t a, __builtin_constant_p(n))\t"
        "a -> Vn.8B;n == 8\tSHLL Vd.8H,Vn.8B,#n\tVd.8H -> result\tA64\n"
    )
    parsed = parse_tabular_sources(
        definitions,
        StringIO("vshll_n_s8\tShift|Left\n"),
        family="neon",
        definitions_source="advsimd.csv",
        classifications_source="advsimd_classification.csv",
    )

    callables = to_concrete_callables(
        parsed.intrinsics,
        repository="ARM-software/acle",
        commit="0123456789abcdef",
    )

    assert len(callables) == 1
    callable_ = callables[0]
    assert callable_.compilation.execution_states == ("AArch64",)
    assert callable_.semantics.operation == (
        "a -> Vn.8B;0 <= n <= 7\na -> Vn.8B;n == 8"
    )
    assert [instruction.form for instruction in callable_.instructions] == [
        "SSHLL Vd.8H,Vn.8B,#n",
        "SHLL Vd.8H,Vn.8B,#n",
    ]
    assert {source.start_line for source in callable_.sources} >= {3, 4}
