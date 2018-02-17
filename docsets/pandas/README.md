pandas Dash Docset
=======================

- __Docset Description__:
    - *pandas* is a Python package providing fast, flexible, and expressive data structures designed to make working with "relational" or "labeled" data both easy and intuitive.

- Author:
    - [Allan Kent](https://github.com/allank)

- __Docset repo__:
    - Pandas latest docset source can be found at [https://github.com/pandas-dev/pandas/tree/master/doc](https://github.com/pandas-dev/pandas/tree/master/doc)
    - Zipped, compiled HTML (via Sphinx) can be downloaded from [http://pandas.pydata.org/pandas-docs/stable/pandas.zip](http://pandas.pydata.org/pandas-docs/stable/pandas.zip)

- Instructions to generate the docset:
    - Fetch the compiled Sphinx HTML from [http://pandas.pydata.org/pandas-docs/stable/pandas.zip](http://pandas.pydata.org/pandas-docs/stable/pandas.zip)
    - Icons for the Docset are included in this repo
    - Install [https://pypi.python.org/pypi/doc2dash](https://pypi.python.org/pypi/doc2dash)
    - Run `doc2dash`, changing the path of the icon file to point to the icon file in this repo, and specifying the downloaded Sphinx files:
    - `doc2dash -A -f -i /Users/allank/Documents/Dev/Dash-User-Contributions/docsets/pandas/icon@2x.png -I index.html -j pandas`