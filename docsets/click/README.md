click Docset
=======================

This docset was created by Florian Knoop ([Twitter](https://twitter.com/floknoo) · [GitHub](https://github.com/flokno))

It contains documentation from [click](https://click.palletsprojects.com/en/8.0.x/), which describes `click`, and was generated with [doc2dash](https://doc2dash.readthedocs.io/en/stable/index.html).

## How to build the docset.

1. Clone the `click` repository from https://github.com/pallets/click/.

2. Check out the branch or tag corresponding to the version you are building.

3. Update `docs/conf.py` for display in Dash following this diff:

```python
-html_theme = "click"
-html_theme_options = {"index_sidebar_logo": False}
+html_theme = "basic"
+html_theme_options = {"nosidebar": True}
```

4. Build with `tox -e docs`.

5. Generate the docset with `doc2dash`: `doc2dash -a -n click -u https://click.palletsprojects.com/en/<version>/ -i icon\@2x.png html/`.

6. Finally, archive the docset: `tar --exclude='.DS_Store' -cvzf click.tgz click.docset`.
