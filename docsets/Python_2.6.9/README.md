[Python](https://www.python.org)
=======================

### Author

[jixiangqd][1]


### Docset Generation Steps

- Download the [Python 2.6.9 source code][2], get into Doc dir use 
 ```
 sphinx-build -b html -d build/doctrees -C -D latex_paper_size=  . build/html
 ```
- to build doc html.
- Then use 
 ```
 doc2dash --name "Python 2.6.9" -f -a -i icon.png build/html
 ```
- build Docset
-
- [1]: https://github.com/jixiangqd
- [2]: https://www.python.org/ftp/python/2.6.9/Python-2.6.9.tgz
