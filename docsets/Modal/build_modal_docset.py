#!/usr/bin/env python3
"""Build a Dash docset for Modal's docs and GPU glossary."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import sqlite3
import subprocess
import tarfile
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent
BUILD_ROOT = ROOT / ".build"
MIRROR_ROOT = BUILD_ROOT / "mirror"
DOCSET_ROOT = ROOT / "Modal.docset"
DOCUMENTS_ROOT = DOCSET_ROOT / "Contents" / "Resources" / "Documents"
INDEX_DB = DOCSET_ROOT / "Contents" / "Resources" / "docSet.dsidx"
ARCHIVE_PATH = ROOT / "Modal.tgz"
CHECKSUM_PATH = ROOT / "Modal.tgz.sha256"
FEED_PATH = ROOT / "Modal.xml"

SEED_URLS = (
    "https://modal.com/docs",
    "https://modal.com/gpu-glossary/readme",
)

HOSTS = {"modal.com", "modal-cdn.com"}
SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script\s*>", re.IGNORECASE | re.DOTALL)
TYPEKIT_RE = re.compile(
    r'<link\b[^>]*href="https://use\.typekit\.net/[^"]+"[^>]*>\s*',
    re.IGNORECASE,
)
TYPEKIT_IMPORT_RE = re.compile(
    r'@import\s+url\(["\']?https://use\.typekit\.net/[^)]+?\)?;?',
    re.IGNORECASE,
)
ABSOLUTE_URL_RE = re.compile(r"https://(?:modal\.com|modal-cdn\.com)[^\s\"'<>)]*")
HEADING_LEVELS = {"h1", "h2", "h3"}


@dataclass(frozen=True)
class Heading:
    level: int
    text: str
    anchor: str | None


class PageParser(HTMLParser):
    """Extract page title and headings for Dash search indexing."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._in_title = False
        self._heading_tag: str | None = None
        self._heading_id: str | None = None
        self._buffer: list[str] = []
        self.title = ""
        self.headings: list[Heading] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        if tag == "title":
            self._in_title = True
            self._buffer = []
            return
        if tag in HEADING_LEVELS:
            self._heading_tag = tag
            self._heading_id = attr_map.get("id")
            self._buffer = []

    def handle_endtag(self, tag: str) -> None:
        text = normalize_text("".join(self._buffer))
        if tag == "title" and self._in_title:
            self.title = text
            self._in_title = False
            self._buffer = []
            return
        if self._heading_tag == tag:
            if text:
                self.headings.append(
                    Heading(level=int(tag[1]), text=text, anchor=self._heading_id)
                )
            self._heading_tag = None
            self._heading_id = None
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._in_title or self._heading_tag:
            self._buffer.append(data)


def normalize_text(text: str) -> str:
    return " ".join(text.split())


def run_checked(args: list[str], ok_returncodes: set[int] | None = None) -> None:
    ok_returncodes = ok_returncodes or {0}
    print("+", " ".join(args), flush=True)
    completed = subprocess.run(args, check=False)
    if completed.returncode not in ok_returncodes:
        raise subprocess.CalledProcessError(completed.returncode, args)


def clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def wget_seed(url: str) -> None:
    args = [
        "wget",
        "--no-netrc",
        "--execute=robots=off",
        "--no-verbose",
        "--recursive",
        "--level=inf",
        "--page-requisites",
        "--convert-links",
        "--adjust-extension",
        "--no-parent",
        "--span-hosts",
        "--domains=modal.com,modal-cdn.com",
        "--accept-regex",
        r"modal\.com/(docs|gpu-glossary|_app|assets)|modal-cdn\.com/",
        "--timeout=30",
        "--tries=3",
        "--directory-prefix",
        str(MIRROR_ROOT),
        url,
    ]
    # Modal's docs currently contain a few malformed embedded asset URLs that 404
    # during mirroring. Wget reports those with exit code 8 even though the mirror
    # itself is still usable, so treat that as non-fatal.
    run_checked(args, ok_returncodes={0, 8})


def strip_scripts_and_typekit(text: str) -> str:
    text = SCRIPT_RE.sub("", text)
    text = TYPEKIT_RE.sub("", text)
    text = TYPEKIT_IMPORT_RE.sub("", text)
    return text


