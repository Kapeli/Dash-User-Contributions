"""Dash bundle, SQLite index, and deterministic archive packaging."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import platform
import plistlib
import shutil
import sqlite3
import stat
import tarfile
import tempfile
import zlib
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as distribution_version
from pathlib import Path, PurePosixPath
from typing import Any, Protocol, cast

DOCSET_DISPLAY_NAME = "Arm C Language Extensions"
DOCSET_BUNDLE_NAME = "Arm_C_Language_Extensions.docset"
ARCHIVE_NAME = "Arm_C_Language_Extensions.tgz"
DOCSET_VERSION = "62d9cbd68abb"
BUNDLE_IDENTIFIER = "io.github.joeyteng.arm-acle"
PLATFORM_FAMILY = "acle"
BUILD_MANIFEST_NAME = "build-manifest.json"
BUILD_MANIFEST_SCHEMA_VERSION = 2
SQLITE_CANONICAL_WRITER_VERSION = 0
CONTRIBUTION_ROOT = Path(__file__).resolve().parents[3]
RELEASE_PERFORMANCE_PROFILES = (
    "cortex-a55",
    "neoverse-n1",
    "neoverse-v1",
    "neoverse-n2",
    "cortex-m55",
    "cortex-m85",
)
EXPECTED_LLVM_TOOLS = ("clang-tblgen", "llvm-mc", "llvm-mca")
LLVM_RELEASE_VERSION = "22.1.1"
LLVM_RELEASE_TAG = "llvmorg-22.1.1"
LLVM_RELEASE_COMMIT = "fef02d48c08db859ef83f84232ed78bd9d1c323a"
PINNED_PYTHON_IMPLEMENTATION = "CPython"
PINNED_PYTHON_VERSION = "3.14.2"
PINNED_SQLITE_VERSION = "3.50.4"
PINNED_SQLITE_SOURCE_ID = (
    "2025-07-30 19:33:53 "
    "4d8adfb30e03f9cf27f800a2c1ba3c48fb4ca1b08b0f5ed59a4d5ecbf45e20a3"
)
PINNED_SQLITE_COMPILE_OPTIONS_SHA256 = (
    "d9db047b0720da2cfba3917a79826a7b1a680f7c4d0948b260e9dccd1026c585"
)
PINNED_ZLIB_RUNTIME_VERSION = "1.2.12"
PINNED_JINJA2_VERSION = "3.1.6"
PINNED_MARKUPSAFE_VERSION = "3.0.3"
PINNED_MARKDOWN_IT_PY_VERSION = "3.0.0"
PINNED_MDURL_VERSION = "0.1.2"


@dataclass(frozen=True, order=True, slots=True)
class IndexEntry:
    """One row in Dash's search index."""

    name: str
    type: str
    path: str


@dataclass(frozen=True, slots=True)
class PackageResult:
    """Paths and counts produced by :func:`package_docset`."""

    docset_path: Path
    archive_path: Path | None
    page_count: int
    index_entry_count: int


@dataclass(frozen=True, slots=True)
class _BundleMember:
    kind: str
    size: int
    sha256: str | None = None


@dataclass(frozen=True, slots=True)
class BuildRuntimeIdentity:
    """Runtime components whose output bytes affect release reproducibility."""

    python_implementation: str
    python_version: str
    sqlite_version: str
    sqlite_source_id: str
    sqlite_compile_options_sha256: str
    zlib_runtime_version: str
    jinja2_version: str
    markupsafe_version: str
    markdown_it_py_version: str
    mdurl_version: str

    def __post_init__(self) -> None:
        for field_name in (
            "python_implementation",
            "python_version",
            "sqlite_version",
            "sqlite_source_id",
            "zlib_runtime_version",
            "jinja2_version",
            "markupsafe_version",
            "markdown_it_py_version",
            "mdurl_version",
        ):
            value = getattr(self, field_name)
            if not value.strip() or value != value.strip():
                raise ValueError(
                    f"build runtime {field_name} must be non-empty and trimmed"
                )
        if not _is_lowercase_sha256(self.sqlite_compile_options_sha256):
            raise ValueError(
                "SQLite compile-options digest must be a lowercase hexadecimal SHA-256"
            )

    def canonical_data(self) -> dict[str, str]:
        return {
            "python_implementation": self.python_implementation,
            "python_version": self.python_version,
            "jinja2_version": self.jinja2_version,
            "markdown_it_py_version": self.markdown_it_py_version,
            "markupsafe_version": self.markupsafe_version,
            "mdurl_version": self.mdurl_version,
            "sqlite_compile_options_sha256": self.sqlite_compile_options_sha256,
            "sqlite_source_id": self.sqlite_source_id,
            "sqlite_version": self.sqlite_version,
            "zlib_runtime_version": self.zlib_runtime_version,
        }

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> BuildRuntimeIdentity:
        expected_keys = {
            "python_implementation",
            "python_version",
            "jinja2_version",
            "markdown_it_py_version",
            "markupsafe_version",
            "mdurl_version",
            "sqlite_compile_options_sha256",
            "sqlite_source_id",
            "sqlite_version",
            "zlib_runtime_version",
        }
        if set(payload) != expected_keys or not all(
            isinstance(payload[key], str) for key in expected_keys
        ):
            raise ValueError("build manifest contains an invalid runtime identity")
        return cls(
            python_implementation=cast(str, payload["python_implementation"]),
            python_version=cast(str, payload["python_version"]),
            jinja2_version=cast(str, payload["jinja2_version"]),
            markdown_it_py_version=cast(str, payload["markdown_it_py_version"]),
            markupsafe_version=cast(str, payload["markupsafe_version"]),
            mdurl_version=cast(str, payload["mdurl_version"]),
            sqlite_compile_options_sha256=cast(
                str, payload["sqlite_compile_options_sha256"]
            ),
            sqlite_source_id=cast(str, payload["sqlite_source_id"]),
            sqlite_version=cast(str, payload["sqlite_version"]),
            zlib_runtime_version=cast(str, payload["zlib_runtime_version"]),
        )


