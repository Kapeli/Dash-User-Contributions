from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from arm_acle_docset.model import AvailabilityExpr, NameRole, ProvenanceKind
from arm_acle_docset.pipeline import _target_guard_concrete_names
from arm_acle_docset.sources.llvm import (
    LLVM_COMMIT,
    LLVM_RELEASE_TAG,
    LLVM_TABLEGEN_FILES,
    LLVMFormatError,
    LLVMPinMismatch,
    LLVMTargetGuard,
    generate_headers,
    load_llvm_include_dir,
    load_normalized_inventory,
    parse_llvm_header,
    parse_sve_target_guards,
    to_model_callables,
    write_normalized_inventory,
)

FIXTURES = Path(__file__).parent / "fixtures" / "llvm"
HEADERS = ("arm_sve.h", "arm_sme.h", "arm_mve.h", "arm_neon.h")


def _fixture_inventory():
    return load_llvm_include_dir(
        FIXTURES,
        expected_hashes=None,
        headers=HEADERS,
    )


def _by_builtin(inventory, builtin: str):
    return next(item for item in inventory.callables if item.builtin == builtin)


def _required_record_name(record: LLVMTargetGuard) -> str:
    assert record.record_name is not None
    return record.record_name


def test_inventory_records_the_exact_llvm_release_pin() -> None:
    inventory = _fixture_inventory()

    assert LLVM_RELEASE_TAG == "llvmorg-22.1.1"
    assert LLVM_COMMIT == "fef02d48c08db859ef83f84232ed78bd9d1c323a"
    assert inventory.release_tag == LLVM_RELEASE_TAG
    assert inventory.commit == LLVM_COMMIT
    assert dict(inventory.header_sha256) == {
        name: hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest()
        for name in HEADERS
    }


def test_sve_uses_builtin_identity_for_one_to_many_overloads() -> None:
    inventory = _fixture_inventory()
    scalar = _by_builtin(inventory, "__builtin_sve_svadd_n_s32_m")
    vector = _by_builtin(inventory, "__builtin_sve_svadd_s32_m")

    assert scalar.explicit_names == ("svadd_n_s32_m",)
    assert scalar.aliases == ("svadd_m",)
    assert scalar.prototype.return_type == "svint32_t"
    assert [parameter.type for parameter in scalar.prototype.parameters] == [
        "svbool_t",
        "svint32_t",
        "int32_t",
    ]
    assert vector.explicit_names == ("svadd_s32_m",)
    assert vector.aliases == ("svadd_m",)
    assert scalar.prototype.signature != vector.prototype.signature


def test_explicit_name_is_not_inferred_from_overloadable_attribute() -> None:
    inventory = _fixture_inventory()
    reinterpret = _by_builtin(inventory, "__builtin_sve_reinterpret_s8_s8")

    assert reinterpret.explicit_names == ("svreinterpret_s8_s8",)
    assert reinterpret.aliases == ("svreinterpret_s8",)
    assert not reinterpret.diagnostics


def test_unnamed_multiword_parameter_types_are_not_mistaken_for_names() -> None:
    inventory = _fixture_inventory()
    probe = _by_builtin(inventory, "__builtin_sve_svprobe_u32")

    assert [
        (parameter.type, parameter.name) for parameter in probe.prototype.parameters
    ] == [
        ("unsigned int", None),
        ("void const *", None),
    ]


def test_mve_preserves_namespace_and_polymorphism_as_independent_axes() -> None:
    inventory = _fixture_inventory()
    vaddq = _by_builtin(inventory, "__builtin_arm_mve_vaddq_n_s32")

    assert vaddq.explicit_names == ("__arm_vaddq_n_s32", "vaddq_n_s32")
    assert vaddq.aliases == ("__arm_vaddq", "vaddq")
    assert [
        (name.spelling, name.namespace, name.availability) for name in vaddq.names
    ] == [
        ("__arm_vaddq_n_s32", "prefixed", None),
        ("__arm_vaddq", "prefixed", None),
        (
            "vaddq_n_s32",
            "unprefixed",
            "!defined(__ARM_MVE_PRESERVE_USER_NAMESPACE)",
        ),
        (
            "vaddq",
            "unprefixed",
            "!defined(__ARM_MVE_PRESERVE_USER_NAMESPACE)",
        ),
    ]
    assert "vaddq_n" not in vaddq.aliases


