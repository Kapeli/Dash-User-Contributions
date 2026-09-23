from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import plistlib
import sqlite3
import stat
import tarfile
from copy import copy
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TypedDict, Unpack

import pytest

import arm_acle_docset.package as package_module
import arm_acle_docset.sources.feature_flags as feature_flags_module
from arm_acle_docset.package import (
    ARCHIVE_NAME,
    BUILD_MANIFEST_NAME,
    BUNDLE_IDENTIFIER,
    DOCSET_BUNDLE_NAME,
    LLVM_RELEASE_COMMIT,
    LLVM_RELEASE_TAG,
    LLVM_RELEASE_VERSION,
    RELEASE_PERFORMANCE_PROFILES,
    BuildManifest,
    BuildRuntimeIdentity,
    IndexEntry,
    LLVMToolIdentity,
    _normalize_sqlite_writer_version,
    build_inputs_sha256,
    current_build_runtime_identity,
    package_docset,
    pinned_build_runtime_identity,
    require_pinned_build_runtime,
    source_manifest_sha256,
    verify_docset,
)


@dataclass(frozen=True)
class Page:
    relative_path: str
    html: str
    index_entries: tuple[IndexEntry, ...]


class Renderer:
    def write_assets(self, documents_directory: Path) -> None:
        assets = documents_directory / "assets"
        assets.mkdir()
        (assets / "style.css").write_text("body { color: #111; }\n", encoding="utf-8")


class _PackageOptions(TypedDict, total=False):
    renderer: object | None
    icon_dir: Path | None
    legal_dir: Path | None


