pandas docset
=======================

- __Docset Description__:
    - [pandas](http://pandas.pydata.org/) is an awesome python library for data analysis.

- __Author__:
    - [Aziz Alto](https://github.com/iamaziz)

- __How to generate the docset__:
    - Download the [zipped HTML documentation](http://pandas.pydata.org/pandas-docs/stable/)
    - generate the docset:
    	- `doc2dash -v -n pandas path/to/downloaded/documentation`
    - Set Info.plist to index page:
    	- `dashIndexFilePath: index.html`
    - Add icon.
    