def test_mve_does_not_invent_an_alias_when_the_header_has_none() -> None:
    inventory = _fixture_inventory()
    vcvt = _by_builtin(inventory, "__builtin_arm_mve_vcvtq_s16_f16")

    assert vcvt.explicit_names == ("__arm_vcvtq_s16_f16", "vcvtq_s16_f16")
    assert vcvt.aliases == ()


def test_mve_polymorphic_only_builtin_is_not_mislabeled_as_explicit() -> None:
    inventory = _fixture_inventory()
    uninitialized = _by_builtin(
        inventory, "__builtin_arm_mve_vuninitializedq_polymorphic_s32"
    )

    assert uninitialized.explicit_names == ()
    assert uninitialized.aliases == ("__arm_vuninitializedq", "vuninitializedq")
    assert [diagnostic.code for diagnostic in uninitialized.diagnostics] == [
        "llvm.explicit_declaration_missing"
    ]


def test_sme_includes_builtin_and_direct_public_functions() -> None:
    inventory = _fixture_inventory()
    mopa = _by_builtin(inventory, "__builtin_sme_svmopa_za32_s8_m")

    assert mopa.explicit_names == ("svmopa_za32_s8_m",)
    assert mopa.aliases == ("svmopa_za32_m",)
    assert any(
        item.builtin is None and item.primary_name == "svundef_za"
        for item in inventory.callables
    )
    assert _by_builtin(
        inventory, "__builtin_sme___arm_in_streaming_mode"
    ).explicit_names == ("__arm_in_streaming_mode",)


def test_neon_collects_functions_but_filters_helpers_and_macros() -> None:
    inventory = _fixture_inventory()
    neon_names = {
        name.spelling
        for item in inventory.callables
        if item.family == "neon"
        for name in item.names
    }

    assert neon_names == {"vaddq_s32"}
    neon_callable = next(
        item for item in inventory.callables if item.primary_name == "vaddq_s32"
    )
    assert neon_callable.target_features == ("neon",)
    assert "vld1q_s32" not in neon_names
    assert any(
        diagnostic.code == "llvm.neon_macros_not_enumerated"
        for diagnostic in inventory.diagnostics
    )


def test_neon_preserves_exact_declaration_target_features() -> None:
    text = """
__ai __attribute__((target("neon"))) int32x4_t vbaseq_s32(int32x4_t a) {
__ai __attribute__((target("fp16fml,neon"))) float32x4_t vfmlalq_low_f16(float32x4_t a, float16x4_t b, float16x4_t c) {
"""
    inventory = parse_llvm_header(
        text,
        header="arm_neon.h",
        sha256=hashlib.sha256(text.encode()).hexdigest(),
    )

    assert {
        item.primary_name: item.target_features for item in inventory.callables
    } == {
        "vbaseq_s32": ("neon",),
        "vfmlalq_low_f16": ("fp16fml", "neon"),
    }
    canonical_callables = json.loads(inventory.canonical_json())["callables"]
    assert [item["target_features"] for item in canonical_callables] == [
        ["neon"],
        ["fp16fml", "neon"],
    ]


def test_neon_target_feature_mismatch_remains_unresolved() -> None:
    text = """
__ai __attribute__((target("neon"))) int32x4_t vprobeq_s32(int32x4_t a) {
__ai __attribute__((target("fp16fml,neon"))) int32x4_t vprobeq_s32(int32x4_t a) {
"""
    inventory = parse_llvm_header(
        text,
        header="arm_neon.h",
        sha256=hashlib.sha256(text.encode()).hexdigest(),
    )
    probe = next(
        item for item in inventory.callables if item.primary_name == "vprobeq_s32"
    )

    assert probe.target_features == ()
    assert [diagnostic.code for diagnostic in probe.diagnostics] == [
        "llvm.target_feature_mismatch"
    ]
    assert "[fp16fml, neon], [neon]" in probe.diagnostics[0].message
    assert tuple(source.line for source in probe.source_refs) == (2, 3)


