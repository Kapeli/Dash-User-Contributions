"""Reproducible, content-addressed inputs for the docset build.

Every network input is pinned by an immutable upstream revision and SHA-256.
Callers may either populate the cache through :func:`fetch_sources` or provide
an offline tree with the same ``local_path`` layout.

The protected access-policy property is that every cache and snapshot object
is owned by the current user and grants no write-class permission to any
non-owner principal, through either mode bits or an extended ACL. Object
identity and content stability are checked separately: only device/inode
changes mean replacement, and only SHA-256 changes mean content mutation.
The boundary does not claim isolation from a malicious same-UID process, which
already has equivalent access to the generator and build output.
"""

from __future__ import annotations

import ctypes
import errno
import hashlib
import os
import secrets
import stat
import sys
import tarfile
import urllib.error
import urllib.request
from contextlib import contextmanager
from dataclasses import dataclass
from enum import StrEnum
from functools import cache
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import IO, Iterable, Iterator, Mapping, Sequence


ACLE_REVISION = "62d9cbd68abb6d18dd8f06980da7758d9dbe0560"
LLVM_TAG = "llvmorg-22.1.1"
LLVM_COMMIT = "fef02d48c08db859ef83f84232ed78bd9d1c323a"
GCC_COMMIT = "fcfb06e236d4d1689a6caf8e5409b078262af481"


def _validate_relative_path(value: str, label: str) -> None:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise ValueError(f"{label} must be a safe relative POSIX path: {value}")


def _validate_sha256(value: str, label: str) -> None:
    if len(value) != 64 or any(
        character not in "0123456789abcdef" for character in value
    ):
        raise ValueError(f"{label} must be a lowercase hexadecimal SHA-256")


class ManifestError(RuntimeError):
    """Raised when a source is absent, corrupt, or unsafe to extract."""


class SourceMissingError(ManifestError):
    """Raised when a required source path does not exist."""


class SourceUnreadableError(ManifestError):
    """Raised when a required source exists but cannot be read safely."""


class SourceDigestMismatchError(ManifestError):
    """Raised when bytes read from a source do not match the manifest."""


class SourceAccessPolicyError(ManifestError):
    """Raised when cache ownership, permissions, or path shape is unsafe."""


class SourceMaterializationError(ManifestError):
    """Raised when verified bytes cannot be committed to a private snapshot."""


class SnapshotCleanupError(ManifestError):
    """Raised when the private snapshot path no longer names its original object."""


class SourceKind(StrEnum):
    """Role of a source in the conversion pipeline."""

    SPECIFICATION = "specification"
    CATALOG = "catalog"
    DECLARATIONS = "declarations"
    VALIDATION = "validation"
    PERFORMANCE = "performance"


@dataclass(frozen=True, slots=True)
class SourceMember:
    """One verified file supplied by a raw artifact or archive member."""

    local_path: str
    sha256: str
    archive_member: str | None = None

    def __post_init__(self) -> None:
        _validate_relative_path(self.local_path, "local_path")
        if self.archive_member is not None:
            _validate_relative_path(self.archive_member, "archive_member")
        _validate_sha256(self.sha256, f"SHA-256 for {self.local_path}")


@dataclass(frozen=True, slots=True)
class SourceArtifact:
    """An immutable upstream download and the files consumed from it."""

    source_id: str
    kind: SourceKind
    url: str
    revision: str
    sha256: str
    members: tuple[SourceMember, ...]
    archive: bool = False
    optional: bool = False
    cpu_profiles: tuple[str, ...] = ()
    download_name: str | None = None

    def __post_init__(self) -> None:
        if not self.source_id or any(char.isspace() for char in self.source_id):
            raise ValueError("source_id must be non-empty and contain no whitespace")
        if not self.url.startswith("https://"):
            raise ValueError(f"source URL must use HTTPS: {self.url}")
        if not self.revision:
            raise ValueError(f"source revision is required: {self.source_id}")
        _validate_sha256(self.sha256, f"artifact SHA-256 for {self.source_id}")
        if not self.members:
            raise ValueError(
                f"source must declare at least one member: {self.source_id}"
            )
        if self.archive and any(
            member.archive_member is None for member in self.members
        ):
            raise ValueError(
                f"archive source members need archive_member: {self.source_id}"
            )
        if not self.archive and len(self.members) != 1:
            raise ValueError(
                f"raw source must contain exactly one member: {self.source_id}"
            )
        if self.kind is not SourceKind.PERFORMANCE and self.cpu_profiles:
            raise ValueError("cpu_profiles are only valid for performance sources")
        filename = self.filename
        _validate_relative_path(filename, "download filename")
        if len(PurePosixPath(filename).parts) != 1:
            raise ValueError(f"download filename must be a basename: {filename}")

    @property
    def filename(self) -> str:
        if self.download_name:
            return self.download_name
        return self.url.rsplit("/", 1)[-1]


def _raw_acle_artifact(
    source_id: str,
    upstream_path: str,
    sha256: str,
    *,
    kind: SourceKind,
) -> SourceArtifact:
    return SourceArtifact(
        source_id=source_id,
        kind=kind,
        url=(
            "https://raw.githubusercontent.com/ARM-software/acle/"
            f"{ACLE_REVISION}/{upstream_path}"
        ),
        revision=ACLE_REVISION,
        sha256=sha256,
        members=(
            SourceMember(
                local_path=f"acle/{upstream_path}",
                sha256=sha256,
            ),
        ),
    )


def _raw_llvm_tablegen_artifact(filename: str, sha256: str) -> SourceArtifact:
    upstream_path = f"clang/include/clang/Basic/{filename}"
    return SourceArtifact(
        source_id=f"llvm-{filename.removesuffix('.td').replace('_', '-')}",
        kind=SourceKind.DECLARATIONS,
        url=(
            "https://raw.githubusercontent.com/llvm/llvm-project/"
            f"{LLVM_COMMIT}/{upstream_path}"
        ),
        revision=f"{LLVM_TAG}@{LLVM_COMMIT}",
        sha256=sha256,
        members=(
            SourceMember(
                local_path=f"llvm/td/{filename}",
                sha256=sha256,
            ),
        ),
    )


def _raw_gcc_validation_artifact(
    source_id: str,
    upstream_path: str,
    sha256: str,
) -> SourceArtifact:
    """Describe a GCC testsuite sample used only during catalog validation."""

    return SourceArtifact(
        source_id=source_id,
        kind=SourceKind.VALIDATION,
        url=(
            "https://raw.githubusercontent.com/gcc-mirror/gcc/"
            f"{GCC_COMMIT}/{upstream_path}"
        ),
        revision=GCC_COMMIT,
        sha256=sha256,
        members=(
            SourceMember(
                local_path=f"gcc/{upstream_path.removeprefix('gcc/')}",
                sha256=sha256,
            ),
        ),
    )


