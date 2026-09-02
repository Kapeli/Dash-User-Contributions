import pytest

from arm_acle_docset.model import AvailabilityExpr, ProvenanceKind
from arm_acle_docset.sources.acle_markdown import ACLE_MARKDOWN_LICENSE
from arm_acle_docset.sources.feature_flags import (
    ACLE_REVISION,
    ARM_FEATURE_REGISTRY_DOCUMENT_ID,
    ARM_FEATURE_REGISTRY_LICENSE,
    ARM_FEATURE_REGISTRY_TITLE,
    ARM_FEATURE_REGISTRY_URL,
    GCC_MANUAL_VERSION,
    LLVM_REVISION,
    ResolutionStatus,
    compilation_requirements_for,
    mappings_for_macro,
)


TOKEN_CASES = (
    (
        "faminmax",
        "__ARM_FEATURE_FAMINMAX",
        "faminmax",
        "FEAT_FAMINMAX",
        "Armv9.2-A",
        "-march=armv9.2-a+faminmax",
        "-mcpu=generic+faminmax",
        ResolutionStatus.RESOLVED,
        (2286, 2288),
        (478, 479),
    ),
    (
        "f64mm",
        "__ARM_FEATURE_SVE_MATMUL_FP64",
        "sve_f64mm",
        "FEAT_F64MM",
        "Armv8.2-A",
        "-march=armv8.2-a+f64mm",
        "-mcpu=generic+f64mm",
        ResolutionStatus.RESOLVED,
        (2490, 2495),
        (169, 171),
    ),
    (
        "ssve-bitperm",
        "__ARM_FEATURE_SSVE_BITPERM",
        "ssve_bitperm",
        "FEAT_SSVE_BitPerm",
        "Armv9.4-A",
        "-march=armv9.4-a+sme2p1+ssve-bitperm",
        "-mcpu=generic+sme2p1+ssve-bitperm",
        ResolutionStatus.PARTIAL,
        (2504, 2505),
        (573, 574),
    ),
    (
        "sve-bitperm",
        "__ARM_FEATURE_SVE2_BITPERM",
        "sve_bitperm",
        "FEAT_SVE_BitPerm",
        "Armv9-A",
        "-march=armv9-a+sve2-bitperm",
        "-mcpu=generic+sve2-bitperm",
        ResolutionStatus.RESOLVED,
        (2497, 2502),
        (385, 389),
    ),
    (
        "lut",
        "__ARM_FEATURE_LUT",
        "lut",
        "FEAT_LUT",
        "Armv9.2-A",
        "-march=armv9.2-a+lut",
        "-mcpu=generic+lut",
        ResolutionStatus.RESOLVED,
        (2297, 2301),
        (481, 482),
    ),
    (
        "sve-aes2",
        "__ARM_FEATURE_SVE_AES2",
        "sve_aes2",
        "FEAT_SVE_AES2",
        "Armv9.5-A",
        "-march=armv9.5-a+sve2p1+sve-aes+sve-aes2",
        "-mcpu=generic+sve2p1+sve-aes+sve-aes2",
        ResolutionStatus.PARTIAL,
        (2218, 2228),
        (552, 553),
    ),
    (
        "ssve-aes",
        "__ARM_FEATURE_SSVE_AES",
        "ssve_aes",
        "FEAT_SSVE_AES",
        "Armv9.5-A",
        "-march=armv9.5-a+sme2p1+ssve-aes",
        "-mcpu=generic+sme2p1+ssve-aes",
        ResolutionStatus.PARTIAL,
        (2222, 2226),
        (546, 547),
    ),
    (
        "fp8fma",
        "__ARM_FEATURE_FP8FMA",
        "fp8fma",
        "FEAT_FP8FMA",
        "Armv9.2-A",
        "-march=armv9.2-a+faminmax+lut+fp8fma",
        "-mcpu=generic+bf16+faminmax+lut+fp8fma",
        ResolutionStatus.RESOLVED,
        (2312, 2314),
        (487, 488),
    ),
    (
        "ssve-fp8fma",
        "__ARM_FEATURE_SSVE_FP8FMA",
        "ssve_fp8fma",
        "FEAT_SSVE_FP8FMA",
        "Armv9.2-A",
        "-march=armv9.2-a+faminmax+lut+fp8+sme2+ssve-fp8fma",
        "-mcpu=generic+bf16+faminmax+lut+fp8+sme2+ssve-fp8fma",
        ResolutionStatus.RESOLVED,
        (2334, 2337),
        (490, 491),
    ),
    (
        "fp8",
        "__ARM_FEATURE_FP8",
        "fp8",
        "FEAT_FP8",
        "Armv9.2-A",
        "-march=armv9.2-a+faminmax+lut+fp8",
        "-mcpu=generic+bf16+faminmax+lut+fp8",
        ResolutionStatus.RESOLVED,
        (2307, 2310),
        (484, 485),
    ),
    (
        "sve-bfscale",
        "__ARM_FEATURE_SVE_BFSCALE",
        "sve_bfscale",
        "FEAT_SVE_BFSCALE",
        "Armv9.2-A",
        "-march=armv9.2-a+sve2+sve-b16b16+sve-bfscale",
        "-mcpu=generic+sve2+sve-b16b16+sve-bfscale",
        ResolutionStatus.RESOLVED,
        (2165, 2173),
        (555, 556),
    ),
    (
        "ssve-fexpa",
        "__ARM_FEATURE_SSVE_FEXPA",
        "ssve_fexpa",
        "FEAT_SSVE_FEXPA",
        "Armv9.4-A",
        "-march=armv9.4-a+sme2p1+ssve-fexpa",
        "-mcpu=generic+sme2p1+ssve-fexpa",
        ResolutionStatus.PARTIAL,
        (2509, 2511),
        (582, 583),
    ),
    (
        "sme-f16f16",
        "__ARM_FEATURE_SME_F16F16",
        "sme_f16f16",
        "FEAT_SME_F16F16",
        "Armv9.2-A",
        "-march=armv9.2-a+sme2+sme-f16f16",
        "-mcpu=generic+sme2+sme-f16f16",
        ResolutionStatus.RESOLVED,
        (2104, 2112),
        (447, 448),
    ),
    (
        "f32mm",
        "__ARM_FEATURE_SVE_MATMUL_FP32",
        "sve_f32mm",
        "FEAT_F32MM",
        "Armv8.2-A",
        "-march=armv8.2-a+f32mm",
        "-mcpu=generic+f32mm",
        ResolutionStatus.RESOLVED,
        (2483, 2488),
        (165, 167),
    ),
    (
        "sve-f16f32mm",
        "__ARM_FEATURE_SVE_F16F32MM",
        "sve_f16f32mm",
        "FEAT_SVE_F16F32MM",
        "Armv9.2-A",
        "-march=armv9.2-a+sve2p1+sve-f16f32mm",
        "-mcpu=generic+sve2p1+sve-f16f32mm",
        ResolutionStatus.PARTIAL,
        (2462, 2466),
        (558, 559),
    ),
    (
        "sme-i16i64",
        "__ARM_FEATURE_SME_I16I64",
        "sme_i16i64",
        "FEAT_SME_I16I64",
        "Armv9.2-A",
        "-march=armv9.2-a+sme+sme-i16i64",
        "-mcpu=generic+sme+sme-i16i64",
        ResolutionStatus.RESOLVED,
        (2513, 2523),
        (417, 418),
    ),
    (
        "sme-f64f64",
        "__ARM_FEATURE_SME_F64F64",
        "sme_f64f64",
        "FEAT_SME_F64F64",
        "Armv9.2-A",
        "-march=armv9.2-a+sme+sme-f64f64",
        "-mcpu=generic+sme+sme-f64f64",
        ResolutionStatus.RESOLVED,
        (2525, 2534),
        (414, 415),
    ),
    (
        "sme-lutv2",
        "__ARM_FEATURE_SME_LUTv2",
        "sme_lutv2",
        "FEAT_SME_LUTv2",
        "Armv9.2-A",
        "-march=armv9.2-a+sme2+sme-lutv2",
        "-mcpu=generic+sme2+sme-lutv2",
        ResolutionStatus.RESOLVED,
        (2297, 2305),
        (505, 506),
    ),
    (
        "sme-mop4",
        "__ARM_FEATURE_SME_MOP4",
        "sme_mop4",
        "FEAT_SME_MOP4",
        "Armv9.4-A",
        "-march=armv9.4-a+sme2p1+sme-mop4",
        "-mcpu=generic+sme2p1+sme-mop4",
        ResolutionStatus.PARTIAL,
        (2548, 2557),
        (576, 577),
    ),
    (
        "sme-tmop",
        "__ARM_FEATURE_SME_TMOP",
        "sme_tmop",
        "FEAT_SME_TMOP",
        "Armv9.4-A",
        "-march=armv9.4-a+sme2p1+sme-tmop",
        "-mcpu=generic+sme2p1+sme-tmop",
        ResolutionStatus.PARTIAL,
        (2536, 2546),
        (579, 580),
    ),
    (
        "fp8dot4",
        "__ARM_FEATURE_FP8DOT4",
        "fp8dot4",
        "FEAT_FP8DOT4",
        "Armv9.2-A",
        "-march=armv9.2-a+faminmax+lut+fp8fma+fp8dot4",
        "-mcpu=generic+bf16+faminmax+lut+fp8fma+fp8dot4",
        ResolutionStatus.RESOLVED,
        (2312, 2323),
        (493, 494),
    ),
    (
        "fp8dot2",
        "__ARM_FEATURE_FP8DOT2",
        "fp8dot2",
        "FEAT_FP8DOT2",
        "Armv9.2-A",
        "-march=armv9.2-a+faminmax+lut+fp8fma+fp8dot4+fp8dot2",
        "-mcpu=generic+bf16+faminmax+lut+fp8fma+fp8dot4+fp8dot2",
        ResolutionStatus.RESOLVED,
        (2312, 2323),
        (496, 497),
    ),
    (
        "ssve-fp8dot4",
        "__ARM_FEATURE_SSVE_FP8DOT4",
        "ssve_fp8dot4",
        "FEAT_SSVE_FP8DOT4",
        "Armv9.2-A",
        "-march=armv9.2-a+faminmax+lut+sme2+ssve-fp8fma+ssve-fp8dot4",
        "-mcpu=generic+bf16+faminmax+lut+sme2+ssve-fp8fma+ssve-fp8dot4",
        ResolutionStatus.RESOLVED,
        (2312, 2323),
        (499, 500),
    ),
    (
        "ssve-fp8dot2",
        "__ARM_FEATURE_SSVE_FP8DOT2",
        "ssve_fp8dot2",
        "FEAT_SSVE_FP8DOT2",
        "Armv9.2-A",
        "-march=armv9.2-a+faminmax+lut+sme2+ssve-fp8fma+ssve-fp8dot4+ssve-fp8dot2",
        "-mcpu=generic+bf16+faminmax+lut+sme2+ssve-fp8fma+ssve-fp8dot4+ssve-fp8dot2",
        ResolutionStatus.RESOLVED,
        (2312, 2323),
        (502, 503),
    ),
    (
        "sme-f8f32",
        "__ARM_FEATURE_SME_F8F32",
        "sme_f8f32",
        "FEAT_SME_F8F32",
        "Armv9.2-A",
        "-march=armv9.2-a+faminmax+lut+fp8+sme2+sme-f8f32",
        "-mcpu=generic+bf16+faminmax+lut+fp8+sme2+sme-f8f32",
        ResolutionStatus.RESOLVED,
        (2339, 2343),
        (508, 509),
    ),
    (
        "sme-f8f16",
        "__ARM_FEATURE_SME_F8F16",
        "sme_f8f16",
        "FEAT_SME_F8F16",
        "Armv9.2-A",
        "-march=armv9.2-a+faminmax+lut+fp8+sme2+sme-f8f32+sme-f8f16",
        "-mcpu=generic+bf16+faminmax+lut+fp8+sme2+sme-f8f32+sme-f8f16",
        ResolutionStatus.RESOLVED,
        (2344, 2348),
        (511, 512),
    ),
)