def test_normalized_inventory_round_trips_without_source_headers(
    tmp_path: Path,
) -> None:
    inventory = _fixture_inventory()
    path = tmp_path / "llvm-inventory.json"

    write_normalized_inventory(inventory, path)
    restored = load_normalized_inventory(path)

    assert restored.canonical_json() == inventory.canonical_json()


def test_normalized_inventory_defaults_missing_target_features_to_empty(
    tmp_path: Path,
) -> None:
    data = json.loads(_fixture_inventory().canonical_json())
    for callable_data in data["callables"]:
        callable_data.pop("target_features")
    path = tmp_path / "legacy-llvm-inventory.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    restored = load_normalized_inventory(path)

    assert all(item.target_features == () for item in restored.callables)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("role", None, "unsupported callable name role"),
        ("namespace", "invalid", "unsupported callable namespace"),
        ("availability", 1, "availability must be a string or null"),
    ),
)
def test_normalized_inventory_rejects_invalid_name_metadata(
    tmp_path: Path,
    field: str,
    value: object,
    message: str,
) -> None:
    data = json.loads(_fixture_inventory().canonical_json())
    data["callables"][0]["names"][0][field] = value
    path = tmp_path / "llvm-inventory.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(LLVMFormatError, match=message):
        load_normalized_inventory(path)


def test_canonical_bridge_defaults_to_sve_and_sme_without_tabular_duplicates() -> None:
    inventory = _fixture_inventory()

    callables = to_model_callables(inventory)
    scalar = next(item for item in callables if item.name == "svadd_n_s32_m")

    assert {item.family for item in callables} == {"sve", "sme"}
    assert not any(item.family in {"neon", "mve"} for item in callables)
    assert [(alias.name, alias.role) for alias in scalar.aliases] == [
        ("svadd_m", NameRole.OVERLOADED)
    ]
    assert scalar.headers == ("arm_sve.h",)
    assert scalar.sources[0].commit == LLVM_COMMIT
    assert scalar.sources[0].license_id == "Apache-2.0 WITH LLVM-exception"
    assert scalar.semantics.provenance.kind is ProvenanceKind.UNRESOLVED
    assert scalar.compilation.provenance.kind is ProvenanceKind.UNRESOLVED


def test_canonical_bridge_can_enable_mve_for_validation_only() -> None:
    inventory = _fixture_inventory()

    callables = to_model_callables(inventory, families=("mve",))
    vaddq = next(item for item in callables if item.name == "__arm_vaddq_n_s32")

    assert {(alias.name, alias.role) for alias in vaddq.aliases} == {
        ("__arm_vaddq", NameRole.OVERLOADED),
        ("vaddq_n_s32", NameRole.UNPREFIXED),
        ("vaddq", NameRole.OVERLOADED),
    }
    assert (
        next(alias for alias in vaddq.aliases if alias.name == "vaddq").availability
        is not None
    )


def test_tablegen_generation_rejects_missing_pinned_inputs(tmp_path: Path) -> None:
    with pytest.raises(LLVMFormatError, match="missing pinned LLVM TableGen inputs"):
        generate_headers(tmp_path, Path(__file__), tmp_path / "include")


def test_tablegen_generation_rejects_wrong_tool_version(tmp_path: Path) -> None:
    for name in LLVM_TABLEGEN_FILES:
        (tmp_path / name).write_text("// fixture\n", encoding="utf-8")
    tool = tmp_path / "clang-tblgen"
    tool.write_text("#!/bin/sh\necho 'LLVM version 99.0.0'\n", encoding="utf-8")
    tool.chmod(0o755)

    with pytest.raises(LLVMPinMismatch, match="version mismatch"):
        generate_headers(tmp_path, tool, tmp_path / "include")


