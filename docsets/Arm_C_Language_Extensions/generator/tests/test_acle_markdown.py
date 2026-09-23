from __future__ import annotations

from pathlib import Path

import pytest

from arm_acle_docset.model import DiagnosticSeverity
from arm_acle_docset.sources.acle_markdown import (
    _macro_expression,
    _parse_expected_variant_names,
    parse_acle_markdown,
    parse_acle_markdown_file,
    to_enrichment_records,
    to_ir_records,
)

FIXTURES = Path(__file__).parent / "fixtures" / "acle"
SOURCE_COMMIT = "62d9cbd68abb6d18dd8f06980da7758d9dbe0560"


def _records(name: str) -> list[dict]:
    parsed = parse_acle_markdown_file(
        FIXTURES / name,
        source_commit=SOURCE_COMMIT,
    )
    return parsed["records"]


def _record(records: list[dict], name: str) -> dict:
    return next(item for item in records if item["names"]["explicit"] == name)


def _requirement_macros(expression: dict) -> set[str]:
    macros: set[str] = set()
    if "macro" in expression:
        macros.add(expression["macro"])
    for child in expression.get("args", []):
        macros.update(_requirement_macros(child))
    return macros


def test_orthogonal_type_and_direction_variants_expand_as_cross_product() -> None:
    variants, exhaustive = _parse_expected_variant_names(
        "svread_hor_za8_s8_m",
        (
            (10, "And similarly for u8, mf8."),
            (20, "Replacing `_hor` with `_ver` gives the associated vertical forms."),
        ),
    )

    assert exhaustive is True
    assert {item["explicit_name"] for item in variants} == {
        "svread_hor_za8_u8_m",
        "svread_hor_za8_mf8_m",
        "svread_ver_za8_s8_m",
        "svread_ver_za8_u8_m",
        "svread_ver_za8_mf8_m",
    }


@pytest.mark.parametrize(
    ("exemplar", "lines", "expected"),
    (
        (
            "svmul_single_f16_x2",
            ((1, "Variants are also available for:"), (2, "[_single_f32_x2]")),
            {"svmul_single_f32_x2"},
        ),
        (
            "svwrite_za8_s8_vg1x4",
            ((1, "Variants are also available for _za8[_u8], za8[_mf8]."),),
            {"svwrite_za8_u8_vg1x4", "svwrite_za8_mf8_vg1x4"},
        ),
        (
            "svdot_f32_f16",
            (
                (1, "Variants are also available for _s32_s16, _u32_u16"),
                (
                    2,
                    "and also for _s16_s8 and _u16_u8 if "
                    "(__ARM_FEATURE_SVE2p3 || __ARM_FEATURE_SME2p3).",
                ),
            ),
            {"svdot_s32_s16", "svdot_u32_u16", "svdot_s16_s8", "svdot_u16_u8"},
        ),
        (
            "svluti6_lane_s16_x4_s16_x2_u8_x2",
            (
                (1, "Variants are also available for:"),
                (2, "_u16_x2_u8_x2, _s16_x2_u8_x3"),
            ),
            {
                "svluti6_lane_s16_x4_u16_x2_u8_x2",
                "svluti6_lane_s16_x4_s16_x2_u8_x3",
            },
        ),
    ),
)
def test_expected_variant_parser_handles_pinned_source_notation(
    exemplar: str,
    lines: tuple[tuple[int, str], ...],
    expected: set[str],
) -> None:
    variants, exhaustive = _parse_expected_variant_names(exemplar, lines)

    assert exhaustive is True
    assert {item["explicit_name"] for item in variants} == expected


def test_identical_duplicate_variant_is_source_faithful() -> None:
    variants, exhaustive = _parse_expected_variant_names(
        "svmop4s_2x2_za32_f32_f32",
        (
            (1, "Variants are also available for:"),
            (2, "_za64_s16_s16"),
            (3, "_za64_s16_s16"),
        ),
    )

    assert exhaustive is True
    assert [item["explicit_name"] for item in variants] == ["svmop4s_2x2_za64_s16_s16"]
    assert variants[0]["line"] == 3


