# Xarray Docset

[xarray](https://github.com/pydata/xarray) is an open source project and Python package that makes working with labelled multi-dimensional arrays simple, efficient, and fun!

## Authors

- Florian Knoop ([Twitter](https://twitter.com/floknoo) · [GitHub](https://github.com/flokno))
- Xavier Yang ([GitHub](https://github.com/ivaquero))
- Clément Haëck ([GitHub](https://github.com/Descanonge)): Update to 2025.6

## Instructions

- download the latest document from https://github.com/pydata/xarray
- unpack the zip file
- `cd xarray-<version>/doc`
- custom sphinx options in `doc/conf.py` in order to remove sidebar and navbar:
```python
html_sidebars = {"**": []}
html_theme_options = {
    "navbar_start": [],
    "navbar_center": [],
    "navbar_end": [],
    "navbar_persistent": [],
}
```

- deactivate rediraffe plugin to avoid duplicate entries:
- you may have to specify extra arguments to jupyter_sphinx to run correctly locally:
``` python
jupyter_execute_kwargs = dict(
    timeout=-1, allow_errors=True, extra_arguments=["--matplotlib=inline"]
)
```

- build the documentation (details  [here](https://docs.xarray.dev/en/stable/contribute/contributing.html#how-to-build-the-xarray-documentation)):
```bash
pixi run doc
```

- Make a [custom parser](./parser.py) available which will filters duplicate entries:
``` bash
cp /.../parser.py xarray
```

- build the docset:
```bash
pixi run doc2dash -v -n xarray -I index.html -u "https://docs.xarray.dev/en/stable/" \
    --parser xarray.parser.InterSphinxFilter \
    doc/_build/html 
```

- copy icons:
``` bash
cp /.../icons*.png xarray.docset
```

- Create archive:
```bash
tar --exclude=".DS_STORE' -cvzf xarray.tgz xarray.docset
```
