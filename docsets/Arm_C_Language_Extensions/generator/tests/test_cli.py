import json
import subprocess
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest

from arm_acle_docset import cli
from arm_acle_docset.cli import DEFAULT_CACHE_DIRECTORY, build_parser
from arm_acle_docset.package import pinned_build_runtime_identity


def test_build_parser_selects_a_repeatable_performance_profile_subset() -> None:
    arguments = build_parser().parse_args(
        [
            "build",
            "--llvm-mca",
            "/toolchain/llvm-mca",
            "--llvm-mc",
            "/toolchain/llvm-mc",
            "--performance-profile",
            "neoverse-n2",
            "--performance-profile",
            "cortex-m85",
        ]
    )

    assert arguments.llvm_mca == Path("/toolchain/llvm-mca")
    assert arguments.llvm_mc == Path("/toolchain/llvm-mc")
    assert arguments.performance_profile == ["neoverse-n2", "cortex-m85"]


def test_build_parser_defaults_to_all_performance_profiles() -> None:
    arguments = build_parser().parse_args(["build"])

    assert arguments.performance_profile is None


def test_default_cache_is_private_to_the_current_user() -> None:
    assert DEFAULT_CACHE_DIRECTORY.is_relative_to(Path.home())
    assert DEFAULT_CACHE_DIRECTORY == Path.home() / ".arm-acle-docset-cache"


def test_requested_profiles_are_canonicalized_independently_of_flag_order() -> None:
    assert cli._canonical_requested_profiles(["cortex-m85", "neoverse-n2"]) == (
        "neoverse-n2",
        "cortex-m85",
    )


@pytest.mark.parametrize(
    "profiles",
    [
        [],
        ["neoverse-n2", "neoverse-n2"],
        ["unknown-cpu"],
        [
            "cortex-a55",
            "neoverse-n1",
            "neoverse-v1",
            "neoverse-n2",
            "cortex-m55",
            "cortex-m85",
        ],
    ],
)
def test_requested_profiles_reject_duplicates_unknowns_and_explicit_full_set(
    profiles: list[str],
) -> None:
    with pytest.raises(ValueError):
        cli._canonical_requested_profiles(profiles)


def test_development_subset_fails_before_resolving_tools_without_no_archive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    arguments = build_parser().parse_args(
        ["build", "--performance-profile", "neoverse-n2"]
    )

    def unexpected_tool_lookup(*_args: object, **_kwargs: object) -> Path:
        raise AssertionError("tool lookup must not run")

    monkeypatch.setattr(cli, "_resolve_clang_tblgen", unexpected_tool_lookup)
    with pytest.raises(ValueError, match="also pass --no-archive"):
        cli._build_command(arguments)


def test_full_release_fails_before_preflight_with_no_archive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    arguments = build_parser().parse_args(["build", "--no-archive"])

    def unexpected_runtime_preflight() -> object:
        raise AssertionError("runtime preflight must not run")

    monkeypatch.setattr(
        cli, "require_pinned_build_runtime", unexpected_runtime_preflight
    )

    with pytest.raises(
        ValueError,
        match="--no-archive requires a development --performance-profile subset",
    ):
        cli._build_command(arguments)


