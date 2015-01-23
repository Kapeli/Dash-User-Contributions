PyMongo Dash Docset
=======================

[PyMongo](http://api.mongodb.org/python) is the Python driver for MongoDB.

### Author:

Docset compiled by [Georg Barikin](https://github.com/gebrkn).

### How to build:

- install [doc2dash](https://pypi.python.org/pypi/doc2dash)

- get [PyMongo](https://github.com/mongodb/mongo-python-driver.git)

- build sphinx docs and the docset:

```
make -C mongo-python-driver/doc SPHINXOPTS="-D html_theme_options.nosidebar=1" html
doc2dash -fv --name PyMongo --index-page index.html mongo-python-driver/doc/_build/html
````
