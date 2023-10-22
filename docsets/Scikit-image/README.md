# scikit-image Dash Docset

[scikit-image](http://scikit-image.org/) is a collection of algorithms for image processing in python.

## Authors

- [Aziz Alto](https://github.com/iamaziz)
- [Xavier Yang](https://github.com/ivaquero)

## Instructions

- download the latest document from https://github.com/scikit-image/
- comment some blocks in `source/conf.py`
- `make html`
- remove `_downloads` and `_sources` in `doc/build/html`
- run the following commands

```bash
doc2dash -v -n scikit-image -i scikit-image-main/doc/build/html/_static/logo.png -I scikit-image-main/doc/build/html/index.html scikit-image-main/doc/build/html
tar cvzf scikit-image.tgz scikit-image.docset
```