def test_pinned_hash_mismatch_is_a_hard_failure() -> None:
    with pytest.raises(LLVMPinMismatch, match="SHA-256 mismatch"):
        load_llvm_include_dir(
            FIXTURES,
            expected_hashes={name: "0" * 64 for name in HEADERS},
            headers=HEADERS,
        )


def test_tablegen_target_guard_parser_inherits_scoped_guards() -> None:
    records = parse_sve_target_guards(
        """
let SVETargetGuard = "sve2|sme" in {
def SVADCLB : SInst<"svadclb[_{d}]", "dddd", "UiUl", MergeNone>;
defm SVADDLB_S : SInstWideDSPLong<"svaddlb", "sil", "builtin">;
let Unrelated = 1 in {
  def SVADDHNB : SInst<"svaddhnb[_{d}]", "hdd", "sil", MergeNone>;
}
}
let SVETargetGuard = "sve-aes", SMETargetGuard = "ssve-aes" in {
def SVAESD : SInst<"svaesd[_{d}]", "ddd", "Uc", MergeNone>;
}
"""
    )
    by_name = {record.spelling: record for record in records}

    expected_sve2 = AvailabilityExpr.any(
        AvailabilityExpr.defined("sme"),
        AvailabilityExpr.defined("sve2"),
    )
    for name in ("svadclb", "svaddhnb", "svaddlb"):
        assert by_name[name].sve_guard == expected_sve2
        assert by_name[name].sme_guard == AvailabilityExpr.defined("sme")
        assert by_name[name].diagnostics == ()
    assert by_name["svaesd"].sve_guard == AvailabilityExpr.defined("sve-aes")
    assert by_name["svaesd"].sme_guard == AvailabilityExpr.defined("ssve-aes")
    assert by_name["svaesd"].source.path.endswith("arm_sve.td")
    assert by_name["svaesd"].source.license_id == ("Apache-2.0 WITH LLVM-exception")
    source_url = by_name["svaesd"].source.url
    assert source_url is not None
    assert source_url.endswith(f"#L{by_name['svaesd'].source.start_line}")


def test_tablegen_target_guard_parser_retains_unparsed_guard_as_raw() -> None:
    record = parse_sve_target_guards(
        'let SVETargetGuard = "sve2 ? sme" in {'
        'def SVPROBE : SInst<"svprobe[_{d}]", "d", "i", MergeNone>;}'
    )[0]

    assert record.sve_guard is not None
    assert record.sve_guard.text == "sve2 ? sme"
    assert record.diagnostics


def test_tablegen_target_guard_parser_accepts_compact_in_and_retains_identity() -> None:
    records = parse_sve_target_guards(
        """
let SVETargetGuard = InvalidMode,
    SMETargetGuard = "sme2,sve-b16b16"in {
def SVBFCLAMP_X2 : SInst<"svclamp[_single_{d}_x2]", "22dd", "b", MergeNone>;
}
let SVETargetGuard = "i8mm"in {
def SVI8MM : SInst<"svi8mm[_{d}]", "ddd", "Uc", MergeNone>;
}
"""
    )

    clamp = next(record for record in records if record.record_name == "SVBFCLAMP_X2")
    assert clamp.sve_guard is None
    assert clamp.sme_guard == AvailabilityExpr.all(
        AvailabilityExpr.defined("sme2"),
        AvailabilityExpr.defined("sve-b16b16"),
    )
    assert clamp.name_pattern == "svclamp[_single_{d}_x2]"
    assert clamp.prototype == "22dd"
    assert clamp.type_spec == "b"
    assert clamp.merge_suffix == ""

    i8mm = next(record for record in records if record.record_name == "SVI8MM")
    assert i8mm.sve_guard == AvailabilityExpr.defined("i8mm")
    assert i8mm.sme_guard == AvailabilityExpr.defined("sme")


