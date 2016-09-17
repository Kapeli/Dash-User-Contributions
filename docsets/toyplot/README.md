# Toyplot Docset

[toyplot](https://toyplot.readthedocs.io) docset for
[Dash](http://kapeli.com/dash). Maintailed by
[Zhang YANG](https://github.com/ProgramFan).

## How to generate the docset

* Download toyplot source and extract it to `toyplot-xxx`
* Build document with sphinx
  * `cd toyplot-xxx/docs && make html`
* Build docset with [doc2dash](https://pypi.python.org/pypi/doc2dash)
  * `cd toyplot-xxx/docs && doc2dash _build/html`
  * Find `html.docset` at `toyplot-xxx/docs`

## Prerequesties

Install the following python packages:

* sphinx
* sphinx_rtd_theme
* sphinxcontrib_napoleon
* doc2dash