REGISTRY_PAGES = {
    "faminmax": 142,
    "sve_f64mm": 42,
    "ssve_bitperm": 163,
    "sve_bitperm": 120,
    "lut": 147,
    "sve_aes2": 165,
    "ssve_aes": 163,
    "fp8fma": 145,
    "ssve_fp8fma": 153,
    "fp8": 143,
    "sve_bfscale": 165,
    "ssve_fexpa": 164,
    "sme_f16f16": 136,
    "sve_f32mm": 42,
    "sve_f16f32mm": 166,
    "sme_i16i64": 126,
    "sme_f64f64": 126,
    "sme_lutv2": 150,
    "sme_mop4": 161,
    "sme_tmop": 161,
    "fp8dot4": 145,
    "fp8dot2": 144,
    "ssve_fp8dot4": 152,
    "ssve_fp8dot2": 152,
    "sme_f8f32": 149,
    "sme_f8f16": 149,
}


@pytest.mark.parametrize(
    (
        "token",
        "macro",
        "key",
        "architecture_feature",
        "architecture_min",
        "march",
        "mcpu",
        "status",
        "acle_lines",
        "llvm_lines",
    ),
    TOKEN_CASES,
)
def test_target_tokens_have_exact_macro_and_compiler_mappings(
    token: str,
    macro: str,
    key: str,
    architecture_feature: str,
    architecture_min: str,
    march: str,
    mcpu: str,
    status: ResolutionStatus,
    acle_lines: tuple[int, int],
    llvm_lines: tuple[int, int],
) -> None:
    (mapping,) = mappings_for_macro(macro)

    assert mapping.key == key
    assert mapping.status is status
    assert mapping.acle_macros == (macro,)
    assert mapping.extension_names == (token,)
    assert mapping.architecture_features == (architecture_feature,)
    assert mapping.gate_for(macro).expression == AvailabilityExpr.defined(macro)

    sources = {source.repository: source for source in mapping.sources}
    assert set(sources) == {
        "ARM-software/acle",
        "Arm documentation",
        "llvm/llvm-project",
        *(() if status is ResolutionStatus.PARTIAL else ("gcc.gnu.org/onlinedocs",)),
    }
    acle = sources["ARM-software/acle"]
    assert (acle.commit, acle.path) == (ACLE_REVISION, "main/acle.md")
    assert (acle.start_line, acle.end_line) == acle_lines
    assert acle.license_id == ACLE_MARKDOWN_LICENSE

    llvm = sources["llvm/llvm-project"]
    assert (llvm.commit, llvm.path) == (
        LLVM_REVISION,
        "llvm/lib/Target/AArch64/AArch64Features.td",
    )
    assert (llvm.start_line, llvm.end_line) == llvm_lines
    assert llvm.license_id == "Apache-2.0 WITH LLVM-exception"

    registry = sources["Arm documentation"]
    assert (registry.commit, registry.path) == (
        ARM_FEATURE_REGISTRY_DOCUMENT_ID,
        f"{ARM_FEATURE_REGISTRY_TITLE}#page={REGISTRY_PAGES[key]}",
    )
    assert (registry.start_line, registry.end_line) == (None, None)
    assert registry.license_id == ARM_FEATURE_REGISTRY_LICENSE
    assert registry.url == f"{ARM_FEATURE_REGISTRY_URL}#page={REGISTRY_PAGES[key]}"

    (requirement,) = compilation_requirements_for(macro, target="aarch64")
    assert requirement.architecture_min == architecture_min
    assert requirement.profiles == ("A",)
    assert requirement.execution_states == ("AArch64",)
    assert requirement.extensions == (token,)
    assert requirement.feature_macros == (macro,)
    assert requirement.availability == AvailabilityExpr.defined(macro)
    assert requirement.unresolved_reason is None
    assert requirement.provenance.kind is ProvenanceKind.MANUAL_OVERRIDE
    assert requirement.provenance.rule is not None
    assert ARM_FEATURE_REGISTRY_DOCUMENT_ID in requirement.provenance.rule
    assert any(
        source.repository == "Arm documentation"
        for source in requirement.provenance.sources
    )

    examples = {
        (
            example.compiler,
            example.version,
            example.base_march,
            example.flags,
            example.default_enabled,
            example.target,
        )
        for example in requirement.compiler_flags
    }
    expected = {
        ("Clang", "22.1.1", None, (mcpu,), None, None),
        (
            "Clang",
            "22.1.1",
            march.removeprefix("-march=").split("+", 1)[0],
            (march,),
            False,
            None,
        ),
    }
    if status is ResolutionStatus.RESOLVED:
        expected.update(
            {
                ("GCC", GCC_MANUAL_VERSION, None, (mcpu,), None, None),
                (
                    "GCC",
                    GCC_MANUAL_VERSION,
                    march.removeprefix("-march=").split("+", 1)[0],
                    (march,),
                    False,
                    None,
                ),
            }
        )
    assert len(requirement.compiler_flags) == len(expected)
    assert examples == expected
    assert compilation_requirements_for(macro, target="aarch32") == ()