@dataclass(frozen=True, order=True, slots=True)
class LLVMToolIdentity:
    """Truthful identity for one concrete LLVM executable and declared release."""

    name: str
    version: str
    declared_release_tag: str
    declared_source_revision: str
    executable_sha256: str
    normalized_version_output_sha256: str

    def __post_init__(self) -> None:
        if not self.name or any(character.isspace() for character in self.name):
            raise ValueError("LLVM tool name must be non-empty with no whitespace")
        if not self.version.strip() or self.version != self.version.strip():
            raise ValueError("LLVM tool version must be non-empty and trimmed")
        if not _is_lowercase_sha1(self.declared_source_revision):
            raise ValueError(
                "LLVM declared source revision must be a lowercase hexadecimal SHA-1"
            )
        if not _is_lowercase_sha256(self.executable_sha256):
            raise ValueError(
                "LLVM executable digest must be lowercase hexadecimal SHA-256"
            )
        if not _is_lowercase_sha256(self.normalized_version_output_sha256):
            raise ValueError(
                "LLVM version-output digest must be lowercase hexadecimal SHA-256"
            )
        if self.version != LLVM_RELEASE_VERSION:
            raise ValueError(
                f"LLVM tool version must be the pinned {LLVM_RELEASE_VERSION} release"
            )
        if self.declared_release_tag != LLVM_RELEASE_TAG:
            raise ValueError("LLVM declared release tag does not match the pin")
        if self.declared_source_revision != LLVM_RELEASE_COMMIT:
            raise ValueError("LLVM declared source revision does not match the pin")

    def canonical_data(self) -> dict[str, str]:
        return {
            "declared_release_tag": self.declared_release_tag,
            "declared_source_revision": self.declared_source_revision,
            "executable_sha256": self.executable_sha256,
            "name": self.name,
            "version": self.version,
            "normalized_version_output_sha256": self.normalized_version_output_sha256,
        }


