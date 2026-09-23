from __future__ import annotations

from pathlib import Path

import pytest

from arm_acle_docset.model import Alias, Catalog, ConcreteCallable, NameRole, Signature
from arm_acle_docset.sources.gcc_validation import (
    GCC_VALIDATION_SAMPLES,
    GCCValidationError,
    GCCValidationSample,
    required_gcc_source_paths,
    validate_catalog_against_gcc,
)
from arm_acle_docset.sources.manifest import GCC_COMMIT, SOURCE_ARTIFACTS, SourceKind


FIXTURES = Path(__file__).parent / "fixtures" / "gcc"


def _callable(
    family: str,
    name: str,
    *,
    families: tuple[str, ...] = (),
    name_role: NameRole = NameRole.TYPED,
    aliases: tuple[Alias, ...] = (),
) -> ConcreteCallable:
    return ConcreteCallable(
        family=family,
        families=families,
        name=name,
        name_role=name_role,
        signature=Signature(return_type="void"),
        aliases=aliases,
    )


def _fixture_sources() -> dict[str, Path]:
    by_family = {
        "neon": FIXTURES / "neon.c",
        "mve": FIXTURES / "mve.c",
        "sve": FIXTURES / "sve.c",
        "sme": FIXTURES / "sme.c",
    }
    return {
        path: by_family[
            next(
                sample.family
                for sample in GCC_VALIDATION_SAMPLES
                if sample.source_path == path
            )
        ]
        for path in required_gcc_source_paths()
    }


def _complete_catalog() -> Catalog:
    return Catalog(
        version="fixture",
        source_commit="fixture",
        callables=(
            _callable("neon", "vaddh_f16"),
            _callable(
                "mve",
                "__arm_vaddq_s32",
                name_role=NameRole.PREFIXED,
                aliases=(
                    Alias("vaddq_s32", NameRole.UNPREFIXED),
                    Alias("vaddq", NameRole.OVERLOADED),
                ),
            ),
            _callable(
                "sve",
                "svadd_s32_m",
                aliases=(Alias("svadd_m", NameRole.OVERLOADED),),
            ),
            _callable(
                "sve",
                "svadd_n_s32_m",
                aliases=(Alias("svadd_m", NameRole.OVERLOADED),),
            ),
            _callable(
                "sme",
                "svmopa_za32_s8_m",
                aliases=(Alias("svmopa_za32_m", NameRole.OVERLOADED),),
            ),
            _callable(
                "sme",
                "svmopa_za32_f32_m",
                aliases=(Alias("svmopa_za32_m", NameRole.OVERLOADED),),
            ),
        ),
    )


def test_manifest_pins_four_transient_gcc_validation_sources() -> None:
    artifacts = tuple(
        artifact
        for artifact in SOURCE_ARTIFACTS
        if artifact.kind is SourceKind.VALIDATION
    )

    assert GCC_COMMIT == "fcfb06e236d4d1689a6caf8e5409b078262af481"
    assert len(artifacts) == 4
    assert {
        member.local_path for artifact in artifacts for member in artifact.members
    } == set(required_gcc_source_paths())
    assert all(artifact.revision == GCC_COMMIT for artifact in artifacts)
    assert all(not artifact.optional for artifact in artifacts)
    assert all(
        artifact.url.startswith(
            f"https://raw.githubusercontent.com/gcc-mirror/gcc/{GCC_COMMIT}/"
        )
        for artifact in artifacts
    )


def test_validation_resolves_explicit_and_overloaded_names_on_one_callable() -> None:
    report = validate_catalog_against_gcc(_complete_catalog(), _fixture_sources())

    assert report.commit == GCC_COMMIT
    assert report.validated_count == 6
    assert all(result.callable_ids for result in report.results)
    assert all(result.source_lines for result in report.results)