def test_return_type_disambiguates_single_atom_variant_suffix() -> None:
    parsed = parse_acle_markdown(
        """
# SVE2 intrinsics

``` c
// Variants are also available for: _bf16
svfloat16_t svcvt1_f16[_mf8]_fpm(svmfloat8_t zn, fpm_t fpm);
```
""",
        source_commit=SOURCE_COMMIT,
    )

    group = parsed["records"][0]["variant_group"]
    assert group["exhaustive"] is True
    assert [item["explicit_name"] for item in group["expected_variants"]] == [
        "svcvt1_bf16_mf8_fpm"
    ]


def test_sme_variant_tag_is_structured_as_a_broadening_requirement() -> None:
    variants, exhaustive = _parse_expected_variant_names(
        "svpsel_lane_b8",
        ((1, "Variants are also available for _b16, _b32 and _b64 [SME]"),),
    )

    assert exhaustive is True
    assert {item["explicit_name"] for item in variants} == {
        "svpsel_lane_b16",
        "svpsel_lane_b32",
        "svpsel_lane_b64",
    }
    assert all(item["availability_merge"] == "broaden_sme" for item in variants)
    assert all(
        item["availability"] == {"op": "defined", "macro": "__ARM_FEATURE_SME"}
        for item in variants
    )


def test_general_intrinsics_inherit_release_and_structured_availability() -> None:
    records = _records("general_crc.md")

    assert {item["names"]["explicit"] for item in records} == {
        "__crc32b",
        "__crc32d",
    }
    record = _record(records, "__crc32b")
    assert record["family"] == ["general"]
    assert record["maturity"]["support_level"] == "release"
    assert record["maturity"]["status"] == "inherited"
    assert record["header"] == [{"name": "arm_acle.h", "status": "explicit"}]
    assert _requirement_macros(record["availability"]["expression"]) == {
        "__ARM_FEATURE_CRC32"
    }
    assert record["availability"]["minimum_architecture"] == [
        {"op": "architecture_min", "version": "8", "profile": "A"}
    ]
    assert record["availability"]["execution_states"] == ["AArch32", "AArch64"]
    assert "Performs a CRC-32 checksum" in record["semantics"]


def test_sve_pattern_and_source_declared_variants_are_expanded() -> None:
    records = _records("sve_sme.md")
    record = _record(records, "svluti6_s8_x2")

    assert record["family"] == ["sve2.3"]
    assert record["names"]["overloaded"] == ["svluti6"]
    assert record["maturity"]["support_level"] == "alpha"
    assert record["header"] == [{"name": "arm_sve.h", "status": "explicit"}]
    assert _requirement_macros(record["availability"]["expression"]) == {
        "__ARM_FEATURE_SVE2p3"
    }
    assert record["variant_origin"] == "expanded_from_pattern"
    assert not record["diagnostics"]
    assert {
        item["names"]["explicit"]
        for item in records
        if item["names"]["explicit"].startswith("svluti6_")
    } == {"svluti6_s8_x2", "svluti6_u8_x2", "svluti6_mf8_x2"}
    unsigned = _record(records, "svluti6_u8_x2")
    assert unsigned["names"]["overloaded"] == ["svluti6"]
    assert unsigned["signature"]["return_type"] == "svuint8_t"
    assert unsigned["signature"]["parameters"][0]["type"] == "svuint8x2_t"
    assert unsigned["variant_origin"] == "expanded_from_variant_list"
    assert (
        unsigned["provenance"]["source"]["start_line"]
        < record["provenance"]["source"]["start_line"]
    )
    assert (
        unsigned["provenance"]["source"]["end_line"]
        == record["provenance"]["source"]["end_line"]
    )
    assert unsigned["provenance"]["fields"]["names"] == "expanded"