@dataclass(frozen=True, slots=True)
class BuildManifest:
    """Canonical description of one bundle built under the pinned runtime."""

    build_inputs_sha256: str
    build_runtime: BuildRuntimeIdentity
    performance_profile_scope: str
    performance_profiles: tuple[str, ...]
    source_manifest_sha256: str
    llvm_tools: tuple[LLVMToolIdentity, ...]

    def __post_init__(self) -> None:
        if not _is_lowercase_sha256(self.build_inputs_sha256):
            raise ValueError(
                "build-input digest must be a lowercase hexadecimal SHA-256"
            )
        if self.build_inputs_sha256 != build_inputs_sha256():
            raise ValueError(
                "build-input digest does not match the current generator inputs"
            )
        require_pinned_build_runtime(self.build_runtime)
        if self.performance_profile_scope not in (
            "full_release",
            "development_subset",
        ):
            raise ValueError(
                "performance profile scope must be full_release or development_subset"
            )
        if (
            not self.performance_profiles
            or len(set(self.performance_profiles)) != len(self.performance_profiles)
            or any(
                profile not in RELEASE_PERFORMANCE_PROFILES
                for profile in self.performance_profiles
            )
        ):
            raise ValueError(
                "performance profiles must be a non-empty unique release subset"
            )
        canonical_profiles = tuple(
            profile
            for profile in RELEASE_PERFORMANCE_PROFILES
            if profile in self.performance_profiles
        )
        if self.performance_profiles != canonical_profiles:
            raise ValueError("performance profiles must use canonical release ordering")
        if self.performance_profile_scope == "full_release":
            if self.performance_profiles != RELEASE_PERFORMANCE_PROFILES:
                raise ValueError(
                    "full_release manifest must contain all six release profiles"
                )
        elif self.performance_profiles == RELEASE_PERFORMANCE_PROFILES:
            raise ValueError(
                "development_subset manifest must omit at least one release profile"
            )
        if not _is_lowercase_sha256(self.source_manifest_sha256):
            raise ValueError(
                "source manifest digest must be a lowercase hexadecimal SHA-256"
            )
        if self.source_manifest_sha256 != source_manifest_sha256():
            raise ValueError(
                "source manifest digest does not match the current source lock"
            )
        if tuple(sorted(self.llvm_tools)) != self.llvm_tools:
            raise ValueError("LLVM tool identities must use canonical name ordering")
        if tuple(tool.name for tool in self.llvm_tools) != EXPECTED_LLVM_TOOLS:
            raise ValueError(
                "build manifest must identify clang-tblgen, llvm-mc, and llvm-mca"
            )
        if len({tool.name for tool in self.llvm_tools}) != len(self.llvm_tools):
            raise ValueError("build manifest contains duplicate LLVM tool identities")

    @property
    def is_full_release(self) -> bool:
        return self.performance_profile_scope == "full_release"

    def canonical_data(self) -> dict[str, object]:
        return {
            "build_inputs_sha256": self.build_inputs_sha256,
            "build_runtime": self.build_runtime.canonical_data(),
            "llvm_tools": [tool.canonical_data() for tool in self.llvm_tools],
            "performance_profile_scope": self.performance_profile_scope,
            "performance_profiles": list(self.performance_profiles),
            "schema_version": BUILD_MANIFEST_SCHEMA_VERSION,
            "source_manifest_sha256": self.source_manifest_sha256,
        }

    def canonical_bytes(self) -> bytes:
        return (
            json.dumps(
                self.canonical_data(),
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            )
            + "\n"
        ).encode("utf-8")

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> BuildManifest:
        expected_keys = {
            "build_inputs_sha256",
            "build_runtime",
            "llvm_tools",
            "performance_profile_scope",
            "performance_profiles",
            "schema_version",
            "source_manifest_sha256",
        }
        if set(payload) != expected_keys:
            raise ValueError("build manifest has unexpected or missing fields")
        schema_version = payload["schema_version"]
        if (
            not isinstance(schema_version, int)
            or isinstance(schema_version, bool)
            or schema_version != BUILD_MANIFEST_SCHEMA_VERSION
        ):
            raise ValueError(
                f"build manifest schema_version must be {BUILD_MANIFEST_SCHEMA_VERSION}"
            )
        profile_scope = payload["performance_profile_scope"]
        profiles = payload["performance_profiles"]
        source_digest = payload["source_manifest_sha256"]
        build_inputs_digest = payload["build_inputs_sha256"]
        runtime = payload["build_runtime"]
        tools = payload["llvm_tools"]
        if not isinstance(profile_scope, str):
            # A decoded JSON document has an invalid value, not an API type misuse.
            raise ValueError(  # noqa: TRY004
                "build manifest performance_profile_scope must be text"
            )
        if not isinstance(profiles, list) or not all(
            isinstance(profile, str) for profile in profiles
        ):
            raise ValueError("build manifest performance_profiles must be text values")
        if not isinstance(source_digest, str):
            raise ValueError(  # noqa: TRY004
                "build manifest source_manifest_sha256 must be text"
            )
        if not isinstance(build_inputs_digest, str):
            raise ValueError(  # noqa: TRY004
                "build manifest build_inputs_sha256 must be text"
            )
        if not isinstance(runtime, Mapping):
            raise ValueError(  # noqa: TRY004
                "build manifest build_runtime must be an object"
            )
        if not isinstance(tools, list):
            raise ValueError(  # noqa: TRY004
                "build manifest llvm_tools must be a list"
            )
        parsed_tools: list[LLVMToolIdentity] = []
        for tool in tools:
            if not isinstance(tool, Mapping) or set(tool) != {
                "declared_release_tag",
                "declared_source_revision",
                "executable_sha256",
                "name",
                "version",
                "normalized_version_output_sha256",
            }:
                raise ValueError(
                    "build manifest contains an invalid LLVM tool identity"
                )
            if not all(isinstance(tool[key], str) for key in tool):
                raise ValueError("LLVM tool identity values must be text")
            parsed_tools.append(
                LLVMToolIdentity(
                    name=tool["name"],
                    version=tool["version"],
                    declared_release_tag=tool["declared_release_tag"],
                    declared_source_revision=tool["declared_source_revision"],
                    executable_sha256=tool["executable_sha256"],
                    normalized_version_output_sha256=tool[
                        "normalized_version_output_sha256"
                    ],
                )
            )
        return cls(
            build_inputs_sha256=build_inputs_digest,
            build_runtime=BuildRuntimeIdentity.from_mapping(runtime),
            performance_profile_scope=profile_scope,
            performance_profiles=tuple(profiles),
            source_manifest_sha256=source_digest,
            llvm_tools=tuple(parsed_tools),
        )


class RenderedPageLike(Protocol):
    """Renderer output consumed by the packaging layer."""

    @property
    def relative_path(self) -> str: ...

    @property
    def html(self) -> str: ...

    @property
    def index_entries(self) -> Sequence[Any]: ...