SOURCE_ARTIFACTS: tuple[SourceArtifact, ...] = (
    _raw_acle_artifact(
        "acle-main",
        "main/acle.md",
        "d9b4fe6d25f2e61554ef7ba4a5953cfa91a387fd3d8746d484c396badfba387d",
        kind=SourceKind.SPECIFICATION,
    ),
    _raw_acle_artifact(
        "acle-advsimd",
        "tools/intrinsic_db/advsimd.csv",
        "0735e2da918e48ab9a917c94a5756d2a47e7d33d46cce2e235d41af6ba2c46d3",
        kind=SourceKind.CATALOG,
    ),
    _raw_acle_artifact(
        "acle-advsimd-classification",
        "tools/intrinsic_db/advsimd_classification.csv",
        "ee277f88dd59c95ac2ecf00868dadbf0155f918097f05d6960bd1bb43939bc27",
        kind=SourceKind.CATALOG,
    ),
    _raw_acle_artifact(
        "acle-mve",
        "tools/intrinsic_db/mve.csv",
        "9562e3893d2bfe70af0ea082f35f837698f27bd2e778123fdde0f2c194ec29a9",
        kind=SourceKind.CATALOG,
    ),
    _raw_acle_artifact(
        "acle-mve-classification",
        "tools/intrinsic_db/mve_classification.csv",
        "3cedaddc5fa0fb575cd4b15bad5769b4136408aecdf8d17e976aad39b3e0dd7f",
        kind=SourceKind.CATALOG,
    ),
    _raw_llvm_tablegen_artifact(
        "arm_immcheck_incl.td",
        "e9d8ac9d002b086ed38d9ad02843697cb8db29f310ae6f42e1fcde3b376ee8f4",
    ),
    _raw_llvm_tablegen_artifact(
        "arm_neon.td",
        "ce3de834be74f8292170f4bb5f83d1b3819414c7bee64a326a770be4e53ee71d",
    ),
    _raw_llvm_tablegen_artifact(
        "arm_neon_incl.td",
        "4e353a31b57e35a5126fd793374630b9f28a41a1980747d875c94604e7129034",
    ),
    _raw_llvm_tablegen_artifact(
        "arm_mve.td",
        "4bd80806e6edbc0c8ee24dd7eef07fb664bed153fa0f06e9ce7bf15a572aca99",
    ),
    _raw_llvm_tablegen_artifact(
        "arm_mve_defs.td",
        "e70efc2d815c754005a1a033c91dd8107b457fb1561761ef248598440c43e9f7",
    ),
    _raw_llvm_tablegen_artifact(
        "arm_sve.td",
        "16d0424f7bbb04ab0e4635623422325fa7ac0a8040adf3ef6fa571651b7f70c5",
    ),
    _raw_llvm_tablegen_artifact(
        "arm_sme.td",
        "c953db7c1f7c7de5b1dddc5efd1bb28e038802733e9f5655c8737eab85228fdf",
    ),
    _raw_llvm_tablegen_artifact(
        "arm_sve_sme_incl.td",
        "27bc8d5e78615404d564301eeb2fb9da5565c146e54259f70757fc2314fb14cd",
    ),
    _raw_gcc_validation_artifact(
        "gcc-neon-vaddh-f16",
        "gcc/testsuite/gcc.target/aarch64/advsimd-intrinsics/vaddh_f16_1.c",
        "8269153dab7cc892b4ff11f077ca42c657c25946a909a770d5699cd4fdd8453b",
    ),
    _raw_gcc_validation_artifact(
        "gcc-mve-vaddq-s32",
        "gcc/testsuite/gcc.target/arm/mve/intrinsics/vaddq_s32.c",
        "33e49ed0dae80d12dcc761eac89f00fbd6c8dc762e509bc1f3b3aa29d5b6a608",
    ),
    _raw_gcc_validation_artifact(
        "gcc-sve-add-s32",
        "gcc/testsuite/gcc.target/aarch64/sve/acle/asm/add_s32.c",
        "d60b623487495c2e7432f02d26b3f8571748c0b9e439c8c59dc803be6c51b54e",
    ),
    _raw_gcc_validation_artifact(
        "gcc-sme-mopa-za32",
        "gcc/testsuite/gcc.target/aarch64/sme/acle-asm/mopa_za32.c",
        "47466a41da1ccc92df2b1f8e3f15f92b3e69cee7d7d288dba25d4616d3f639b2",
    ),
)

# clang-tblgen 22.1.1 deterministically produces these declaration inputs from
# the pinned TableGen artifacts above. They are verified before any adapter is
# allowed to consume the generated include directory.
LLVM_GENERATED_HEADERS: tuple[SourceMember, ...] = (
    SourceMember(
        local_path="llvm/generated/include/arm_sve.h",
        sha256="52c7dd2eb8ddb280ce24d041a6504d1d5937cc46a288ec78c0041d14ec71ce72",
    ),
    SourceMember(
        local_path="llvm/generated/include/arm_sme.h",
        sha256="0dae22d987ada9594b197285e1f1528b1c51eafd4579345d2949367c3e788943",
    ),
    SourceMember(
        local_path="llvm/generated/include/arm_mve.h",
        sha256="8e6fa1bb91c0e5403e6f6152380b4ff318833028b0d4e9c91911e4dd107bd762",
    ),
    SourceMember(
        local_path="llvm/generated/include/arm_neon.h",
        sha256="ed8fc4135aef7c5af5f30ca3715d96ee9ad5a2bc97f558214fadda5704742b26",
    ),
)


def select_artifacts(
    artifacts: Sequence[SourceArtifact] = SOURCE_ARTIFACTS,
    *,
    include_optional: bool = False,
    cpu_profiles: Iterable[str] = (),
) -> tuple[SourceArtifact, ...]:
    """Select mandatory sources and matching optional performance profiles."""

    requested_profiles = frozenset(cpu_profiles)
    known_profiles = {
        profile
        for artifact in artifacts
        if artifact.kind is SourceKind.PERFORMANCE
        for profile in artifact.cpu_profiles
    }
    unknown = requested_profiles - known_profiles
    if unknown:
        raise ManifestError(f"unknown CPU profile(s): {', '.join(sorted(unknown))}")

    selected: list[SourceArtifact] = []
    for artifact in artifacts:
        if not artifact.optional:
            selected.append(artifact)
            continue
        if include_optional:
            selected.append(artifact)
            continue
        if artifact.kind is SourceKind.PERFORMANCE and requested_profiles.intersection(
            artifact.cpu_profiles
        ):
            selected.append(artifact)
    return tuple(selected)


