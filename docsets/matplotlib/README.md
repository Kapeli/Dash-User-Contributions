matplotlib docset
=======================

- __Docset Description__:
    - [matplotlib](http://matplotlib.org/) is a python library for 2D plotting.

- __Author__:
    - [Aziz Alto](https://github.com/iamaziz)

- __How to generate the docset__:
    - fetch html: 
    	- `httrack "matplotlib.org/1.3.1/" -O "matplotlib" "+*matplotlib.org/*" -v`
    - generate docset: 
    	- `doc2dash -v -n matplotlib matplotlib/matplotlib.org/1.4.3`
    - Set Info.plist to index page:
    	- `dashIndexFilePath: index.html`
    - Add icon.
    
