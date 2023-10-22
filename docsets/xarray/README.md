# Xarray Docset

[xarray](https://github.com/pydata/xarray) is an open source project and Python package that makes working with labelled multi-dimensional arrays simple, efficient, and fun!

## Authors

- Florian Knoop ([Twitter](https://twitter.com/floknoo) · [GitHub](https://github.com/flokno))
- Xavier Yang ([GitHub](https://github.com/ivaquero))

## Instructions

- download the latest document from https://github.com/pydata/xarray
- unpack the zip file
- `cd xarray-main/doc`
- comment `intersphinx_mapping` block
- custom options in `sphinx` `conf.py` in order to remove sidebar

```python
html_theme = 'alabaster'

html_theme_options = dict(
    logo_only=True,
    nosidebar=True,
)
```

- run the following commands

```bash
make html
doc2dash -v -n xarray -i xarray-main/doc/_build/html/_static/dataset-diagram-square-logo -I xarray-main/doc/_build/html/index.html xarray-main/doc/_build/html
tar cvzf xarray.tgz xarray.docset
```

## More details

Details on how to build the `xarray` documentation can be found [here](http://xarray.pydata.org/en/stable/contributing.html#how-to-build-the-xarray-documentation).
