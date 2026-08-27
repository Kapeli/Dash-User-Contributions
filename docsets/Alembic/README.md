Alembic Docset
=======================

**Docset description:**
[Alembic](https://alembic.sqlalchemy.org/) is a lightweight database migration
tool for usage with the [SQLAlchemy](https://www.sqlalchemy.org/) Database
Toolkit for Python.

**Author:**
The Alembic documentation is written by [Mike Bayer](https://github.com/sqlalchemy/alembic).
This docset was originally created by [Ashera Scout](https://github.com/asheraScout)
(Alembic `0.8.4`, 2015) and updated to the current release by
[pleasedodisturb](https://github.com/pleasedodisturb).

**How to generate the docset:**

- Clone Alembic at the release tag and build its Sphinx docs (source lives at
  [github.com/sqlalchemy/alembic](https://github.com/sqlalchemy/alembic),
  published at [alembic.sqlalchemy.org](https://alembic.sqlalchemy.org/)):

        git clone --branch rel_1_18_5 https://github.com/sqlalchemy/alembic.git
        python -m venv .venv && source .venv/bin/activate
        pip install "alembic==1.18.5" sphinx sphinx-book-theme \
            sphinx_copybutton Mako sphinx-paramlinks changelog
        sphinx-build -b html alembic/docs/build alembic/docs/build/output/html

- Run [doc2dash](https://github.com/drgrib/doc2dash) on the built HTML, setting
  the index page and the online-redirect (fallback) URL, and adding the icon:

        doc2dash -n Alembic \
            -I index.html \
            -u "https://alembic.sqlalchemy.org/en/latest/" \
            -i icon.png --icon-2x icon@2x.png \
            alembic/docs/build/output/html

- Archive the docset:

        tar --exclude='.DS_Store' -cvzf Alembic.tgz Alembic.docset

- Copy the archived docset `Alembic.tgz` to two locations (keep the filename the same):
    1. `versions/<version>/` sub-folder (e.g. `versions/1.18.5/Alembic.tgz`)
    2. the main `docsets/Alembic` folder

- Update the `version` and `specific_versions` in `docset.json`.

**Icon:**

- The SQLAlchemy project mark, from https://www.sqlalchemy.org/favicon.ico
