[mypy](https://github.com/python/mypy)
=======================

**Docset description:**
[mypy](https://www.mypy-lang.org/) is an optional static type checker for Python.

**Author:**
This docset was originally created by [NeuroForLunch](https://github.com/NeuroForLunch)
(mypy `0.9.1`) and updated to the current release by
[pleasedodisturb](https://github.com/pleasedodisturb).

**How to generate the docset:**

- Clone mypy at the release tag and build its Sphinx docs (`furo` theme):

        git clone --branch v2.3.0 https://github.com/python/mypy.git
        python -m venv .venv && source .venv/bin/activate
        pip install "mypy==2.3.0" sphinx furo myst-parser sphinx_inline_tabs
        sphinx-build -b html mypy/docs/source mypy/docs/_build/html

- Run [doc2dash](https://github.com/drgrib/doc2dash) on the built HTML, setting
  the index page and the online-redirect (fallback) URL:

        doc2dash -n mypy \
            -I index.html \
            -u "https://mypy.readthedocs.io/en/stable/" \
            mypy/docs/_build/html

- Archive the docset:

        tar --exclude='.DS_Store' -cvzf mypy.tgz mypy.docset

- Copy the archived docset `mypy.tgz` to two locations (keep the filename the same):
    1. `versions/<version>/` sub-folder (e.g. `versions/2.3.0/mypy.tgz`)
    2. the main `docsets/mypy` folder

- Update the `version` and `specific_versions` in `docset.json`.