@pytest.mark.parametrize(
    (
        "macro",
        "key",
        "token",
        "architecture_min",
        "march",
        "mcpu",
        "default_enabled",
        "acle_lines",
        "llvm_lines",
    ),
    [
        (
            "__ARM_FEATURE_JCVT",
            "jcvt",
            "jscvt",
            "Armv8.3-A",
            "-march=armv8.3-a+jscvt",
            "-mcpu=generic+jscvt",
            True,
            (2387, 2392),
            (183, 186),
        ),
        (
            "__ARM_FEATURE_RNG",
            "rng",
            "rng",
            "Armv8.5-A",
            "-march=armv8.5-a+rng",
            "-mcpu=generic+rng",
            False,
            (1736, 1741),
            (268, 270),
        ),
        (
            "__ARM_FEATURE_MEMORY_TAGGING",
            "memory_tagging",
            "memtag",
            "Armv8.5-A",
            "-march=armv8.5-a+memtag",
            "-mcpu=generic+memtag",
            False,
            (5254, 5299),
            (272, 276),
        ),
        (
            "__ARM_FEATURE_LS64",
            "ls64",
            "ls64",
            "Armv8.7-A",
            "-march=armv8.7-a+ls64",
            "-mcpu=generic+ls64",
            True,
            (1798, 1805),
            (309, 311),
        ),
        (
            "__ARM_FEATURE_SYSREG128",
            "sysreg128",
            "d128",
            "Armv9.4-A",
            "-march=armv9.4-a+d128",
            "-mcpu=generic+d128",
            True,
            (1841, 1847),
            (466, 473),
        ),
        (
            "__ARM_FEATURE_SVE_B16MM",
            "sve_b16mm",
            "sve-b16mm",
            "Armv9.7-A",
            "-march=armv9.7-a+sve-b16mm",
            "-mcpu=generic+sve-b16mm",
            True,
            (2178, 2190),
            (613, 614),
        ),
    ],
)
def test_general_aarch64_features_have_pinned_compiler_examples(
    macro: str,
    key: str,
    token: str,
    architecture_min: str,
    march: str,
    mcpu: str,
    default_enabled: bool,
    acle_lines: tuple[int, int],
    llvm_lines: tuple[int, int],
) -> None:
    (mapping,) = mappings_for_macro(macro)

    assert mapping.key == key
    assert mapping.extension_names == (token,)
    sources = {source.repository: source for source in mapping.sources}
    assert set(sources) == {
        "ARM-software/acle",
        "llvm/llvm-project",
        "gcc.gnu.org/onlinedocs",
    }
    assert (sources["ARM-software/acle"].start_line, sources["ARM-software/acle"].end_line) == acle_lines
    assert (
        sources["llvm/llvm-project"].start_line,
        sources["llvm/llvm-project"].end_line,
    ) == llvm_lines

    (requirement,) = compilation_requirements_for(macro, target="aarch64")
    assert requirement.architecture_min == architecture_min
    assert requirement.extensions == (token,)
    assert {
        (example.compiler, example.flags, example.default_enabled)
        for example in requirement.compiler_flags
    } == {
        ("Clang", (march,), default_enabled),
        ("Clang", (mcpu,), None),
        ("GCC", (march,), default_enabled),
        ("GCC", (mcpu,), None),
    }
    assert compilation_requirements_for(macro, target="aarch32") == ()


