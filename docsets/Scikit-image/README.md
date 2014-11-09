Scikit-image Dash Docset
=======================

- Docset Description:
    - [Scikit-image](http://scikit-image.org/) is a collection of algorithms for image processing in python.

- Author:
    - [Aziz Alto](https://github.com/iamaziz)

- Instructions to generate the docset:
    - fetch html:
    	- `httrack "http://scikit-image.org/docs/0.10.x/" -O "Scikit-image" "+*scikit-image.org/docs/0.10.x/*" -v`
    - generate docset:
    	- `doc2dash -v -n Scikit-image Contents/Resources/Documents/scikit-image.org/docs/0.10.x/`
    - set [index page](http://kapeli.com/docsets#settingindexpage) in Info.plist:
    	- `dashIndexFilePath: index.html`
    - [add icon](http://kapeli.com/docsets#addingicon).