def resolve_sources(
    cache_dir: Path,
    *,
    source_dir: Path | None = None,
    offline: bool = False,
    artifacts: Sequence[SourceArtifact] = SOURCE_ARTIFACTS,
    include_optional: bool = False,
    cpu_profiles: Iterable[str] = (),
) -> Mapping[str, Path]:
    """Return verified cache paths, fetching missing entries if allowed.

    This compatibility API does not pin the returned files after verification.
    Build callers must use :func:`resolved_source_snapshot` so every consumed
    byte comes from the immutable, verified snapshot yielded by that context.
    """

    selected = select_artifacts(
        artifacts,
        include_optional=include_optional,
        cpu_profiles=cpu_profiles,
    )
    root = Path(source_dir) if source_dir is not None else Path(cache_dir)
    if source_dir is None:
        fetch_sources(
            root,
            offline=offline,
            artifacts=selected,
        )
    elif not root.is_dir():
        raise ManifestError(f"offline source directory does not exist: {root}")
    return verify_source_tree(root, artifacts=selected)


def fetch_sources(
    cache_dir: Path,
    *,
    offline: bool = False,
    artifacts: Sequence[SourceArtifact] = SOURCE_ARTIFACTS,
) -> Mapping[str, Path]:
    """Populate and verify a private cache without following path links."""

    root_path = _absolute_path(cache_dir)
    with _open_secure_root(
        root_path,
        create=True,
        repair_permissions=True,
    ) as root:
        for artifact in artifacts:
            if _artifact_members_valid(root, artifact):
                continue
            if offline:
                _verify_source_tree(root, artifacts=(artifact,))
                raise AssertionError("invalid source unexpectedly passed verification")
            _fetch_artifact(root, artifact)
        return _verify_source_tree(root, artifacts=artifacts)


def verify_source_tree(
    root: Path,
    *,
    artifacts: Sequence[SourceArtifact] = SOURCE_ARTIFACTS,
) -> Mapping[str, Path]:
    """Verify selected files and return their current cache paths.

    The check distinguishes a missing source, an unreadable source, a digest
    mismatch, and an access-policy violation. The mapping is useful for fetch
    diagnostics only; it deliberately offers no content-stability guarantee.
    Use :func:`verified_source_snapshot` before a build consumes source bytes.
    """

    root_path = _absolute_path(root)
    with _open_secure_root(
        root_path,
        create=False,
        repair_permissions=False,
    ) as secure_root:
        return _verify_source_tree(secure_root, artifacts=artifacts)


@contextmanager
def verified_source_snapshot(
    source_root: Path,
    *,
    snapshot_parent: Path | None = None,
    artifacts: Sequence[SourceArtifact] = SOURCE_ARTIFACTS,
) -> Iterator[Mapping[str, Path]]:
    """Yield a private snapshot containing the exact bytes that were verified.

    Each manifest member is opened without following links, then that same file
    descriptor is hashed while its bytes are copied. The build therefore never
    reopens a cache pathname after verification. Replacing or modifying cache
    entries after this context yields cannot change the snapshot. The threat
    boundary covers other UIDs and ordinary concurrent cache updates. A
    malicious process with the same UID can also modify the generator and build
    output and is intentionally outside this isolation claim.

    By default the random snapshot is created inside ``source_root``. Callers
    that supply a separate read-only source tree must pass their private cache
    root as ``snapshot_parent``.
    """

    root_path = _absolute_path(source_root)
    with _open_secure_root(
        root_path,
        create=False,
        repair_permissions=False,
    ) as opened_source_root:
        snapshot_parent_path = _absolute_path(
            root_path if snapshot_parent is None else snapshot_parent
        )
        with _open_secure_root(
            snapshot_parent_path,
            create=True,
            repair_permissions=True,
        ) as opened_snapshot_parent:
            with _private_snapshot_root(opened_snapshot_parent) as snapshot_root:
                resolved: dict[str, Path] = {}
                for artifact in artifacts:
                    for member in artifact.members:
                        source_fd = _open_source_fd(
                            opened_source_root,
                            member.local_path,
                        )
                        with os.fdopen(source_fd, "rb") as source:
                            _atomic_write_from_reader(
                                snapshot_root,
                                member.local_path,
                                source,
                                member.sha256,
                                digest_label=str(
                                    opened_source_root.path / member.local_path
                                ),
                            )
                        resolved[member.local_path] = (
                            snapshot_root.path / member.local_path
                        )
                _seal_snapshot(snapshot_root, tuple(resolved))
                yield MappingProxyType(resolved)


@contextmanager
def resolved_source_snapshot(
    cache_dir: Path,
    *,
    source_dir: Path | None = None,
    offline: bool = False,
    artifacts: Sequence[SourceArtifact] = SOURCE_ARTIFACTS,
    include_optional: bool = False,
    cpu_profiles: Iterable[str] = (),
) -> Iterator[Mapping[str, Path]]:
    """Fetch selected inputs if needed, then yield a verified byte snapshot."""

    selected = select_artifacts(
        artifacts,
        include_optional=include_optional,
        cpu_profiles=cpu_profiles,
    )
    root = Path(source_dir) if source_dir is not None else Path(cache_dir)
    if source_dir is None:
        fetch_sources(root, offline=offline, artifacts=selected)
    with verified_source_snapshot(
        root,
        snapshot_parent=Path(cache_dir),
        artifacts=selected,
    ) as resolved:
        yield resolved


@dataclass(frozen=True, slots=True)
class _SecureRoot:
    """An opened directory that pins the caller-selected cache object."""

    path: Path
    fd: int
    repair_permissions: bool


_DIRECTORY_OPEN_FLAGS = (
    os.O_RDONLY
    | getattr(os, "O_CLOEXEC", 0)
    | getattr(os, "O_DIRECTORY", 0)
    | getattr(os, "O_NOFOLLOW", 0)
)
_FILE_OPEN_FLAGS = (
    os.O_RDONLY
    | getattr(os, "O_CLOEXEC", 0)
    | getattr(os, "O_NONBLOCK", 0)
    | getattr(os, "O_NOFOLLOW", 0)
)


