Scikit-image Dash Docset
=======================

- Docset Description:
    - [Scikit-image](http://scikit-image.org/) is a collection of algorithms for image processing in python.

- Author:
    - [Aziz Alto](https://github.com/iamaziz)

- Instructions to generate the docset:
    - clone the docs repo (this may take a while as the repo is quite heavy):
        - `git clone https://github.com/scikit-image/docs scikit-image-docs`
    - checkout the html branch
        - `git checkout gh-pages`
    - download the icon
        - `wget https://raw.githubusercontent.com/Kapeli/Dash-User-Contributions/master/docsets/Scikit-image/icon%402x.png -O icon.png`
    - generate docset:
    	- `doc2dash --verbose --name Scikit-image --icon icon.png --index-page index.html --enable-js 0.16.x`
