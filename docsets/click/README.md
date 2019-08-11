click Docset
=======================

This docset was created by Florian Knoop ([Twitter](https://twitter.com/floknoo) · [GitHub](https://github.com/flokno))

It contains documentation from [click](https://click.palletsprojects.com/en/7.x/), which describes `click`, and was generated with [doc2dash](https://doc2dash.readthedocs.io/en/stable/index.html).

## Details

- Version: `0.7`

- Date: `2019-08-10`

- Custom options in `sphinx` `conf.py` in order to remove sidebar:

```python
-html_theme_options = {"index_sidebar_logo": False}
+html_theme_options = {"index_sidebar_logo": False, 'nosidebar': True}

```