def _pages() -> tuple[Page, ...]:
    return (
        Page(
            "index.html",
            "<!doctype html><title>ACLE</title>\n",
            (IndexEntry("Arm C Language Extensions", "Guide", "index.html"),),
        ),
        Page(
            "intrinsics/svadd-s32.html",
            "<!doctype html><title>svadd_s32_m</title>\n",
            (
                IndexEntry("svadd_s32_m", "Function", "intrinsics/svadd-s32.html"),
                IndexEntry("svadd_m", "Function", "intrinsics/svadd-s32.html"),
            ),
        ),
        Page(
            "intrinsics/svadd-u32.html",
            "<!doctype html><title>svadd_u32_m</title>\n",
            (
                IndexEntry("svadd_u32_m", "Function", "intrinsics/svadd-u32.html"),
                IndexEntry("svadd_m", "Function", "intrinsics/svadd-u32.html"),
            ),
        ),
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_source_manifest_digest_binds_feature_flag_source_refs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_digest = source_manifest_sha256()
    manifest = feature_flags_module.DEFAULT_FEATURE_FLAG_MANIFEST
    index, mapping = next(
        (index, mapping)
        for index, mapping in enumerate(manifest)
        if any(source.repository == "Arm documentation" for source in mapping.sources)
    )
    changed_sources = tuple(
        replace(source, url=f"{source.url}&digest-probe=1")
        if source.repository == "Arm documentation"
        else source
        for source in mapping.sources
    )
    changed_manifest = (
        *manifest[:index],
        replace(mapping, sources=changed_sources),
        *manifest[index + 1 :],
    )
    monkeypatch.setattr(
        feature_flags_module,
        "DEFAULT_FEATURE_FLAG_MANIFEST",
        changed_manifest,
    )

    assert source_manifest_sha256() != original_digest


def _build_manifest(
    *, profiles: tuple[str, ...] = RELEASE_PERFORMANCE_PROFILES
) -> BuildManifest:
    scope = (
        "full_release"
        if profiles == RELEASE_PERFORMANCE_PROFILES
        else "development_subset"
    )
    return BuildManifest(
        build_inputs_sha256=build_inputs_sha256(),
        build_runtime=pinned_build_runtime_identity(),
        performance_profile_scope=scope,
        performance_profiles=profiles,
        source_manifest_sha256=source_manifest_sha256(),
        llvm_tools=tuple(
            LLVMToolIdentity(
                name=name,
                version=LLVM_RELEASE_VERSION,
                declared_release_tag=LLVM_RELEASE_TAG,
                declared_source_revision=LLVM_RELEASE_COMMIT,
                executable_sha256=hashlib.sha256(name.encode()).hexdigest(),
                normalized_version_output_sha256=hashlib.sha256(
                    f"{name} --version".encode()
                ).hexdigest(),
            )
            for name in ("clang-tblgen", "llvm-mc", "llvm-mca")
        ),
    )


def _package(
    output: Path,
    *,
    pages: tuple[Page, ...] | None = None,
    archive: bool = True,
    profiles: tuple[str, ...] = RELEASE_PERFORMANCE_PROFILES,
    **kwargs: Unpack[_PackageOptions],
):
    return package_docset(
        pages if pages is not None else _pages(),
        output,
        build_manifest=_build_manifest(profiles=profiles),
        archive=archive,
        **kwargs,
    )


def _archive_entries(path: Path) -> list[tuple[tarfile.TarInfo, bytes | None]]:
    entries: list[tuple[tarfile.TarInfo, bytes | None]] = []
    with tarfile.open(path, "r:gz") as archive:
        for member in archive.getmembers():
            extracted = archive.extractfile(member) if member.isreg() else None
            entries.append((copy(member), extracted.read() if extracted else None))
    return entries


def _write_archive(
    path: Path,
    entries: list[tuple[tarfile.TarInfo, bytes | None]],
    *,
    gzip_mtime: int = 0,
) -> None:
    with (
        path.open("wb") as raw_output,
        gzip.GzipFile(
            filename="", mode="wb", fileobj=raw_output, mtime=gzip_mtime
        ) as compressed,
        tarfile.open(
            fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT
        ) as archive,
    ):
        for member, data in entries:
            archive.addfile(
                member,
                io.BytesIO(data) if data is not None else None,
            )
    path.chmod(0o644)


def _regular_member(name: str, data: bytes) -> tuple[tarfile.TarInfo, bytes]:
    member = tarfile.TarInfo(name)
    member.type = tarfile.REGTYPE
    member.size = len(data)
    member.mode = 0o644
    member.uid = 0
    member.gid = 0
    member.uname = ""
    member.gname = ""
    member.mtime = 0
    return member, data


def _minimal_build_input_tree(root: Path) -> dict[str, Path]:
    files = {
        ".python-version": b"3.14.2\n",
        "generate_docset.py": b"from arm_acle_docset.cli import main\n",
        "generator/pyproject.toml": b"[project]\nname = 'fixture'\n",
        "generator/uv.lock": b"version = 1\n",
        "generator/src/fixture/__init__.py": b"VALUE = 1\n",
        "generator/templates/landing.html.j2": b"<h1>{{ title }}</h1>\n",
        "icon.png": b"png-one",
        "icon@2x.png": b"png-two",
        "NOTICE.md": b"notice without newline",
        "LICENSES/Example.txt": b"license without newline",
    }
    paths: dict[str, Path] = {}
    for relative, content in files.items():
        path = root.joinpath(*relative.split("/"))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        paths[relative] = path
    return paths


def test_package_writes_dash_bundle_alias_overloads_and_docset_only_archive(
    tmp_path: Path,
) -> None:
    result = _package(tmp_path, renderer=Renderer())

    assert result.docset_path == tmp_path / DOCSET_BUNDLE_NAME
    assert result.archive_path == tmp_path / ARCHIVE_NAME
    assert result.page_count == 3
    assert result.index_entry_count == 5

    plist_path = result.docset_path / "Contents" / "Info.plist"
    with plist_path.open("rb") as input_file:
        plist = plistlib.load(input_file)
    assert plist["CFBundleIdentifier"] == BUNDLE_IDENTIFIER
    assert plist["DashDocSetFamily"] == "dashtoc"
    assert "CFBundleShortVersionString" not in plist
    assert "CFBundleVersion" not in plist

    manifest_path = result.docset_path / "Contents" / "Resources" / BUILD_MANIFEST_NAME
    assert manifest_path.read_bytes() == _build_manifest().canonical_bytes()
    manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest_payload["schema_version"] == 2
    assert manifest_payload["build_inputs_sha256"] == build_inputs_sha256()
    assert manifest_payload["build_runtime"] == (
        pinned_build_runtime_identity().canonical_data()
    )

    index_path = result.docset_path / "Contents" / "Resources" / "docSet.dsidx"
    with sqlite3.connect(index_path) as connection:
        overload_paths = connection.execute(
            "SELECT path FROM searchIndex WHERE name = ? ORDER BY path",
            ("svadd_m",),
        ).fetchall()
    assert overload_paths == [
        ("intrinsics/svadd-s32.html",),
        ("intrinsics/svadd-u32.html",),
    ]

    assert result.archive_path is not None
    assert stat.S_IMODE(result.archive_path.stat().st_mode) == 0o644
    with tarfile.open(result.archive_path, "r:gz") as archive:
        assert archive.getnames()
        assert all(
            name == DOCSET_BUNDLE_NAME or name.startswith(f"{DOCSET_BUNDLE_NAME}/")
            for name in archive.getnames()
        )


def test_archive_is_reproducible(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first_result = _package(first, renderer=Renderer())
    second_result = _package(second, renderer=Renderer())

    assert first_result.archive_path is not None
    assert second_result.archive_path is not None
    assert _sha256(first_result.archive_path) == _sha256(second_result.archive_path)


def test_build_runtime_matches_the_pinned_release_baseline() -> None:
    identity = current_build_runtime_identity()

    assert isinstance(identity, BuildRuntimeIdentity)
    assert identity == pinned_build_runtime_identity()
    assert identity.python_implementation == "CPython"
    assert identity.python_version == "3.14.2"
    assert identity.sqlite_version == "3.50.4"
    assert identity.sqlite_source_id == (
        "2025-07-30 19:33:53 "
        "4d8adfb30e03f9cf27f800a2c1ba3c48fb4ca1b08b0f5ed59a4d5ecbf45e20a3"
    )
    assert identity.sqlite_compile_options_sha256 == (
        "d9db047b0720da2cfba3917a79826a7b1a680f7c4d0948b260e9dccd1026c585"
    )
    assert identity.zlib_runtime_version == "1.2.12"
    assert identity.jinja2_version == "3.1.6"
    assert identity.markupsafe_version == "3.0.3"
    assert identity.markdown_it_py_version == "3.0.0"
    assert identity.mdurl_version == "0.1.2"


def test_build_runtime_fails_closed_on_any_component_drift() -> None:
    mismatch = replace(pinned_build_runtime_identity(), sqlite_version="3.50.5")

    with pytest.raises(RuntimeError, match="unpinned build runtime.*sqlite_version"):
        require_pinned_build_runtime(mismatch)


@pytest.mark.parametrize("mutation", ["missing", "extra", "nontext"])
def test_build_runtime_mapping_requires_the_exact_text_schema(mutation: str) -> None:
    payload = dict[str, object](pinned_build_runtime_identity().canonical_data())
    if mutation == "missing":
        del payload["mdurl_version"]
    elif mutation == "extra":
        payload["unexpected"] = "value"
    else:
        payload["sqlite_version"] = 3_050_004

    with pytest.raises(ValueError, match="invalid runtime identity"):
        BuildRuntimeIdentity.from_mapping(payload)


def test_package_preflights_runtime_before_creating_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mismatch = replace(pinned_build_runtime_identity(), python_version="3.14.3")
    monkeypatch.setattr(
        package_module, "current_build_runtime_identity", lambda: mismatch
    )
    output = tmp_path / "must-not-exist"

    with pytest.raises(RuntimeError, match="unpinned build runtime"):
        package_docset(
            _pages(),
            output,
            build_manifest=_build_manifest(),
            renderer=Renderer(),
        )

    assert not output.exists()


@pytest.mark.parametrize(
    "relative_path",
    [
        "NOTICE.md",
        "LICENSES/Example.txt",
        "generator/templates/landing.html.j2",
        "generate_docset.py",
        "icon.png",
    ],
)
def test_manifest_rejects_stale_tracked_build_input_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    relative_path: str,
) -> None:
    inputs = _minimal_build_input_tree(tmp_path / "contribution")
    monkeypatch.setattr(package_module, "CONTRIBUTION_ROOT", tmp_path / "contribution")
    manifest = _build_manifest()
    inputs[relative_path].write_bytes(inputs[relative_path].read_bytes() + b"\n")

    with pytest.raises(ValueError, match="build-input digest does not match"):
        BuildManifest.from_mapping(manifest.canonical_data())


def test_build_input_inventory_rejects_missing_symlink_and_special_files(
    tmp_path: Path,
) -> None:
    missing_root = tmp_path / "missing"
    missing = _minimal_build_input_tree(missing_root)
    missing["generate_docset.py"].unlink()
    with pytest.raises(ValueError, match="missing build input: generate_docset.py"):
        build_inputs_sha256(missing_root)

    symlink_root = tmp_path / "symlink"
    symlink = _minimal_build_input_tree(symlink_root)
    target = symlink_root / "real-template"
    target.write_bytes(b"template\n")
    symlink["generator/templates/landing.html.j2"].unlink()
    symlink["generator/templates/landing.html.j2"].symlink_to(target)
    with pytest.raises(ValueError, match="must not be a symlink"):
        build_inputs_sha256(symlink_root)

    special_root = tmp_path / "special"
    special = _minimal_build_input_tree(special_root)
    special["generator/src/fixture/__init__.py"].unlink()
    os.mkfifo(special["generator/src/fixture/__init__.py"])
    with pytest.raises(ValueError, match="must be a regular file"):
        build_inputs_sha256(special_root)


def test_build_inputs_use_exact_icons_and_ignore_empty_legal_directories(
    tmp_path: Path,
) -> None:
    root = tmp_path / "contribution"
    _minimal_build_input_tree(root)
    baseline = build_inputs_sha256(root)

    (root / "icon-unused.png").write_bytes(b"not consumed")
    (root / "LICENSES" / "empty-untracked-directory").mkdir()

    assert build_inputs_sha256(root) == baseline


def test_package_copies_notice_and_licenses_into_documents(tmp_path: Path) -> None:
    legal_source = tmp_path / "legal-source"
    (legal_source / "LICENSES").mkdir(parents=True)
    (legal_source / "NOTICE.md").write_bytes(b"# Notice")
    (legal_source / "LICENSES" / "Example.txt").write_bytes(b"License terms\r\n")

    result = _package(tmp_path / "output", renderer=Renderer(), legal_dir=legal_source)
    documents = result.docset_path / "Contents" / "Resources" / "Documents"

    assert (documents / "legal" / "NOTICE.md").read_bytes() == b"# Notice"
    assert (
        documents / "legal" / "LICENSES" / "Example.txt"
    ).read_bytes() == b"License terms\r\n"

    (documents / "legal" / "NOTICE.md").write_bytes(b"# Notice\n")
    with pytest.raises(ValueError, match="(size|content) does not match"):
        verify_docset(result.docset_path, archive_path=result.archive_path)


def test_package_rejects_missing_index_target(tmp_path: Path) -> None:
    pages = (
        _pages()[0],
        Page(
            "intrinsics/item.html",
            "<!doctype html><title>item</title>\n",
            (IndexEntry("item", "Function", "intrinsics/missing.html"),),
        ),
    )

    with pytest.raises(ValueError, match="target does not exist"):
        _package(tmp_path, pages=pages, renderer=Renderer())


def test_verify_rejects_archive_sidecar(tmp_path: Path) -> None:
    result = _package(tmp_path, renderer=Renderer())
    assert result.archive_path is not None

    invalid_archive = tmp_path / ARCHIVE_NAME
    entries = _archive_entries(invalid_archive)
    entries.append(_regular_member("generator.py", b"pass\n"))
    _write_archive(invalid_archive, entries)

    with pytest.raises(ValueError, match="outside the docset"):
        verify_docset(result.docset_path, archive_path=invalid_archive)


def test_verify_requires_a_full_release_archive(tmp_path: Path) -> None:
    result = _package(tmp_path, renderer=Renderer())
    assert result.archive_path is not None
    result.archive_path.unlink()

    with pytest.raises(ValueError, match="missing expected archive"):
        verify_docset(result.docset_path)
    with pytest.raises(ValueError, match="missing expected archive"):
        verify_docset(
            result.docset_path,
            require_archive=False,
            allow_development_subset=True,
        )


def test_development_subset_requires_opt_in_and_has_no_release_archive(
    tmp_path: Path,
) -> None:
    profiles = ("neoverse-n2",)
    result = _package(
        tmp_path,
        renderer=Renderer(),
        profiles=profiles,
        archive=False,
    )

    assert result.archive_path is None
    assert not (tmp_path / ARCHIVE_NAME).exists()
    with pytest.raises(ValueError, match="explicit verification opt-in"):
        verify_docset(
            result.docset_path,
            archive_path=None,
            require_archive=False,
        )
    verify_docset(
        result.docset_path,
        archive_path=None,
        require_archive=False,
        allow_development_subset=True,
    )
    stale_archive = tmp_path / ARCHIVE_NAME
    stale_archive.write_bytes(b"stale\n")
    with pytest.raises(ValueError, match="must not have an archive path"):
        verify_docset(
            result.docset_path,
            archive_path=stale_archive,
            require_archive=False,
            allow_development_subset=True,
        )

    with pytest.raises(ValueError, match="must use archive=False"):
        package_docset(
            _pages(),
            tmp_path / "invalid",
            build_manifest=_build_manifest(profiles=profiles),
            renderer=Renderer(),
        )


def test_full_release_rejects_no_archive_without_touching_existing_artifacts(
    tmp_path: Path,
) -> None:
    docset = tmp_path / DOCSET_BUNDLE_NAME
    docset.mkdir()
    marker = docset / "tracked-marker"
    marker.write_bytes(b"docset\n")
    archive = tmp_path / ARCHIVE_NAME
    archive.write_bytes(b"tracked archive\n")

    with pytest.raises(ValueError, match="full release builds must use archive=True"):
        _package(tmp_path, renderer=Renderer(), archive=False)

    assert marker.read_bytes() == b"docset\n"
    assert archive.read_bytes() == b"tracked archive\n"


def test_development_subset_removes_stale_release_archive_after_success(
    tmp_path: Path,
) -> None:
    release = _package(tmp_path, renderer=Renderer())
    assert release.archive_path is not None and release.archive_path.exists()

    result = _package(
        tmp_path,
        renderer=Renderer(),
        profiles=("neoverse-n2",),
        archive=False,
    )

    assert result.archive_path is None
    assert not (tmp_path / ARCHIVE_NAME).exists()


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("missing", "member set does not match"),
        ("extra", "member set does not match"),
        ("duplicate", "duplicate member"),
        ("tampered", "content does not match"),
        ("reordered", "ordering does not match"),
        ("timestamp", "non-canonical ownership or time"),
        ("unsafe", "unsafe path"),
    ],
)
def test_verify_rejects_noncanonical_archive_members(
    tmp_path: Path, mutation: str, message: str
) -> None:
    result = _package(tmp_path, renderer=Renderer())
    assert result.archive_path is not None
    entries = _archive_entries(result.archive_path)

    if mutation == "missing":
        entries.pop()
    elif mutation == "extra":
        entries.append(
            _regular_member(f"{DOCSET_BUNDLE_NAME}/Contents/stale.txt", b"stale\n")
        )
    elif mutation == "duplicate":
        entries.append((copy(entries[-1][0]), entries[-1][1]))
    elif mutation == "tampered":
        for index, (member, data) in enumerate(entries):
            if member.name.endswith("Documents/index.html"):
                assert data is not None
                changed = data.replace(b"ACLE", b"AXLE", 1)
                assert changed != data and len(changed) == len(data)
                entries[index] = (member, changed)
                break
    elif mutation == "reordered":
        entries[-1], entries[-2] = entries[-2], entries[-1]
    elif mutation == "timestamp":
        entries[0][0].mtime = 1
    elif mutation == "unsafe":
        entries[-1][
            0
        ].name = f"{DOCSET_BUNDLE_NAME}/Contents/Resources/Documents/../escape.html"
    else:
        raise AssertionError(mutation)

    _write_archive(result.archive_path, entries)
    with pytest.raises(ValueError, match=message):
        verify_docset(result.docset_path, archive_path=result.archive_path)


