Typst Docset
=======================

Docset for [Typst](https://typst.app), the markup-based typesetting system,
built from the official documentation.

- **Author:** [Taliesin Beynon](https://github.com/taliesinb) (GitHub: `taliesinb`)
- **Generator:** https://github.com/taliesinb/typst-dash

How to generate
---------------

The docset is built from the [typst/typst](https://github.com/typst/typst)
repository itself: its `typst-docs` crate compiles the complete official
documentation website (the same content served at typst.app/docs) as a static
site, including a `search.json` that enumerates every documented item.

Prerequisites: a clone of typst/typst, a Rust toolchain, and Python 3.

```sh
git clone https://github.com/taliesinb/typst-dash
cd typst-dash
TYPST_REPO=/path/to/typst ./build.sh v0.15.1
```

This checks out a git worktree of the typst clone at the given release tag,
builds the docs site with `cargo run -p typst-docs --release -- compile`, and
packages `dist/Typst.docset`: the site is copied in, absolute URLs are
rewritten to relative ones so pages work offline, and the SQLite search index
is generated from the site's `search.json` using code-style entry names
derived from routes and anchors (`heading`, `array.at`, `calc.abs`,
`text.size`), typed as Function / Method / Parameter / Type / Module /
Category / Guide.

Then archive it:

```sh
cd dist && tar --exclude='.DS_Store' -czf Typst.tgz Typst.docset
```

Known limitations
-----------------

- Individual math symbols and emoji (the `sym` and `emoji` pages) are indexed
  as two Section pages rather than one entry per symbol.
- Pages keep the site's own navigation sidebar.
