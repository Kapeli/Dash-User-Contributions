"""Command-line interface for fetching, building, and verifying the docset."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Protocol, cast

from .package import (
    ARCHIVE_NAME,
    DOCSET_BUNDLE_NAME,
    DOCSET_VERSION,
    RELEASE_PERFORMANCE_PROFILES,
    BuildManifest,
    BuildRuntimeIdentity,
    LLVMToolIdentity,
    build_inputs_sha256,
    package_docset,
    require_pinned_build_runtime,
    source_manifest_sha256,
    verify_docset,
)
from .sources.manifest import (
    ACLE_REVISION,
    LLVM_COMMIT,
    LLVM_GENERATED_HEADERS,
    LLVM_TAG,
    SOURCE_ARTIFACTS,
    ManifestError,
    fetch_sources,
    resolved_source_snapshot,
    select_artifacts,
)

CONTRIBUTION_DIRECTORY = Path(__file__).resolve().parents[3]
DEFAULT_CACHE_DIRECTORY = Path.home() / ".arm-acle-docset-cache"
CLANG_TBLGEN_VERSION = "22.1.1"
GENERATED_HEADER_SHA256: Mapping[str, str] = {
    Path(member.local_path).name: member.sha256 for member in LLVM_GENERATED_HEADERS
}
_TABLEGEN_TARGETS = (
    ("arm_neon.td", "--gen-arm-neon", "arm_neon.h"),
    ("arm_neon.td", "--gen-arm-vector-type", "arm_vector_types.h"),
    ("arm_bf16.td", "--gen-arm-bf16", "arm_bf16.h"),
    ("arm_sve.td", "--gen-arm-sve-header", "arm_sve.h"),
    ("arm_sme.td", "--gen-arm-sme-header", "arm_sme.h"),
    ("arm_mve.td", "--gen-arm-mve-header", "arm_mve.h"),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="generate_docset.py",
        description="Build the Arm C Language Extensions Dash docset.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch_parser = subparsers.add_parser(
        "fetch",
        help="download and verify all selected pinned sources",
    )
    _add_source_arguments(fetch_parser, allow_source_dir=False)
    fetch_parser.add_argument(
        "--include-optional",
        action="store_true",
        help="also fetch every optional manifest source",
    )

    build_parser_ = subparsers.add_parser(
        "build",
        help="generate the docset and deterministic archive",
    )
    _add_source_arguments(build_parser_, allow_source_dir=True)
    build_parser_.add_argument(
        "--output-dir",
        type=Path,
        default=CONTRIBUTION_DIRECTORY,
        help="output directory (default: contribution directory)",
    )
    build_parser_.add_argument(
        "--clang-tblgen",
        type=Path,
        help="path to clang-tblgen 22.1.1 (default: PATH lookup)",
    )
    build_parser_.add_argument(
        "--llvm-mca",
        type=Path,
        help="path to llvm-mca 22.1.1 (default: PATH lookup)",
    )
    build_parser_.add_argument(
        "--llvm-mc",
        type=Path,
        help="path to llvm-mc 22.1.1 (default: sibling of llvm-mca)",
    )
    build_parser_.add_argument(
        "--performance-profile",
        action="append",
        default=None,
        metavar="CPU",
        help=(
            "run only this fixed LLVM CPU profile; repeat for a subset "
            "and also pass --no-archive (default: all six release profiles)"
        ),
    )
    build_parser_.add_argument(
        "--no-archive",
        action="store_true",
        help="build a development subset without writing the .tgz archive",
    )

    verify_parser = subparsers.add_parser(
        "verify",
        help="validate an existing bundle, archive, and optionally source tree",
    )
    verify_parser.add_argument(
        "--output-dir",
        type=Path,
        default=CONTRIBUTION_DIRECTORY,
        help="directory containing the generated artifacts",
    )
    verify_parser.add_argument(
        "--source-dir",
        type=Path,
        help="also verify a complete offline source tree",
    )
    verify_parser.add_argument(
        "--allow-development-subset",
        action="store_true",
        help=(
            "accept an explicitly marked development performance-profile subset "
            "without a release archive"
        ),
    )
    return parser


def _add_source_arguments(
    parser: argparse.ArgumentParser, *, allow_source_dir: bool
) -> None:
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=DEFAULT_CACHE_DIRECTORY,
        help=f"verified source cache (default: {DEFAULT_CACHE_DIRECTORY})",
    )
    if allow_source_dir:
        parser.add_argument(
            "--source-dir",
            type=Path,
            help="pre-populated source tree; all files are SHA-256 verified",
        )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="forbid network access and require all selected sources locally",
    )


def _canonical_requested_profiles(
    profiles: Sequence[str] | None,
) -> tuple[str, ...] | None:
    if profiles is None:
        return None
    if not profiles:
        raise ValueError("--performance-profile requires at least one CPU")
    if len(set(profiles)) != len(profiles):
        raise ValueError("--performance-profile values must be unique")
    unknown = set(profiles) - set(RELEASE_PERFORMANCE_PROFILES)
    if unknown:
        raise ValueError(
            "unsupported --performance-profile value(s): " + ", ".join(sorted(unknown))
        )
    canonical = tuple(
        profile for profile in RELEASE_PERFORMANCE_PROFILES if profile in profiles
    )
    if canonical == RELEASE_PERFORMANCE_PROFILES:
        raise ValueError(
            "omit --performance-profile to select the full release profile set"
        )
    return canonical


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "fetch":
            return _fetch_command(args)
        if args.command == "build":
            return _build_command(args)
        if args.command == "verify":
            return _verify_command(args)
    except (ManifestError, OSError, RuntimeError, ValueError) as error:
        message = " ".join(str(error).splitlines()) or error.__class__.__name__
        print(f"error: {message}", file=sys.stderr)
        return 1
    raise AssertionError(f"unhandled command: {args.command}")


def _fetch_command(args: argparse.Namespace) -> int:
    artifacts = select_artifacts(
        SOURCE_ARTIFACTS,
        include_optional=args.include_optional,
    )
    resolved = fetch_sources(
        args.cache_dir,
        offline=args.offline,
        artifacts=artifacts,
    )
    print(f"Verified {len(resolved)} source files in {Path(args.cache_dir).resolve()}")
    return 0


def _build_command(args: argparse.Namespace) -> int:
    requested_profiles = _canonical_requested_profiles(args.performance_profile)
    if requested_profiles is None and args.no_archive:
        raise ValueError(
            "--no-archive requires a development --performance-profile subset"
        )
    if requested_profiles is not None and not args.no_archive:
        raise ValueError(
            "--performance-profile is a development subset; also pass --no-archive"
        )
    build_runtime = require_pinned_build_runtime()
    build_inputs_digest = build_inputs_sha256()
    clang_tblgen = _resolve_clang_tblgen(args.clang_tblgen)
    llvm_mca = _resolve_llvm_tool(args.llvm_mca, "llvm-mca")
    llvm_mc = _resolve_llvm_tool(
        args.llvm_mc if args.llvm_mc is not None else llvm_mca.with_name("llvm-mc"),
        "llvm-mc",
    )
    llvm_tools = _collect_llvm_tool_identities(clang_tblgen, llvm_mc, llvm_mca)

    with resolved_source_snapshot(
        args.cache_dir,
        source_dir=args.source_dir,
        offline=args.offline,
    ) as source_paths:
        summary = _build_from_source_snapshot(
            args,
            source_paths,
            clang_tblgen=clang_tblgen,
            llvm_mca=llvm_mca,
            llvm_mc=llvm_mc,
            requested_profiles=requested_profiles,
            build_runtime=build_runtime,
            build_inputs_digest=build_inputs_digest,
            llvm_tools=llvm_tools,
        )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _build_from_source_snapshot(
    args: argparse.Namespace,
    source_paths: Mapping[str, Path],
    *,
    clang_tblgen: Path,
    llvm_mca: Path,
    llvm_mc: Path,
    requested_profiles: tuple[str, ...] | None,
    build_runtime: BuildRuntimeIdentity,
    build_inputs_digest: str,
    llvm_tools: tuple[LLVMToolIdentity, ...],
) -> dict[str, object]:
    tablegen_directory = source_paths["llvm/td/arm_neon.td"].parent
    with tempfile.TemporaryDirectory(prefix=".arm-acle-derived-") as derived:
        llvm_include_dir = Path(derived) / LLVM_TAG / "include"
        generate_llvm_headers(
            tablegen_directory,
            llvm_include_dir,
            clang_tblgen=clang_tblgen,
        )
        return _build_from_generated_headers(
            args,
            source_paths,
            llvm_include_dir=llvm_include_dir,
            clang_tblgen=clang_tblgen,
            llvm_mca=llvm_mca,
            llvm_mc=llvm_mc,
            requested_profiles=requested_profiles,
            build_runtime=build_runtime,
            build_inputs_digest=build_inputs_digest,
            llvm_tools=llvm_tools,
        )


def _build_from_generated_headers(
    args: argparse.Namespace,
    source_paths: Mapping[str, Path],
    *,
    llvm_include_dir: Path,
    clang_tblgen: Path,
    llvm_mca: Path,
    llvm_mc: Path,
    requested_profiles: tuple[str, ...] | None,
    build_runtime: BuildRuntimeIdentity,
    build_inputs_digest: str,
    llvm_tools: tuple[LLVMToolIdentity, ...],
) -> dict[str, object]:
    # Imported only for a build so fetch/verify remain usable with no rendering
    # dependencies and while adapters are tested independently.
    from .pipeline import build_catalog, completeness_report
    from .render import DashRenderer
    from .sources.gcc_validation import validate_catalog_against_gcc
    from .sources.performance import build_default_performance_datasets

    performance_datasets = build_default_performance_datasets(
        llvm_mca=llvm_mca,
        llvm_mc=llvm_mc,
        profiles=requested_profiles,
    )

    catalog = build_catalog(
        source_paths,
        llvm_include_dir,
        feature_db=None,
        performance_db=performance_datasets,
    )
    callables = tuple(catalog.callables)
    if not callables:
        raise ValueError("the canonical pipeline produced no callables")
    gcc_validation = validate_catalog_against_gcc(catalog, source_paths)

    report = completeness_report(catalog)
    if requested_profiles is None and report.release_blockers > 0:
        blocker_label = (
            "release blocker" if report.release_blockers == 1 else "release blockers"
        )
        raise ValueError(
            f"release build has {report.release_blockers} {blocker_label}; "
            "refusing to package"
        )
    renderer = DashRenderer()
    pages = [
        renderer.render_index(
            callables,
            version=DOCSET_VERSION,
            source_revision=ACLE_REVISION,
            catalog_diagnostics=catalog.diagnostics,
        )
    ]
    pages.extend(renderer.render_callable(callable_) for callable_ in callables)
    performance_profiles = tuple(
        dataset.manifest.cpu for dataset in performance_datasets
    )
    if not all(isinstance(profile, str) for profile in performance_profiles):
        raise ValueError("performance dataset is missing a CPU profile")
    typed_profiles = tuple(str(profile) for profile in performance_profiles)
    profile_scope = _validated_performance_profile_scope(
        requested_profiles, typed_profiles
    )
    final_llvm_tools = _collect_llvm_tool_identities(clang_tblgen, llvm_mc, llvm_mca)
    if final_llvm_tools != llvm_tools:
        raise RuntimeError("LLVM tool contents or version output changed during build")
    build_manifest = BuildManifest(
        build_inputs_sha256=build_inputs_digest,
        build_runtime=build_runtime,
        performance_profile_scope=profile_scope,
        performance_profiles=typed_profiles,
        source_manifest_sha256=source_manifest_sha256(),
        llvm_tools=llvm_tools,
    )
    result = package_docset(
        pages,
        args.output_dir,
        build_manifest=build_manifest,
        renderer=renderer,
        icon_dir=CONTRIBUTION_DIRECTORY,
        legal_dir=CONTRIBUTION_DIRECTORY,
        archive=not args.no_archive,
    )

    return {
        "archive": str(result.archive_path) if result.archive_path else None,
        "build_manifest": build_manifest.canonical_data(),
        "callables": len(callables),
        "completeness": _json_compatible(report),
        "docset": str(result.docset_path),
        "gcc_validation": {
            "commit": gcc_validation.commit,
            "samples": gcc_validation.validated_count,
        },
        "index_entries": result.index_entry_count,
        "pages": result.page_count,
        "performance_profiles": list(typed_profiles),
    }


def _validated_performance_profile_scope(
    requested_profiles: tuple[str, ...] | None,
    actual_profiles: tuple[str, ...],
) -> str:
    if requested_profiles is None:
        if actual_profiles != RELEASE_PERFORMANCE_PROFILES:
            raise ValueError(
                "release build did not produce the canonical six performance profiles"
            )
        return "full_release"
    if actual_profiles != requested_profiles:
        raise ValueError(
            "performance datasets do not exactly match the requested profiles"
        )
    return "development_subset"


def _verify_command(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir)
    docset = output_dir / DOCSET_BUNDLE_NAME
    archive = output_dir / ARCHIVE_NAME
    verify_docset(
        docset,
        archive_path=archive if archive.exists() or archive.is_symlink() else None,
        require_archive=not args.allow_development_subset,
        allow_development_subset=args.allow_development_subset,
    )
    if args.source_dir is not None:
        with resolved_source_snapshot(
            DEFAULT_CACHE_DIRECTORY,
            source_dir=args.source_dir,
            offline=True,
        ):
            pass
    print(f"Verified {docset}")
    return 0


def generate_llvm_headers(
    tablegen_directory: Path,
    output_directory: Path,
    *,
    clang_tblgen: Path | None = None,
) -> Mapping[str, Path]:
    """Generate and verify the four public Arm headers from pinned TableGen."""

    tablegen_directory = Path(tablegen_directory)
    if not tablegen_directory.is_dir():
        raise RuntimeError(
            f"LLVM TableGen input directory does not exist: {tablegen_directory}"
        )
    tool = _resolve_clang_tblgen(clang_tblgen)
    _verify_clang_tblgen_version(tool)
    output_directory = Path(output_directory)
    output_directory.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix=".llvm-headers-",
        dir=output_directory.parent,
    ) as temporary_directory:
        generated_root = Path(temporary_directory)
        for source_name, backend, output_name in _TABLEGEN_TARGETS:
            source = tablegen_directory / source_name
            if not source.is_file():
                raise RuntimeError(f"missing pinned LLVM TableGen input: {source}")
            output = generated_root / output_name
            command = [
                str(tool),
                backend,
                "-I",
                str(tablegen_directory),
                "-o",
                str(output),
                str(source),
            ]
            try:
                completed = subprocess.run(
                    command,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=180,
                )
            except (OSError, subprocess.TimeoutExpired) as error:
                raise RuntimeError(
                    f"cannot generate {output_name} with clang-tblgen: {error}"
                ) from error
            if completed.returncode != 0:
                details = (completed.stderr or completed.stdout).strip()
                raise RuntimeError(
                    f"clang-tblgen failed for {source_name} ({completed.returncode}): "
                    f"{details[-2000:]}"
                )
            _verify_file_sha256(output, GENERATED_HEADER_SHA256[output_name])

        if output_directory.exists():
            shutil.rmtree(output_directory)
        shutil.move(str(generated_root), output_directory)

    return {name: output_directory / name for name in sorted(GENERATED_HEADER_SHA256)}


def _resolve_clang_tblgen(value: Path | None) -> Path:
    if value is not None:
        tool = Path(value).expanduser().resolve()
        if not tool.is_file():
            raise RuntimeError(f"clang-tblgen does not exist: {tool}")
        return tool
    discovered = shutil.which("clang-tblgen")
    if discovered is None:
        raise RuntimeError(
            "clang-tblgen 22.1.1 was not found; pass --clang-tblgen with an exact tool path"
        )
    return Path(discovered).resolve()


def _resolve_llvm_tool(value: Path | None, name: str) -> Path:
    if value is not None:
        tool = Path(value).expanduser().resolve()
        if not tool.is_file():
            raise RuntimeError(f"{name} does not exist: {tool}")
        return tool
    discovered = shutil.which(name)
    if discovered is None:
        raise RuntimeError(
            f"{name} 22.1.1 was not found; pass --{name} with an exact tool path"
        )
    return Path(discovered).resolve()


def _verify_clang_tblgen_version(tool: Path) -> None:
    _llvm_tool_version(tool, "clang-tblgen")


def _collect_llvm_tool_identities(
    clang_tblgen: Path,
    llvm_mc: Path,
    llvm_mca: Path,
) -> tuple[LLVMToolIdentity, ...]:
    return tuple(
        sorted(
            (
                _llvm_tool_identity(clang_tblgen, "clang-tblgen"),
                _llvm_tool_identity(llvm_mc, "llvm-mc"),
                _llvm_tool_identity(llvm_mca, "llvm-mca"),
            )
        )
    )


def _llvm_tool_identity(tool: Path, name: str) -> LLVMToolIdentity:
    executable_sha256 = _file_sha256(tool)
    version, version_output_sha256 = _llvm_version_probe(tool, name)
    if _file_sha256(tool) != executable_sha256:
        raise RuntimeError(f"{name} executable contents changed during identity probe")
    return LLVMToolIdentity(
        name=name,
        version=version,
        declared_release_tag=LLVM_TAG,
        declared_source_revision=LLVM_COMMIT,
        executable_sha256=executable_sha256,
        normalized_version_output_sha256=version_output_sha256,
    )


def _llvm_tool_version(tool: Path, name: str) -> str:
    version, _output_digest = _llvm_version_probe(tool, name)
    return version


def _llvm_version_probe(tool: Path, name: str) -> tuple[str, str]:
    try:
        completed = subprocess.run(
            [str(tool), "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RuntimeError(f"cannot execute {name} --version: {error}") from error
    normalized_stdout = completed.stdout.replace("\r\n", "\n").replace("\r", "\n")
    normalized_stderr = completed.stderr.replace("\r\n", "\n").replace("\r", "\n")
    normalized_output = (
        b"stdout\x00"
        + normalized_stdout.encode("utf-8")
        + b"\x00stderr\x00"
        + normalized_stderr.encode("utf-8")
    )
    output = f"{normalized_stdout}\n{normalized_stderr}"
    match = re.search(r"(?:Homebrew )?LLVM version\s+([^\s]+)", output)
    if completed.returncode != 0 or match is None:
        raise RuntimeError(f"could not determine {name} version from {tool}")
    if match.group(1) != CLANG_TBLGEN_VERSION:
        raise RuntimeError(
            f"{name} {CLANG_TBLGEN_VERSION} is required; found {match.group(1)}"
        )
    return match.group(1), hashlib.sha256(normalized_output).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as input_file:
        while chunk := input_file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _verify_file_sha256(path: Path, expected: str) -> None:
    actual = _file_sha256(path)
    if actual != expected:
        raise RuntimeError(
            f"generated header SHA-256 mismatch for {path.name}: "
            f"expected {expected}, got {actual}"
        )


def _json_compatible(value: object) -> object:
    if hasattr(value, "canonical_data"):
        return cast(_CanonicalDataLike, value).canonical_data()
    if hasattr(value, "__dict__"):
        return {key: _json_compatible(item) for key, item in vars(value).items()}
    if isinstance(value, Mapping):
        return {str(key): _json_compatible(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_json_compatible(item) for item in value]
    return value


class _CanonicalDataLike(Protocol):
    def canonical_data(self) -> object: ...


if __name__ == "__main__":
    raise SystemExit(main())
