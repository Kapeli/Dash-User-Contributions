mlpy Dash Docset
=======================

- __Docset Description__:
    - [Machine Learning PYthon (mlpy)](http://mlpy.sourceforge.net/docs/3.5/) is a high-performance Python library for predictive modeling.

- __Author__:
    - [Aziz Alto](https://github.com/iamaziz)

- __How to generate the docset__:
    - fetch html: 
    	- `httrack "http://mlpy.sourceforge.net/docs/3.5/" -O "mlpy" "+*mlpy.sourceforge.net/docs/3.5/*" -v`
    - generate docset: 
    	- `doc2dash -v -n mlpy mlpy.sourceforge.net/docs/3.5/`
    - Set Info.plist to index page: 
    	- `dashIndexFilePath: index.html`
    - Add icon.
    