def test_tablegen_target_guard_parser_interprets_direct_inst_as_sinst() -> None:
    records = parse_sve_target_guards(
        """let SVETargetGuard = InvalidMode, SMETargetGuard = "sme2,fp8" in {
def FSCALE_X2 : Inst<"svscale[_{d}_x2]", "222.x", "fhd", MergeNone,
                     "aarch64_sme_fp8_scale_x2", [IsStreaming], []>;
}
"""
    )

    assert len(records) == 1
    record = records[0]
    assert record.record_name == "FSCALE_X2"
    assert record.record_class == "SInst"
    assert record.prototype == "222.x"
    assert record.type_spec == "fhd"
    assert record.merge_suffix == ""
    assert record.sve_guard is None
    assert record.sme_guard == AvailabilityExpr.all(
        AvailabilityExpr.defined("fp8"),
        AvailabilityExpr.defined("sme2"),
    )
    assert _target_guard_concrete_names(record) == (
        "svscale_f16_x2",
        "svscale_f32_x2",
        "svscale_f64_x2",
    )


def test_tablegen_target_guard_parser_accepts_typed_direct_inst_prefixes() -> None:
    records = parse_sve_target_guards(
        """let SVETargetGuard = InvalidMode, SMETargetGuard = "sme2,fp8" in {
def SVF1CVT_X2 : Inst<"svcvt1_{d}[_mf8]_x2", "2~>", "bh", MergeNone,
                      "aarch64_sve_fp8_cvt1_x2", [IsStreaming], []>;
def SVF2CVT_X2 : Inst<"svcvt2_{d}[_mf8]_x2", "2~>", "bh", MergeNone,
                      "aarch64_sve_fp8_cvt2_x2", [IsStreaming], []>;
def SVF1CVTL_X2 : Inst<"svcvtl1_{d}[_mf8]_x2", "2~>", "bh", MergeNone,
                       "aarch64_sve_fp8_cvtl1_x2", [IsStreaming], []>;
def SVF2CVTL_X2 : Inst<"svcvtl2_{d}[_mf8]_x2", "2~>", "bh", MergeNone,
                       "aarch64_sve_fp8_cvtl2_x2", [IsStreaming], []>;
}
"""
    )
    by_record = {_required_record_name(record): record for record in records}

    assert {name: record.spelling for name, record in by_record.items()} == {
        "SVF1CVT_X2": "svcvt1",
        "SVF2CVT_X2": "svcvt2",
        "SVF1CVTL_X2": "svcvtl1",
        "SVF2CVTL_X2": "svcvtl2",
    }
    assert {
        name for record in records for name in _target_guard_concrete_names(record)
    } == {
        "svcvt1_bf16_mf8_x2_fpm",
        "svcvt1_f16_mf8_x2_fpm",
        "svcvt2_bf16_mf8_x2_fpm",
        "svcvt2_f16_mf8_x2_fpm",
        "svcvtl1_bf16_mf8_x2_fpm",
        "svcvtl1_f16_mf8_x2_fpm",
        "svcvtl2_bf16_mf8_x2_fpm",
        "svcvtl2_f16_mf8_x2_fpm",
    }


@pytest.mark.parametrize(
    "statement",
    (
        'defm OPAQUE : UnknownMulticlass<"svcvt1_{d}[_mf8]_x2", "bh">;',
        'def BROKEN : Inst<"svcvt1_{d}[_mf8]_x2", "2~>", "bh", UnknownMerge>;',
    ),
)
def test_tablegen_target_guard_parser_rejects_unproven_typed_prefixes(
    statement: str,
) -> None:
    assert parse_sve_target_guards(statement) == ()