def test_compound_and_streaming_tokens_preserve_exact_dependencies() -> None:
    expected = {
        "__ARM_FEATURE_SVE2_BITPERM": ("sve2",),
        "__ARM_FEATURE_SSVE_BITPERM": ("sme2p1",),
        "__ARM_FEATURE_SVE_AES2": ("sve_pmull128",),
        "__ARM_FEATURE_SSVE_AES": ("sme2p1",),
        "__ARM_FEATURE_FP8": ("fpmr", "faminmax", "lut", "bf16"),
        "__ARM_FEATURE_FP8FMA": ("fp8",),
        "__ARM_FEATURE_SSVE_FP8FMA": ("sme2", "fp8"),
        "__ARM_FEATURE_SVE_BFSCALE": ("sve_b16b16",),
        "__ARM_FEATURE_SSVE_FEXPA": ("sme2p1",),
        "__ARM_FEATURE_SME_F16F16": ("sme2",),
        "__ARM_FEATURE_SVE_F16F32MM": ("sve2p1",),
    }

    for macro, dependencies in expected.items():
        (mapping,) = mappings_for_macro(macro)
        assert mapping.implies == dependencies

    (bitperm,) = compilation_requirements_for(
        "__ARM_FEATURE_SVE2_BITPERM", target="aarch64"
    )
    assert {example.flags for example in bitperm.compiler_flags} == {
        ("-march=armv9-a+sve2-bitperm",),
        ("-mcpu=generic+sve2-bitperm",),
    }
    assert all("sve2-bitperm" in example.flags[0] for example in bitperm.compiler_flags)


