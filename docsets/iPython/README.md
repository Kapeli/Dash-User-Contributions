iPython Dash Docset
=======================

- __Docset Description__:
    - iPython is an awesome interactive Python.

- __Author__:
    - [Aziz Alto](https://github.com/iamaziz)

- Instructions to generate the docset:
    - fetch html: 
    	- `httrack "http://ipython.org/ipython-doc/stable/" -O "iPython" "+*ipython.org/ipython-doc/stable/*" -v`
    - generate docset:
    	- `doc2dash -v -n iPython ipython.org/ipython-doc/stable/`
    - Set Info.plist to index page: 
    	- `dashIndexFilePath: index.html`
    - Add icon.