def test_tablegen_target_guard_parser_adds_fpm_suffix_from_prototype() -> None:
    records = parse_sve_target_guards(
        """
def SVFDOT : SInst<"svdot[_f16_mf8]", "dd~~>", "h", MergeNone>;
def SVFCVTN : Inst<"svcvtn_mf8[_{d}_x2]", "~2>", "bh", MergeNone,
                    "aarch64_sve_fp8_cvtn", [IsStreaming], []>;
"""
    )
    by_record = {_required_record_name(record): record for record in records}

    assert by_record["SVFDOT"].merge_suffix == "_fpm"
    assert _target_guard_concrete_names(by_record["SVFDOT"]) == ("svdot_f16_mf8_fpm",)
    assert by_record["SVFCVTN"].record_class == "SInst"
    assert by_record["SVFCVTN"].merge_suffix == "_fpm"
    assert _target_guard_concrete_names(by_record["SVFCVTN"]) == (
        "svcvtn_mf8_bf16_x2_fpm",
        "svcvtn_mf8_f16_x2_fpm",
    )


def test_tablegen_target_guard_parser_uses_only_allowlisted_multiclass_layouts() -> (
    None
):
    records = parse_sve_target_guards(
        """
defm ZPZ : SInstZPZ<"svabs", "csil", "intrinsic">;
defm ZPZZ : SInstZPZZ<"svadd", "csil", "m", "x">;
defm ZPZZZ : SInstZPZZZ<"svmla", "csil", "m", "x">;
defm ZPZXZ : SInstZPZxZ<"svqshl", "csil", "dPdx", "dPdK", "m", "x">;
defm WIDE : SInstWideDSPAcc<"svabalb", "sil", "intrinsic">;
defm CVTMXZ : SInstCvtMXZ<"svcvt_s32[_f16]", "ddPO", "dPO", "i", "intrinsic">;
defm CVTMX : SInstCvtMX<"svcvtlt_f32[_f16]", "ddPh", "dPh", "f", "intrinsic">;
defm OPAQUE : UnknownMulticlass<"svopaque", "must-not-be-guessed", "other">;
"""
    )
    by_record = {record.record_name: record for record in records}

    assert {name: by_record[name].type_spec for name in by_record} == {
        "ZPZ": "csil",
        "ZPZZ": "csil",
        "ZPZZZ": "csil",
        "ZPZXZ": "csil",
        "WIDE": "sil",
        "CVTMXZ": "i",
        "CVTMX": "f",
        "OPAQUE": None,
    }
    assert all(record.prototype is None for record in records)
    assert all(record.merge_suffix is None for record in records)


def test_tablegen_target_guard_parser_expands_exact_pinned_minmax_defms() -> None:
    records = parse_sve_target_guards(
        """let SVETargetGuard = InvalidMode, SMETargetGuard = "sme2" in {
defm MAX_SINGLE_X2 : MinMaxIntr<"max", "_single", "x2", "22d">;
defm MAX_MULTI_X2  : MinMaxIntr<"max", "",        "x2", "222">;
defm MAX_SINGLE_X4 : MinMaxIntr<"max", "_single", "x4", "44d">;
defm MAX_MULTI_X4  : MinMaxIntr<"max", "",        "x4", "444">;
defm MIN_SINGLE_X2 : MinMaxIntr<"min", "_single", "x2", "22d">;
defm MIN_MULTI_X2  : MinMaxIntr<"min", "",        "x2", "222">;
defm MIN_SINGLE_X4 : MinMaxIntr<"min", "_single", "x4", "44d">;
defm MIN_MULTI_X4  : MinMaxIntr<"min", "",        "x4", "444">;
}
"""
    )
    expected = (
        ("MAX_SINGLE_X2", "svmax[_single_{d}_x2]", "22d", 2),
        ("MAX_MULTI_X2", "svmax[_{d}_x2]", "222", 3),
        ("MAX_SINGLE_X4", "svmax[_single_{d}_x4]", "44d", 4),
        ("MAX_MULTI_X4", "svmax[_{d}_x4]", "444", 5),
        ("MIN_SINGLE_X2", "svmin[_single_{d}_x2]", "22d", 6),
        ("MIN_MULTI_X2", "svmin[_{d}_x2]", "222", 7),
        ("MIN_SINGLE_X4", "svmin[_single_{d}_x4]", "44d", 8),
        ("MIN_MULTI_X4", "svmin[_{d}_x4]", "444", 9),
    )

    assert len(records) == 24
    for defm_name, pattern, prototype, source_line in expected:
        expanded = [
            record
            for record in records
            if _required_record_name(record).endswith(defm_name)
        ]
        assert {record.record_name for record in expanded} == {
            f"SVS{defm_name}",
            f"SVU{defm_name}",
            f"SVF{defm_name}",
        }
        assert {record.record_class for record in expanded} == {"SInst"}
        assert {record.name_pattern for record in expanded} == {pattern}
        assert {record.prototype for record in expanded} == {prototype}
        assert {record.type_spec for record in expanded} == {
            "csil",
            "UcUsUiUl",
            "hfd",
        }
        assert {record.merge_suffix for record in expanded} == {""}
        assert {record.source.start_line for record in expanded} == {source_line}
        assert {record.sve_guard for record in expanded} == {None}
        assert {record.sme_guard for record in expanded} == {
            AvailabilityExpr.defined("sme2")
        }

    max_multi_x2 = [
        record
        for record in records
        if _required_record_name(record).endswith("MAX_MULTI_X2")
    ]
    concrete_names = {
        name for record in max_multi_x2 for name in _target_guard_concrete_names(record)
    }
    assert concrete_names == {
        "svmax_s8_x2",
        "svmax_s16_x2",
        "svmax_s32_x2",
        "svmax_s64_x2",
        "svmax_u8_x2",
        "svmax_u16_x2",
        "svmax_u32_x2",
        "svmax_u64_x2",
        "svmax_f16_x2",
        "svmax_f32_x2",
        "svmax_f64_x2",
    }
    assert not any(
        "bf16" in name
        for record in records
        for name in _target_guard_concrete_names(record)
    )


