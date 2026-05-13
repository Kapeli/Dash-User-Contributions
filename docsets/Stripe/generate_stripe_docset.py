#!/usr/bin/env python3
"""Build a Dash docset from Stripe's public Markdown documentation."""

from __future__ import annotations

import argparse
from datetime import date
import hashlib
import html
import os
from pathlib import Path
import posixpath
import re
import shutil
import sqlite3
import struct
import tarfile
import time
from typing import NamedTuple
from urllib.parse import urlsplit
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import zlib


ROOT = Path(__file__).resolve().parent
DOCSET_NAME = "Stripe"
DOCS_HOST = "docs.stripe.com"
LLMS_URL = f"https://{DOCS_HOST}/llms.txt"
USER_AGENT = "dash-stripe-docset-generator/0.1"
LINK_RE = re.compile(r"\[([^\]]+)\]\((https://docs\.stripe\.com/[^)\s]+?\.md(?:#[^)]+)?)\)")
HEADING_RE = re.compile(r"^(#{1,4})\s+(.+?)\s*$")
FENCE_RE = re.compile(r"^```")


class PageSpec(NamedTuple):
    title: str
    url: str

    @property
    def markdown_path(self) -> str:
        parsed = urlsplit(self.url)
        return parsed.path.lstrip("/")

    @property
    def output_path(self) -> str:
        path = self.markdown_path
        if path.endswith(".md"):
            path = path[:-3] + ".html"
        return path


class Heading(NamedTuple):
    level: int
    title: str
    anchor: str


class BuildResult(NamedTuple):
    docset_root: Path
    documents_root: Path
    index_db: Path
    archive_path: Path
    page_count: int


def parse_llms_links(text: str) -> list[PageSpec]:
    pages: list[PageSpec] = []
    seen: set[str] = set()
    for title, url in LINK_RE.findall(text):
        parsed = urlsplit(url)
        if parsed.netloc != DOCS_HOST or not parsed.path.endswith(".md"):
            continue
        canonical_url = f"https://{DOCS_HOST}{parsed.path}"
        if canonical_url in seen:
            continue
        seen.add(canonical_url)
        pages.append(PageSpec(normalize_text(title), canonical_url))
    return pages


def normalize_text(text: str) -> str:
    return " ".join(text.strip().split())


def slugify(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text).lower()
    text = re.sub(r"[^a-z0-9\s_-]", "", text)
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return text or "section"


def fetch_text(
    url: str,
    timeout_seconds: int,
    attempts: int = 3,
    retry_delay_seconds: float = 1.0,
) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    last_error: URLError | None = None
    for attempt in range(1, attempts + 1):
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                return response.read().decode("utf-8", errors="replace")
        except HTTPError:
            raise
        except URLError as error:
            last_error = error
            if attempt == attempts:
                break
            print(f"Retrying {url} after transient network error: {error}", flush=True)
            time.sleep(retry_delay_seconds)
    assert last_error is not None
    raise last_error


def read_llms(source_dir: Path | None, build_root: Path, timeout_seconds: int) -> str:
    if source_dir is not None:
        return (source_dir / "llms.txt").read_text(encoding="utf-8")

    text = fetch_text(LLMS_URL, timeout_seconds)
    cache_path = build_root / "markdown" / "llms.txt"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(text, encoding="utf-8")
    return text


def read_page_markdown(
    page: PageSpec,
    source_dir: Path | None,
    build_root: Path,
    timeout_seconds: int,
    delay_seconds: float,
) -> str:
    if source_dir is not None:
        return (source_dir / page.markdown_path).read_text(encoding="utf-8")

    cache_path = build_root / "markdown" / page.markdown_path
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")

    time.sleep(delay_seconds)
    text = fetch_text(page.url, timeout_seconds)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(text, encoding="utf-8")
    return text


def render_inline(text: str, page_paths: dict[str, str]) -> str:
    rendered: list[str] = []
    last = 0
    for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
        rendered.append(render_text_span(text[last : match.start()]))
        href = rewrite_link(match.group(2), page_paths)
        label = render_text_span(match.group(1))
        rendered.append(f'<a href="{html.escape(href, quote=True)}">{label}</a>')
        last = match.end()
    rendered.append(render_text_span(text[last:]))
    return "".join(rendered)


