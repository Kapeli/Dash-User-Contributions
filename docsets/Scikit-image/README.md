# scikit-image Dash Docset

[scikit-image](http://scikit-image.org/) is a collection of algorithms for image processing in python.

## Authors

- [Aziz Alto](https://github.com/iamaziz)
- [Xavier Yang](https://github.com/ivaquero)

## Instructions

- download the latest source code from https://github.com/scikit-image/scikit-image/tags
- comment some blocks in `doc/source/conf.py`
- back to `doc`
- `make api & make html`
- remove `_downloads` and `_sources` in `doc/build/html`
- run the following commands

```bash
cd doc
doc2dash -v -n scikit-image -i build/html/_static/logo.png -I scikit-image-0.22.0/doc/build/html/index.html build/html
tar cvzf scikit-image.tgz scikit-image.docset
```
