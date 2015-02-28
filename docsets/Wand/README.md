Wand Docset
=======================

Wand is a ctypes-based simple ImageMagick binding for Python.

* Author: [Hong Minhee](https://github.com/dahlia/wand)
* Docset by: [Joao](https://github.com/joaoponceleao)
* Instructions to generate docset:
    - Clone the Wand [repo](https://github.com/dahlia/wand)
    - Install [doc2dash](https://pypi.python.org/pypi/doc2dash) in a virtualenv
    - Follow the doc2dash [instructions](https://doc2dash.readthedocs.org/en/2.0.2/) and Kapelli's [guidelines](http://kapeli.com/docsets):
        + heme, layout and rst files underwent minor cosemtic changes to work inside Dash
        + `make html`
        + `doc2dash -n Wand -i _static/icon.png -I index.html -v _build/html -a`
