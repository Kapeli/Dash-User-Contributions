TensorLayer Docset
=======================


* Authors:
  * Stack:[twitter](https://twitter.com/Stack0149)
  * Weiqiang Li:[mail him](1261707134@qq.com)
* The docset is compiled with [sphinx-build](http://www.sphinx-doc.org/en/master/man/sphinx-build.html) and [doc2dash](https://doc2dash.readthedocs.io/en/stable/)
  * You should git clone the [tensorlayer repo](https://github.com/tensorlayer/tensorlayer)
  * compile html docs according to the official instruction: http://tensorlayer.readthedocs.io/en/stable/
  * cp `deldom.py` in the build html folder and run it.
  * cd into docs/_build,run `doc2dash -A ./html --name TensorLayer -j` and done!
  * You may meet some python dependencies problems,just `pip install some-dependencies` and virtualenv will be your friend