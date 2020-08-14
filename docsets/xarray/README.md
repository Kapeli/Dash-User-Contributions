xarray Docset
=======================

This docset was created by Florian Knoop ([Twitter](https://twitter.com/floknoo) · [GitHub](https://github.com/flokno))

It contains documentation from [xarray.pydata.org](http://xarray.pydata.org/en/stable/), which describes `xarray`, and was generated with [doc2dash](https://doc2dash.readthedocs.io/en/stable/index.html).

Details on how to build the `xarray` documentation can be found [here](http://xarray.pydata.org/en/stable/contributing.html#how-to-build-the-xarray-documentation).

## Details

- Version: `0.12.3`

- Date: `2019-08-01`

- Custom options in `sphinx` `conf.py` in order to remove sidebar:

```python
html_theme = 'alabaster'

html_theme_options = {
    'logo_only': True,
    'nosidebar': True,
}
```