def test_partial_mappings_explain_gcc_16_2_gaps_without_aliasing() -> None:
    partial_macros = {
        "__ARM_FEATURE_SSVE_BITPERM",
        "__ARM_FEATURE_SVE_AES2",
        "__ARM_FEATURE_SSVE_AES",
        "__ARM_FEATURE_SSVE_FEXPA",
        "__ARM_FEATURE_SVE_F16F32MM",
    }

    for macro in partial_macros:
        (mapping,) = mappings_for_macro(macro)
        assert mapping.status is ResolutionStatus.PARTIAL
        assert any("GCC 16.2 does not document" in note for note in mapping.notes)
        (requirement,) = compilation_requirements_for(macro, target="aarch64")
        assert {example.compiler for example in requirement.compiler_flags} == {"Clang"}
        assert requirement.unresolved_reason is None
        assert requirement.provenance.rule is not None
        assert "Clang-only examples" in requirement.provenance.rule
        assert "validate" not in requirement.provenance.rule

    (aes2,) = mappings_for_macro("__ARM_FEATURE_SVE_AES2")
    assert any("distinct ssve-aes" in note for note in aes2.notes)
    assert any("either FEAT_SVE2p1 or FEAT_SSVE_AES" in note for note in aes2.notes)

    (ssve_aes,) = mappings_for_macro("__ARM_FEATURE_SSVE_AES")
    assert "sve2_aes" not in ssve_aes.implies
    assert any(
        "distinct from __ARM_FEATURE_SVE2_AES" in note for note in ssve_aes.notes
    )

    (f16f32mm,) = mappings_for_macro("__ARM_FEATURE_SVE_F16F32MM")
    assert any("distinct +f16f32mm" in note for note in f16f32mm.notes)


