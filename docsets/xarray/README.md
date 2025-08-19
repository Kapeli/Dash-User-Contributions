# Xarray Docset

[xarray](https://github.com/pydata/xarray) is an open source project and Python package that makes working with labelled multi-dimensional arrays simple, efficient, and fun!

## Authors

- Florian Knoop ([Twitter](https://twitter.com/floknoo) · [GitHub](https://github.com/flokno))
- Xavier Yang ([GitHub](https://github.com/ivaquero))
- Clément Haëck ([GitHub](https://github.com/Descanonge)): Update to 2026.6

## Instructions

- download the latest document from https://github.com/pydata/xarray
- unpack the zip file
- `cd xarray-main/doc`
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

- Make available a [custom parser](./parser.py) which will filters duplicate entries:
``` bash
cp parser.py xarray-main/xarray
```

- build the documentation:
```bash
make html
doc2dash -v -n xarray -I index.html -u "https://docs.xarray.dev/en/stable/" \
    --parser xarray.parser.InterSphinxFilter \
    xarray-main/doc/_build/html 
```

- copy icons:
``` bash
cp icons*.png xarray.docset
```

- Create archive:
```bash
tar --exclude=".DS_STORE' -cvzf xarray.tgz xarray.docset
```

## More details

Details on how to build the `xarray` documentation can be found [here](https://docs.xarray.dev/en/stable/contribute/contributing.html#how-to-build-the-xarray-documentation).