def test_source_declared_addqp_variants_expand_to_concrete_signatures() -> None:
    parsed = parse_acle_markdown(
        """
# SVE2.3 and SME2.3 instruction intrinsics

## ADDQP

``` c
// Variants are also available for _s16, _s32, _s64, _u8, _u16, _u32 and _u64.
svint8_t svaddqp[_s8](svint8_t zn, svint8_t zm);
```
""",
        source_commit=SOURCE_COMMIT,
    )

    records = parsed["records"]
    assert {item["names"]["explicit"] for item in records} == {
        "svaddqp_s8",
        "svaddqp_s16",
        "svaddqp_s32",
        "svaddqp_s64",
        "svaddqp_u8",
        "svaddqp_u16",
        "svaddqp_u32",
        "svaddqp_u64",
    }
    assert not parsed["diagnostics"]
    exemplar = _record(records, "svaddqp_s8")
    unsigned = _record(records, "svaddqp_u64")
    assert unsigned["names"] == {
        "pattern": "svaddqp[_u64]",
        "explicit": "svaddqp_u64",
        "overloaded": ["svaddqp"],
    }
    assert unsigned["signature"]["return_type"] == "svuint64_t"
    assert [item["type"] for item in unsigned["signature"]["parameters"]] == [
        "svuint64_t",
        "svuint64_t",
    ]
    assert (
        unsigned["signature"]["raw"]
        == "svuint64_t svaddqp_u64(svuint64_t zn, svuint64_t zm);"
    )
    assert (
        unsigned["provenance"]["source"]["start_line"]
        < exemplar["provenance"]["source"]["start_line"]
    )
    assert (
        unsigned["provenance"]["source"]["end_line"]
        == exemplar["provenance"]["source"]["end_line"]
    )
    assert unsigned["variant_origin"] == "expanded_from_variant_list"
    assert not any(
        item["code"] == "unexpanded_variant_prose"
        for record in records
        for item in record["diagnostics"]
    )

    canonical = next(
        item
        for item in to_ir_records(parsed, families=("sve2.3",))
        if item.name == "svaddqp_u64"
    )
    provenance = {item.field: item.provenance for item in canonical.field_provenance}
    assert provenance["names"].kind.value == "expanded"
    assert provenance["signature"].kind.value == "expanded"
    assert provenance["signature"].rule == "ACLE source-declared variant list expansion"


def test_variant_list_applies_to_adjacent_declaration_group_only() -> None:
    parsed = parse_acle_markdown(
        """
# SVE2 intrinsics

## Logical reductions

``` c
// Variants are also available for: _s16 and _u16.
svint8_t svandqv[_s8](svint8_t zn);
svint8_t sveorqv[_s8](svint8_t zn);

svint8_t svunrelated[_s8](svint8_t zn);
```
""",
        source_commit=SOURCE_COMMIT,
    )

    assert {item["names"]["explicit"] for item in parsed["records"]} == {
        "svandqv_s8",
        "svandqv_s16",
        "svandqv_u16",
        "sveorqv_s8",
        "sveorqv_s16",
        "sveorqv_u16",
        "svunrelated_s8",
    }
    assert _record(parsed["records"], "sveorqv_u16")["signature"]["return_type"] == (
        "svuint16_t"
    )
    assert not _record(parsed["records"], "svunrelated_s8")["variant_hints"]


def test_variant_comments_do_not_cross_an_unsupported_statement() -> None:
    parsed = parse_acle_markdown(
        """
# SVE2 intrinsics

## Unsupported statement boundary

``` c
// Variants are also available for _u16.
typedef svint16_t svunsupported_alias_t;
svint16_t svafter[_s16](svint16_t zn);
```
""",
        source_commit=SOURCE_COMMIT,
    )

    assert {item["names"]["explicit"] for item in parsed["records"]} == {"svafter_s16"}
    record = _record(parsed["records"], "svafter_s16")
    assert not record["variant_hints"]
    assert not record["diagnostics"]


