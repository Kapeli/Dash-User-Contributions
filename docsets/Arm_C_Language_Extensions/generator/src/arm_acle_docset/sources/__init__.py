"""Pinned source inputs for the docset generator."""

from .manifest import (
    ACLE_REVISION,
    LLVM_COMMIT,
    LLVM_GENERATED_HEADERS,
    LLVM_TAG,
    SOURCE_ARTIFACTS,
    ManifestError,
    SourceArtifact,
    SourceKind,
    SourceMember,
    fetch_sources,
    resolved_source_snapshot,
    verified_source_snapshot,
    verify_source_tree,
)

__all__ = [
    "ACLE_REVISION",
    "LLVM_COMMIT",
    "LLVM_GENERATED_HEADERS",
    "LLVM_TAG",
    "SOURCE_ARTIFACTS",
    "ManifestError",
    "SourceArtifact",
    "SourceKind",
    "SourceMember",
    "fetch_sources",
    "resolved_source_snapshot",
    "verified_source_snapshot",
    "verify_source_tree",
]
