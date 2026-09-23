import pytest

from arm_acle_docset.model import AvailabilityExpr
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


@pytest.mark.parametrize(
    (
        "macro",
        "key",
        "feature",
        "alias",
        "implies",
        "registry_page",
        "acle_lines",
        "llvm_lines",
    ),
    (
        (
            "__ARM_FEATURE_SVE_B16B16",
            "sve_b16b16",
            "FEAT_SVE_B16B16",
            "sve-b16b16",
            (),
            137,
            (2141, 2160),
            (440, 441),
        ),
        (
            "__ARM_FEATURE_SME_B16B16",
            "sme_b16b16",
            "FEAT_SME_B16B16",
            "sme-b16b16",
            ("sme2", "sve_b16b16"),
            135,
            (2161, 2163),
            (443, 445),
        ),
    ),
)
def test_b16b16_mappings_have_exact_aliases_and_primary_sources(
    macro: str,
    key: str,
    feature: str,
    alias: str,
    implies: tuple[str, ...],
    registry_page: int,
    acle_lines: tuple[int, int],
    llvm_lines: tuple[int, int],
) -> None:
    mappings = mappings_for_macro(macro)

    assert tuple(mapping.key for mapping in mappings) == (key,)
    mapping = mappings[0]
    assert mapping.status is ResolutionStatus.RESOLVED
    assert mapping.acle_macros == (macro,)
    assert mapping.gate_for(macro).expression == AvailabilityExpr.defined(macro)
    assert mapping.architecture_features == (feature,)
    assert mapping.extension_names == (alias,)
    assert mapping.implies == implies

    sources = {source.repository: source for source in mapping.sources}
    acle = sources["ARM-software/acle"]
    assert (acle.commit, acle.path) == (ACLE_REVISION, "main/acle.md")
    assert (acle.start_line, acle.end_line) == acle_lines
    assert acle.license_id == ACLE_MARKDOWN_LICENSE
    assert acle.url and acle.url.endswith(
        "#non-widening-brain-16-bit-floating-point-support"
    )

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
        f"{ARM_FEATURE_REGISTRY_TITLE}#page={registry_page}",
    )
    assert registry.license_id == ARM_FEATURE_REGISTRY_LICENSE
    assert registry.url == f"{ARM_FEATURE_REGISTRY_URL}#page={registry_page}"

    gcc = sources["gcc.gnu.org/onlinedocs"]
    assert gcc.commit == GCC_MANUAL_VERSION
    assert gcc.path == "gcc/AArch64-Options.html"
    assert gcc.license_id == "GFDL-1.3-invariants-or-later"
    assert gcc.url == (
        f"https://gcc.gnu.org/onlinedocs/gcc-{GCC_MANUAL_VERSION}/"
        "gcc/AArch64-Options.html"
    )


def test_sve_b16b16_has_complete_sve2_and_sme2_alternatives() -> None:
    requirements = compilation_requirements_for(
        "__ARM_FEATURE_SVE_B16B16", target="aarch64"
    )

    assert {requirement.architecture_min for requirement in requirements} == {
        "Armv9.2-A"
    }
    assert all(
        requirement.extensions == ("sve-b16b16",)
        and requirement.feature_macros == ("__ARM_FEATURE_SVE_B16B16",)
        and requirement.availability
        == AvailabilityExpr.defined("__ARM_FEATURE_SVE_B16B16")
        for requirement in requirements
    )

    actual = {
        (
            example.compiler,
            example.version,
            example.base_march,
            example.flags,
        )
        for requirement in requirements
        for example in requirement.compiler_flags
    }
    expected: set[tuple[str, str, str | None, tuple[str, ...]]] = set()
    for compiler, version in (("Clang", "22.1.1"), ("GCC", GCC_MANUAL_VERSION)):
        for dependency in ("sve2", "sme2"):
            expected.add(
                (
                    compiler,
                    version,
                    "armv9.2-a",
                    (f"-march=armv9.2-a+{dependency}+sve-b16b16",),
                )
            )
            expected.add(
                (
                    compiler,
                    version,
                    None,
                    (f"-mcpu=generic+{dependency}+sve-b16b16",),
                )
            )
    assert actual == expected
    assert all(
        any(
            source.repository == "Arm documentation"
            for source in requirement.provenance.sources
        )
        for requirement in requirements
    )
    assert all(
        example.flags
        not in {
            ("-march=armv9.2-a+sve-b16b16",),
            ("-mcpu=generic+sve-b16b16",),
        }
        for requirement in requirements
        for example in requirement.compiler_flags
    )


def test_sme_b16b16_uses_the_source_defined_complete_alias() -> None:
    (requirement,) = compilation_requirements_for(
        "__ARM_FEATURE_SME_B16B16", target="aarch64"
    )

    assert requirement.architecture_min == "Armv9.2-A"
    assert requirement.extensions == ("sme-b16b16",)
    assert requirement.feature_macros == ("__ARM_FEATURE_SME_B16B16",)
    assert requirement.availability == AvailabilityExpr.defined(
        "__ARM_FEATURE_SME_B16B16"
    )
    assert {
        (example.compiler, example.version, example.base_march, example.flags)
        for example in requirement.compiler_flags
    } == {
        (
            "Clang",
            "22.1.1",
            "armv9.2-a",
            ("-march=armv9.2-a+sme2+sve-b16b16+sme-b16b16",),
        ),
        (
            "Clang",
            "22.1.1",
            None,
            ("-mcpu=generic+sme2+sve-b16b16+sme-b16b16",),
        ),
        (
            "GCC",
            GCC_MANUAL_VERSION,
            "armv9.2-a",
            ("-march=armv9.2-a+sme2+sve-b16b16+sme-b16b16",),
        ),
        (
            "GCC",
            GCC_MANUAL_VERSION,
            None,
            ("-mcpu=generic+sme2+sve-b16b16+sme-b16b16",),
        ),
    }
    assert any(
        source.repository == "Arm documentation"
        for source in requirement.provenance.sources
    )


def test_b16b16_compiler_examples_cite_the_matching_compiler_source() -> None:
    requirements = (
        *compilation_requirements_for("__ARM_FEATURE_SVE_B16B16", target="aarch64"),
        *compilation_requirements_for("__ARM_FEATURE_SME_B16B16", target="aarch64"),
    )

    for requirement in requirements:
        for example in requirement.compiler_flags:
            repositories = {source.repository for source in example.provenance.sources}
            if example.compiler == "Clang":
                assert repositories == {"llvm/llvm-project"}
            else:
                assert example.compiler == "GCC"
                assert repositories == {"gcc.gnu.org/onlinedocs"}