def test_tablegen_target_guard_parser_expands_pinned_minmax_by_vector() -> None:
    records = parse_sve_target_guards(
        """let SVETargetGuard = InvalidMode, SMETargetGuard = "sme2" in {
defm SVMINNM : SInstMinMaxByVector<"min">;
defm SVMAXNM : SInstMinMaxByVector<"max">;
}
"""
    )
    forms = (
        ("_SINGLE_X2", "_single_{d}_x2", "22d"),
        ("_SINGLE_X4", "_single_{d}_x4", "44d"),
        ("_X2", "_{d}_x2", "222"),
        ("_X4", "_{d}_x4", "444"),
    )

    assert len(records) == 8
    for record_prefix, operation, source_line in (
        ("SVMINNM", "min", 2),
        ("SVMAXNM", "max", 3),
    ):
        expanded = [
            record
            for record in records
            if _required_record_name(record).startswith(record_prefix)
        ]
        assert {record.record_name for record in expanded} == {
            f"{record_prefix}{suffix}" for suffix, _, _ in forms
        }
        assert {record.record_class for record in expanded} == {"SInst"}
        assert {(record.name_pattern, record.prototype) for record in expanded} == {
            (f"sv{operation}nm[{pattern}]", prototype)
            for _, pattern, prototype in forms
        }
        assert {record.type_spec for record in expanded} == {"hfd"}
        assert {record.merge_suffix for record in expanded} == {""}
        assert {record.source.start_line for record in expanded} == {source_line}
        assert {record.sve_guard for record in expanded} == {None}
        assert {record.sme_guard for record in expanded} == {
            AvailabilityExpr.defined("sme2")
        }

    concrete_names = {
        name for record in records for name in _target_guard_concrete_names(record)
    }
    assert len(concrete_names) == 24
    assert concrete_names == {
        f"sv{operation}nm{single}_{type_name}_{multiplicity}"
        for operation in ("min", "max")
        for single in ("", "_single")
        for type_name in ("f16", "f32", "f64")
        for multiplicity in ("x2", "x4")
    }