def _absolute_path(path: Path) -> Path:
    absolute = Path(os.path.abspath(os.fspath(path)))
    if absolute == Path(absolute.anchor):
        raise SourceAccessPolicyError(
            f"source cache root cannot be a filesystem root: {absolute}"
        )
    return absolute


def _require_secure_path_support() -> None:
    required_dir_fd_functions = (os.open, os.mkdir, os.rename, os.stat, os.unlink)
    required_open_flags = (
        getattr(os, "O_DIRECTORY", 0),
        getattr(os, "O_NONBLOCK", 0),
        getattr(os, "O_NOFOLLOW", 0),
    )
    if not all(required_open_flags) or any(
        function not in os.supports_dir_fd for function in required_dir_fd_functions
    ):
        raise SourceAccessPolicyError(
            "this platform lacks the no-follow dirfd operations required for a "
            "secure source cache"
        )


def _current_uid() -> int | None:
    getter = getattr(os, "geteuid", None) or getattr(os, "getuid", None)
    return getter() if getter is not None else None


def _validate_owner(metadata: os.stat_result, label: str) -> None:
    current_uid = _current_uid()
    file_uid = getattr(metadata, "st_uid", None)
    if current_uid is not None and file_uid is not None and file_uid != current_uid:
        raise SourceAccessPolicyError(
            f"{label} is not owned by the current user: owner {file_uid}, "
            f"expected {current_uid}"
        )


def _object_identity(metadata: os.stat_result) -> tuple[int, int]:
    """Return only the signals that identify a filesystem object."""

    return metadata.st_dev, metadata.st_ino


_DARWIN_ACL_TYPE_EXTENDED = 0x00000100
_DARWIN_ACL_FIRST_ENTRY = 0
_DARWIN_ACL_NEXT_ENTRY = -1
_DARWIN_ACL_EXTENDED_ALLOW = 1
# These rights can mutate content, directory entries, object metadata, or the
# access policy itself. Read-only and synchronization rights do not threaten
# the protected property: no non-owner principal may write the cache object.
_DARWIN_ACL_WRITE_RIGHTS = (
    (1 << 2)  # write data / add file
    | (1 << 4)  # delete
    | (1 << 5)  # append data / add subdirectory
    | (1 << 6)  # delete child
    | (1 << 8)  # write attributes
    | (1 << 10)  # write extended attributes
    | (1 << 12)  # write security, including the ACL
    | (1 << 13)  # change owner
)


@cache
def _darwin_acl_library() -> ctypes.CDLL | None:
    """Return the descriptor-based Darwin ACL API, if this is Darwin."""

    if sys.platform != "darwin":
        return None
    library = ctypes.CDLL(None, use_errno=True)
    try:
        library.acl_get_fd_np.argtypes = (ctypes.c_int, ctypes.c_int)
        library.acl_get_fd_np.restype = ctypes.c_void_p
        library.acl_get_entry.argtypes = (
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_void_p),
        )
        library.acl_get_entry.restype = ctypes.c_int
        library.acl_get_tag_type.argtypes = (
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_int),
        )
        library.acl_get_tag_type.restype = ctypes.c_int
        library.acl_get_permset_mask_np.argtypes = (
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint64),
        )
        library.acl_get_permset_mask_np.restype = ctypes.c_int
        library.acl_get_qualifier.argtypes = (ctypes.c_void_p,)
        library.acl_get_qualifier.restype = ctypes.c_void_p
        library.acl_free.argtypes = (ctypes.c_void_p,)
        library.acl_free.restype = ctypes.c_int
        library.mbr_uid_to_uuid.argtypes = (
            ctypes.c_uint,
            ctypes.POINTER(ctypes.c_ubyte),
        )
        library.mbr_uid_to_uuid.restype = ctypes.c_int
    except AttributeError as error:
        raise SourceAccessPolicyError(
            "Darwin ACL APIs are unavailable; extended access policy cannot "
            "be validated"
        ) from error
    return library


def _darwin_acl_error(operation: str) -> OSError:
    error_number = ctypes.get_errno() or errno.EIO
    return OSError(error_number, f"{operation}: {os.strerror(error_number)}")


def _darwin_acl_grants_nonowner_write(fd: int, owner_uid: int | None) -> bool:
    """Return whether a Darwin extended ACL contains an external write grant.

    Qualifiers are stable UUIDs. Comparing an allow entry's UUID only with the
    object's owner UUID identifies the one principal exempt from this policy;
    groups, everyone, and every other user remain non-owner principals. A deny
    entry never grants access, so it is intentionally not considered.
    """

    library = _darwin_acl_library()
    if library is None:
        # POSIX access ACL write grants are reflected in the group-class mode
        # mask checked by callers. Darwin extended ACL grants are not, so only
        # Darwin needs this additional descriptor-based inspection.
        return False

    owner_uuid: bytes | None = None
    if owner_uid is not None:
        owner_buffer = (ctypes.c_ubyte * 16)()
        error_number = library.mbr_uid_to_uuid(owner_uid, owner_buffer)
        if error_number != 0:
            raise OSError(
                error_number,
                f"could not resolve owner UUID: {os.strerror(error_number)}",
            )
        owner_uuid = bytes(owner_buffer)

    ctypes.set_errno(0)
    acl = library.acl_get_fd_np(fd, _DARWIN_ACL_TYPE_EXTENDED)
    if not acl:
        error_number = ctypes.get_errno()
        if error_number in {errno.ENOENT, errno.EOPNOTSUPP}:
            # Darwin reports ENOENT when an existing descriptor has no
            # extended ACL; EOPNOTSUPP means the filesystem cannot store one.
            return False
        raise _darwin_acl_error("could not read extended ACL")

    try:
        entry = ctypes.c_void_p()
        entry_id = _DARWIN_ACL_FIRST_ENTRY
        while True:
            ctypes.set_errno(0)
            result = library.acl_get_entry(acl, entry_id, ctypes.byref(entry))
            if result != 0:
                if (
                    entry_id == _DARWIN_ACL_NEXT_ENTRY
                    and ctypes.get_errno() == errno.EINVAL
                ):
                    return False
                raise _darwin_acl_error("could not enumerate extended ACL")

            tag = ctypes.c_int()
            ctypes.set_errno(0)
            if library.acl_get_tag_type(entry, ctypes.byref(tag)) != 0:
                raise _darwin_acl_error("could not read extended ACL tag")
            if tag.value == _DARWIN_ACL_EXTENDED_ALLOW:
                permissions = ctypes.c_uint64()
                ctypes.set_errno(0)
                if (
                    library.acl_get_permset_mask_np(
                        entry,
                        ctypes.byref(permissions),
                    )
                    != 0
                ):
                    raise _darwin_acl_error("could not read extended ACL permissions")
                if permissions.value & _DARWIN_ACL_WRITE_RIGHTS:
                    ctypes.set_errno(0)
                    qualifier = library.acl_get_qualifier(entry)
                    if not qualifier:
                        raise _darwin_acl_error("could not read extended ACL qualifier")
                    try:
                        if (
                            owner_uuid is None
                            or ctypes.string_at(qualifier, 16) != owner_uuid
                        ):
                            return True
                    finally:
                        library.acl_free(qualifier)
            entry_id = _DARWIN_ACL_NEXT_ENTRY
    finally:
        library.acl_free(acl)


