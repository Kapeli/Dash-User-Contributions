from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path
from urllib.error import URLError


def load_generator():
    script = Path(__file__).resolve().parents[1] / "generate_stripe_docset.py"
    spec = importlib.util.spec_from_file_location("generate_stripe_docset", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_parse_llms_links_keeps_stripe_markdown_links_in_order():
    generator = load_generator()
    text = """
    # Stripe Documentation
    - [API Reference](https://docs.stripe.com/api.md)
    - [External](https://example.com/nope.md)
    - [Checkout](https://docs.stripe.com/checkout/quickstart.md): Build checkout.
    - [Duplicate](https://docs.stripe.com/api.md)
    """

    pages = generator.parse_llms_links(text)

    assert [(page.title, page.url) for page in pages] == [
        ("API Reference", "https://docs.stripe.com/api.md"),
        ("Checkout", "https://docs.stripe.com/checkout/quickstart.md"),
    ]


def test_build_docset_from_offline_markdown_source(tmp_path):
    generator = load_generator()
    source = tmp_path / "source"
    (source / "checkout").mkdir(parents=True)
    (source / "llms.txt").write_text(
        """
        # Stripe Documentation
        - [API Reference](https://docs.stripe.com/api.md)
        - [Checkout](https://docs.stripe.com/checkout/quickstart.md)
        """,
        encoding="utf-8",
    )
    (source / "api.md").write_text(
        "# API Reference\n\n## Authentication\n\nUse HTTPS for API requests.\n",
        encoding="utf-8",
    )
    (source / "checkout" / "quickstart.md").write_text(
        "# Checkout quickstart\n\n## Create a Session\n\nBuild a checkout page.\n",
        encoding="utf-8",
    )

    result = generator.build_docset(
        source_dir=source,
        output_root=tmp_path / "out",
        version="test",
        delay_seconds=0,
    )

    assert (result.docset_root / "Contents" / "Info.plist").is_file()
    assert (result.documents_root / "index.html").is_file()
    assert (result.documents_root / "api.html").is_file()
    assert (result.documents_root / "checkout" / "quickstart.html").is_file()
    assert result.archive_path.is_file()

    with sqlite3.connect(result.index_db) as connection:
        rows = connection.execute(
            "SELECT name, type, path FROM searchIndex ORDER BY name, type"
        ).fetchall()

    assert ("API Reference", "Guide", "api.html") in rows
    assert ("Authentication", "Section", "api.html#authentication") in rows
    assert ("Checkout", "Guide", "checkout/quickstart.html") in rows
    assert ("Create a Session", "Section", "checkout/quickstart.html#create-a-session") in rows


def test_build_docset_skips_missing_markdown_pages(tmp_path):
    generator = load_generator()
    source = tmp_path / "source"
    source.mkdir()
    (source / "llms.txt").write_text(
        """
        # Stripe Documentation
        - [API Reference](https://docs.stripe.com/api.md)
        - [Missing](https://docs.stripe.com/missing.md)
        """,
        encoding="utf-8",
    )
    (source / "api.md").write_text(
        "# API Reference\n\n## Authentication\n\nUse HTTPS for API requests.\n",
        encoding="utf-8",
    )

    result = generator.build_docset(
        source_dir=source,
        output_root=tmp_path / "out",
        version="test",
        delay_seconds=0,
    )

    assert result.page_count == 1
    assert (result.documents_root / "api.html").is_file()
    assert not (result.documents_root / "missing.html").exists()


def test_fetch_text_retries_transient_url_errors(monkeypatch):
    generator = load_generator()
    calls = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return b"ok"

    def fake_urlopen(request, timeout):
        calls.append(request.full_url)
        if len(calls) == 1:
            raise URLError("temporary")
        return Response()

    monkeypatch.setattr(generator, "urlopen", fake_urlopen)

    assert generator.fetch_text(
        "https://docs.stripe.com/llms.txt",
        timeout_seconds=1,
        retry_delay_seconds=0,
    ) == "ok"
    assert calls == [
        "https://docs.stripe.com/llms.txt",
        "https://docs.stripe.com/llms.txt",
    ]