def test_bfscale_complete_example_uses_sve2_b16b16_alternative() -> None:
    (requirement,) = compilation_requirements_for(
        "__ARM_FEATURE_SVE_BFSCALE", target="aarch64"
    )

    assert requirement.architecture_min == "Armv9.2-A"
    march_examples = [
        example
        for example in requirement.compiler_flags
        if example.base_march is not None
    ]
    assert {example.base_march for example in march_examples} == {"armv9.2-a"}
    assert all(
        "+sve2+sve-b16b16+sve-bfscale" in example.flags[0] for example in march_examples
    )


def test_fp8_examples_keep_unspellable_fpmr_as_an_isa_requirement() -> None:
    for macro in (
        "__ARM_FEATURE_FP8",
        "__ARM_FEATURE_FP8FMA",
        "__ARM_FEATURE_SSVE_FP8FMA",
    ):
        (mapping,) = mappings_for_macro(macro)
        assert any("FEAT_FPMR" in note for note in mapping.notes)
        assert any("no +fpmr modifier" in note for note in mapping.notes)
        (requirement,) = compilation_requirements_for(macro, target="aarch64")
        assert all(
            "+fpmr" not in example.flags[0] for example in requirement.compiler_flags
        )
        assert all(
            "+faminmax" in example.flags[0] and "+lut" in example.flags[0]
            for example in requirement.compiler_flags
        )