def _validate_extended_acl(
    fd: int,
    owner_uid: int | None,
    label: str,
) -> None:
    """Enforce the cache access policy without reopening a pathname."""

    try:
        grants_write = _darwin_acl_grants_nonowner_write(fd, owner_uid)
    except OSError as error:
        raise SourceAccessPolicyError(
            f"could not inspect source access policy safely: {label}: {error}"
        ) from error
    if grants_write:
        raise SourceAccessPolicyError(
            f"extended ACL grants non-owner write access: {label}"
        )


def _validate_directory(
    fd: int,
    label: str,
    *,
    repair_permissions: bool,
) -> None:
    metadata = os.fstat(fd)
    if not stat.S_ISDIR(metadata.st_mode):
        raise SourceAccessPolicyError(
            f"source path component is not a directory: {label}"
        )
    _validate_owner(metadata, label)
    if repair_permissions:
        os.fchmod(fd, 0o700)
        metadata = os.fstat(fd)
    mode = stat.S_IMODE(metadata.st_mode)
    if mode & stat.S_IRUSR == 0 or mode & stat.S_IXUSR == 0:
        raise SourceUnreadableError(f"source directory is unreadable: {label}")
    allowed_modes = {0o700} if repair_permissions else {0o500, 0o700}
    if mode not in allowed_modes:
        raise SourceAccessPolicyError(
            "source directory permissions must be 0700 or read-only 0500: "
            f"{label} has {mode:04o}"
        )
    _validate_extended_acl(fd, getattr(metadata, "st_uid", None), label)


def _validate_ancestor_directory(fd: int, label: str) -> None:
    """Reject ancestors another UID could use to replace a protected path."""

    metadata = os.fstat(fd)
    if not stat.S_ISDIR(metadata.st_mode):
        raise SourceAccessPolicyError(
            f"source path ancestor is not a directory: {label}"
        )
    current_uid = _current_uid()
    owner_uid = getattr(metadata, "st_uid", None)
    trusted_owners = {0}
    if current_uid is not None:
        trusted_owners.add(current_uid)
    if owner_uid is not None and owner_uid not in trusted_owners:
        raise SourceAccessPolicyError(
            "source path ancestor is owned by an untrusted UID: "
            f"{label} owner {owner_uid}"
        )
    mode = stat.S_IMODE(metadata.st_mode)
    if mode & 0o022 and not metadata.st_mode & stat.S_ISVTX:
        raise SourceAccessPolicyError(
            "group/world-writable source path ancestor lacks the sticky bit: "
            f"{label} has {mode:04o}"
        )
    _validate_extended_acl(fd, owner_uid, label)


@contextmanager
def _open_secure_root(
    path: Path,
    *,
    create: bool,
    repair_permissions: bool,
) -> Iterator[_SecureRoot]:
    _require_secure_path_support()
    anchor = Path(path.anchor)
    parts = path.parts[1:]
    current_fd = os.open(anchor, _DIRECTORY_OPEN_FLAGS)
    try:
        _validate_ancestor_directory(current_fd, str(anchor))
        for index, part in enumerate(parts):
            try:
                next_fd = os.open(part, _DIRECTORY_OPEN_FLAGS, dir_fd=current_fd)
            except FileNotFoundError as error:
                if not create:
                    raise SourceMissingError(
                        f"missing source directory: {path}"
                    ) from error
                if index != len(parts) - 1:
                    raise SourceMissingError(
                        f"cache root parent does not exist: {path.parent}"
                    ) from error
                try:
                    os.mkdir(part, mode=0o700, dir_fd=current_fd)
                    next_fd = os.open(
                        part,
                        _DIRECTORY_OPEN_FLAGS,
                        dir_fd=current_fd,
                    )
                except OSError as create_error:
                    raise _classify_directory_error(
                        path,
                        create_error,
                        creating=True,
                    ) from create_error
            except OSError as error:
                raise _classify_directory_error(path, error) from error
            os.close(current_fd)
            current_fd = next_fd
            if index == len(parts) - 1:
                _validate_directory(
                    current_fd,
                    str(path),
                    repair_permissions=repair_permissions,
                )
            else:
                _validate_ancestor_directory(
                    current_fd,
                    str(Path(path.anchor, *parts[: index + 1])),
                )
        yield _SecureRoot(path, current_fd, repair_permissions)
    finally:
        os.close(current_fd)


def _classify_directory_error(
    path: Path,
    error: OSError,
    *,
    creating: bool = False,
) -> ManifestError:
    if creating and error.errno in {
        errno.EDQUOT,
        errno.EIO,
        errno.ENOSPC,
        errno.EROFS,
    }:
        return SourceMaterializationError(
            f"failed to create private source path {path}: {error}"
        )
    if isinstance(error, PermissionError):
        return SourceUnreadableError(f"source directory is unreadable: {path}")
    if error.errno in {errno.ELOOP, errno.ENOTDIR}:
        return SourceAccessPolicyError(
            f"source directory contains a symlink or non-directory component: {path}"
        )
    return SourceAccessPolicyError(
        f"could not safely open source directory {path}: {error}"
    )


def _relative_parts(value: str) -> tuple[str, ...]:
    _validate_relative_path(value, "source path")
    return PurePosixPath(value).parts