def package_docset(
    pages: Iterable[RenderedPageLike],
    output_dir: Path,
    *,
    build_manifest: BuildManifest,
    renderer: Any | None = None,
    icon_dir: Path | None = None,
    legal_dir: Path | None = None,
    archive: bool = True,
) -> PackageResult:
    """Build a Dash docset and an optional reproducible ``.tgz`` archive."""

    require_pinned_build_runtime()
    if build_manifest.is_full_release and not archive:
        raise ValueError("full release builds must use archive=True")
    if archive and not build_manifest.is_full_release:
        raise ValueError("development subset builds must use archive=False")

    output_root = Path(output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    final_docset = output_root / DOCSET_BUNDLE_NAME
    archive_target = output_root / ARCHIVE_NAME
    final_archive = archive_target if archive else None

    materialized_pages = tuple(pages)
    if not materialized_pages:
        raise ValueError("refusing to package an empty docset")

    with tempfile.TemporaryDirectory(
        prefix=".arm-acle-build-", dir=output_root
    ) as staging:
        staged_docset = Path(staging) / DOCSET_BUNDLE_NAME
        contents = staged_docset / "Contents"
        resources = contents / "Resources"
        documents = resources / "Documents"
        documents.mkdir(parents=True)

        _write_info_plist(contents / "Info.plist")
        _write_build_manifest(resources / BUILD_MANIFEST_NAME, build_manifest)
        if icon_dir is not None:
            _copy_icons(Path(icon_dir), staged_docset)
        if renderer is not None:
            renderer.write_assets(documents)
        if legal_dir is not None:
            _copy_legal_materials(Path(legal_dir), documents)

        entries: list[IndexEntry] = []
        seen_paths: set[str] = set()
        for page in sorted(materialized_pages, key=lambda item: item.relative_path):
            relative_path = _safe_relative_path(page.relative_path)
            if relative_path in seen_paths:
                raise ValueError(f"duplicate rendered page path: {relative_path}")
            seen_paths.add(relative_path)
            destination = documents.joinpath(*PurePosixPath(relative_path).parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(page.html, encoding="utf-8", newline="\n")
            entries.extend(_coerce_index_entry(entry) for entry in page.index_entries)

        if "index.html" not in seen_paths:
            raise ValueError("renderer output must include index.html")

        unique_entries = sorted(set(entries))
        _write_search_index(resources / "docSet.dsidx", unique_entries)
        _validate_index_targets(documents, unique_entries)
        if build_inputs_sha256() != build_manifest.build_inputs_sha256:
            raise ValueError("build inputs changed while packaging the docset")

        if final_docset.exists():
            shutil.rmtree(final_docset)
        os.replace(staged_docset, final_docset)

    if not archive:
        archive_target.unlink(missing_ok=True)

    if final_archive is not None:
        _write_deterministic_tgz(final_docset, final_archive)

    verify_docset(
        final_docset,
        archive_path=final_archive,
        require_archive=archive,
        allow_development_subset=True,
        allow_missing_release_archive=not archive,
    )
    return PackageResult(
        docset_path=final_docset,
        archive_path=final_archive,
        page_count=len(materialized_pages),
        index_entry_count=len(unique_entries),
    )


def verify_docset(
    docset_path: Path,
    *,
    archive_path: Path | None = None,
    require_archive: bool = True,
    allow_development_subset: bool = False,
    allow_missing_release_archive: bool = False,
) -> None:
    """Validate the bundle, release manifest, index, and exact archive contents."""

    require_pinned_build_runtime()
    docset = Path(docset_path)
    if docset.name != DOCSET_BUNDLE_NAME or not docset.is_dir():
        raise ValueError(f"not the expected docset bundle: {docset}")
    bundle_inventory = _bundle_inventory(docset)

    contents = docset / "Contents"
    resources = contents / "Resources"
    documents = resources / "Documents"
    plist_path = contents / "Info.plist"
    index_path = resources / "docSet.dsidx"
    build_manifest_path = resources / BUILD_MANIFEST_NAME
    if (
        not documents.is_dir()
        or not plist_path.is_file()
        or not index_path.is_file()
        or not build_manifest_path.is_file()
    ):
        raise ValueError(
            "docset is missing Info.plist, Documents, docSet.dsidx, or "
            f"{BUILD_MANIFEST_NAME}"
        )

    build_manifest = _read_build_manifest(build_manifest_path)
    if not build_manifest.is_full_release and archive_path is not None:
        raise ValueError("development subset must not have an archive path")
    if not build_manifest.is_full_release and not allow_development_subset:
        raise ValueError(
            "development performance subset requires explicit verification opt-in"
        )

    with plist_path.open("rb") as input_file:
        metadata = plistlib.load(input_file)
    expected_metadata = {
        "CFBundleIdentifier": BUNDLE_IDENTIFIER,
        "CFBundleName": DOCSET_DISPLAY_NAME,
        "DocSetPlatformFamily": PLATFORM_FAMILY,
        "DashDocSetFamily": "dashtoc",
        "dashIndexFilePath": "index.html",
        "isDashDocset": True,
    }
    for key, expected in expected_metadata.items():
        if metadata.get(key) != expected:
            raise ValueError(
                f"unexpected Info.plist value for {key}: {metadata.get(key)!r}"
            )
    for forbidden_key in ("CFBundleShortVersionString", "CFBundleVersion"):
        if forbidden_key in metadata:
            raise ValueError(f"docset Info.plist must not contain {forbidden_key}")

    _verify_sqlite_header(index_path)
    try:
        with sqlite3.connect(
            f"{index_path.resolve().as_uri()}?mode=ro", uri=True
        ) as connection:
            columns = [
                row[1]
                for row in connection.execute(
                    "PRAGMA table_info(searchIndex)"
                ).fetchall()
            ]
            if columns != ["id", "name", "type", "path"]:
                raise ValueError(f"unexpected searchIndex schema: {columns}")
            rows = connection.execute(
                "SELECT name, type, path FROM searchIndex ORDER BY name, type, path"
            ).fetchall()
    except sqlite3.DatabaseError as error:
        message = " ".join(str(error).splitlines()) or error.__class__.__name__
        raise ValueError(f"invalid SQLite search index: {message}") from error
    if not rows:
        raise ValueError("search index is empty")
    _validate_index_targets(
        documents,
        (
            IndexEntry(name=name, type=entry_type, path=path)
            for name, entry_type, path in rows
        ),
    )

    if archive_path is None:
        if require_archive or (
            build_manifest.is_full_release and not allow_missing_release_archive
        ):
            raise ValueError(
                f"missing expected archive: {docset.parent / ARCHIVE_NAME}"
            )
    else:
        _verify_archive(docset, Path(archive_path), bundle_inventory)


def _write_info_plist(path: Path) -> None:
    metadata = {
        "CFBundleIdentifier": BUNDLE_IDENTIFIER,
        "CFBundleName": DOCSET_DISPLAY_NAME,
        "CFBundleDisplayName": DOCSET_DISPLAY_NAME,
        "DocSetPlatformFamily": PLATFORM_FAMILY,
        "DashDocSetFamily": "dashtoc",
        "DashDocSetFallbackURL": "https://arm-software.github.io/acle/main/acle.html",
        "dashIndexFilePath": "index.html",
        "isDashDocset": True,
    }
    with path.open("wb") as output:
        plistlib.dump(metadata, output, fmt=plistlib.FMT_XML, sort_keys=True)


def _write_build_manifest(path: Path, manifest: BuildManifest) -> None:
    path.write_bytes(manifest.canonical_bytes())


def _read_build_manifest(path: Path) -> BuildManifest:
    raw = path.read_bytes()
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid {BUILD_MANIFEST_NAME}: {error}") from error
    if not isinstance(payload, Mapping):
        # A decoded JSON document has an invalid value, not an API type misuse.
        raise ValueError(  # noqa: TRY004
            f"{BUILD_MANIFEST_NAME} root must be an object"
        )
    manifest = BuildManifest.from_mapping(payload)
    if raw != manifest.canonical_bytes():
        raise ValueError(f"{BUILD_MANIFEST_NAME} is not in canonical JSON form")
    return manifest


def _copy_icons(source_directory: Path, docset: Path) -> None:
    for name in ("icon.png", "icon@2x.png"):
        source = source_directory / name
        if source.is_symlink() or not source.is_file():
            raise ValueError(f"missing docset icon: {source}")
        shutil.copyfile(source, docset / name)


def _copy_legal_materials(source_directory: Path, documents: Path) -> None:
    notice = source_directory / "NOTICE.md"
    licenses = source_directory / "LICENSES"
    if notice.is_symlink() or not notice.is_file():
        raise ValueError(f"missing docset notice: {notice}")
    if licenses.is_symlink() or not licenses.is_dir():
        raise ValueError(f"missing docset licenses: {licenses}")

    destination = documents / "legal"
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(notice, destination / notice.name)
    for source in sorted(licenses.rglob("*"), key=lambda item: item.as_posix()):
        if source.is_symlink():
            raise ValueError(f"legal material must not be a symlink: {source}")
        relative = source.relative_to(licenses)
        target = destination / "LICENSES" / relative
        if source.is_dir():
            continue
        elif source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        else:
            raise ValueError(f"unsupported legal material: {source}")


def _write_search_index(path: Path, entries: Sequence[IndexEntry]) -> None:
    with sqlite3.connect(path) as connection:
        if connection.execute("PRAGMA secure_delete=OFF").fetchone() != (0,):
            raise ValueError("SQLite refused the pinned secure_delete=OFF setting")
        connection.execute("PRAGMA page_size = 4096")
        connection.execute("PRAGMA journal_mode = DELETE")
        connection.execute(
            "CREATE TABLE searchIndex("
            "id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT"
            ")"
        )
        connection.execute(
            "CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path)"
        )
        connection.executemany(
            "INSERT INTO searchIndex(name, type, path) VALUES (?, ?, ?)",
            ((entry.name, entry.type, entry.path) for entry in entries),
        )
        connection.commit()
        connection.execute("VACUUM")
    _normalize_sqlite_writer_version(path)


def _normalize_sqlite_writer_version(path: Path) -> None:
    """Normalize the SQLite release field under the pinned build runtime.

    SQLite stores ``SQLITE_VERSION_NUMBER`` at bytes 96 through 99.  This
    generator deliberately uses zero as its canonical sentinel after the final
    transaction.  The complete runtime identity remains pinned and recorded;
    zeroing this field is not a claim about arbitrary SQLite compatibility.
    """

    with path.open("r+b") as database:
        header = database.read(100)
        if len(header) < 100 or header[:16] != b"SQLite format 3\x00":
            raise ValueError(f"not a valid SQLite 3 database: {path}")
        database.seek(96)
        database.write(SQLITE_CANONICAL_WRITER_VERSION.to_bytes(4, "big"))
    _verify_sqlite_header(path)
    with sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True) as connection:
        if connection.execute("PRAGMA quick_check").fetchone() != ("ok",):
            raise ValueError(
                f"SQLite index failed quick_check after normalization: {path}"
            )


def _verify_sqlite_header(path: Path) -> None:
    with path.open("rb") as database:
        header = database.read(100)
    if len(header) < 100 or header[:16] != b"SQLite format 3\x00":
        raise ValueError(f"not a valid SQLite 3 database: {path}")
    expected = SQLITE_CANONICAL_WRITER_VERSION.to_bytes(4, "big")
    if header[96:100] != expected:
        raise ValueError("SQLite writer-version field is not canonical")


def _write_deterministic_tgz(docset: Path, archive_path: Path) -> None:
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=f".{archive_path.name}.",
            dir=archive_path.parent,
            delete=False,
        ) as raw_output:
            temporary = Path(raw_output.name)
            with (
                gzip.GzipFile(
                    filename="", mode="wb", fileobj=raw_output, mtime=0
                ) as compressed,
                tarfile.open(
                    fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT
                ) as archive,
            ):
                paths = [
                    docset,
                    *sorted(docset.rglob("*"), key=lambda item: item.as_posix()),
                ]
                for path in paths:
                    arcname = path.relative_to(docset.parent).as_posix()
                    info = archive.gettarinfo(str(path), arcname=arcname)
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    info.mtime = 0
                    info.pax_headers = {}
                    if info.isdir():
                        info.mode = 0o755
                        archive.addfile(info)
                    elif info.isfile():
                        info.mode = 0o644
                        with path.open("rb") as input_file:
                            archive.addfile(info, input_file)
                    else:
                        raise ValueError(f"unsupported file type in docset: {path}")
        os.replace(temporary, archive_path)
        archive_path.chmod(0o644)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _verify_archive(
    docset: Path,
    archive_path: Path,
    expected_inventory: Mapping[str, _BundleMember],
) -> None:
    if (
        archive_path.name != ARCHIVE_NAME
        or archive_path.is_symlink()
        or not archive_path.is_file()
    ):
        raise ValueError(f"missing expected archive: {archive_path}")
    if archive_path.stat().st_size == 0:
        raise ValueError("docset archive is empty")
    if stat.S_IMODE(archive_path.lstat().st_mode) != 0o644:
        raise ValueError("docset archive mode must be 0644")

    try:
        with tarfile.open(archive_path, mode="r:gz") as archive:
            members = archive.getmembers()
            if not members:
                raise ValueError("docset archive is empty")

            actual_members: dict[str, tarfile.TarInfo] = {}
            for member in members:
                name = member.name
                path = PurePosixPath(name)
                if (
                    path.is_absolute()
                    or not path.parts
                    or ".." in path.parts
                    or path.as_posix() != name
                ):
                    raise ValueError(f"archive contains an unsafe path: {name}")
                if name != DOCSET_BUNDLE_NAME and not name.startswith(
                    f"{DOCSET_BUNDLE_NAME}/"
                ):
                    raise ValueError(
                        f"archive contains a file outside the docset: {name}"
                    )
                if name in actual_members:
                    raise ValueError(f"archive contains duplicate member: {name}")
                if member.type == tarfile.DIRTYPE:
                    kind = "directory"
                    expected_mode = 0o755
                elif member.type == tarfile.REGTYPE:
                    kind = "file"
                    expected_mode = 0o644
                else:
                    raise ValueError(
                        f"archive contains a link or special member: {name}"
                    )
                if member.linkname:
                    raise ValueError(
                        f"archive member has an unexpected link name: {name}"
                    )
                if member.mode != expected_mode:
                    raise ValueError(
                        f"archive member has unexpected mode {member.mode:o}: {name}"
                    )
                if (
                    member.uid != 0
                    or member.gid != 0
                    or member.uname != ""
                    or member.gname != ""
                    or member.mtime != 0
                ):
                    raise ValueError(
                        f"archive member has non-canonical ownership or time: {name}"
                    )
                expected = expected_inventory.get(name)
                if expected is not None and expected.kind != kind:
                    raise ValueError(
                        f"archive member type does not match bundle: {name}"
                    )
                actual_members[name] = member

            actual_names = set(actual_members)
            expected_names = set(expected_inventory)
            if actual_names != expected_names:
                missing = sorted(expected_names - actual_names)
                unexpected = sorted(actual_names - expected_names)
                details = []
                if missing:
                    details.append(f"missing {_summarize_names(missing)}")
                if unexpected:
                    details.append(f"unexpected {_summarize_names(unexpected)}")
                raise ValueError(
                    "archive member set does not match bundle: " + "; ".join(details)
                )

            expected_order = list(expected_inventory)
            actual_order = [member.name for member in members]
            if actual_order != expected_order:
                raise ValueError("archive member ordering does not match the bundle")

            for name, expected in expected_inventory.items():
                member = actual_members[name]
                if member.size != expected.size:
                    raise ValueError(
                        f"archive member size does not match bundle: {name}"
                    )
                if expected.kind != "file":
                    continue
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise ValueError(f"cannot read archive member: {name}")
                actual_digest = _sha256_stream(extracted)
                if actual_digest != expected.sha256:
                    raise ValueError(
                        f"archive member content does not match bundle: {name}"
                    )
    except (tarfile.TarError, EOFError, gzip.BadGzipFile, OSError) as error:
        message = " ".join(str(error).splitlines()) or error.__class__.__name__
        raise ValueError(f"cannot read docset archive: {message}") from error

    with tempfile.TemporaryDirectory(
        prefix=".arm-acle-verify-", dir=archive_path.parent
    ) as temporary_directory:
        canonical_archive = Path(temporary_directory) / ARCHIVE_NAME
        _write_deterministic_tgz(docset, canonical_archive)
        if _sha256_path(canonical_archive) != _sha256_path(archive_path):
            raise ValueError("docset archive is not the canonical bundle archive")


