from __future__ import annotations

import ctypes
import errno
import hashlib
import io
import os
import shutil
import stat
import sys
from pathlib import Path

import pytest

from arm_acle_docset.sources import manifest
from arm_acle_docset.sources.manifest import (
    LLVM_GENERATED_HEADERS,
    SOURCE_ARTIFACTS,
    ManifestError,
    SourceAccessPolicyError,
    SourceArtifact,
    SourceDigestMismatchError,
    SourceKind,
    SourceMaterializationError,
    SourceMember,
    SourceMissingError,
    SourceUnreadableError,
    SnapshotCleanupError,
    fetch_sources,
    resolved_source_snapshot,
    select_artifacts,
    verified_source_snapshot,
    verify_source_tree,
)


def _digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _artifact(
    *,
    source_id: str = "fixture",
    kind: SourceKind = SourceKind.CATALOG,
    optional: bool = False,
    cpu_profiles: tuple[str, ...] = (),
) -> SourceArtifact:
    content = b"locked input\n"
    return SourceArtifact(
        source_id=source_id,
        kind=kind,
        url=f"https://example.invalid/{source_id}.txt",
        revision="deadbeef",
        sha256=_digest(content),
        members=(SourceMember(f"inputs/{source_id}.txt", _digest(content)),),
        optional=optional,
        cpu_profiles=cpu_profiles,
    )


def _write_source(
    root: Path,
    artifact: SourceArtifact,
    content: bytes = b"locked input\n",
) -> Path:
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(root, 0o700)
    path = root / artifact.members[0].local_path
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    path.write_bytes(content)
    os.chmod(path, 0o600)
    return path


def _permissions(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


def _set_darwin_acl(
    path: Path,
    *,
    allow: bool,
    permission_mask: int,
    owner_principal: bool = False,
) -> None:
    """Install one Darwin ACL entry without reopening through a shell tool."""

    if sys.platform != "darwin":
        pytest.skip("Darwin extended ACLs are unavailable")
    library = ctypes.CDLL(None, use_errno=True)
    required_symbols = (
        "acl_init",
        "acl_create_entry",
        "acl_set_tag_type",
        "acl_set_qualifier",
        "acl_set_permset_mask_np",
        "acl_set_fd_np",
        "acl_free",
        "mbr_uid_to_uuid",
        "mbr_gid_to_uuid",
    )
    if any(not hasattr(library, name) for name in required_symbols):
        pytest.skip("Darwin ACL APIs are unavailable")

    library.acl_init.argtypes = (ctypes.c_int,)
    library.acl_init.restype = ctypes.c_void_p
    library.acl_create_entry.argtypes = (
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(ctypes.c_void_p),
    )
    library.acl_create_entry.restype = ctypes.c_int
    library.acl_set_tag_type.argtypes = (ctypes.c_void_p, ctypes.c_int)
    library.acl_set_tag_type.restype = ctypes.c_int
    library.acl_set_qualifier.argtypes = (ctypes.c_void_p, ctypes.c_void_p)
    library.acl_set_qualifier.restype = ctypes.c_int
    library.acl_set_permset_mask_np.argtypes = (ctypes.c_void_p, ctypes.c_uint64)
    library.acl_set_permset_mask_np.restype = ctypes.c_int
    library.acl_set_fd_np.argtypes = (ctypes.c_int, ctypes.c_void_p, ctypes.c_int)
    library.acl_set_fd_np.restype = ctypes.c_int
    library.acl_free.argtypes = (ctypes.c_void_p,)
    library.acl_free.restype = ctypes.c_int
    library.mbr_uid_to_uuid.argtypes = (
        ctypes.c_uint,
        ctypes.POINTER(ctypes.c_ubyte),
    )
    library.mbr_uid_to_uuid.restype = ctypes.c_int
    library.mbr_gid_to_uuid.argtypes = (
        ctypes.c_uint,
        ctypes.POINTER(ctypes.c_ubyte),
    )
    library.mbr_gid_to_uuid.restype = ctypes.c_int

    acl = ctypes.c_void_p(library.acl_init(1))
    if not acl:
        raise OSError(ctypes.get_errno(), "could not allocate test ACL")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0))
    try:
        entry = ctypes.c_void_p()
        if library.acl_create_entry(ctypes.byref(acl), ctypes.byref(entry)) != 0:
            raise OSError(ctypes.get_errno(), "could not create test ACL entry")
        tag = 1 if allow else 2
        if library.acl_set_tag_type(entry, tag) != 0:
            raise OSError(ctypes.get_errno(), "could not set test ACL tag")
        qualifier = (ctypes.c_ubyte * 16)()
        if owner_principal:
            identity_error = library.mbr_uid_to_uuid(os.getuid(), qualifier)
        else:
            identity_error = library.mbr_gid_to_uuid(os.getgid(), qualifier)
        if identity_error != 0:
            raise OSError(identity_error, "could not resolve test ACL principal")
        if library.acl_set_qualifier(entry, qualifier) != 0:
            raise OSError(ctypes.get_errno(), "could not set test ACL qualifier")
        if library.acl_set_permset_mask_np(entry, permission_mask) != 0:
            raise OSError(ctypes.get_errno(), "could not set test ACL permissions")
        ctypes.set_errno(0)
        if (
            library.acl_set_fd_np(
                descriptor,
                acl,
                manifest._DARWIN_ACL_TYPE_EXTENDED,
            )
            != 0
        ):
            error_number = ctypes.get_errno()
            if error_number in {errno.EOPNOTSUPP, getattr(errno, "ENOTSUP", -1)}:
                pytest.skip("test filesystem does not support Darwin ACLs")
            raise OSError(error_number, "could not install test ACL")
    finally:
        os.close(descriptor)
        library.acl_free(acl)


