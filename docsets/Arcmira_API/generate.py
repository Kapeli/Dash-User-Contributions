"""Build the Arcmira API docset from its published OpenAPI document (Python 3.9+)."""
import argparse
import gzip
import hashlib
from html import escape
import json
from pathlib import Path
import plistlib
import re
import sqlite3
import tarfile
from tempfile import TemporaryDirectory
from urllib.request import urlopen

SOURCE = "https://api.arcmira.com/v1/openapi.json"
DOCS = "https://arcmira.com/docs"
HERE = Path(__file__).resolve().parent
STYLE = """html{color-scheme:light dark;font:16px/1.5 system-ui}body{margin:1rem;max-width:56rem}
a{color:#2461ae}code,pre{font-family:ui-monospace,monospace}pre{white-space:pre-wrap}
code,pre,a,td,th{overflow-wrap:anywhere}table{border-collapse:collapse;width:100%}
td,th{text-align:left;vertical-align:top;padding:.4rem;border-bottom:1px solid #8886}
h1{font-size:1.6rem}h2{font-size:1.2rem}nav,small{font-size:.88rem}
@media(prefers-color-scheme:dark){a{color:#91c6ff}}"""
METHODS = {"get", "post", "put", "patch", "delete", "options", "head", "trace"}
KINDS = {"schemas": "Type", "responses": "Response", "headers": "Header",
         "securitySchemes": "Guide", "parameters": "Parameter"}


def link(path, label):
    return f'<a href="{escape(path, quote=True)}">{escape(label)}</a>'


def page(title, body):
    return (f'<!doctype html><html lang="en"><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{escape(title)}</title><link rel="stylesheet" href="style.css">'
            f'<nav>{link("index.html", "Reference index")} · {link(DOCS, "Online guides")}</nav>'
            f'<main><h1>{escape(title)}</h1>{body}</main></html>')