@pytest.mark.parametrize(
    "member_type", [tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.FIFOTYPE]
)
def test_verify_rejects_archive_links_and_special_members(
    tmp_path: Path, member_type: bytes
) -> None:
    result = _package(tmp_path, renderer=Renderer())
    assert result.archive_path is not None
    entries = _archive_entries(result.archive_path)
    member, _data = entries[-1]
    member.type = member_type
    member.size = 0
    member.linkname = "target" if member_type != tarfile.FIFOTYPE else ""
    entries[-1] = (member, None)
    _write_archive(result.archive_path, entries)

    with pytest.raises(ValueError, match="link or special member"):
        verify_docset(result.docset_path, archive_path=result.archive_path)


@pytest.mark.parametrize("payload", [b"", b"not a gzip stream\n"])
def test_verify_rejects_empty_or_corrupt_archive(
    tmp_path: Path, payload: bytes
) -> None:
    result = _package(tmp_path, renderer=Renderer())
    assert result.archive_path is not None
    result.archive_path.write_bytes(payload)
    result.archive_path.chmod(0o644)

    with pytest.raises(ValueError, match="empty|cannot read"):
        verify_docset(result.docset_path, archive_path=result.archive_path)


def test_verify_rejects_noncanonical_gzip_header(tmp_path: Path) -> None:
    result = _package(tmp_path, renderer=Renderer())
    assert result.archive_path is not None
    entries = _archive_entries(result.archive_path)
    _write_archive(result.archive_path, entries, gzip_mtime=1)

    with pytest.raises(ValueError, match="not the canonical bundle archive"):
        verify_docset(result.docset_path, archive_path=result.archive_path)