def test_validation_matches_a_secondary_callable_family() -> None:
    sample = GCCValidationSample(
        sample_id="dual-family-probe",
        family="sve",
        source_path=GCC_VALIDATION_SAMPLES[2].source_path,
        explicit_name="svadd_s32_m",
        overloaded_name="svadd_m",
    )
    catalog = Catalog(
        version="fixture",
        source_commit="fixture",
        callables=(
            _callable(
                "sme",
                "svadd_s32_m",
                families=("sme", "sve"),
                aliases=(Alias("svadd_m", NameRole.OVERLOADED),),
            ),
        ),
    )

    report = validate_catalog_against_gcc(
        catalog,
        _fixture_sources(),
        samples=(sample,),
    )

    assert report.validated_count == 1
    assert report.results[0].callable_ids == (catalog.callables[0].id,)


def test_validation_requires_overloaded_role_not_only_name_presence() -> None:
    sample = GCCValidationSample(
        sample_id="role-probe",
        family="sve",
        source_path=GCC_VALIDATION_SAMPLES[2].source_path,
        explicit_name="svadd_s32_m",
        overloaded_name="svadd_m",
    )
    catalog = Catalog(
        version="fixture",
        source_commit="fixture",
        callables=(
            _callable(
                "sve",
                "svadd_s32_m",
                aliases=(Alias("svadd_m", NameRole.ALTERNATE),),
            ),
        ),
    )

    with pytest.raises(GCCValidationError, match="overloaded matches=0") as error:
        validate_catalog_against_gcc(
            catalog,
            _fixture_sources(),
            samples=(sample,),
        )

    assert error.value.issues[0].code == "gcc.catalog_relation_missing"
    assert "canonical alias merge" in str(error.value)


def test_validation_reports_missing_source_with_fetch_guidance() -> None:
    sample = GCC_VALIDATION_SAMPLES[0]

    with pytest.raises(
        GCCValidationError, match="complete pinned source manifest"
    ) as error:
        validate_catalog_against_gcc(_complete_catalog(), {}, samples=(sample,))

    assert error.value.issues[0].code == "gcc.source_missing"
    assert sample.source_path in str(error.value)


def test_validation_rejects_a_rule_that_drifted_from_the_pinned_sample() -> None:
    sample = GCCValidationSample(
        sample_id="drift-probe",
        family="sve",
        source_path=GCC_VALIDATION_SAMPLES[2].source_path,
        explicit_name="svname_that_is_not_in_the_sample",
    )

    with pytest.raises(GCCValidationError, match="source pin and rule") as error:
        validate_catalog_against_gcc(
            _complete_catalog(),
            _fixture_sources(),
            samples=(sample,),
        )

    assert error.value.issues[0].code == "gcc.sample_identifier_missing"


def test_static_cross_check_ignores_comments_if_zero_and_unrelated_cases(
    tmp_path: Path,
) -> None:
    sample = GCCValidationSample(
        sample_id="source-scope-probe",
        family="sve",
        source_path="gcc/testsuite/synthetic.c",
        explicit_name="svadd_s32_m",
        overloaded_name="svadd_m",
    )
    source = tmp_path / "synthetic.c"
    source.write_text(
        """
/* CHECK_PAIR(svadd_s32_m(pg, z0, z1), svadd_m(pg, z0, z1)); */
#if 0
CHECK_PAIR(svadd_s32_m(pg, z0, z1), svadd_m(pg, z0, z1));
#endif
CHECK_EXPLICIT(svadd_s32_m(pg, z0, z1));
CHECK_OVERLOADED(svadd_m(pg, z0, z1));
""",
        encoding="utf-8",
    )

    with pytest.raises(
        GCCValidationError, match="not in one related active TEST construct"
    ) as error:
        validate_catalog_against_gcc(
            _complete_catalog(),
            {sample.source_path: source},
            samples=(sample,),
        )

    assert error.value.issues[0].code == "gcc.sample_relation_missing"
    assert str(error.value).startswith("GCC static sample cross-check failed:")


