PyGraphviz docset
=======================

- __Docset Description__:
    - [PyGraphviz](http://pygraphviz.github.io/) is a Python interface to the Graphviz graph layout and visualization package.

- __Author__:
    - [Aziz Alto](https://github.com/iamaziz)

- __How to generate the docset__:
    - Download the [zipped HTML documentation](http://pygraphviz.github.io/documentation/pygraphviz-1.3rc1/)
    - generate the docset:
    	- `doc2dash -v -n PyGraphviz pygraphviz-documentation/`
    - Set Info.plist to index page:
    	- `dashIndexFilePath: index.html`
    