def test_tablegen_target_guard_parser_expands_exact_pinned_bf_defms() -> None:
    records = parse_sve_target_guards(
        """let SVETargetGuard = InvalidMode, SMETargetGuard = "sme2,sve-b16b16" in {
defm SVBFMIN : BfSingleMultiVector<"min">;
defm SVBFMAX : BfSingleMultiVector<"max">;
defm SVBFMINNM : BfSingleMultiVector<"minnm">;
defm SVBFMAXNM : BfSingleMultiVector<"maxnm">;
}
let SVETargetGuard = InvalidMode, SMETargetGuard = "sme2,sve-bfscale" in {
defm SVBFMUL : BfSingleMultiVector<"mul">;
}
"""
    )
    expected = (
        ("SVBFMIN", "min", 2, "sve-b16b16"),
        ("SVBFMAX", "max", 3, "sve-b16b16"),
        ("SVBFMINNM", "minnm", 4, "sve-b16b16"),
        ("SVBFMAXNM", "maxnm", 5, "sve-b16b16"),
        ("SVBFMUL", "mul", 8, "sve-bfscale"),
    )
    forms = (
        ("_SINGLE_X2", "_single_{d}_x2", "22d"),
        ("_SINGLE_X4", "_single_{d}_x4", "44d"),
        ("_X2", "_{d}_x2", "222"),
        ("_X4", "_{d}_x4", "444"),
    )

    assert len(records) == 20
    for defm_name, operation, source_line, feature in expected:
        expanded = [
            record
            for record in records
            if _required_record_name(record).startswith(f"{defm_name}_")
        ]
        assert {record.record_name for record in expanded} == {
            f"{defm_name}{suffix}" for suffix, _, _ in forms
        }
        assert {record.record_class for record in expanded} == {"SInst"}
        assert {(record.name_pattern, record.prototype) for record in expanded} == {
            (f"sv{operation}[{pattern}]", prototype) for _, pattern, prototype in forms
        }
        assert {record.type_spec for record in expanded} == {"b"}
        assert {record.merge_suffix for record in expanded} == {""}
        assert {record.source.start_line for record in expanded} == {source_line}
        assert {record.sve_guard for record in expanded} == {None}
        assert {record.sme_guard for record in expanded} == {
            AvailabilityExpr.all(
                AvailabilityExpr.defined("sme2"),
                AvailabilityExpr.defined(feature),
            )
        }

    bfmax = [
        record
        for record in records
        if _required_record_name(record).startswith("SVBFMAX_")
    ]
    concrete_names = {
        name for record in bfmax for name in _target_guard_concrete_names(record)
    }
    assert concrete_names == {
        "svmax_single_bf16_x2",
        "svmax_single_bf16_x4",
        "svmax_bf16_x2",
        "svmax_bf16_x4",
    }
    assert not any(
        "_f16_" in name
        for record in records
        for name in _target_guard_concrete_names(record)
    )


@pytest.mark.parametrize(
    "statement",
    (
        'defm MAX_MULTI_X2 : MinMaxIntr<"max", "", "x2", "22d">;',
        'defm MAX_MULTI_X2 : MinMaxIntr<"max", "", "x2", "222", "extra">;',
        'defm MAX_MULTI_X2 : MinMaxIntr<"maxnm", "", "x2", "222">;',
        'defm MAX_MULTI_X2 : MinMaxIntr<"min", "", "x2", "222">;',
        'defm SVBFMAX : BfSingleMultiVector<"min">;',
        'defm SVBFSUB : BfSingleMultiVector<"sub">;',
        'defm MAX : SInstMinMaxByVector<"max">;',
        'defm SVMAXNM : SInstMinMaxByVector<"min">;',
        'defm SVMINNM : SInstMinMaxByVector<"max">;',
    ),
)
def test_tablegen_target_guard_parser_rejects_non_pinned_defm_shapes(
    statement: str,
) -> None:
    assert parse_sve_target_guards(statement) == ()


def test_tablegen_target_guard_parser_keeps_unknown_multiclass_opaque() -> None:
    records = parse_sve_target_guards(
        'defm OPAQUE : UnknownMulticlass<"svopaque", "must-not-be-guessed">;'
    )

    assert len(records) == 1
    assert records[0].record_class == "UnknownMulticlass"
    assert _target_guard_concrete_names(records[0]) == ()