def candidate_local_path(url: str) -> Path | None:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or parsed.netloc not in HOSTS:
        return None

    rel = parsed.path.lstrip("/")
    if not rel:
        return None

    base = DOCUMENTS_ROOT / parsed.netloc / rel
    candidates = [base]

    if base.suffix != ".html":
        candidates.append(Path(f"{base}.html"))
    candidates.append(base / "index.html")

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def rewrite_absolute_urls(text: str, current_file: Path) -> str:
    def repl(match: re.Match[str]) -> str:
        raw_url = match.group(0)
        parsed = urlsplit(raw_url)
        local_target = candidate_local_path(raw_url)
        if local_target is None:
            return raw_url

        fragment = f"#{parsed.fragment}" if parsed.fragment else ""
        if local_target == current_file and fragment:
            return fragment

        relative = os.path.relpath(local_target, current_file.parent)
        return relative + fragment

    return ABSOLUTE_URL_RE.sub(repl, text)


def post_process_text_file(path: Path) -> None:
    original = path.read_text(encoding="utf-8", errors="replace")
    updated = strip_scripts_and_typekit(original)
    updated = rewrite_absolute_urls(updated, path)
    if updated != original:
        path.write_text(updated, encoding="utf-8")


def mirror_to_docset() -> None:
    clean_dir(DOCSET_ROOT)
    (DOCSET_ROOT / "Contents" / "Resources").mkdir(parents=True, exist_ok=True)
    shutil.copytree(MIRROR_ROOT, DOCUMENTS_ROOT)


def prune_unused_assets() -> None:
    for pattern in ("**/*.js", "**/*.map", "**/*.mp4", "**/*.zip", "**/*.ttf"):
        for path in DOCUMENTS_ROOT.glob(pattern):
            if path.is_file():
                path.unlink()
    robots = DOCUMENTS_ROOT / "modal.com" / "robots.txt"
    if robots.exists():
        robots.unlink()


def post_process_downloads() -> None:
    for path in DOCUMENTS_ROOT.rglob("*.html"):
        post_process_text_file(path)
    for path in DOCUMENTS_ROOT.rglob("*.css"):
        post_process_text_file(path)
    prune_unused_assets()


def docs_entry_path() -> str:
    candidates = (
        DOCUMENTS_ROOT / "modal.com" / "docs.html",
        DOCUMENTS_ROOT / "modal.com" / "docs" / "index.html",
    )
    for candidate in candidates:
        if candidate.exists():
            return str(candidate.relative_to(DOCUMENTS_ROOT).as_posix())
    raise FileNotFoundError("Could not find mirrored docs landing page")


def write_info_plist() -> None:
    info_path = DOCSET_ROOT / "Contents" / "Info.plist"
    info_path.parent.mkdir(parents=True, exist_ok=True)
    info_path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