def render_text_span(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    return escaped


def rewrite_link(url: str, page_paths: dict[str, str]) -> str:
    parsed = urlsplit(url)
    if parsed.netloc == DOCS_HOST and parsed.path.endswith(".md"):
        canonical = f"https://{DOCS_HOST}{parsed.path}"
        target = page_paths.get(canonical)
        if target:
            return target + (f"#{parsed.fragment}" if parsed.fragment else "")

    if not parsed.netloc and parsed.path.endswith(".md"):
        target = page_paths.get(f"https://{DOCS_HOST}/{parsed.path.lstrip('/')}")
        if target:
            return target + (f"#{parsed.fragment}" if parsed.fragment else "")

    return url


def markdown_to_html(markdown: str, page: PageSpec, page_paths: dict[str, str]) -> tuple[str, list[Heading]]:
    lines = markdown.splitlines()
    body: list[str] = []
    headings: list[Heading] = []
    paragraph: list[str] = []
    in_list = False
    in_code = False
    code_lines: list[str] = []
    anchor_counts: dict[str, int] = {}

    def flush_paragraph() -> None:
        nonlocal paragraph
        if not paragraph:
            return
        text = normalize_text(" ".join(paragraph))
        body.append(f"<p>{render_inline(text, page_paths)}</p>")
        paragraph = []

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            body.append("</ul>")
            in_list = False

    for line in lines:
        if FENCE_RE.match(line):
            if in_code:
                body.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
                code_lines = []
                in_code = False
            else:
                flush_paragraph()
                close_list()
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not line.strip():
            flush_paragraph()
            close_list()
            continue

        heading_match = HEADING_RE.match(line)
        if heading_match:
            flush_paragraph()
            close_list()
            level = len(heading_match.group(1))
            title = normalize_text(re.sub(r"\s+#$", "", heading_match.group(2)))
            anchor = unique_anchor(title, anchor_counts)
            if level > 1:
                headings.append(Heading(level, title, anchor))
            body.append(f'<h{level} id="{anchor}">{render_inline(title, page_paths)}</h{level}>')
            continue

        stripped = line.lstrip()
        if stripped.startswith(("- ", "* ")):
            flush_paragraph()
            if not in_list:
                body.append("<ul>")
                in_list = True
            body.append(f"<li>{render_inline(stripped[2:].strip(), page_paths)}</li>")
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            close_list()
            body.append(f"<blockquote>{render_inline(stripped.lstrip('> ').strip(), page_paths)}</blockquote>")
            continue

        paragraph.append(line.strip())

    if in_code:
        body.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
    flush_paragraph()
    close_list()

    return render_page(page.title, "\n".join(body)), headings


def unique_anchor(title: str, counts: dict[str, int]) -> str:
    base = slugify(title)
    count = counts.get(base, 0)
    counts[base] = count + 1
    if count == 0:
        return base
    return f"{base}-{count + 1}"


def render_page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="assets/stripe-docset.css">
</head>
<body>
  <main>
{body}
  </main>
</body>
</html>
"""


def render_index(pages: list[PageSpec]) -> str:
    items = "\n".join(
        f'    <li><a href="{html.escape(page.output_path, quote=True)}">{html.escape(page.title)}</a></li>'
        for page in pages
    )
    return render_page(
        "Stripe Documentation",
        f"""<h1>Stripe Documentation</h1>
<p>Offline reference generated from Stripe's public Markdown documentation.</p>
<ul>
{items}
</ul>""",
    )


def write_info_plist(docset_root: Path) -> None:
    info_path = docset_root / "Contents" / "Info.plist"
    info_path.parent.mkdir(parents=True, exist_ok=True)
    info_path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleIdentifier</key>
  <string>stripe</string>
  <key>CFBundleName</key>
  <string>Stripe</string>
  <key>DocSetPlatformFamily</key>
  <string>stripe</string>
  <key>DashDocSetFamily</key>
  <string>dashtoc</string>
  <key>DashDocSetFallbackURL</key>
  <string>https://docs.stripe.com/</string>
  <key>dashIndexFilePath</key>
  <string>index.html</string>
  <key>isDashDocset</key>
  <true/>
</dict>
</plist>
""",
        encoding="utf-8",
    )