def _open_relative_directory(
    root: _SecureRoot,
    parts: Sequence[str],
    *,
    create: bool,
) -> int:
    current_fd = os.dup(root.fd)
    current_label = root.path
    try:
        for part in parts:
            current_label /= part
            try:
                next_fd = os.open(part, _DIRECTORY_OPEN_FLAGS, dir_fd=current_fd)
            except FileNotFoundError as error:
                if not create:
                    raise SourceMissingError(
                        f"missing source directory: {current_label}"
                    ) from error
                try:
                    os.mkdir(part, mode=0o700, dir_fd=current_fd)
                    next_fd = os.open(
                        part,
                        _DIRECTORY_OPEN_FLAGS,
                        dir_fd=current_fd,
                    )
                except OSError as create_error:
                    raise _classify_directory_error(
                        current_label,
                        create_error,
                        creating=True,
                    ) from create_error
            except OSError as error:
                raise _classify_directory_error(current_label, error) from error
            os.close(current_fd)
            current_fd = next_fd
            _validate_directory(
                current_fd,
                str(current_label),
                repair_permissions=root.repair_permissions,
            )
        return current_fd
    except Exception:
        os.close(current_fd)
        raise


def _validate_source_file(metadata: os.stat_result, label: str) -> None:
    if stat.S_ISLNK(metadata.st_mode):
        raise SourceAccessPolicyError(f"source path is a symlink: {label}")
    if not stat.S_ISREG(metadata.st_mode):
        raise SourceAccessPolicyError(f"source path is not a regular file: {label}")
    _validate_owner(metadata, label)
    mode = stat.S_IMODE(metadata.st_mode)
    if mode & stat.S_IRUSR == 0:
        raise SourceUnreadableError(f"unreadable source file: {label}")
    if mode & 0o022:
        raise SourceAccessPolicyError(
            f"source file permissions allow non-owner writes: {label} has {mode:04o}"
        )


def _source_open_race_hook(parent_fd: int, name: str) -> None:
    """Test hook for a replacement between leaf inspection and open."""


def _open_source_fd(root: _SecureRoot, relative_path: str) -> int:
    parts = _relative_parts(relative_path)
    parent_fd = _open_relative_directory(root, parts[:-1], create=False)
    label = str(root.path / relative_path)
    try:
        try:
            before_open = os.stat(
                parts[-1],
                dir_fd=parent_fd,
                follow_symlinks=False,
            )
        except FileNotFoundError as error:
            raise SourceMissingError(f"missing source file: {label}") from error
        except PermissionError as error:
            raise SourceUnreadableError(f"unreadable source file: {label}") from error
        except OSError as error:
            raise SourceAccessPolicyError(
                f"could not inspect source file safely: {label}: {error}"
            ) from error
        _validate_source_file(before_open, label)
        _source_open_race_hook(parent_fd, parts[-1])

        try:
            source_fd = os.open(parts[-1], _FILE_OPEN_FLAGS, dir_fd=parent_fd)
        except FileNotFoundError as error:
            raise SourceMissingError(f"missing source file: {label}") from error
        except PermissionError as error:
            raise SourceUnreadableError(f"unreadable source file: {label}") from error
        except OSError as error:
            if error.errno in {errno.ELOOP, errno.ENOTDIR}:
                raise SourceAccessPolicyError(
                    f"source file is a symlink or has an unsafe parent: {label}"
                ) from error
            raise SourceUnreadableError(
                f"could not safely read source file {label}: {error}"
            ) from error
        try:
            after_open = os.fstat(source_fd)
            _validate_source_file(after_open, label)
            if _object_identity(after_open) != _object_identity(before_open):
                raise SourceAccessPolicyError(
                    f"source file was replaced while being opened: {label}"
                )
            _validate_extended_acl(
                source_fd,
                getattr(after_open, "st_uid", None),
                label,
            )
        except Exception:
            os.close(source_fd)
            raise
        return source_fd
    finally:
        os.close(parent_fd)


def _verify_source_tree(
    root: _SecureRoot,
    *,
    artifacts: Sequence[SourceArtifact],
) -> Mapping[str, Path]:
    resolved: dict[str, Path] = {}
    for artifact in artifacts:
        for member in artifact.members:
            actual = _sha256_source(root, member.local_path)
            path = root.path / member.local_path
            if actual != member.sha256:
                raise SourceDigestMismatchError(
                    f"SHA-256 mismatch for {path}: expected {member.sha256}, got {actual}"
                )
            resolved[member.local_path] = path
    return MappingProxyType(resolved)


def _create_private_snapshot_root(
    parent: _SecureRoot,
) -> tuple[_SecureRoot, str, tuple[int, int]]:
    for _attempt in range(128):
        name = f".arm-acle-source-snapshot-{secrets.token_hex(16)}"
        try:
            os.mkdir(name, mode=0o700, dir_fd=parent.fd)
        except FileExistsError:
            continue
        except OSError as error:
            raise SourceMaterializationError(
                f"failed to create private source snapshot in {parent.path}: {error}"
            ) from error

        snapshot_fd: int | None = None
        expected_identity: tuple[int, int] | None = None
        try:
            before_open = os.stat(name, dir_fd=parent.fd, follow_symlinks=False)
            if not stat.S_ISDIR(before_open.st_mode):
                raise SourceAccessPolicyError(
                    f"new source snapshot is not a directory: {parent.path / name}"
                )
            _validate_owner(before_open, str(parent.path / name))
            expected_identity = _object_identity(before_open)
            snapshot_fd = os.open(name, _DIRECTORY_OPEN_FLAGS, dir_fd=parent.fd)
            after_open = os.fstat(snapshot_fd)
            if _object_identity(after_open) != expected_identity:
                raise SourceAccessPolicyError(
                    "new source snapshot was replaced while being opened: "
                    f"{parent.path / name}"
                )
            os.fchmod(snapshot_fd, 0o700)
            _validate_directory(
                snapshot_fd,
                str(parent.path / name),
                repair_permissions=False,
            )
            assert expected_identity is not None
            return (
                _SecureRoot(parent.path / name, snapshot_fd, False),
                name,
                expected_identity,
            )
        except BaseException as error:
            cleanup_error: OSError | None = None
            if snapshot_fd is not None:
                try:
                    os.close(snapshot_fd)
                except OSError as close_error:
                    cleanup_error = close_error
            try:
                current = os.stat(name, dir_fd=parent.fd, follow_symlinks=False)
            except FileNotFoundError:
                pass
            except OSError as inspect_error:
                cleanup_error = cleanup_error or inspect_error
            else:
                if stat.S_ISDIR(current.st_mode) and (
                    expected_identity is None
                    or _object_identity(current) == expected_identity
                ):
                    try:
                        os.rmdir(name, dir_fd=parent.fd)
                    except OSError as remove_error:
                        cleanup_error = cleanup_error or remove_error
            if isinstance(error, OSError) or cleanup_error is not None:
                cleanup_note = (
                    f"; cleanup also failed: {cleanup_error}"
                    if cleanup_error is not None
                    else ""
                )
                raise SourceMaterializationError(
                    f"failed to initialize private source snapshot: {error}"
                    f"{cleanup_note}"
                ) from error
            raise
    raise SourceMaterializationError(
        f"could not allocate a unique source snapshot in {parent.path}"
    )


