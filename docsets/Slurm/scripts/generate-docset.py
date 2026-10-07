#!/usr/bin/env python3
"""Generate the Slurm Dash docset from mirrored SchedMD HTML docs."""

from __future__ import annotations

import argparse
import html
import os
import plistlib
import re
import shutil
import sqlite3
import subprocess
import tarfile
from pathlib import Path


DOCSET_NAME = "Slurm"
DOCSET_VERSION = "26.05"
INDEX_FILE = "documentation.html"


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    value = re.sub(r"\s+", " ", value)
    return value.strip(" \t\r\n:;,.")


def normalize_entry_name(value: str) -> str:
    value = html.unescape(value)
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def extract_page_title(content: str, fallback: str) -> str:
    h1_matches = re.findall(r"<h1[^>]*>(.*?)</h1>", content, re.I | re.S)
    for h1_match in h1_matches:
        title = clean_text(h1_match)
        if title == "Slurm Workload Manager":
            continue
        if title:
            return title

    match = re.search(r"<title[^>]*>(.*?)</title>", content, re.I | re.S)
    if match:
        title = clean_text(match.group(1))
        title = re.sub(r"^Slurm Workload Manager\s*-\s*", "", title)
        if title:
            return title

    return fallback


def extract_man_section(content: str) -> str:
    match = re.search(r"Section:\s*([^<]+)<br", content, re.I)
    return clean_text(match.group(1)) if match else ""


def entry_type_for_page(title: str, section: str) -> str:
    if "Configuration File" in section:
        return "Guide"
    if "Slurm Commands" in section or "Slurm Daemon" in section:
        return "Command"
    if title.endswith((".conf", ".yaml")):
        return "Guide"
    return "Guide"


def strip_title_prefix(content: str) -> str:
    return re.sub(
        r"(<title[^>]*>)\s*Slurm Workload Manager\s*-\s*([^<]+)(</title>)",
        lambda match: f"{match.group(1)}{match.group(2).strip()}{match.group(3)}",
        content,
        flags=re.I,
    )


def sanitize_html(content: str, local_html_files: set[str]) -> str:
    content = re.sub(
        r"\s*<script\b[^>]*\bsrc=[\"']https://cse\.google\.com/[^\"']*[\"'][^>]*>\s*</script>",
        "",
        content,
        flags=re.I,
    )
    content = re.sub(
        r"\s*<link\b[^>]*\brel=[\"']canonical[\"'][^>]*>",
        "",
        content,
        flags=re.I,
    )
    content = re.sub(
        r"\s*<section\b[^>]*class=[\"'][^\"']*\bslurm-search\b[^\"']*[\"'][^>]*>.*?</section>",
        "",
        content,
        flags=re.I | re.S,
    )
    content = re.sub(
        r"\s*<(script|iframe|img)\b[^>]*\bsrc=[\"']https?://[^\"']+[\"'][^>]*>(?:\s*</\1>)?",
        "",
        content,
        flags=re.I | re.S,
    )
    content = re.sub(
        r"\s*<link\b[^>]*\bhref=[\"']https?://[^\"']+[\"'][^>]*>",
        "",
        content,
        flags=re.I,
    )
    content = strip_title_prefix(content)
    content = content.replace('href="/"', 'href="index.html"')
    content = content.replace("href='/'", "href='index.html'")

    def rewrite_schedmd_href(match: re.Match[str]) -> str:
        quote = match.group(1)
        path = match.group(2)
        fragment = match.group(3) or ""
        local_path = path.rsplit("/", 1)[-1]
        if local_path in local_html_files:
            return f"href={quote}{local_path}{fragment}{quote}"
        return match.group(0)

    content = re.sub(
        r"href=(['\"])https://slurm\.schedmd\.com/([^'\"#?]+\.html)(#[^'\"]*)?\1",
        rewrite_schedmd_href,
        content,
        flags=re.I,
    )
    return content


def add_entry(entries: set[tuple[str, str, str]], name: str, entry_type: str, path: str) -> None:
    name = normalize_entry_name(name)
    if not name or "\n" in name or "\r" in name:
        return
    if not path or "\n" in path or "\r" in path:
        return
    entries.add((name, entry_type, path))


def extract_option_entries(
    entries: set[tuple[str, str, str]],
    filename: str,
    title: str,
    section: str,
    content: str,
) -> None:
    option_blocks = []
    for block in re.findall(r"<dt\b[^>]*>((?:(?!</dt>).)*?)</dt>", content, flags=re.I | re.S):
        anchor_match = re.search(r"<a\b[^>]*(?:id|name)=[\"'](OPT_[^\"']+)[\"']", block, flags=re.I)
        if anchor_match:
            option_blocks.append((block, anchor_match.group(1)))

    for block, anchor in option_blocks:
        text = clean_text(block)
        if not text or text in {"*", "####"}:
            continue

        long_options = sorted(set(re.findall(r"--[A-Za-z0-9][A-Za-z0-9_-]*", text)))
        short_options = []
        if not long_options:
            short_options = sorted(set(re.findall(r"(?<![\w-])-[A-Za-z0-9](?![\w-])", text)))

        for option in long_options + short_options:
            add_entry(entries, f"{title} {option}", "Option", f"{filename}#{anchor}")

        if "Configuration File" in section and not long_options and not short_options:
            param_match = re.search(r"<b[^>]*>\s*([^<]+?)\s*</b>", block, flags=re.I | re.S)
            parameter = clean_text(param_match.group(1)) if param_match else text.split(" ", 1)[0]
            if re.match(r"^[A-Za-z][A-Za-z0-9_.-]+$", parameter):
                add_entry(entries, f"{title} {parameter}", "Option", f"{filename}#{anchor}")