def test_verify_rejects_archive_from_another_bundle(tmp_path: Path) -> None:
    first = _package(tmp_path / "first", renderer=Renderer())
    changed_pages = (
        Page(
            "index.html",
            "<!doctype html><title>Different</title>\n",
            (IndexEntry("Arm C Language Extensions", "Guide", "index.html"),),
        ),
        *_pages()[1:],
    )
    second = _package(tmp_path / "second", pages=changed_pages, renderer=Renderer())
    assert first.archive_path is not None
    assert second.archive_path is not None
    first.archive_path.write_bytes(second.archive_path.read_bytes())
    first.archive_path.chmod(0o644)

    with pytest.raises(ValueError, match="(size|content) does not match"):
        verify_docset(first.docset_path, archive_path=first.archive_path)


@pytest.mark.parametrize(
    "change",
    [
        {"schema_version": True},
        {"schema_version": 3},
        {"source_manifest_sha256": "0" * 64},
    ],
)
def test_verify_rejects_invalid_build_manifest(
    tmp_path: Path, change: dict[str, object]
) -> None:
    result = _package(tmp_path, renderer=Renderer())
    manifest_path = result.docset_path / "Contents" / "Resources" / BUILD_MANIFEST_NAME
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload.update(change)
    manifest_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    with pytest.raises(ValueError, match="schema_version|source manifest digest"):
        verify_docset(result.docset_path, archive_path=result.archive_path)