\t<key>CFBundleIdentifier</key>
\t<string>modal</string>
\t<key>CFBundleName</key>
\t<string>Modal</string>
\t<key>DashDocSetDeclaredInStyle</key>
\t<string>originalName</string>
\t<key>DashDocSetFallbackURL</key>
\t<string>https://modal.com/docs</string>
\t<key>DashDocSetFamily</key>
\t<string>modal</string>
\t<key>DocSetPlatformFamily</key>
\t<string>modal</string>
\t<key>dashIndexFilePath</key>
\t<string>{index_file}</string>
\t<key>isDashDocset</key>
\t<true/>
\t<key>isJavaScriptEnabled</key>
\t<false/>
</dict>
</plist>
""".format(index_file=docs_entry_path()),
        encoding="utf-8",
    )


def classify_reference_page(stem: str) -> str:
    if stem.startswith("modal."):
        parts = stem.split(".")
        if len(parts) >= 3:
            return "Method" if parts[-1][:1].islower() else "Class"
        if len(parts) == 2 and parts[-1][:1].isupper():
            return "Class"
        if stem in {"modal.billing", "modal.call_graph", "modal.config", "modal.file_io", "modal.io_streams"}:
            return "Module"
        return "Function"
    return "Guide"


def page_type_for(path: Path) -> str:
    posix = path.relative_to(DOCUMENTS_ROOT).as_posix()
    if "/docs/examples/" in posix:
        return "Example"
    if "/docs/reference/cli/" in posix:
        return "Command"
    if "/docs/reference/" in posix:
        return classify_reference_page(path.stem)
    if "/docs/guide/" in posix:
        return "Guide"
    if "/gpu-glossary/" in posix:
        return "Guide"
    return "Guide"


def display_name_for(parser: PageParser, path: Path) -> str:
    for heading in parser.headings:
        if heading.level == 1 and heading.text:
            return heading.text
    title = parser.title.replace("| Modal Docs", "").replace("| Modal", "").strip()
    if title:
        return title
    return path.stem


def iter_index_rows() -> Iterable[tuple[str, str, str]]:
    seen: set[tuple[str, str, str]] = set()
    for html_path in sorted(DOCUMENTS_ROOT.rglob("*.html")):
        rel_path = html_path.relative_to(DOCUMENTS_ROOT).as_posix()
        text = html_path.read_text(encoding="utf-8", errors="replace")
        parser = PageParser()
        parser.feed(text)

        page_name = display_name_for(parser, html_path)
        page_type = page_type_for(html_path)
        row = (page_name, page_type, rel_path)
        if row not in seen:
            seen.add(row)
            yield row

        for heading in parser.headings:
            if not heading.anchor or heading.text == page_name:
                continue
            section_row = (heading.text, "Section", f"{rel_path}#{heading.anchor}")
            if section_row not in seen:
                seen.add(section_row)
                yield section_row


def build_index() -> None:
    INDEX_DB.parent.mkdir(parents=True, exist_ok=True)
    if INDEX_DB.exists():
        INDEX_DB.unlink()

    conn = sqlite3.connect(INDEX_DB)
    try:
        conn.executescript(
            """
            CREATE TABLE searchIndex(
                id INTEGER PRIMARY KEY,
                name TEXT,
                type TEXT,
                path TEXT
            );
            CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);
            """
        )
        conn.executemany(
            "INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?)",
            list(iter_index_rows()),
        )
        conn.commit()
    finally:
        conn.close()


def write_archive() -> None:
    if ARCHIVE_PATH.exists():
        ARCHIVE_PATH.unlink()
    with tarfile.open(ARCHIVE_PATH, "w:gz") as tar:
        tar.add(DOCSET_ROOT, arcname="Modal.docset")


def write_checksum() -> None:
    digest = hashlib.sha256(ARCHIVE_PATH.read_bytes()).hexdigest()
    CHECKSUM_PATH.write_text(f"{digest}  {ARCHIVE_PATH.name}\n", encoding="utf-8")


def write_feed(version: str, archive_url: str) -> None:
    FEED_PATH.write_text(
        f"""<entry>
  <version>{version}</version>
  <url>{archive_url}</url>
</entry>
""",
        encoding="utf-8",
    )


def maybe_write_icons() -> None:
    icon_1x = DOCSET_ROOT / "icon.png"
    icon_2x = DOCSET_ROOT / "icon@2x.png"

    src_candidates = (
        DOCUMENTS_ROOT / "modal.com" / "assets" / "favicon.ico.html",
        DOCUMENTS_ROOT / "modal.com" / "assets" / "favicon.ico",
        DOCUMENTS_ROOT / "modal.com" / "assets" / "favicon.svg",
    )
    src = next((path for path in src_candidates if path.exists()), None)
    if src is None:
        return

    for output, size in ((icon_1x, 16), (icon_2x, 32)):
        try:
            subprocess.run(
                ["sips", "-s", "format", "png", str(src), "--out", str(output)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            subprocess.run(
                ["sips", "-z", str(size), str(size), str(output)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            if output.exists():
                output.unlink()
            return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--archive-url",
        default="__ARCHIVE_URL__",
        help="Hosted URL for Modal.tgz to embed in Modal.xml",
    )
    parser.add_argument(
        "--version",
        default=date.today().strftime("%Y.%m.%d"),
        help="Feed version to embed in Modal.xml",
    )
    parser.add_argument(
        "--keep-build",
        action="store_true",
        help="Keep the intermediate mirrored site under .build/",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    clean_dir(BUILD_ROOT)
    for url in SEED_URLS:
        wget_seed(url)

    mirror_to_docset()
    post_process_downloads()
    write_info_plist()
    maybe_write_icons()
    build_index()
    write_archive()
    write_checksum()
    write_feed(args.version, args.archive_url)

    if not args.keep_build:
        shutil.rmtree(BUILD_ROOT)

    print(f"Built docset: {DOCSET_ROOT}")
    print(f"Archive: {ARCHIVE_PATH}")
    print(f"Checksum: {CHECKSUM_PATH}")
    print(f"Feed: {FEED_PATH}")


if __name__ == "__main__":
    main()