@contextmanager
def _private_snapshot_root(parent: _SecureRoot) -> Iterator[_SecureRoot]:
    root, name, expected_identity = _create_private_snapshot_root(parent)
    try:
        yield root
    finally:
        try:
            _cleanup_snapshot(
                root,
                parent_fd=parent.fd,
                name=name,
                expected_identity=expected_identity,
            )
        finally:
            os.close(root.fd)


def _seal_snapshot(root: _SecureRoot, relative_paths: Sequence[str]) -> None:
    """Make a complete snapshot read-only before any build path is exposed."""

    try:
        directory_paths: set[tuple[str, ...]] = {()}
        for relative_path in relative_paths:
            parts = _relative_parts(relative_path)
            directory_paths.update(
                tuple(parts[:index]) for index in range(1, len(parts))
            )
            source_fd = _open_source_fd(root, relative_path)
            try:
                os.fchmod(source_fd, 0o400)
                metadata = os.fstat(source_fd)
                _validate_source_file(metadata, str(root.path / relative_path))
                _validate_extended_acl(
                    source_fd,
                    getattr(metadata, "st_uid", None),
                    str(root.path / relative_path),
                )
            finally:
                os.close(source_fd)

        directory_fds: list[tuple[int, str]] = []
        try:
            for parts in sorted(directory_paths, key=lambda value: (len(value), value)):
                directory_fds.append(
                    (
                        os.dup(root.fd)
                        if not parts
                        else _open_relative_directory(root, parts, create=False),
                        str(root.path.joinpath(*parts)),
                    )
                )
            for directory_fd, label in reversed(directory_fds):
                os.fchmod(directory_fd, 0o500)
                _validate_directory(
                    directory_fd,
                    label,
                    repair_permissions=False,
                )
        finally:
            for directory_fd, _label in directory_fds:
                os.close(directory_fd)
    except OSError as error:
        raise SourceMaterializationError(
            f"failed to seal private source snapshot: {error}"
        ) from error


def _clear_snapshot_directory(directory_fd: int) -> None:
    try:
        os.fchmod(directory_fd, 0o700)
        names = os.listdir(directory_fd)
    except OSError as error:
        raise SnapshotCleanupError(
            f"failed to inspect private source snapshot during cleanup: {error}"
        ) from error

    for name in names:
        try:
            before = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        except FileNotFoundError:
            continue
        identity = _object_identity(before)
        if stat.S_ISDIR(before.st_mode):
            try:
                child_fd = os.open(name, _DIRECTORY_OPEN_FLAGS, dir_fd=directory_fd)
            except OSError as error:
                raise SnapshotCleanupError(
                    f"failed to open snapshot directory {name!r}: {error}"
                ) from error
            try:
                if _object_identity(os.fstat(child_fd)) != identity:
                    raise SnapshotCleanupError(
                        f"snapshot directory {name!r} changed while being opened"
                    )
                _clear_snapshot_directory(child_fd)
            finally:
                os.close(child_fd)
            try:
                current = os.stat(
                    name,
                    dir_fd=directory_fd,
                    follow_symlinks=False,
                )
            except FileNotFoundError as error:
                raise SnapshotCleanupError(
                    f"snapshot directory {name!r} moved during cleanup"
                ) from error
            if (
                not stat.S_ISDIR(current.st_mode)
                or _object_identity(current) != identity
            ):
                raise SnapshotCleanupError(
                    f"snapshot directory {name!r} was replaced during cleanup"
                )
            try:
                os.rmdir(name, dir_fd=directory_fd)
            except OSError as error:
                raise SnapshotCleanupError(
                    f"failed to remove snapshot directory {name!r}: {error}"
                ) from error
            continue

        if not stat.S_ISREG(before.st_mode):
            raise SnapshotCleanupError(
                f"unexpected non-regular snapshot entry during cleanup: {name!r}"
            )
        try:
            current = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        except FileNotFoundError:
            continue
        if not stat.S_ISREG(current.st_mode) or _object_identity(current) != identity:
            raise SnapshotCleanupError(
                f"snapshot file {name!r} was replaced during cleanup"
            )
        try:
            os.unlink(name, dir_fd=directory_fd)
        except OSError as error:
            raise SnapshotCleanupError(
                f"failed to remove snapshot file {name!r}: {error}"
            ) from error


def _snapshot_cleanup_race_hook(parent_fd: int, name: str) -> None:
    """Test hook after pinned recursive cleanup and before root removal."""


def _cleanup_snapshot(
    root: _SecureRoot,
    *,
    parent_fd: int,
    name: str,
    expected_identity: tuple[int, int],
) -> None:
    _clear_snapshot_directory(root.fd)
    _snapshot_cleanup_race_hook(parent_fd, name)
    try:
        current = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError as error:
        raise SnapshotCleanupError(
            "private source snapshot disappeared before cleanup; the original "
            "snapshot object may remain under another name"
        ) from error
    if (
        not stat.S_ISDIR(current.st_mode)
        or _object_identity(current) != expected_identity
    ):
        raise SnapshotCleanupError(
            "private source snapshot was replaced before cleanup; refusing to "
            "delete the replacement"
        )
    try:
        os.rmdir(name, dir_fd=parent_fd)
    except OSError as error:
        raise SnapshotCleanupError(
            f"failed to remove private source snapshot: {error}"
        ) from error


def _artifact_members_valid(root: _SecureRoot, artifact: SourceArtifact) -> bool:
    try:
        _verify_source_tree(root, artifacts=(artifact,))
    except (SourceMissingError, SourceDigestMismatchError):
        return False
    return True


def _fetch_artifact(root: _SecureRoot, artifact: SourceArtifact) -> None:
    download_relative = f".downloads/{artifact.filename}"
    try:
        download_digest = _sha256_source(root, download_relative)
    except (SourceMissingError, SourceDigestMismatchError):
        download_digest = None

    if download_digest != artifact.sha256:
        _download_verified(root, artifact.url, download_relative, artifact.sha256)

    if artifact.archive:
        _extract_verified_members(root, download_relative, artifact)
        return

    member = artifact.members[0]
    source_fd = _open_source_fd(root, download_relative)
    with os.fdopen(source_fd, "rb") as source:
        _atomic_write_from_reader(
            root,
            member.local_path,
            source,
            member.sha256,
            digest_label=str(root.path / download_relative),
        )


