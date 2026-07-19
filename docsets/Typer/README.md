Typer Docset
=======================

**Docset description:**
[Typer](https://typer.tiangolo.com/) is a library for building CLI applications
in Python, based on type hints. It is built on top of [click](https://click.palletsprojects.com/).

**Author:**
Contributed by [pleasedodisturb](https://github.com/pleasedodisturb). There was
no existing official or User-Contributed Typer docset.

**How to generate the docset:**

Typer's docs are a [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
site built with [zensical](https://github.com/squidfunk/zensical), so there is no
Sphinx `objects.inv` for `doc2dash`. A small generator script builds the docset
directly from the built HTML.

- Clone Typer at the release tag and build its docs:

        git clone --branch 0.27.0 https://github.com/fastapi/typer.git
        cd typer
        python -m venv .venv && source .venv/bin/activate
        pip install -e . cairosvg griffe-typingdoc griffe-warnings-deprecated \
            markdown-include-variants mdx-include "mkdocstrings[python]" pillow \
            pyyaml "zensical>=0.0.42" mkdocs-material
        zensical build            # -> ./site

- Run the generator (`make_docset.py`, included below) on the built site. It:
    - copies the site into `Typer.docset/Contents/Resources/Documents`;
    - writes `Info.plist` (`dashIndexFilePath`, `DashDocSetFallbackURL`, no version);
    - builds the SQLite index — each page as a `Guide`, `h2` sections as `Section`,
      and mkdocstrings API symbols as typed entries (`Class`/`Method`/`Function`/
      `Attribute`/`Module`);
    - injects Dash Table-of-Contents anchors; and
    - rewrites site-absolute (`https://typer.tiangolo.com/…`) navigation links to
      relative paths so every page works offline.

        python make_docset.py site Typer.docset Typer \
            "https://typer.tiangolo.com/" icon.png icon@2x.png

- Archive the docset:

        tar --exclude='.DS_Store' -cvzf Typer.tgz Typer.docset

- Copy the archive to the main `docsets/Typer` folder and to `versions/0.27.0/`.

**Icon:**

- Typer's project icon, from `docs/img/favicon.png` in the Typer repository.

The generator script (`make_docset.py`) is available on request / in the PR
discussion; it is a generic Material-for-MkDocs → Dash indexer.