def test_build_consumes_sources_only_inside_verified_snapshot(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    arguments = build_parser().parse_args(
        ["build", "--cache-dir", str(tmp_path / "cache")]
    )
    active = False

    @contextmanager
    def snapshot(*_args: object, **_kwargs: object):
        nonlocal active
        active = True
        try:
            yield {"llvm/td/arm_neon.td": tmp_path / "snapshot/llvm/td/arm_neon.td"}
        finally:
            active = False

    def build_from_snapshot(*_args: object, **_kwargs: object) -> dict[str, object]:
        assert active
        return {"status": "ok"}

    monkeypatch.setattr(cli, "resolved_source_snapshot", snapshot)
    monkeypatch.setattr(
        cli, "_resolve_clang_tblgen", lambda _value: tmp_path / "tblgen"
    )
    monkeypatch.setattr(cli, "_resolve_llvm_tool", lambda _value, name: tmp_path / name)
    monkeypatch.setattr(cli, "_collect_llvm_tool_identities", lambda *_args: ())
    monkeypatch.setattr(cli, "_build_from_source_snapshot", build_from_snapshot)

    assert cli._build_command(arguments) == 0
    assert not active
    assert json.loads(capsys.readouterr().out) == {"status": "ok"}


def test_build_runtime_preflight_happens_before_tools_cache_or_output(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    output = tmp_path / "output"
    arguments = build_parser().parse_args(["build", "--output-dir", str(output)])

    def reject_runtime() -> object:
        raise RuntimeError("unpinned build runtime")

    def unexpected(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("build continued after runtime preflight failure")

    monkeypatch.setattr(cli, "require_pinned_build_runtime", reject_runtime)
    monkeypatch.setattr(cli, "build_inputs_sha256", unexpected)
    monkeypatch.setattr(cli, "_resolve_clang_tblgen", unexpected)
    monkeypatch.setattr(cli, "resolved_source_snapshot", unexpected)

    with pytest.raises(RuntimeError, match="unpinned build runtime"):
        cli._build_command(arguments)
    assert not output.exists()


def test_release_blockers_fail_before_packaging(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from arm_acle_docset import pipeline
    from arm_acle_docset.sources import gcc_validation, performance

    catalog = SimpleNamespace(callables=(object(),), diagnostics=())
    monkeypatch.setattr(pipeline, "build_catalog", lambda *_args, **_kwargs: catalog)
    monkeypatch.setattr(
        pipeline,
        "completeness_report",
        lambda _catalog: SimpleNamespace(release_blockers=2),
    )
    monkeypatch.setattr(
        gcc_validation,
        "validate_catalog_against_gcc",
        lambda *_args, **_kwargs: SimpleNamespace(commit="fixture", validated_count=1),
    )
    monkeypatch.setattr(
        performance,
        "build_default_performance_datasets",
        lambda **_kwargs: (),
    )

    def unexpected_package(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("packaging must not run with release blockers")

    monkeypatch.setattr(cli, "package_docset", unexpected_package)
    arguments = build_parser().parse_args(
        ["build", "--output-dir", str(tmp_path / "output")]
    )

    with pytest.raises(
        ValueError,
        match="release build has 2 release blockers; refusing to package",
    ):
        cli._build_from_generated_headers(
            arguments,
            {},
            llvm_include_dir=tmp_path / "include",
            clang_tblgen=tmp_path / "clang-tblgen",
            llvm_mca=tmp_path / "llvm-mca",
            llvm_mc=tmp_path / "llvm-mc",
            requested_profiles=None,
            build_runtime=pinned_build_runtime_identity(),
            build_inputs_digest="a" * 64,
            llvm_tools=(),
        )


@pytest.mark.parametrize(
    ("requested", "actual"),
    [
        (("neoverse-n2",), ()),
        (("neoverse-n2",), ("neoverse-n1",)),
        (("neoverse-n2",), ("neoverse-n2", "cortex-m85")),
        (("neoverse-n2", "cortex-m85"), ("cortex-m85", "neoverse-n2")),
    ],
)
def test_performance_scope_rejects_any_nonexact_subset(
    requested: tuple[str, ...], actual: tuple[str, ...]
) -> None:
    with pytest.raises(ValueError, match="exactly match"):
        cli._validated_performance_profile_scope(requested, actual)


def test_performance_scope_accepts_only_exact_subset_and_canonical_release() -> None:
    assert (
        cli._validated_performance_profile_scope(
            ("neoverse-n2", "cortex-m85"),
            ("neoverse-n2", "cortex-m85"),
        )
        == "development_subset"
    )
    assert (
        cli._validated_performance_profile_scope(
            None,
            cli.RELEASE_PERFORMANCE_PROFILES,
        )
        == "full_release"
    )


def test_llvm_identity_binds_executable_bytes_and_complete_version_output(
    tmp_path: Path,
) -> None:
    first = tmp_path / "llvm-mc-a"
    second = tmp_path / "llvm-mc-b"
    first.write_text(
        "#!/bin/sh\nprintf 'Homebrew LLVM version 22.1.1\\nTarget: fixture\\n'\n",
        encoding="utf-8",
    )
    second.write_text(
        "#!/bin/sh\n# different executable bytes\n"
        "printf 'Homebrew LLVM version 22.1.1\\nTarget: fixture\\n'\n",
        encoding="utf-8",
    )
    first.chmod(0o755)
    second.chmod(0o755)

    first_identity = cli._llvm_tool_identity(first, "llvm-mc")
    second_identity = cli._llvm_tool_identity(second, "llvm-mc")

    assert first_identity.version == second_identity.version == "22.1.1"
    assert (
        first_identity.normalized_version_output_sha256
        == second_identity.normalized_version_output_sha256
    )
    assert first_identity.executable_sha256 != second_identity.executable_sha256
    assert first_identity != second_identity


def test_llvm_identity_ignores_metadata_but_rejects_content_replacement(
    tmp_path: Path,
) -> None:
    tool = tmp_path / "llvm-mca"
    tool.write_text(
        "#!/bin/sh\nprintf 'LLVM version 22.1.1\\nTarget: fixture\\n'\n",
        encoding="utf-8",
    )
    tool.chmod(0o755)
    original = cli._llvm_tool_identity(tool, "llvm-mca")

    tool.touch()
    assert cli._llvm_tool_identity(tool, "llvm-mca") == original

    tool.write_text(
        "#!/bin/sh\n# replaced bytes\n"
        "printf 'LLVM version 22.1.1\\nTarget: fixture\\n'\n",
        encoding="utf-8",
    )
    tool.chmod(0o755)
    assert cli._llvm_tool_identity(tool, "llvm-mca") != original


def test_llvm_identity_rejects_content_change_during_probe(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    tool = tmp_path / "llvm-mc"
    tool.write_bytes(b"fixture")
    digests = iter(("a" * 64, "b" * 64))
    monkeypatch.setattr(cli, "_file_sha256", lambda _path: next(digests))
    monkeypatch.setattr(
        cli,
        "_llvm_version_probe",
        lambda _path, _name: ("22.1.1", "c" * 64),
    )

    with pytest.raises(RuntimeError, match="contents changed during identity probe"):
        cli._llvm_tool_identity(tool, "llvm-mc")


def test_llvm_version_probe_timeout_uses_stable_cli_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    tool = tmp_path / "llvm-mca"
    command = [str(tool), "--version"]

    def timeout(*_args: object, **_kwargs: object) -> object:
        raise subprocess.TimeoutExpired(command, 30)

    def probe(_args: object) -> int:
        cli._llvm_tool_version(tool, "llvm-mca")
        return 0

    monkeypatch.setattr(cli.subprocess, "run", timeout)
    monkeypatch.setattr(cli, "_build_command", probe)

    assert cli.main(["build"]) == 1
    assert capsys.readouterr().err.splitlines() == [
        f"error: cannot execute llvm-mca --version: "
        f"{subprocess.TimeoutExpired(command, 30)}"
    ]


def test_tablegen_timeout_does_not_publish_generated_headers(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    tablegen_directory = tmp_path / "tablegen"
    tablegen_directory.mkdir()
    (tablegen_directory / "arm_neon.td").write_bytes(b"fixture\n")
    tool = tmp_path / "clang-tblgen"
    tool.write_bytes(b"fixture\n")
    output_directory = tmp_path / "generated" / "include"

    monkeypatch.setattr(cli, "_verify_clang_tblgen_version", lambda _tool: None)

    def timeout(command: list[str], **_kwargs: object) -> object:
        raise subprocess.TimeoutExpired(command, 180)

    monkeypatch.setattr(cli.subprocess, "run", timeout)

    with pytest.raises(
        RuntimeError,
        match="cannot generate arm_neon.h with clang-tblgen",
    ) as raised:
        cli.generate_llvm_headers(
            tablegen_directory,
            output_directory,
            clang_tblgen=tool,
        )

    assert isinstance(raised.value.__cause__, subprocess.TimeoutExpired)
    assert not output_directory.exists()


def test_verify_passes_a_broken_archive_symlink_to_package_validation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    archive = tmp_path / cli.ARCHIVE_NAME
    archive.symlink_to(tmp_path / "missing-archive")
    captured: dict[str, object] = {}

    def capture_verify(
        docset_path: Path,
        *,
        archive_path: Path | None,
        require_archive: bool,
        allow_development_subset: bool,
    ) -> None:
        captured.update(
            docset_path=docset_path,
            archive_path=archive_path,
            require_archive=require_archive,
            allow_development_subset=allow_development_subset,
        )

    monkeypatch.setattr(cli, "verify_docset", capture_verify)
    arguments = build_parser().parse_args(
        ["verify", "--output-dir", str(tmp_path), "--allow-development-subset"]
    )

    assert cli._verify_command(arguments) == 0
    assert captured["archive_path"] == archive


def test_cli_flattens_multiline_verification_errors(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    def fail(_args: object) -> int:
        raise ValueError("cannot read docset archive:\ntruncated gzip")

    monkeypatch.setattr(cli, "_verify_command", fail)

    assert cli.main(["verify", "--output-dir", str(tmp_path)]) == 1
    assert capsys.readouterr().err.splitlines() == [
        "error: cannot read docset archive: truncated gzip"
    ]
