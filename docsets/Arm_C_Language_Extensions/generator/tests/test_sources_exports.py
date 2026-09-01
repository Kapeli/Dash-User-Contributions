from arm_acle_docset import sources


def test_sources_facade_exports_only_snapshot_build_apis() -> None:
    assert "resolved_source_snapshot" in sources.__all__
    assert "verified_source_snapshot" in sources.__all__
    assert "resolve_sources" not in sources.__all__
    assert not hasattr(sources, "resolve_sources")