def test_manifest_pins_every_download_and_member() -> None:
    assert SOURCE_ARTIFACTS
    assert len({artifact.source_id for artifact in SOURCE_ARTIFACTS}) == len(
        SOURCE_ARTIFACTS
    )
    for artifact in SOURCE_ARTIFACTS:
        assert artifact.url.startswith("https://")
        assert artifact.revision
        assert len(artifact.sha256) == 64
        assert artifact.members
        for member in artifact.members:
            assert len(member.sha256) == 64
    assert {Path(member.local_path).name for member in LLVM_GENERATED_HEADERS} == {
        "arm_bf16.h",
        "arm_mve.h",
        "arm_neon.h",
        "arm_sme.h",
        "arm_sve.h",
        "arm_vector_types.h",
    }


def test_verify_source_tree_accepts_only_matching_content(tmp_path: Path) -> None:
    artifact = _artifact()
    path = _write_source(tmp_path, artifact)

    resolved = verify_source_tree(tmp_path, artifacts=(artifact,))
    assert resolved[artifact.members[0].local_path] == path

    path.write_bytes(b"tampered\n")
    with pytest.raises(SourceDigestMismatchError, match="SHA-256 mismatch"):
        verify_source_tree(tmp_path, artifacts=(artifact,))


def test_verify_source_tree_distinguishes_missing_and_unreadable(
    tmp_path: Path,
) -> None:
    artifact = _artifact()
    os.chmod(tmp_path, 0o700)

    with pytest.raises(SourceMissingError, match="missing source"):
        verify_source_tree(tmp_path, artifacts=(artifact,))

    path = _write_source(tmp_path, artifact)
    os.chmod(path, 0o000)
    try:
        with pytest.raises(SourceUnreadableError, match="unreadable source"):
            verify_source_tree(tmp_path, artifacts=(artifact,))
    finally:
        os.chmod(path, 0o600)


def test_verify_source_tree_rejects_symlinked_root(tmp_path: Path) -> None:
    artifact = _artifact()
    real_root = tmp_path / "real"
    _write_source(real_root, artifact)
    linked_root = tmp_path / "linked"
    linked_root.symlink_to(real_root, target_is_directory=True)

    with pytest.raises(SourceAccessPolicyError, match="symlink"):
        verify_source_tree(linked_root, artifacts=(artifact,))