def test_source_declared_variants_can_replace_typed_unbracketed_suffixes() -> None:
    parsed = parse_acle_markdown(
        """
# SME2 intrinsics

## LUTI4

``` c
// Variants are also available for _zt_u8 and _zt_mf8.
svint8x4_t svluti4_zt_s8_x4(svint8x4_t table, svuint8_t indices);
```
""",
        source_commit=SOURCE_COMMIT,
    )

    assert {item["names"]["explicit"] for item in parsed["records"]} == {
        "svluti4_zt_s8_x4",
        "svluti4_zt_u8_x4",
        "svluti4_zt_mf8_x4",
    }
    floating = _record(parsed["records"], "svluti4_zt_mf8_x4")
    assert floating["names"]["overloaded"] == []
    assert floating["signature"]["return_type"] == "svmfloat8x4_t"
    assert floating["signature"]["parameters"][0]["type"] == "svmfloat8x4_t"
    assert floating["signature"]["parameters"][1]["type"] == "svuint8_t"
    assert (
        floating["signature"]["raw"]
        == "svmfloat8x4_t svluti4_zt_mf8_x4(svmfloat8x4_t table, "
        "svuint8_t indices);"
    )
    assert floating["variant_origin"] == "expanded_from_variant_list"
    assert not floating["diagnostics"]

    canonical = next(
        item
        for item in to_ir_records(parsed, families=("sme2",))
        if item.name == "svluti4_zt_mf8_x4"
    )
    provenance = {item.field: item.provenance for item in canonical.field_provenance}
    assert provenance["names"].kind.value == "expanded"
    assert provenance["signature"].kind.value == "expanded"


def test_name_only_predicate_granularity_variants_preserve_signature() -> None:
    parsed = parse_acle_markdown(
        """
# SVE2 intrinsics

## Predicate creation

``` c
// Variants are also available for _b16, _b32 and _b64.
svbool_t svptrue_b8(void);
```
""",
        source_commit=SOURCE_COMMIT,
    )

    assert {item["names"]["explicit"] for item in parsed["records"]} == {
        "svptrue_b8",
        "svptrue_b16",
        "svptrue_b32",
        "svptrue_b64",
    }
    variant = _record(parsed["records"], "svptrue_b64")
    assert variant["signature"]["return_type"] == "svbool_t"
    assert variant["signature"]["parameters"] == []
    assert variant["signature"]["raw"] == "svbool_t svptrue_b64(void);"
    assert not variant["diagnostics"]


def test_name_only_and_typed_suffix_classes_cannot_cross() -> None:
    cases = (
        (
            "// Variants are also available for _u16.\nsvbool_t svcross_b8(void);",
            "svcross_b8",
        ),
        (
            (
                "// Variants are also available for _b16.\n"
                "svint8_t svcross_s8(svint8_t zn);"
            ),
            "svcross_s8",
        ),
        (
            (
                "// Variants are also available for _f8.\n"
                "svint8_t svunsupported_s8(svint8_t zn);"
            ),
            "svunsupported_s8",
        ),
    )
    for declaration, exemplar_name in cases:
        parsed = parse_acle_markdown(
            f"""
# SVE2 intrinsics

## Invalid cross-class variants

``` c
{declaration}
```
""",
            source_commit=SOURCE_COMMIT,
        )

        assert {item["names"]["explicit"] for item in parsed["records"]} == {
            exemplar_name
        }
        diagnostic = parsed["records"][0]["diagnostics"][0]
        assert diagnostic["code"] == "unexpanded_variant_prose"
        assert diagnostic["severity"] == "error"


def test_mixed_variant_list_is_all_or_nothing() -> None:
    parsed = parse_acle_markdown(
        """
# SVE2 intrinsics

## Mixed suffix grammar

``` c
// Variants are also available for _u16 and _za32.
svint16_t svmixed[_s16](svint16_t zn);
```
""",
        source_commit=SOURCE_COMMIT,
    )

    assert {item["names"]["explicit"] for item in parsed["records"]} == {"svmixed_s16"}
    diagnostic = _record(parsed["records"], "svmixed_s16")["diagnostics"][0]
    assert diagnostic["code"] == "unexpanded_variant_prose"
    assert diagnostic["severity"] == "error"


def test_widening_variant_relationship_stays_unresolved() -> None:
    parsed = parse_acle_markdown(
        """
# SVE2.3 intrinsics

## SABAL

``` c
// Variants are also available for _s32, _s64, _u16, _u32 and _u64.
svint16_t svabal[_s16](svint16_t zda, svint8_t zn, svint8_t zm);
```
""",
        source_commit=SOURCE_COMMIT,
    )

    assert {item["names"]["explicit"] for item in parsed["records"]} == {"svabal_s16"}
    diagnostic = _record(parsed["records"], "svabal_s16")["diagnostics"][0]
    assert diagnostic["code"] == "unexpanded_variant_prose"
    assert diagnostic["severity"] == "error"


