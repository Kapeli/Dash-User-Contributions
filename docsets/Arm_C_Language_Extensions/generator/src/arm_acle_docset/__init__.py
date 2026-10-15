"""Arm C Language Extensions docset generator."""

from .package import (
    ARCHIVE_NAME,
    DOCSET_BUNDLE_NAME,
    DOCSET_VERSION,
    IndexEntry,
    PackageResult,
    package_docset,
    verify_docset,
)

__all__ = [
    "ARCHIVE_NAME",
    "DOCSET_BUNDLE_NAME",
    "DOCSET_VERSION",
    "IndexEntry",
    "PackageResult",
    "package_docset",
    "verify_docset",
]