def test_verify_source_tree_rejects_symlinked_root_parent(tmp_path: Path) -> None:
    artifact = _artifact()
    real_parent = tmp_path / "real-parent"
    real_root = real_parent / "cache"
    _write_source(real_root, artifact)
    linked_parent = tmp_path / "linked-parent"
    linked_parent.symlink_to(real_parent, target_is_directory=True)

    with pytest.raises(SourceAccessPolicyError, match="symlink"):
        verify_source_tree(linked_parent / "cache", artifacts=(artifact,))


def test_verify_source_tree_rejects_symlinked_member_parent(tmp_path: Path) -> None:
    artifact = _artifact()
    root = tmp_path / "cache"
    root.mkdir(mode=0o700)
    outside = tmp_path / "outside"
    outside.mkdir(mode=0o700)
    outside_file = outside / "fixture.txt"
    outside_file.write_bytes(b"locked input\n")
    os.chmod(outside_file, 0o600)
    (root / "inputs").symlink_to(outside, target_is_directory=True)

    with pytest.raises(SourceAccessPolicyError, match="symlink"):
        verify_source_tree(root, artifacts=(artifact,))


def test_verify_source_tree_rejects_symlinked_member_leaf(tmp_path: Path) -> None:
    artifact = _artifact()
    root = tmp_path / "cache"
    outside = tmp_path / "outside.txt"
    outside.write_bytes(b"locked input\n")
    os.chmod(outside, 0o600)
    member_path = root / artifact.members[0].local_path
    member_path.parent.mkdir(mode=0o700, parents=True)
    os.chmod(root, 0o700)
    member_path.symlink_to(outside)

    with pytest.raises(SourceAccessPolicyError, match="symlink"):
        verify_source_tree(root, artifacts=(artifact,))


def test_verify_source_tree_rejects_fifo_without_blocking(tmp_path: Path) -> None:
    if not hasattr(os, "mkfifo"):
        pytest.skip("platform does not support FIFOs")
    artifact = _artifact()
    root = tmp_path / "cache"
    member_path = root / artifact.members[0].local_path
    member_path.parent.mkdir(mode=0o700, parents=True)
    os.chmod(root, 0o700)
    os.mkfifo(member_path, mode=0o600)

    with pytest.raises(SourceAccessPolicyError, match="not a regular file"):
        verify_source_tree(root, artifacts=(artifact,))