def test_scalar_only_widening_variant_relationship_stays_unresolved() -> None:
    parsed = parse_acle_markdown(
        """
# SVE2 intrinsics

## Scalar widening

``` c
// Variants are also available for _s32.
svint16_t svscalar_widen_s16(svint16_t acc, int8_t zm);
```
""",
        source_commit=SOURCE_COMMIT,
    )

    assert {item["names"]["explicit"] for item in parsed["records"]} == {
        "svscalar_widen_s16"
    }
    record = parsed["records"][0]
    assert record["variant_group"]["exhaustive"] is True
    assert record["variant_group"]["expected_variants"] == [
        {
            "explicit_name": "svscalar_widen_s32",
            "suffix": "_s32",
            "line": 7,
            "availability": {"op": "always"},
        }
    ]
    assert record["diagnostics"][0]["severity"] == "error"


def test_complex_variant_names_are_exhaustive_without_fabricating_signatures() -> None:
    parsed = parse_acle_markdown(
        """
# SVE2 intrinsics

## Narrowing

``` c
// Variant for _u8[_s16_x2] is also available.
svuint16_t svqshrun[_n]_u16[_s32_x2](svuint16_t zda, svint32x2_t zn);
```
""",
        source_commit=SOURCE_COMMIT,
    )

    assert {item["names"]["explicit"] for item in parsed["records"]} == {
        "svqshrun_n_u16_s32_x2"
    }
    record = parsed["records"][0]
    group = record["variant_group"]
    assert set(group) == {
        "group_id",
        "exemplar_name",
        "expected_variants",
        "exhaustive",
    }
    assert group["group_id"].endswith(":7:8:svqshrun_n_u16_s32_x2")
    assert group["exemplar_name"] == "svqshrun_n_u16_s32_x2"
    assert group["exhaustive"] is True
    assert group["expected_variants"] == [
        {
            "explicit_name": "svqshrun_n_u8_s16_x2",
            "suffix": "_u8[_s16_x2]",
            "line": 7,
            "availability": {"op": "always"},
        }
    ]
    assert record["diagnostics"][0]["severity"] == "error"

    patch = to_enrichment_records(parsed)[0]
    assert patch["variant_group"] == group
    assert patch["source_signature"] == record["signature"]


def test_expected_variant_names_preserve_per_variant_availability() -> None:
    parsed = parse_acle_markdown(
        """
# SME2 intrinsics

## Outer products

``` c
// Variants are also available for:
//   _za16[_bf16]_m (only if __ARM_FEATURE_SME_B16B16 != 0)
//   and _za64[_f16]_m if __ARM_FEATURE_SME_F16F16 != 0
void svmopa_za32[_f32]_m(svbool_t pn, svfloat32_t zn, svfloat32_t zm);
```
""",
        source_commit=SOURCE_COMMIT,
    )

    record = parsed["records"][0]
    group = record["variant_group"]
    assert group["exhaustive"] is True
    assert group["expected_variants"] == [
        {
            "explicit_name": "svmopa_za16_bf16_m",
            "suffix": "_za16[_bf16]_m",
            "line": 8,
            "availability": {
                "op": "compare",
                "macro": "__ARM_FEATURE_SME_B16B16",
                "comparator": "!=",
                "value": 0,
            },
        },
        {
            "explicit_name": "svmopa_za64_f16_m",
            "suffix": "_za64[_f16]_m",
            "line": 9,
            "availability": {
                "op": "compare",
                "macro": "__ARM_FEATURE_SME_F16F16",
                "comparator": "!=",
                "value": 0,
            },
        },
    ]
    assert record["diagnostics"][0]["severity"] == "error"


def test_expected_variant_group_never_exposes_a_partial_name_list() -> None:
    parsed = parse_acle_markdown(
        """
# SVE2 intrinsics

## Incomplete prose

``` c
// Variants are also available for _u16 and an implementation-defined _u32.
svint16_t svpartial_s16(svint16_t zn);
```
""",
        source_commit=SOURCE_COMMIT,
    )

    record = parsed["records"][0]
    assert record["variant_group"]["exhaustive"] is False
    assert record["variant_group"]["expected_variants"] == []
    assert record["diagnostics"][0]["severity"] == "error"