def _download_verified(
    root: _SecureRoot,
    url: str,
    destination: str,
    expected_sha256: str,
) -> None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "arm-acle-docset-generator/0.1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            _atomic_write_from_reader(
                root,
                destination,
                response,
                expected_sha256,
                digest_label=url,
            )
    except (OSError, urllib.error.URLError) as error:
        raise ManifestError(f"failed to download {url}: {error}") from error


def _extract_verified_members(
    root: _SecureRoot,
    archive_relative: str,
    artifact: SourceArtifact,
) -> None:
    archive_fd = _open_source_fd(root, archive_relative)
    with os.fdopen(archive_fd, "rb") as archive_file:
        with tarfile.open(fileobj=archive_file, mode="r:*") as archive:
            for member in artifact.members:
                assert member.archive_member is not None
                try:
                    tar_info = archive.getmember(member.archive_member)
                except KeyError as error:
                    raise ManifestError(
                        f"archive {root.path / archive_relative} lacks "
                        f"{member.archive_member}"
                    ) from error
                if not tar_info.isfile():
                    raise ManifestError(
                        f"archive member is not a file: {member.archive_member}"
                    )
                source = archive.extractfile(tar_info)
                if source is None:
                    raise ManifestError(
                        f"could not read archive member: {member.archive_member}"
                    )
                try:
                    _atomic_write_from_reader(
                        root,
                        member.local_path,
                        source,
                        member.sha256,
                        digest_label=member.archive_member,
                    )
                finally:
                    source.close()


def _validate_replace_target(parent_fd: int, name: str, label: str) -> None:
    try:
        metadata = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    if stat.S_ISLNK(metadata.st_mode):
        raise SourceAccessPolicyError(f"refusing to replace symlinked source: {label}")
    if not stat.S_ISREG(metadata.st_mode):
        raise SourceAccessPolicyError(f"refusing to replace non-file source: {label}")
    _validate_owner(metadata, label)
    if stat.S_IMODE(metadata.st_mode) & 0o022:
        raise SourceAccessPolicyError(
            f"refusing to replace source with unsafe permissions: {label}"
        )
    try:
        target_fd = os.open(name, _FILE_OPEN_FLAGS, dir_fd=parent_fd)
    except FileNotFoundError:
        return
    except PermissionError as error:
        raise SourceUnreadableError(
            f"source replacement target is unreadable: {label}"
        ) from error
    except OSError as error:
        if error.errno in {errno.ELOOP, errno.ENOTDIR}:
            raise SourceAccessPolicyError(
                f"source replacement target is a symlink or unsafe: {label}"
            ) from error
        raise SourceAccessPolicyError(
            f"could not inspect source replacement target safely: {label}: {error}"
        ) from error
    try:
        opened = os.fstat(target_fd)
        _validate_source_file(opened, label)
        # Device/inode alone identify replacement. Permission, ACL, timestamp,
        # and link-count churn are validated for their own properties instead.
        if _object_identity(opened) != _object_identity(metadata):
            raise SourceAccessPolicyError(
                f"source replacement target was replaced while being opened: {label}"
            )
        _validate_extended_acl(
            target_fd,
            getattr(opened, "st_uid", None),
            label,
        )
    finally:
        os.close(target_fd)


def _write_all(fd: int, value: bytes) -> None:
    view = memoryview(value)
    while view:
        written = os.write(fd, view)
        if written == 0:
            raise OSError("short write while materializing source")
        view = view[written:]


def _atomic_write_from_reader(
    root: _SecureRoot,
    destination: str,
    source: IO[bytes],
    expected_sha256: str,
    *,
    digest_label: str,
) -> None:
    parts = _relative_parts(destination)
    parent_fd = _open_relative_directory(root, parts[:-1], create=True)
    temporary_name = f".{parts[-1]}.{secrets.token_hex(16)}.tmp"
    temporary_fd: int | None = None
    operation_failed = False
    try:
        _validate_replace_target(
            parent_fd,
            parts[-1],
            str(root.path / destination),
        )
        temporary_fd = os.open(
            temporary_name,
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=parent_fd,
        )
        os.fchmod(temporary_fd, 0o600)
        digest = hashlib.sha256()
        try:
            chunk = source.read(1024 * 1024)
        except OSError as error:
            raise SourceUnreadableError(
                f"unreadable source bytes: {digest_label}: {error}"
            ) from error
        while chunk:
            digest.update(chunk)
            _write_all(temporary_fd, chunk)
            try:
                chunk = source.read(1024 * 1024)
            except OSError as error:
                raise SourceUnreadableError(
                    f"unreadable source bytes: {digest_label}: {error}"
                ) from error
        actual = digest.hexdigest()
        if actual != expected_sha256:
            raise SourceDigestMismatchError(
                f"SHA-256 mismatch for {digest_label}: expected "
                f"{expected_sha256}, got {actual}"
            )
        os.fsync(temporary_fd)
        completed_fd = temporary_fd
        temporary_fd = None
        os.close(completed_fd)
        os.rename(
            temporary_name,
            parts[-1],
            src_dir_fd=parent_fd,
            dst_dir_fd=parent_fd,
        )
    except OSError as error:
        operation_failed = True
        raise SourceMaterializationError(
            f"failed to commit verified bytes for {destination}: {error}"
        ) from error
    except BaseException:
        operation_failed = True
        raise
    finally:
        cleanup_error: OSError | None = None
        if temporary_fd is not None:
            try:
                os.close(temporary_fd)
            except OSError as error:
                cleanup_error = error
        try:
            os.unlink(temporary_name, dir_fd=parent_fd)
        except FileNotFoundError:
            pass
        except OSError as error:
            cleanup_error = cleanup_error or error
        try:
            os.close(parent_fd)
        except OSError as error:
            cleanup_error = cleanup_error or error
        if cleanup_error is not None and not operation_failed:
            raise SourceMaterializationError(
                f"failed to clean temporary source for {destination}: {cleanup_error}"
            ) from cleanup_error


def _sha256_source(root: _SecureRoot, relative_path: str) -> str:
    source_fd = _open_source_fd(root, relative_path)
    digest = hashlib.sha256()
    try:
        with os.fdopen(source_fd, "rb") as input_file:
            while chunk := input_file.read(1024 * 1024):
                digest.update(chunk)
    except OSError as error:
        raise SourceUnreadableError(
            f"unreadable source bytes: {root.path / relative_path}: {error}"
        ) from error
    return digest.hexdigest()