def extract_rest_entries(entries: set[tuple[str, str, str]], content: str) -> None:
    for anchor, code in re.findall(
        r'href=["\']rest_api\.html#([^"\']+)["\']>\s*<code[^>]*>(.*?)</code>',
        content,
        flags=re.I | re.S,
    ):
        endpoint = clean_text(code)
        endpoint = re.sub(r"^(delete|get|post|put|patch)\s+", lambda m: m.group(1).upper() + " ", endpoint)
        if endpoint:
            add_entry(entries, endpoint, "Function", f"rest_api.html#{anchor}")


def build_docset(source_dir: Path, build_dir: Path, archive_path: Path | None, icon_dir: Path | None) -> None:
    source_dir = source_dir.resolve()
    build_dir = build_dir.resolve()
    docset_dir = build_dir / f"{DOCSET_NAME}.docset"
    resources_dir = docset_dir / "Contents" / "Resources"
    documents_dir = resources_dir / "Documents"

    if docset_dir.exists():
        shutil.rmtree(docset_dir)
    documents_dir.mkdir(parents=True)

    for item in source_dir.iterdir():
        if item.name == ".DS_Store":
            continue
        destination = documents_dir / item.name
        if item.is_dir():
            shutil.copytree(item, destination, ignore=shutil.ignore_patterns(".DS_Store"))
        else:
            shutil.copy2(item, destination)

    local_html_files = {path.name for path in documents_dir.glob("*.html")}
    entries: set[tuple[str, str, str]] = set()
    add_entry(entries, DOCSET_NAME, "Guide", INDEX_FILE)

    for html_path in sorted(documents_dir.glob("*.html")):
        content = html_path.read_text(encoding="utf-8", errors="replace")
        title = extract_page_title(content, html_path.stem)
        section = extract_man_section(content)
        filename = html_path.name

        add_entry(entries, title, entry_type_for_page(title, section), filename)
        extract_option_entries(entries, filename, title, section, content)
        if filename == "rest_api.html":
            extract_rest_entries(entries, content)

        html_path.write_text(sanitize_html(content, local_html_files), encoding="utf-8")

    plist_path = docset_dir / "Contents" / "Info.plist"
    plist_path.parent.mkdir(parents=True, exist_ok=True)
    plist_path.write_bytes(
        plistlib.dumps(
            {
                "CFBundleIdentifier": DOCSET_NAME,
                "CFBundleName": DOCSET_NAME,
                "DocSetPlatformFamily": DOCSET_NAME.lower(),
                "dashIndexFilePath": INDEX_FILE,
                "isDashDocset": True,
            },
            sort_keys=False,
        )
    )

    db_path = resources_dir / "docSet.dsidx"
    with sqlite3.connect(db_path) as db:
        db.execute("CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT)")
        db.execute("CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path)")
        db.executemany(
            "INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?)",
            sorted(entries, key=lambda item: (item[1], item[0].lower(), item[2])),
        )
        db.commit()

    if icon_dir:
        icon_dir.mkdir(parents=True, exist_ok=True)
        favicon = documents_dir / "favicon.ico"
        if favicon.exists():
            imagemagick = shutil.which("magick") or shutil.which("convert")
            if not imagemagick:
                raise RuntimeError("ImageMagick is required to generate Dash icons")
            subprocess.run([imagemagick, f"{favicon}[2]", str(icon_dir / "icon.png")], check=True)
            subprocess.run([imagemagick, f"{favicon}[1]", str(icon_dir / "icon@2x.png")], check=True)

    if archive_path:
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(archive_path, "w:gz") as archive:
            archive.add(docset_dir, arcname=docset_dir.name, filter=lambda info: None if info.name.endswith(".DS_Store") else info)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", required=True, type=Path, help="Mirrored slurm.schedmd.com directory")
    parser.add_argument("--build-dir", required=True, type=Path, help="Temporary output directory")
    parser.add_argument("--archive", type=Path, help="Optional .tgz output path")
    parser.add_argument("--icon-dir", type=Path, help="Optional directory for Dash icons")
    args = parser.parse_args()

    build_docset(args.source_dir, args.build_dir, args.archive, args.icon_dir)


if __name__ == "__main__":
    main()
