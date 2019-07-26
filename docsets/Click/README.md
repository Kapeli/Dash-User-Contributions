Click Docset
============

> [Click](http://click.palletsprojects.com/) is a Python package for creating beautiful command line interfaces in a composable way with as little code as necessary. It’s the “Command Line Interface Creation Kit”. It’s highly configurable but comes with sensible defaults out of the box. It aims to make the process of writing command line tools quick and fun while also preventing any frustration caused by the inability to implement an intended CLI API.

This docset was created by [Robert Coup](https://github.com/rcoup) from the [Click](https://github.com/pallets/click/) Sphinx documentation.

To generate this docset:

```console
$ git clone --branch=dash-docset https://github.com/rcoup/click.git
$ cd click
$ virtualenv venv
$ source venv/bin/activate
$ pip install sphinx doc2dash
$ cd docs
$ make dashdoc
```

This will generate `docs/_build/Click.docset` and `docs/_build/Click.tgz`.

* https://github.com/pallets/click/pull/1360 is a PR to include the Dash docset generation into the main Click repository.

Known Issues
------------

* Some of the section names aren't fantastic.

