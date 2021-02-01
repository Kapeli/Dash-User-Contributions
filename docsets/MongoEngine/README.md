MongoEngine
=======================

[MongoEngine](http://mongoengine.org) is a Document-Object Mapper (think ORM, but for document databases) for working with MongoDB from Python.

### Author:

MongoEngine Author:	Harry Marr (http://github.com/hmarr)
Maintainer:	Ross Lawley (http://github.com/rozza)

Updated by [AZLisme](https://github.com/AZLisme).

### How to build:

- install [doc2dash](https://pypi.python.org/pypi/doc2dash)

- get [MongoEngine](https://github.com/MongoEngine/mongoengine.git)

- build sphinx docs and the docset:

```
make -C mongoengine/docs html
doc2dash -fv --name MongoEngine --index-page index.html mongoengine/docs/_build/html
````