@pytest.mark.parametrize(
    ("macro", "architecture_min", "modifier", "status"),
    (
        ("__ARM_FEATURE_QRDMX", "Armv8-A", "+rdma", ResolutionStatus.RESOLVED),
        (
            "__ARM_FEATURE_COMPLEX",
            "Armv8.2-A",
            "+fcma",
            ResolutionStatus.RESOLVED,
        ),
        (
            "__ARM_FEATURE_F16F32DOT",
            "Armv9.4-A",
            "+f16f32dot",
            ResolutionStatus.RESOLVED,
        ),
        (
            "__ARM_FEATURE_F16F32MM",
            "Armv9.4-A",
            "+f16f32mm",
            ResolutionStatus.RESOLVED,
        ),
        (
            "__ARM_FEATURE_F16MM",
            "Armv9.6-A",
            "+f16mm",
            ResolutionStatus.RESOLVED,
        ),
        (
            "__ARM_FEATURE_F8F16MM",
            "Armv9.2-A",
            "+f8f16mm",
            ResolutionStatus.PARTIAL,
        ),
        (
            "__ARM_FEATURE_F8F32MM",
            "Armv9.2-A",
            "+f8f32mm",
            ResolutionStatus.PARTIAL,
        ),
    ),
)
def test_late_neon_feature_mappings_keep_exact_modifiers(
    macro: str,
    architecture_min: str,
    modifier: str,
    status: ResolutionStatus,
) -> None:
    (mapping,) = mappings_for_macro(macro)
    (requirement,) = compilation_requirements_for(macro, target="aarch64")

    assert mapping.status is status
    assert requirement.architecture_min == architecture_min
    assert requirement.compiler_flags
    assert all(
        modifier in flag
        for example in requirement.compiler_flags
        for flag in example.flags
    )


def test_frint_preserves_compiler_specific_march_examples() -> None:
    (mapping,) = mappings_for_macro("__ARM_FEATURE_FRINT")
    (requirement,) = compilation_requirements_for(
        "__ARM_FEATURE_FRINT", target="aarch64"
    )

    assert mapping.architecture_features == ("FEAT_FRINTTS",)
    assert requirement.architecture_min == "Armv8.4-A"
    assert {
        (example.compiler, example.flags) for example in requirement.compiler_flags
    } == {
        ("Clang", ("-march=armv8.5-a+simd",)),
        ("GCC", ("-march=armv8.4-a+simd+frintts",)),
    }
    assert all(
        not any(flag.startswith("-mcpu=") for flag in example.flags)
        for example in requirement.compiler_flags
    )


def test_simd32_keeps_aarch32_profile_specific_architectures() -> None:
    requirements = compilation_requirements_for(
        "__ARM_FEATURE_SIMD32", target="aarch32"
    )

    assert {item.architecture_min for item in requirements} == {
        "Armv6",
        "Armv7E-M",
    }
    assert {item.profiles for item in requirements} == {("A", "R"), ("M",)}
    assert all(item.execution_states for item in requirements)
    assert all(item.compiler_flags for item in requirements)
    assert compilation_requirements_for("__ARM_FEATURE_SIMD32", target="aarch64") == ()


def test_lut_is_optional_at_its_minimum_architecture() -> None:
    (requirement,) = compilation_requirements_for("__ARM_FEATURE_LUT", target="aarch64")

    assert requirement.architecture_min == "Armv9.2-A"
    march_examples = [
        example for example in requirement.compiler_flags if example.base_march
    ]
    assert {example.base_march for example in march_examples} == {"armv9.2-a"}
    assert all(example.default_enabled is False for example in march_examples)