def build(raw, output):
    spec = json.loads(raw)
    version = spec["info"]["version"]
    digest = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    refs = {}
    for group, members in spec["components"].items():
        for name in members:
            if not re.fullmatch(r"[A-Za-z0-9._-]+", name):
                raise ValueError(f"Unexpected component name: {name}")
            refs[f"#/components/{group}/{name}"] = f"{group}-{name}.html"

    def definition(data):
        code = escape(json.dumps(data, ensure_ascii=False, indent=2), quote=False)
        def referenced(m):
            ref = m.group(1)
            return '"$ref": "' + link(refs[ref], ref) + '"'
        return '<pre><code>' + re.sub(r'"\$ref": "(#/components/[^"]+)"', referenced, code) + '</code></pre>'

    output.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory() as tmp:
        root = Path(tmp) / "Arcmira_API.docset"
        resources = root / "Contents" / "Resources"
        documents = resources / "Documents"
        documents.mkdir(parents=True)
        for icon in ("icon.png", "icon@2x.png"):
            (root / icon).write_bytes((HERE / icon).read_bytes())
        (root / "Contents" / "Info.plist").write_bytes(plistlib.dumps({
            "CFBundleIdentifier": "com.arcmira.api", "CFBundleName": "Arcmira API",
            "DocSetPlatformFamily": "arcmira", "isDashDocset": True,
            "dashIndexFilePath": "index.html"}))
        (documents / "openapi.json").write_bytes(raw)
        (documents / "style.css").write_text(STYLE, encoding="utf-8")
        entries = []
        index = [f'<p>{escape(spec["info"]["description"])}</p>',
                 f'<p>API version {escape(version)} · {link("openapi.json", "Offline OpenAPI document")}</p>']
        for server in spec.get("servers", []):
            index.append('<p>Base URL <code>'+escape(server["url"])+'</code></p>')

        index.append('<h2>Endpoints</h2><ul>')
        for path, methods in spec["paths"].items():
            for method, op in methods.items():
                if method not in METHODS:
                    continue
                op_id = op["operationId"]
                if not re.fullmatch(r"[A-Za-z0-9._-]+", op_id):
                    raise ValueError(f"Unexpected operation ID: {op_id}")
                dest = f"op-{op_id}.html"
                route = f"{method.upper()} {path}"
                title = op.get("summary", op_id)
                body = [f'<p><code>{escape(route)}</code></p>',
                        f'<p>{escape(op.get("description", ""))}</p>']
                params = methods.get("parameters", []) + op.get("parameters", [])
                if params:
                    body.append('<h2>Parameters</h2><table><tr><th>Name</th><th>Location</th><th>Description</th></tr>')
                    for param in params:
                        if "$ref" in param:
                            body.append('<tr><td colspan="3">'+link(refs[param["$ref"]], param["$ref"])+'</td></tr>')
                            continue
                        label = param["name"] + (" (required)" if param.get("required") else "")
                        body.append('<tr><td>'+escape(label)+'</td><td>'+escape(param["in"])+'</td><td>'+
                                    escape(param.get("description", ""))+'</td></tr>')
                    body.append('</table>')
                if "requestBody" in op:
                    body.extend(['<h2>Request body</h2>', definition(op["requestBody"])])
                body.append('<h2>Responses</h2>')
                for status, resp in op["responses"].items():
                    label = status + " " + (resp.get("description") or resp.get("$ref", "").split("/")[-1])
                    body.append('<details><summary>'+escape(label)+'</summary>'+definition(resp)+'</details>')
                body.extend(['<h2>Operation definition</h2>',definition(op)])
                (documents / dest).write_text(page(title, "".join(body)), encoding="utf-8")
                entries.extend([(route, "Method", dest), (op_id, "Function", dest)])
                if title not in (route, op_id):
                    entries.append((title, "Method", dest))
                index.append('<li>'+link(dest, route)+' · '+escape(title)+'</li>')
        index.append('</ul>')
        for group, members in spec["components"].items():
            if members:
                index.append('<h2>'+escape(group)+'</h2><ul>')
                for name, obj in members.items():
                    dest = refs[f"#/components/{group}/{name}"]
                    (documents / dest).write_text(page(name, definition(obj)), encoding="utf-8")
                    entries.append((name, KINDS[group], dest))
                    index.append('<li>'+link(dest, name)+'</li>')
                index.append('</ul>')
        (documents / "index.html").write_text(page("HTTP API reference", "".join(index)), encoding="utf-8")
        entries.append(("HTTP API reference", "Guide", "index.html"))
        with sqlite3.connect(resources / "docSet.dsidx") as db:
            db.execute("CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT)")
            db.execute("CREATE UNIQUE INDEX anchor ON searchIndex(name, type, path)")
            db.executemany("INSERT INTO searchIndex(name,type,path) VALUES(?,?,?)", sorted(entries))
        archive = "Arcmira_API.tgz"
        with (output / archive).open("wb") as out, gzip.GzipFile(filename="",fileobj=out,mode="wb",mtime=0) as gz:
            with tarfile.open(fileobj=gz,mode="w") as tar:
                for f in sorted(root.rglob("*")):
                    if f.is_file():
                        info = tarfile.TarInfo(f.relative_to(root.parent).as_posix())
                        info.size = f.stat().st_size
                        with f.open("rb") as src:
                            tar.addfile(info,src)
    meta = {"name": "Arcmira API", "version": version+"/"+digest[:12], "archive": archive,
            "author": {"name": "Arcmira", "link": "https://arcmira.com"},
            "aliases": ["Arcmira", "YouTube transcript search API"]}
    (output / "docset.json").write_text(json.dumps(meta, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, help="use a saved copy of the published OpenAPI JSON")
    parser.add_argument("--output", type=Path, default=HERE)
    args = parser.parse_args()
    if args.spec:
        raw = args.spec.read_bytes()
    else:
        with urlopen(SOURCE,timeout=30) as response:
            raw = response.read()
    build(raw,args.output)
