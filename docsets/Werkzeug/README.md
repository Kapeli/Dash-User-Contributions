Werkzeug Docset
=======================

[Werkzeug](https://github.com/pallets/werkzeug) is a comprehensive WSGI web application library.

### Author:

Docset created by [Byron Yi](https://github.com/byronyi).

Updated by [Torin Kwok](https://github.com/torinkwok) to v0.16.1.

Updated by [Torin Kwok](https://github.com/torinkwok) to v1.0.1.

### How to build:

- Install [doc2dash](https://pypi.python.org/pypi/doc2dash)

- Get [Werkzeug's latest release](https://github.com/pallets/werkzeug/releases)

- Build Sphinx docs and the docset:

```shell
make -C werkzeug/docs SPHINXOPTS="-D html_theme_options.nosidebar=1" html 

doc2dash -fv --name Werkzeug --index-page index.html werkzeug/docs/_build/html
```