def test_pinned_variant_cue_spellings_cannot_be_silently_ignored() -> None:
    parsed = parse_acle_markdown(
        """
# SME2 intrinsics

## Additional suffix spellings

``` c
// Also for _za16, _za32, _za64 and _za128 (with the same prototype).
void svld1_hor_za8(uint64_t slice, void *ptr);

// Variant for _u8[_s16_x2] is also available.
svuint16_t svqshrun[_n]_u16[_s32_x2](svuint16_t zda, svint32x2_t zn);
```
""",
        source_commit=SOURCE_COMMIT,
    )

    for name in ("svld1_hor_za8", "svqshrun_n_u16_s32_x2"):
        diagnostic = _record(parsed["records"], name)["diagnostics"][0]
        assert diagnostic["code"] == "unexpanded_variant_prose"
        assert diagnostic["severity"] == "error"


def test_also_for_cue_preserves_its_first_variant_token() -> None:
    parsed = parse_acle_markdown(
        """
# SVE2 intrinsics

## Additional integer spellings

``` c
// Also for _u16, _u32.
svint16_t svadditional_s16(svint16_t zn);
```
""",
        source_commit=SOURCE_COMMIT,
    )

    assert {item["names"]["explicit"] for item in parsed["records"]} == {
        "svadditional_s16",
        "svadditional_u16",
        "svadditional_u32",
    }


def test_variant_only_requirements_do_not_pollute_exemplar_availability() -> None:
    parsed = parse_acle_markdown(
        """
# SME2 intrinsics

## Multi-vector min/max

``` c
// Only if __ARM_FEATURE_SME_TMOP != 0
// Variants are also available for:
//   _bf16_x2 (only if __ARM_FEATURE_SVE_B16B16 != 0)
//   and also _s16_x2 if __ARM_FEATURE_SVE2p3 != 0
svfloat16x2_t svmax[_f16_x2](svfloat16x2_t zdn, svfloat16x2_t zm)
  __arm_streaming;
```
""",
        source_commit=SOURCE_COMMIT,
    )

    record = _record(parsed["records"], "svmax_f16_x2")

    assert _requirement_macros(record["availability"]["expression"]) == {
        "__ARM_FEATURE_SME_TMOP"
    }
    assert record["variant_origin"] == "unresolved"
    assert any(
        diagnostic["code"] == "unexpanded_variant_prose"
        for diagnostic in record["diagnostics"]
    )
    unresolved = next(
        diagnostic
        for diagnostic in record["diagnostics"]
        if diagnostic["code"] == "unexpanded_variant_prose"
    )
    assert unresolved["severity"] == "error"

    canonical = to_ir_records(parsed, families=("sme2",))
    diagnostic = next(
        item
        for item in canonical[0].diagnostics
        if item.code == "unexpanded_variant_prose"
    )
    assert diagnostic.severity is DiagnosticSeverity.ERROR


def test_pinned_variant_intro_spellings_start_a_variant_only_suffix() -> None:
    parsed = parse_acle_markdown(
        """
# SME2 intrinsics

## Variant spellings

``` c
// Only if __ARM_FEATURE_SME2 != 0
// Variant also available for _f16 if __ARM_FEATURE_SME_F16F16 != 0.
svbfloat16_t svvariant_one[_bf16](svbfloat16_t zn);

// Only if __ARM_FEATURE_SME2 != 0
// Variant for _u8 is available if __ARM_FEATURE_SVE2p3 != 0.
svint8_t svvariant_two[_s8](svint8_t zn);

// Only if __ARM_FEATURE_SME2 != 0
// Available variants are: _za16 if __ARM_FEATURE_SME_F8F16 != 0
//                         _za32 if __ARM_FEATURE_SME_F8F32 != 0
void svvariant_three[_za32](svfloat32_t zn);
```
""",
        source_commit=SOURCE_COMMIT,
    )

    for name in (
        "svvariant_one_bf16",
        "svvariant_two_s8",
        "svvariant_three_za32",
    ):
        record = _record(parsed["records"], name)
        assert _requirement_macros(record["availability"]["expression"]) == {
            "__ARM_FEATURE_SME2"
        }
        assert record["variant_origin"] == "unresolved"