def _bundle_inventory(docset: Path) -> dict[str, _BundleMember]:
    if docset.is_symlink():
        raise ValueError(f"docset bundle must not be a symlink: {docset}")
    inventory = {
        DOCSET_BUNDLE_NAME: _BundleMember(kind="directory", size=0),
    }
    for path in sorted(docset.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(docset.parent).as_posix()
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise ValueError(f"docset bundle contains a symlink: {relative}")
        if stat.S_ISDIR(mode):
            inventory[relative] = _BundleMember(kind="directory", size=0)
        elif stat.S_ISREG(mode):
            inventory[relative] = _BundleMember(
                kind="file",
                size=path.stat().st_size,
                sha256=_sha256_path(path),
            )
        else:
            raise ValueError(f"docset bundle contains a special file: {relative}")
    return inventory


def _sha256_path(path: Path) -> str:
    with path.open("rb") as input_file:
        return _sha256_stream(input_file)


def _sha256_stream(input_file: Any) -> str:
    digest = hashlib.sha256()
    while chunk := input_file.read(1024 * 1024):
        digest.update(chunk)
    return digest.hexdigest()


def _summarize_names(names: Sequence[str]) -> str:
    preview = ", ".join(names[:3])
    if len(names) > 3:
        preview += f", ... ({len(names)} total)"
    return preview


def pinned_build_runtime_identity() -> BuildRuntimeIdentity:
    """Return the only runtime identity accepted for release generation."""

    return BuildRuntimeIdentity(
        python_implementation=PINNED_PYTHON_IMPLEMENTATION,
        python_version=PINNED_PYTHON_VERSION,
        sqlite_version=PINNED_SQLITE_VERSION,
        sqlite_source_id=PINNED_SQLITE_SOURCE_ID,
        sqlite_compile_options_sha256=PINNED_SQLITE_COMPILE_OPTIONS_SHA256,
        zlib_runtime_version=PINNED_ZLIB_RUNTIME_VERSION,
        jinja2_version=PINNED_JINJA2_VERSION,
        markupsafe_version=PINNED_MARKUPSAFE_VERSION,
        markdown_it_py_version=PINNED_MARKDOWN_IT_PY_VERSION,
        mdurl_version=PINNED_MDURL_VERSION,
    )


def current_build_runtime_identity() -> BuildRuntimeIdentity:
    """Inspect the Python, SQLite, and zlib components that write package bytes."""

    with sqlite3.connect(":memory:") as connection:
        source_id = connection.execute("SELECT sqlite_source_id()").fetchone()[0]
        compile_options = sorted(
            row[0] for row in connection.execute("PRAGMA compile_options")
        )
    compile_options_bytes = json.dumps(
        compile_options,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")
    try:
        dependency_versions = {
            "jinja2_version": distribution_version("Jinja2"),
            "markupsafe_version": distribution_version("MarkupSafe"),
            "markdown_it_py_version": distribution_version("markdown-it-py"),
            "mdurl_version": distribution_version("mdurl"),
        }
    except PackageNotFoundError as error:
        raise RuntimeError(f"missing pinned build dependency: {error.name}") from error
    return BuildRuntimeIdentity(
        python_implementation=platform.python_implementation(),
        python_version=platform.python_version(),
        sqlite_version=sqlite3.sqlite_version,
        sqlite_source_id=str(source_id),
        sqlite_compile_options_sha256=hashlib.sha256(compile_options_bytes).hexdigest(),
        zlib_runtime_version=zlib.ZLIB_RUNTIME_VERSION,
        **dependency_versions,
    )


def require_pinned_build_runtime(
    identity: BuildRuntimeIdentity | None = None,
) -> BuildRuntimeIdentity:
    """Fail closed unless every byte-affecting runtime component is pinned."""

    actual = identity or current_build_runtime_identity()
    expected = pinned_build_runtime_identity()
    if actual != expected:
        differences = [
            f"{field_name}={getattr(actual, field_name)!r} "
            f"(expected {getattr(expected, field_name)!r})"
            for field_name in expected.__dataclass_fields__
            if getattr(actual, field_name) != getattr(expected, field_name)
        ]
        raise RuntimeError("unpinned build runtime: " + "; ".join(differences))
    return actual


def build_inputs_sha256(root: Path | None = None) -> str:
    """Hash every tracked generator input as relative path plus exact bytes."""

    contribution_root = Path(root) if root is not None else CONTRIBUTION_ROOT
    inputs = _enumerate_build_inputs(contribution_root)
    digest = hashlib.sha256(b"arm-acle-build-inputs-v1\x00")
    for relative_path, path in inputs:
        path_bytes = relative_path.encode("utf-8")
        content = _read_build_input(path)
        digest.update(len(path_bytes).to_bytes(8, "big"))
        digest.update(path_bytes)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def _enumerate_build_inputs(root: Path) -> tuple[tuple[str, Path], ...]:
    _require_build_input_directory(root, ".")
    selected: dict[str, Path] = {}

    for relative in (
        ".python-version",
        "generate_docset.py",
        "generator/pyproject.toml",
        "generator/uv.lock",
        "icon.png",
        "icon@2x.png",
    ):
        path = root.joinpath(*PurePosixPath(relative).parts)
        _add_build_input(selected, root, path, required=True)

    groups = (
        ("generator/src", lambda relative: relative.endswith(".py")),
        ("generator/templates", lambda _relative: True),
        ("LICENSES", lambda _relative: True),
    )
    for relative_root, include in groups:
        directory = root.joinpath(*PurePosixPath(relative_root).parts)
        _require_build_input_directory(directory, relative_root)
        count_before = len(selected)
        _collect_build_inputs(selected, root, directory, include=include)
        if len(selected) == count_before:
            raise ValueError(f"build-input group is empty: {relative_root}")

    for relative in ("NOTICE.md",):
        path = root / relative
        _add_build_input(selected, root, path, required=True)

    return tuple((relative, selected[relative]) for relative in sorted(selected))


def _collect_build_inputs(
    selected: dict[str, Path],
    root: Path,
    directory: Path,
    *,
    include: Callable[[str], bool],
) -> None:
    with os.scandir(directory) as directory_entries:
        for entry in sorted(directory_entries, key=lambda item: item.name):
            path = Path(entry.path)
            metadata = entry.stat(follow_symlinks=False)
            relative = path.relative_to(root).as_posix()
            if stat.S_ISLNK(metadata.st_mode):
                raise ValueError(f"build input must not be a symlink: {relative}")
            if stat.S_ISDIR(metadata.st_mode):
                _collect_build_inputs(selected, root, path, include=include)
            elif include(relative):
                _add_build_input(selected, root, path, required=True)


def _require_build_input_directory(path: Path, label: str) -> None:
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError as error:
        raise ValueError(f"missing build-input directory: {label}") from error
    if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
        raise ValueError(f"build-input directory must be a real directory: {label}")


def _add_build_input(
    selected: dict[str, Path],
    root: Path,
    path: Path,
    *,
    required: bool,
) -> None:
    relative = path.relative_to(root).as_posix()
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError as error:
        if required:
            raise ValueError(f"missing build input: {relative}") from error
        return
    if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
        raise ValueError(f"build input must be a regular file: {relative}")
    selected[relative] = path


def _read_build_input(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ValueError(f"cannot open build input safely: {path}") from error
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError(f"build input must be a regular file: {path}")
        with os.fdopen(descriptor, "rb", closefd=False) as input_file:
            return input_file.read()
    finally:
        os.close(descriptor)


def source_manifest_sha256() -> str:
    """Hash the complete pinned source lock without host-specific paths."""

    from .sources.feature_flags import DEFAULT_FEATURE_FLAG_MANIFEST
    from .sources.manifest import LLVM_GENERATED_HEADERS, SOURCE_ARTIFACTS

    feature_sources = {}
    for mapping in DEFAULT_FEATURE_FLAG_MANIFEST:
        for source in mapping.sources:
            previous = feature_sources.setdefault(source.id, source)
            if previous != source:
                raise ValueError(
                    f"feature source id {source.id!r} refers to multiple locations"
                )

    payload = {
        "artifacts": [
            {
                "archive": artifact.archive,
                "cpu_profiles": list(artifact.cpu_profiles),
                "download_name": artifact.download_name,
                "kind": artifact.kind.value,
                "members": [
                    {
                        "archive_member": member.archive_member,
                        "local_path": member.local_path,
                        "sha256": member.sha256,
                    }
                    for member in sorted(
                        artifact.members, key=lambda item: item.local_path
                    )
                ],
                "optional": artifact.optional,
                "revision": artifact.revision,
                "sha256": artifact.sha256,
                "source_id": artifact.source_id,
                "url": artifact.url,
            }
            for artifact in sorted(SOURCE_ARTIFACTS, key=lambda item: item.source_id)
        ],
        "generated_headers": [
            {
                "local_path": member.local_path,
                "sha256": member.sha256,
            }
            for member in sorted(
                LLVM_GENERATED_HEADERS, key=lambda item: item.local_path
            )
        ],
        "feature_flag_sources": [
            {
                "commit": source.commit,
                "end_line": source.end_line,
                "id": source.id,
                "license_id": source.license_id,
                "path": source.path,
                "repository": source.repository,
                "start_line": source.start_line,
                "url": source.url,
            }
            for source in sorted(feature_sources.values(), key=lambda item: item.id)
        ],
        "schema_version": 2,
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _validate_index_targets(documents: Path, entries: Iterable[IndexEntry]) -> None:
    for entry in entries:
        if not entry.name.strip() or entry.name != entry.name.strip():
            raise ValueError(f"invalid search index name: {entry.name!r}")
        if not entry.type.strip() or entry.type != entry.type.strip():
            raise ValueError(f"invalid search index type: {entry.type!r}")
        if (
            "\n" in entry.name
            or "\r" in entry.name
            or "\n" in entry.path
            or "\r" in entry.path
        ):
            raise ValueError(f"search index entry contains a newline: {entry!r}")
        document_path, _, _anchor = entry.path.partition("#")
        safe_path = _safe_relative_path(document_path)
        if not documents.joinpath(*PurePosixPath(safe_path).parts).is_file():
            raise ValueError(f"search index target does not exist: {entry.path}")


def _coerce_index_entry(value: Any) -> IndexEntry:
    if isinstance(value, IndexEntry):
        return value
    if isinstance(value, tuple) and len(value) == 3:
        return IndexEntry(str(value[0]), str(value[1]), str(value[2]))
    entry_type = getattr(value, "type", getattr(value, "entry_type", None))
    return IndexEntry(
        name=str(getattr(value, "name")),
        type=str(entry_type),
        path=str(getattr(value, "path")),
    )


def _safe_relative_path(value: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise ValueError(f"unsafe relative path: {value}")
    return path.as_posix()


def _is_lowercase_sha256(value: str) -> bool:
    return len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


def _is_lowercase_sha1(value: str) -> bool:
    return len(value) == 40 and all(
        character in "0123456789abcdef" for character in value
    )