def test_verify_requires_canonical_build_manifest_json(tmp_path: Path) -> None:
    result = _package(tmp_path, renderer=Renderer())
    manifest_path = result.docset_path / "Contents" / "Resources" / BUILD_MANIFEST_NAME
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="not in canonical JSON form"):
        verify_docset(result.docset_path, archive_path=result.archive_path)


def test_manifest_rejects_unpinned_render_dependency(tmp_path: Path) -> None:
    result = _package(tmp_path, renderer=Renderer())
    manifest_path = result.docset_path / "Contents" / "Resources" / BUILD_MANIFEST_NAME
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["build_runtime"]["jinja2_version"] = "3.1.7"
    manifest_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    with pytest.raises(RuntimeError, match="unpinned build runtime.*jinja2_version"):
        verify_docset(result.docset_path, archive_path=result.archive_path)


def test_sqlite_writer_version_is_canonical_and_readable(tmp_path: Path) -> None:
    result = _package(
        tmp_path,
        renderer=Renderer(),
        profiles=("neoverse-n2",),
        archive=False,
    )
    index_path = result.docset_path / "Contents" / "Resources" / "docSet.dsidx"
    canonical = index_path.read_bytes()
    assert canonical[96:100] == b"\x00\x00\x00\x00"

    normalized: list[bytes] = []
    for writer_version in (3_050_004, 3_051_000):
        candidate = tmp_path / f"index-{writer_version}.dsidx"
        data = bytearray(canonical)
        data[96:100] = writer_version.to_bytes(4, "big")
        candidate.write_bytes(data)
        _normalize_sqlite_writer_version(candidate)
        normalized.append(candidate.read_bytes())
        with sqlite3.connect(candidate) as connection:
            assert connection.execute("PRAGMA quick_check").fetchone() == ("ok",)

    assert normalized == [canonical, canonical]


def test_verify_rejects_noncanonical_sqlite_writer_sentinel(tmp_path: Path) -> None:
    result = _package(
        tmp_path,
        renderer=Renderer(),
        profiles=("neoverse-n2",),
        archive=False,
    )
    index_path = result.docset_path / "Contents" / "Resources" / "docSet.dsidx"
    data = bytearray(index_path.read_bytes())
    data[96:100] = (3_050_004).to_bytes(4, "big")
    index_path.write_bytes(data)

    with pytest.raises(ValueError, match="writer-version field is not canonical"):
        verify_docset(
            result.docset_path,
            require_archive=False,
            allow_development_subset=True,
            allow_missing_release_archive=True,
        )


def test_verify_reports_corrupt_sqlite_as_validation_error(tmp_path: Path) -> None:
    result = _package(tmp_path, renderer=Renderer())
    index_path = result.docset_path / "Contents" / "Resources" / "docSet.dsidx"
    index_path.write_bytes(b"not sqlite\n")

    with pytest.raises(ValueError, match="not a valid SQLite 3 database"):
        verify_docset(result.docset_path, archive_path=result.archive_path)