def test_sme_attributes_semantics_and_instruction_group_are_preserved() -> None:
    records = _records("sve_sme.md")
    support = _record(records, "__arm_za_disable")
    intrinsic = _record(records, "svmopa_za32_f32_m")

    assert support["kind"] == "support_function"
    assert "turns ZA off" in support["semantics"]
    assert intrinsic["family"] == ["sme"]
    assert intrinsic["maturity"]["support_level"] == "beta"
    assert intrinsic["names"]["overloaded"] == ["svmopa_za32_m"]
    assert intrinsic["state"] == [
        {"state": "za", "mode": "inout"},
        {"state": "zt0", "mode": "preserves"},
    ]
    assert {item["mnemonics"][0] for item in intrinsic["instructions"]} >= {"BFMOPA"}
    assert intrinsic["availability"]["expression"] == {
        "op": "calling_context",
        "values": ["streaming"],
    }


def test_mode_specific_availability_remains_separate() -> None:
    record = _record(_records("sve_sme.md"), "svclamp_s32")

    assert record["family"] == ["sve2.1", "sme2"]
    assert _requirement_macros(record["availability"]["by_mode"]["non_streaming"]) == {
        "__ARM_FEATURE_SVE2p1"
    }
    assert _requirement_macros(record["availability"]["by_mode"]["streaming"]) == {
        "__ARM_FEATURE_SME2"
    }
    assert {item["name"] for item in record["header"]} == {
        "arm_sve.h",
        "arm_sme.h",
    }
    assert record["availability"]["expression"]["op"] == "any"


def test_sve_mapping_rows_defer_isa_family_to_tablegen_guards() -> None:
    parsed = parse_acle_markdown(
        """
# SVE language extensions and intrinsics

### Mapping of SVE instructions to intrinsics

| **Instruction** | **Intrinsic** |
| --------------- | ------------- |
| SADDLB | [`svaddlb`](https://example.invalid/?q=svaddlb) |
""",
        source_commit=SOURCE_COMMIT,
    )

    patch = next(
        item
        for item in to_enrichment_records(parsed)
        if item["match"]["base_names"] == ["svaddlb"]
    )

    assert patch["family"] == ["sve"]


def test_macro_expression_preserves_mixed_boolean_precedence() -> None:
    expression, diagnostic = _macro_expression(
        "Available when `(__ARM_FEATURE_SVE2 && __ARM_FEATURE_FP8DOT2) || "
        "__ARM_FEATURE_SSVE_FP8DOT2`.",
        (
            "__ARM_FEATURE_SVE2",
            "__ARM_FEATURE_FP8DOT2",
            "__ARM_FEATURE_SSVE_FP8DOT2",
        ),
    )

    assert diagnostic is None
    assert expression["op"] == "any"
    assert any(child["op"] == "all" for child in expression["args"])

    expression, diagnostic = _macro_expression(
        "Available when `__ARM_FEATURE_FP8 && (__ARM_FEATURE_SVE2 || "
        "__ARM_FEATURE_SME2)`.",
        (
            "__ARM_FEATURE_FP8",
            "__ARM_FEATURE_SVE2",
            "__ARM_FEATURE_SME2",
        ),
    )

    assert diagnostic is None
    assert expression["op"] == "all"
    assert any(child["op"] == "any" for child in expression["args"])


def test_ambiguous_macro_prose_is_retained_as_raw_with_diagnostic() -> None:
    sentence = "Available when __ARM_FEATURE_SVE2 and/or __ARM_FEATURE_SME2 is defined."
    expression, diagnostic = _macro_expression(
        sentence,
        ("__ARM_FEATURE_SVE2", "__ARM_FEATURE_SME2"),
    )

    assert expression == {"op": "raw", "text": sentence}
    assert diagnostic is not None


