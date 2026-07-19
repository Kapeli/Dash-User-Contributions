FastAPI Docset
=======================

**Docset description:**
[FastAPI](https://fastapi.tiangolo.com/) is a modern, high-performance web
framework for building APIs with Python, based on standard type hints.

**Author:**
Contributed by [pleasedodisturb](https://github.com/pleasedodisturb). There was
no existing official or User-Contributed FastAPI docset.

**How to generate the docset:**

FastAPI's docs are a [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
site built with [zensical](https://github.com/squidfunk/zensical), so there is no
Sphinx `objects.inv` for `doc2dash`. A small generator builds the docset directly
from the built HTML.

- Clone FastAPI at the release tag and build the English docs:

        git clone --branch 0.139.2 https://github.com/fastapi/fastapi.git
        cd fastapi
        python -m venv .venv && source .venv/bin/activate
        pip install -e ".[standard]" black cairosvg griffe-typingdoc \
            griffe-warnings-deprecated jieba markdown-include-variants mdx-include \
            "mkdocstrings[python]" pillow python-slugify pyyaml typer ruff httpx \
            "zensical>=0.0.42" mkdocs-material
        python scripts/docs.py build-lang en        # -> ./site

- Localize the site's own absolute asset links and generate the docset with the
  `make_docset.py` script (a generic Material-for-MkDocs -> Dash indexer):

        python localize_assets.py site "https://fastapi.tiangolo.com/"
        python make_docset.py site FastAPI.docset FastAPI \
            "https://fastapi.tiangolo.com/" icon.png icon@2x.png

  The generator: copies the site into the docset; writes `Info.plist`
  (`dashIndexFilePath`, `DashDocSetFallbackURL`, no version); builds the SQLite
  index — each page as `Guide`, `h2` sections as `Section`, and mkdocstrings API
  symbols as typed entries (`Class`/`Method`/`Function`/`Attribute`/`Module`);
  injects Dash Table-of-Contents anchors; and rewrites site-absolute navigation
  links to relative paths so every page works offline.

- Archive the docset:

        tar --exclude='.DS_Store' -cvzf FastAPI.tgz FastAPI.docset

- Copy the archive to the main `docsets/FastAPI` folder and to `versions/0.139.2/`.

**Icon:**

- FastAPI's project icon, from `docs/en/docs/img/favicon.png` in the FastAPI repository.

**Note on offline use:** all rendering assets (Material theme CSS/JS and images)
are bundled locally. The only remaining external references are the CDN-hosted
Swagger UI / ReDoc bundles on the three "how-to" pages that specifically
demonstrate loading those tools from a CDN (unavoidable — the pages are about
that), and a newsletter widget on one page.