def test_verify_source_tree_rejects_leaf_replaced_between_lstat_and_open(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = _artifact()
    root = tmp_path / "cache"
    path = _write_source(root, artifact)
    original_path = path.with_name("original.txt")

    def replace_leaf(parent_fd: int, name: str) -> None:
        path.rename(original_path)
        path.write_bytes(b"locked input\n")
        os.chmod(path, 0o600)

    monkeypatch.setattr(manifest, "_source_open_race_hook", replace_leaf)

    with pytest.raises(SourceAccessPolicyError, match="replaced while being opened"):
        verify_source_tree(root, artifacts=(artifact,))


def test_verify_source_tree_rejects_non_current_owner(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = _artifact()
    _write_source(tmp_path, artifact)
    current_uid = manifest._current_uid()
    if current_uid is None:
        pytest.skip("platform does not expose file ownership")
    monkeypatch.setattr(
        manifest,
        "_validate_ancestor_directory",
        lambda fd, label: None,
    )
    monkeypatch.setattr(manifest, "_current_uid", lambda: current_uid + 1)

    with pytest.raises(SourceAccessPolicyError, match="not owned"):
        verify_source_tree(tmp_path, artifacts=(artifact,))


def test_verify_source_tree_rejects_non_current_leaf_owner(
    tmp_path: Path,
) -> None:
    artifact = _artifact()
    path = _write_source(tmp_path, artifact)
    current_uid = manifest._current_uid()
    if current_uid is None:
        pytest.skip("platform does not expose file ownership")
    values = list(path.stat())
    values[4] = next(uid for uid in (1, 2, 3) if uid not in {0, current_uid})
    foreign_owned = os.stat_result(values)

    with pytest.raises(SourceAccessPolicyError, match="not owned"):
        manifest._validate_source_file(foreign_owned, str(path))


def test_verify_source_tree_rejects_non_private_directory_permissions(
    tmp_path: Path,
) -> None:
    artifact = _artifact()
    root = tmp_path / "cache"
    _write_source(root, artifact)
    os.chmod(root, 0o755)

    with pytest.raises(SourceAccessPolicyError, match="permissions must be 0700"):
        verify_source_tree(root, artifacts=(artifact,))


def test_verify_source_tree_rejects_non_private_file_permissions(
    tmp_path: Path,
) -> None:
    artifact = _artifact()
    root = tmp_path / "cache"
    path = _write_source(root, artifact)
    os.chmod(path, 0o666)

    with pytest.raises(SourceAccessPolicyError, match="non-owner writes"):
        verify_source_tree(root, artifacts=(artifact,))


def test_verify_source_tree_rejects_extended_acl_write_policy(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = _artifact()
    path = _write_source(tmp_path, artifact)
    target_identity = (path.stat().st_dev, path.stat().st_ino)

    def grants_write(fd: int, owner_uid: int | None) -> bool:
        metadata = os.fstat(fd)
        return (
            stat.S_ISREG(metadata.st_mode)
            and (metadata.st_dev, metadata.st_ino) == target_identity
        )

    monkeypatch.setattr(
        manifest,
        "_darwin_acl_grants_nonowner_write",
        grants_write,
    )

    with pytest.raises(SourceAccessPolicyError, match="extended ACL grants"):
        verify_source_tree(tmp_path, artifacts=(artifact,))


def test_verify_source_tree_reports_acl_revalidation_failure_as_policy_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = _artifact()
    path = _write_source(tmp_path, artifact)
    target_identity = (path.stat().st_dev, path.stat().st_ino)

    def fail_acl_read(fd: int, owner_uid: int | None) -> bool:
        metadata = os.fstat(fd)
        if (
            stat.S_ISREG(metadata.st_mode)
            and (metadata.st_dev, metadata.st_ino) == target_identity
        ):
            raise OSError(errno.EIO, "simulated ACL read failure")
        return False

    monkeypatch.setattr(
        manifest,
        "_darwin_acl_grants_nonowner_write",
        fail_acl_read,
    )

    with pytest.raises(
        SourceAccessPolicyError,
        match="could not inspect source access policy safely",
    ):
        verify_source_tree(tmp_path, artifacts=(artifact,))


def test_verify_source_tree_does_not_treat_ctime_churn_as_replacement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = _artifact()
    path = _write_source(tmp_path, artifact)
    target_identity = (path.stat().st_dev, path.stat().st_ino)
    original_fstat = manifest.os.fstat

    def report_benign_ctime_churn(fd: int) -> os.stat_result:
        metadata = original_fstat(fd)
        if (metadata.st_dev, metadata.st_ino) != target_identity:
            return metadata
        values = list(metadata)
        values[9] += 1
        return os.stat_result(values)

    monkeypatch.setattr(manifest.os, "fstat", report_benign_ctime_churn)

    resolved = verify_source_tree(tmp_path, artifacts=(artifact,))

    assert resolved[artifact.members[0].local_path] == path


@pytest.mark.parametrize(
    ("allow", "permission_mask", "rejected"),
    (
        (True, 1 << 2, True),  # write data
        (False, 1 << 2, False),  # deny entries do not grant write
        (True, 1 << 1, False),  # read-only grants do not mutate the object
    ),
)
def test_verify_source_tree_enforces_darwin_extended_acl_entries(
    tmp_path: Path,
    allow: bool,
    permission_mask: int,
    rejected: bool,
) -> None:
    artifact = _artifact()
    path = _write_source(tmp_path, artifact)
    _set_darwin_acl(
        path,
        allow=allow,
        permission_mask=permission_mask,
    )
    assert _permissions(path) == 0o600

    if rejected:
        with pytest.raises(SourceAccessPolicyError, match="extended ACL grants"):
            verify_source_tree(tmp_path, artifacts=(artifact,))
    else:
        verify_source_tree(tmp_path, artifacts=(artifact,))


def test_verify_source_tree_allows_darwin_owner_acl_write(
    tmp_path: Path,
) -> None:
    artifact = _artifact()
    path = _write_source(tmp_path, artifact)
    _set_darwin_acl(
        path,
        allow=True,
        permission_mask=1 << 2,
        owner_principal=True,
    )
    assert _permissions(path) == 0o600

    verify_source_tree(tmp_path, artifacts=(artifact,))


def test_fetch_rejects_darwin_extended_acl_on_ancestor(
    tmp_path: Path,
) -> None:
    artifact = _artifact()
    root = tmp_path / "cache"
    _set_darwin_acl(
        tmp_path,
        allow=True,
        permission_mask=1 << 2,  # add file on a directory
    )
    assert _permissions(tmp_path) == 0o700

    with pytest.raises(SourceAccessPolicyError, match="extended ACL grants"):
        fetch_sources(root, artifacts=(artifact,))
    assert not root.exists()


def test_fetch_creates_private_cache_and_regular_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = _artifact()
    root = tmp_path / "cache"
    monkeypatch.setattr(
        manifest.urllib.request,
        "urlopen",
        lambda request, timeout: io.BytesIO(b"locked input\n"),
    )

    resolved = fetch_sources(root, artifacts=(artifact,))

    assert resolved[artifact.members[0].local_path].read_bytes() == b"locked input\n"
    assert _permissions(root) == 0o700
    assert _permissions(root / ".downloads") == 0o700
    assert _permissions(root / "inputs") == 0o700
    assert _permissions(root / ".downloads" / artifact.filename) == 0o600
    assert _permissions(root / artifact.members[0].local_path) == 0o600


def test_fetch_does_not_create_directories_outside_selected_root(
    tmp_path: Path,
) -> None:
    artifact = _artifact()
    missing_parent = tmp_path / "missing-parent"

    with pytest.raises(SourceMissingError, match="root parent does not exist"):
        fetch_sources(missing_parent / "cache", artifacts=(artifact,))
    assert not missing_parent.exists()


def test_fetch_rejects_writable_non_sticky_ancestor(tmp_path: Path) -> None:
    artifact = _artifact()
    unsafe_parent = tmp_path / "unsafe-parent"
    unsafe_parent.mkdir(mode=0o700)
    os.chmod(unsafe_parent, 0o777)

    with pytest.raises(SourceAccessPolicyError, match="lacks the sticky bit"):
        fetch_sources(unsafe_parent / "cache", artifacts=(artifact,))
    assert not (unsafe_parent / "cache").exists()


def test_fetch_rejects_foreign_owned_0755_ancestor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_uid = manifest._current_uid()
    if current_uid is None:
        pytest.skip("platform does not expose file ownership")
    artifact = _artifact()
    foreign_parent = tmp_path / "foreign-parent"
    foreign_parent.mkdir(mode=0o755)
    os.chmod(foreign_parent, 0o755)
    target_identity = (foreign_parent.stat().st_dev, foreign_parent.stat().st_ino)
    foreign_uid = next(uid for uid in (1, 2, 3) if uid not in {0, current_uid})
    original_fstat = manifest.os.fstat

    def report_foreign_owner(fd: int) -> os.stat_result:
        metadata = original_fstat(fd)
        if (metadata.st_dev, metadata.st_ino) != target_identity:
            return metadata
        values = list(metadata)
        values[4] = foreign_uid
        return os.stat_result(values)

    monkeypatch.setattr(manifest.os, "fstat", report_foreign_owner)

    with pytest.raises(SourceAccessPolicyError, match="untrusted UID"):
        fetch_sources(foreign_parent / "cache", artifacts=(artifact,))
    assert not (foreign_parent / "cache").exists()


def test_fetch_allows_writable_sticky_ancestor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if not hasattr(stat, "S_ISVTX"):
        pytest.skip("platform does not expose the sticky bit")
    artifact = _artifact()
    sticky_parent = tmp_path / "sticky-parent"
    sticky_parent.mkdir(mode=0o700)
    os.chmod(sticky_parent, 0o1777)
    monkeypatch.setattr(
        manifest.urllib.request,
        "urlopen",
        lambda request, timeout: io.BytesIO(b"locked input\n"),
    )

    resolved = fetch_sources(sticky_parent / "cache", artifacts=(artifact,))

    assert resolved[artifact.members[0].local_path].read_bytes() == b"locked input\n"


def test_fetch_offline_preserves_digest_mismatch_error(tmp_path: Path) -> None:
    artifact = _artifact()
    root = tmp_path / "cache"
    _write_source(root, artifact, b"tampered\n")

    with pytest.raises(SourceDigestMismatchError, match="SHA-256 mismatch"):
        fetch_sources(root, artifacts=(artifact,), offline=True)


def test_fetch_rejects_symlinked_root(tmp_path: Path) -> None:
    artifact = _artifact()
    real_root = tmp_path / "real"
    real_root.mkdir(mode=0o700)
    linked_root = tmp_path / "linked"
    linked_root.symlink_to(real_root, target_is_directory=True)

    with pytest.raises(SourceAccessPolicyError, match="symlink"):
        fetch_sources(linked_root, artifacts=(artifact,))


def test_fetch_rejects_symlinked_leaf_without_changing_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = _artifact()
    root = tmp_path / "cache"
    root.mkdir(mode=0o700)
    member_path = root / artifact.members[0].local_path
    member_path.parent.mkdir(mode=0o700)
    outside = tmp_path / "outside.txt"
    outside.write_bytes(b"outside\n")
    os.chmod(outside, 0o600)
    member_path.symlink_to(outside)
    monkeypatch.setattr(
        manifest.urllib.request,
        "urlopen",
        lambda request, timeout: io.BytesIO(b"locked input\n"),
    )

    with pytest.raises(SourceAccessPolicyError, match="symlink"):
        fetch_sources(root, artifacts=(artifact,))
    assert outside.read_bytes() == b"outside\n"


def test_verified_snapshot_survives_cache_replacement(tmp_path: Path) -> None:
    artifact = _artifact()
    root = tmp_path / "cache"
    path = _write_source(root, artifact)

    with verified_source_snapshot(root, artifacts=(artifact,)) as resolved:
        snapshot_path = resolved[artifact.members[0].local_path]
        path.unlink()
        path.write_bytes(b"replacement\n")
        os.chmod(path, 0o600)
        assert snapshot_path.read_bytes() == b"locked input\n"
        assert _permissions(snapshot_path) == 0o400
        assert _permissions(snapshot_path.parent) == 0o500
        assert _permissions(snapshot_path.parents[1]) == 0o500
    assert not snapshot_path.parents[1].exists()


def test_verified_snapshot_survives_cache_in_place_mutation(tmp_path: Path) -> None:
    artifact = _artifact()
    root = tmp_path / "cache"
    path = _write_source(root, artifact)

    with verified_source_snapshot(root, artifacts=(artifact,)) as resolved:
        snapshot_path = resolved[artifact.members[0].local_path]
        with path.open("r+b") as output:
            output.seek(0)
            output.write(b"changed input\n")
            output.truncate()
        assert snapshot_path.read_bytes() == b"locked input\n"


def test_verified_snapshot_pins_file_descriptor_before_replacement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = _artifact()
    root = tmp_path / "cache"
    path = _write_source(root, artifact)
    original_open = manifest._open_source_fd

    def replace_after_open(secure_root: object, relative_path: str) -> int:
        source_fd = original_open(secure_root, relative_path)  # type: ignore[arg-type]
        path.unlink()
        path.write_bytes(b"replacement\n")
        os.chmod(path, 0o600)
        return source_fd

    monkeypatch.setattr(manifest, "_open_source_fd", replace_after_open)

    with verified_source_snapshot(root, artifacts=(artifact,)) as resolved:
        assert (
            resolved[artifact.members[0].local_path].read_bytes() == b"locked input\n"
        )


def test_verified_snapshot_detects_in_place_change_after_open(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = _artifact()
    root = tmp_path / "cache"
    path = _write_source(root, artifact)
    original_open = manifest._open_source_fd

    def mutate_after_open(secure_root: object, relative_path: str) -> int:
        source_fd = original_open(secure_root, relative_path)  # type: ignore[arg-type]
        path.write_bytes(b"tampered\n")
        os.chmod(path, 0o600)
        return source_fd

    monkeypatch.setattr(manifest, "_open_source_fd", mutate_after_open)

    with pytest.raises(SourceDigestMismatchError, match="SHA-256 mismatch"):
        with verified_source_snapshot(root, artifacts=(artifact,)):
            pass


def test_verified_snapshot_is_read_only_while_yielded(tmp_path: Path) -> None:
    if getattr(os, "geteuid", lambda: 1)() == 0:
        pytest.skip("root can bypass file permission checks")
    artifact = _artifact()
    root = tmp_path / "cache"
    _write_source(root, artifact)

    with verified_source_snapshot(root, artifacts=(artifact,)) as resolved:
        snapshot_path = resolved[artifact.members[0].local_path]
        with pytest.raises(PermissionError):
            snapshot_path.write_bytes(b"tampered\n")
        with pytest.raises(PermissionError):
            snapshot_path.unlink()


def test_verified_snapshot_revalidates_acl_after_sealing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = _artifact()
    root = tmp_path / "cache"
    _write_source(root, artifact)

    def grant_only_after_file_seal(fd: int, owner_uid: int | None) -> bool:
        metadata = os.fstat(fd)
        return (
            stat.S_ISREG(metadata.st_mode) and stat.S_IMODE(metadata.st_mode) == 0o400
        )

    monkeypatch.setattr(
        manifest,
        "_darwin_acl_grants_nonowner_write",
        grant_only_after_file_seal,
    )

    with pytest.raises(SourceAccessPolicyError, match="extended ACL grants"):
        with verified_source_snapshot(root, artifacts=(artifact,)):
            pass
    assert list(root.glob(".arm-acle-source-snapshot-*")) == []


def test_verified_snapshot_refuses_to_delete_root_replaced_at_cleanup_hook(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = _artifact()
    root = tmp_path / "cache"
    _write_source(root, artifact)
    moved_snapshot: Path | None = None
    replacement_root: Path | None = None

    def replace_after_pinned_cleanup(parent_fd: int, name: str) -> None:
        assert replacement_root is not None
        assert moved_snapshot is not None
        replacement_root.rename(moved_snapshot)
        replacement_root.mkdir(mode=0o700)
        (replacement_root / "marker").write_text("keep\n")

    monkeypatch.setattr(
        manifest,
        "_snapshot_cleanup_race_hook",
        replace_after_pinned_cleanup,
    )

    try:
        with pytest.raises(SnapshotCleanupError, match="replaced before cleanup"):
            with verified_source_snapshot(root, artifacts=(artifact,)) as resolved:
                snapshot_path = resolved[artifact.members[0].local_path]
                replacement_root = snapshot_path.parents[1]
                moved_snapshot = replacement_root.with_name(
                    f"{replacement_root.name}-moved"
                )
        assert replacement_root is not None
        assert (replacement_root / "marker").read_text() == "keep\n"
        assert moved_snapshot is not None and moved_snapshot.exists()
        assert list(moved_snapshot.iterdir()) == []
    finally:
        if moved_snapshot is not None and moved_snapshot.exists():
            os.chmod(moved_snapshot, 0o700)
            moved_snapshot.rmdir()
        if replacement_root is not None and replacement_root.exists():
            shutil.rmtree(replacement_root)


@pytest.mark.parametrize(
    ("operation", "error_number"),
    (
        ("write", errno.ENOSPC),
        ("fsync", errno.EIO),
        ("rename", errno.EIO),
    ),
)
def test_snapshot_output_failure_is_materialization_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
    error_number: int,
) -> None:
    artifact = _artifact()
    root = tmp_path / "cache"
    _write_source(root, artifact)

    def fail_output(*args: object, **kwargs: object) -> None:
        raise OSError(error_number, f"simulated {operation} failure")

    if operation == "rename":
        monkeypatch.setattr(manifest, "_require_secure_path_support", lambda: None)
    monkeypatch.setattr(manifest.os, operation, fail_output)

    with pytest.raises(SourceMaterializationError, match="failed to commit"):
        with verified_source_snapshot(root, artifacts=(artifact,)):
            pass
    assert list(root.glob(".arm-acle-source-snapshot-*")) == []


def test_snapshot_initialization_failure_closes_fd_and_removes_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = _artifact()
    root = tmp_path / "cache"
    _write_source(root, artifact)
    original_fchmod = manifest.os.fchmod
    private_mode_calls = 0
    failed_fd: int | None = None

    def fail_snapshot_fchmod(fd: int, mode: int) -> None:
        nonlocal failed_fd, private_mode_calls
        if mode == 0o700:
            private_mode_calls += 1
            if private_mode_calls == 2:
                failed_fd = fd
                raise OSError(errno.EIO, "simulated snapshot initialization failure")
        original_fchmod(fd, mode)

    monkeypatch.setattr(manifest.os, "fchmod", fail_snapshot_fchmod)

    with pytest.raises(SourceMaterializationError, match="failed to initialize"):
        with verified_source_snapshot(root, artifacts=(artifact,)):
            pass

    assert list(root.glob(".arm-acle-source-snapshot-*")) == []
    assert failed_fd is not None
    with pytest.raises(OSError) as closed:
        os.fstat(failed_fd)
    assert closed.value.errno == errno.EBADF


def test_resolved_source_snapshot_fetches_and_cleans_private_copy(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = _artifact()
    root = tmp_path / "cache"
    monkeypatch.setattr(
        manifest.urllib.request,
        "urlopen",
        lambda request, timeout: io.BytesIO(b"locked input\n"),
    )

    with resolved_source_snapshot(root, artifacts=(artifact,)) as resolved:
        snapshot_path = resolved[artifact.members[0].local_path]
        assert snapshot_path.read_bytes() == b"locked input\n"
        assert snapshot_path.parents[1].parent == root
    assert not snapshot_path.parents[1].exists()


def test_resolved_snapshot_uses_cache_when_source_tree_is_read_only(
    tmp_path: Path,
) -> None:
    artifact = _artifact()
    source_root = tmp_path / "sources"
    source_path = _write_source(source_root, artifact)
    source_entries = {path.relative_to(source_root) for path in source_root.rglob("*")}
    os.chmod(source_path, 0o400)
    os.chmod(source_path.parent, 0o500)
    os.chmod(source_root, 0o500)
    cache_root = tmp_path / "cache"

    try:
        with resolved_source_snapshot(
            cache_root,
            source_dir=source_root,
            offline=True,
            artifacts=(artifact,),
        ) as resolved:
            snapshot_path = resolved[artifact.members[0].local_path]
            assert snapshot_path.read_bytes() == b"locked input\n"
            assert snapshot_path.parents[1].parent == cache_root
            assert _permissions(cache_root) == 0o700
            assert not any(
                path.name.startswith(".arm-acle-source-snapshot-")
                for path in source_root.iterdir()
            )
        assert {path.relative_to(source_root) for path in source_root.rglob("*")} == (
            source_entries
        )
        assert not snapshot_path.parents[1].exists()
    finally:
        os.chmod(source_root, 0o700)
        os.chmod(source_path.parent, 0o700)
        os.chmod(source_path, 0o600)


def test_performance_profiles_select_only_matching_optional_sources() -> None:
    required = _artifact(source_id="required")
    performance = _artifact(
        source_id="perf-neoverse-v2",
        kind=SourceKind.PERFORMANCE,
        optional=True,
        cpu_profiles=("neoverse-v2",),
    )

    assert select_artifacts((required, performance)) == (required,)
    assert select_artifacts((required, performance), cpu_profiles=("neoverse-v2",)) == (
        required,
        performance,
    )
    with pytest.raises(ManifestError, match="unknown CPU profile"):
        select_artifacts((required, performance), cpu_profiles=("unknown",))


def test_manifest_rejects_performance_profiles_on_non_performance_source() -> None:
    with pytest.raises(ValueError, match="only valid for performance"):
        _artifact(cpu_profiles=("neoverse-v2",))