def test_static_cross_check_accepts_pair_in_one_active_test_construct(
    tmp_path: Path,
) -> None:
    sample = GCCValidationSample(
        sample_id="source-scope-probe",
        family="sve",
        source_path="gcc/testsuite/synthetic.c",
        explicit_name="svadd_s32_m",
        overloaded_name="svadd_m",
    )
    source = tmp_path / "synthetic.c"
    source.write_text(
        "CHECK_PAIR(svadd_s32_m(pg, z0, z1), svadd_m(pg, z0, z1));\n",
        encoding="utf-8",
    )

    report = validate_catalog_against_gcc(
        _complete_catalog(),
        {sample.source_path: source},
        samples=(sample,),
    )

    assert report.validated_count == 1
    assert report.results[0].source_lines == (1, 1)
    assert len(report.results[0].callable_ids) == 1


def test_catalog_match_rejects_duplicate_canonical_signature_stably() -> None:
    sample = GCCValidationSample(
        sample_id="duplicate-probe",
        family="sve",
        source_path=GCC_VALIDATION_SAMPLES[2].source_path,
        explicit_name="svadd_s32_m",
        overloaded_name="svadd_m",
    )
    duplicate = _callable(
        "sve",
        "svadd_s32_m",
        aliases=(Alias("svadd_m", NameRole.OVERLOADED),),
    )
    catalog = Catalog(
        version="fixture",
        source_commit="fixture",
        callables=(duplicate, duplicate),
    )

    with pytest.raises(GCCValidationError, match="expected exactly one") as error:
        validate_catalog_against_gcc(
            catalog,
            _fixture_sources(),
            samples=(sample,),
        )

    assert error.value.issues[0].code == "gcc.catalog_relation_ambiguous"
    assert "2 canonical callables" in str(error.value)


def test_ambiguity_diagnostic_is_stable_across_catalog_order() -> None:
    sample = GCCValidationSample(
        sample_id="stable-ambiguity-probe",
        family="sve",
        source_path=GCC_VALIDATION_SAMPLES[2].source_path,
        explicit_name="svadd_s32_m",
        overloaded_name="svadd_m",
    )
    first = _callable(
        "sve",
        "svadd_s32_m",
        aliases=(Alias("svadd_m", NameRole.OVERLOADED),),
    )
    second = ConcreteCallable(
        family="sve",
        name="svadd_s32_m",
        signature=Signature(return_type="int"),
        aliases=(Alias("svadd_m", NameRole.OVERLOADED),),
    )
    diagnostics: list[str] = []
    for callables in ((first, second), (second, first)):
        catalog = Catalog(
            version="fixture",
            source_commit="fixture",
            callables=callables,
        )
        with pytest.raises(GCCValidationError) as error:
            validate_catalog_against_gcc(
                catalog,
                _fixture_sources(),
                samples=(sample,),
            )
        diagnostics.append(str(error.value))

    assert diagnostics[0] == diagnostics[1]


def test_catalog_match_rejects_partial_alias_split_across_callables() -> None:
    sample = GCCValidationSample(
        sample_id="partial-alias-probe",
        family="sve",
        source_path=GCC_VALIDATION_SAMPLES[2].source_path,
        explicit_name="svadd_s32_m",
        overloaded_name="svadd_m",
    )
    catalog = Catalog(
        version="fixture",
        source_commit="fixture",
        callables=(
            _callable("sve", "svadd_s32_m"),
            _callable("sve", "svadd_m", name_role=NameRole.OVERLOADED),
        ),
    )

    with pytest.raises(GCCValidationError, match="on one callable") as error:
        validate_catalog_against_gcc(
            catalog,
            _fixture_sources(),
            samples=(sample,),
        )

    assert error.value.issues[0].code == "gcc.catalog_relation_missing"
    assert "explicit matches=1, overloaded matches=1" in str(error.value)