def write_styles(documents_root: Path) -> None:
    assets = documents_root / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "stripe-docset.css").write_text(
        """
:root {
  color-scheme: light dark;
  --stripe-purple: #635bff;
  --stripe-ink: #0a2540;
  --stripe-muted: #425466;
  --stripe-border: #d9e2ec;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.55;
  margin: 0;
  color: var(--stripe-ink);
  background: #ffffff;
}

main {
  max-width: 920px;
  padding: 32px;
}

a {
  color: var(--stripe-purple);
}

pre, code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}

pre {
  overflow-x: auto;
  padding: 14px;
  border: 1px solid var(--stripe-border);
  border-radius: 6px;
  background: #f6f9fc;
}

blockquote {
  border-left: 4px solid var(--stripe-purple);
  margin-left: 0;
  padding-left: 16px;
  color: var(--stripe-muted);
}

@media (prefers-color-scheme: dark) {
  body {
    color: #f6f9fc;
    background: #0a2540;
  }

  pre {
    background: #101f33;
    border-color: #253b53;
  }
}
""".strip()
        + "\n",
        encoding="utf-8",
    )


def write_search_index(index_db: Path, entries: list[tuple[str, str, str]]) -> None:
    index_db.parent.mkdir(parents=True, exist_ok=True)
    if index_db.exists():
        index_db.unlink()
    with sqlite3.connect(index_db) as connection:
        connection.execute(
            "CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);"
        )
        connection.execute("CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);")
        connection.executemany(
            "INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?)",
            entries,
        )