def test_pinned_fp8_prose_groups_sve2_or_sme2_as_one_clause() -> None:
    expression, diagnostic = _macro_expression(
        "Available when __ARM_FEATURE_FP8 is defined, and "
        "__ARM_FEATURE_SVE2 or __ARM_FEATURE_SME2 is defined.",
        (
            "__ARM_FEATURE_FP8",
            "__ARM_FEATURE_SVE2",
            "__ARM_FEATURE_SME2",
        ),
    )

    assert diagnostic is None
    assert expression == {
        "op": "all",
        "args": [
            {"op": "defined", "macro": "__ARM_FEATURE_FP8"},
            {
                "op": "any",
                "args": [
                    {"op": "defined", "macro": "__ARM_FEATURE_SVE2"},
                    {"op": "defined", "macro": "__ARM_FEATURE_SME2"},
                ],
            },
        ],
    }


def test_pinned_faminmax_prose_groups_either_clause_before_and() -> None:
    expression, diagnostic = _macro_expression(
        "Available when either __ARM_FEATURE_SVE2 or __ARM_FEATURE_SME2 is "
        "defined, and __ARM_FEATURE_FAMINMAX is defined.",
        (
            "__ARM_FEATURE_SVE2",
            "__ARM_FEATURE_SME2",
            "__ARM_FEATURE_FAMINMAX",
        ),
    )

    assert diagnostic is None
    assert expression == {
        "op": "all",
        "args": [
            {
                "op": "any",
                "args": [
                    {"op": "defined", "macro": "__ARM_FEATURE_SVE2"},
                    {"op": "defined", "macro": "__ARM_FEATURE_SME2"},
                ],
            },
            {"op": "defined", "macro": "__ARM_FEATURE_FAMINMAX"},
        ],
    }


def test_examples_are_ignored_and_missing_default_is_unspecified() -> None:
    records = _records("edge_cases.md")

    assert {item["names"]["explicit"] for item in records} == {
        "__arm_fpm_init",
        "__unnamed_parameters",
        "svsample_s32",
    }
    record = _record(records, "svsample_s32")
    assert record["maturity"] == {
        "support_level": "unspecified",
        "status": "unresolved",
        "source_line": None,
    }
    assert record["diagnostics"][0]["code"] == "unexpanded_variant_prose"

    unnamed = _record(records, "__unnamed_parameters")
    assert unnamed["signature"]["parameters"] == [
        {"name": None, "type": "uint64_t", "constraints": []},
        {"name": None, "type": "unsigned int", "constraints": []},
    ]


def test_conversion_boundary_can_parse_text_directly() -> None:
    markdown = (FIXTURES / "general_crc.md").read_text(encoding="utf-8")
    records = to_ir_records(markdown, source_commit=SOURCE_COMMIT)

    record = next(item for item in records if item.name == "__crc32b")
    assert record.sources[0].commit == SOURCE_COMMIT
    assert record.compilation.feature_macros == ("__ARM_FEATURE_CRC32",)
    assert record.compilation.architecture_min == "Armv8-A"
    assert record.compilation.execution_states == ("AArch32", "AArch64")


def test_sve_mapping_without_signature_is_an_enrichment_not_a_fake_callable() -> None:
    parsed = parse_acle_markdown_file(
        FIXTURES / "sve_sme.md",
        source_commit=SOURCE_COMMIT,
    )
    patches = to_enrichment_records(parsed)
    add = next(item for item in patches if item["match"]["base_names"] == ["svadd"])
    asr = next(item for item in patches if item["match"]["base_names"] == ["svasr"])

    assert add["source_signature"] is None
    assert (
        add["diagnostics"][0]["code"] == "signature_missing_use_declaration_inventory"
    )
    assert add["instructions"][0]["relation"] == "group"
    assert asr["instructions"][0]["relation"] == "optimizer_candidate"


def test_conversion_boundary_requires_commit_for_text() -> None:
    try:
        to_ir_records("# Empty")
    except ValueError as error:
        assert "source_commit" in str(error)
    else:
        raise AssertionError("expected source_commit validation")


def test_function_multiversion_attributes_are_not_parsed_as_acle_callables() -> None:
    parsed = parse_acle_markdown(
        """
# Function Multi Versioning

```cpp
int __attribute__((target_version("simd"))) f(int value);
int __attribute__((target_version("default"))) f(int value);
```
""",
        source_commit=SOURCE_COMMIT,
    )

    assert parsed["records"] == []