def write_png(path: Path, size: int) -> None:
    pixels: list[bytes] = []
    for y in range(size):
        row = bytearray()
        for x in range(size):
            purple = (99, 91, 255)
            white = (255, 255, 255)
            on_stripe = (
                y in range(size // 4, size // 4 + max(2, size // 8))
                or y in range(size // 2 - 1, size // 2 + max(2, size // 8))
                or y in range(3 * size // 4 - max(2, size // 8), 3 * size // 4)
            )
            color = white if on_stripe and size // 5 <= x <= 4 * size // 5 else purple
            row.extend(color)
        pixels.append(bytes([0]) + bytes(row))

    raw = b"".join(pixels)
    png = b"\x89PNG\r\n\x1a\n"
    png += png_chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
    png += png_chunk(b"IDAT", zlib.compress(raw))
    png += png_chunk(b"IEND", b"")
    path.write_bytes(png)


def png_chunk(kind: bytes, data: bytes) -> bytes:
    checksum = zlib.crc32(kind + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", checksum)


def write_icons(output_root: Path, docset_root: Path) -> None:
    for name, size in (("icon.png", 16), ("icon@2x.png", 32)):
        root_icon = output_root / name
        write_png(root_icon, size)
        shutil.copy2(root_icon, docset_root / name)


def archive_docset(docset_root: Path, archive_path: Path) -> None:
    if archive_path.exists():
        archive_path.unlink()
    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(docset_root, arcname=docset_root.name, filter=tar_filter)


def tar_filter(info: tarfile.TarInfo) -> tarfile.TarInfo | None:
    if posixpath.basename(info.name) == ".DS_Store":
        return None
    return info


def write_checksum(archive_path: Path) -> None:
    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    archive_path.with_suffix(archive_path.suffix + ".sha256").write_text(
        f"{digest}  {archive_path.name}\n",
        encoding="utf-8",
    )


def clean_path(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def build_docset(
    source_dir: Path | None = None,
    output_root: Path = ROOT,
    version: str | None = None,
    max_pages: int | None = None,
    delay_seconds: float = 0.2,
    timeout_seconds: int = 30,
    keep_build: bool = False,
    refresh_cache: bool = False,
) -> BuildResult:
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    build_root = output_root / ".build"
    docset_root = output_root / f"{DOCSET_NAME}.docset"
    documents_root = docset_root / "Contents" / "Resources" / "Documents"
    index_db = docset_root / "Contents" / "Resources" / "docSet.dsidx"
    archive_path = output_root / f"{DOCSET_NAME}.tgz"

    if refresh_cache:
        clean_path(build_root)
    clean_path(docset_root)
    build_root.mkdir(parents=True, exist_ok=True)
    documents_root.mkdir(parents=True, exist_ok=True)

    llms_text = read_llms(source_dir, build_root, timeout_seconds)
    pages = parse_llms_links(llms_text)
    if max_pages is not None:
        pages = pages[:max_pages]
    if not pages:
        raise RuntimeError("No Stripe Markdown pages found in llms.txt")

    page_paths = {page.url: page.output_path for page in pages}
    entries: list[tuple[str, str, str]] = [("Stripe Documentation", "Guide", "index.html")]

    write_styles(documents_root)
    written_pages = 0
    for index, page in enumerate(pages, start=1):
        print(f"[{index}/{len(pages)}] {page.url}", flush=True)
        try:
            markdown = read_page_markdown(
                page,
                source_dir,
                build_root,
                timeout_seconds,
                delay_seconds,
            )
        except FileNotFoundError as error:
            print(f"Skipping unavailable page: {page.url} ({error})", flush=True)
            continue
        except HTTPError as error:
            if error.code != 404:
                raise
            print(f"Skipping unavailable page: {page.url} (HTTP 404)", flush=True)
            continue
        page_html, headings = markdown_to_html(markdown, page, page_paths)
        output_path = documents_root / page.output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        relative_css = os.path.relpath(documents_root / "assets" / "stripe-docset.css", output_path.parent)
        page_html = page_html.replace("assets/stripe-docset.css", relative_css)
        output_path.write_text(page_html, encoding="utf-8")
        entries.append((page.title, "Guide", page.output_path))
        for heading in headings:
            entries.append((heading.title, "Section", f"{page.output_path}#{heading.anchor}"))
        written_pages += 1

    if written_pages == 0:
        raise RuntimeError("No Stripe Markdown pages were available")

    available_pages = [
        page for page in pages if (documents_root / page.output_path).exists()
    ]
    (documents_root / "index.html").write_text(render_index(available_pages), encoding="utf-8")
    write_info_plist(docset_root)
    write_search_index(index_db, entries)
    write_icons(output_root, docset_root)
    archive_docset(docset_root, archive_path)
    write_checksum(archive_path)

    if not keep_build:
        clean_path(build_root)

    if version:
        print(f"Built Stripe docset version {version}", flush=True)
    return BuildResult(docset_root, documents_root, index_db, archive_path, written_pages)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a Stripe Dash docset.")
    parser.add_argument("--source-dir", type=Path, help="Read llms.txt and Markdown files from a local directory.")
    parser.add_argument("--output-root", type=Path, default=ROOT, help="Directory for generated docset artifacts.")
    parser.add_argument("--version", default=date.today().strftime("%Y.%m.%d"), help="Version label printed after build.")
    parser.add_argument("--max-pages", type=int, help="Limit downloaded pages for smoke testing.")
    parser.add_argument("--delay", type=float, default=0.2, help="Delay between upstream Markdown requests.")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds.")
    parser.add_argument("--keep-build", action="store_true", help="Keep downloaded Markdown cache under .build/.")
    parser.add_argument("--refresh-cache", action="store_true", help="Delete cached Markdown before downloading.")
    args = parser.parse_args()

    result = build_docset(
        source_dir=args.source_dir,
        output_root=args.output_root,
        version=args.version,
        max_pages=args.max_pages,
        delay_seconds=args.delay,
        timeout_seconds=args.timeout,
        keep_build=args.keep_build,
        refresh_cache=args.refresh_cache,
    )
    print(f"wrote {result.page_count} pages to {result.docset_root}")
    print(f"wrote archive to {result.archive_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
