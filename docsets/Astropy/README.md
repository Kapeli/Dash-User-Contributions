Astropy Dash Docset
=======================

- __Docset Description__:
    - [Astropy](http://www.astropy.org/) is a community python library for Astronomy.

- Author:
    - [Aziz Alto](https://github.com/iamaziz)

- Instructions to generate the docset:
    - fetch html: 
    	- `httrack "http://docs.astropy.org/en/stable/" -O "Astropy" "+*docs.astropy.org/en/stable/*" -v`
    - generate docset:
    	- `doc2dash -v -n Astropy Astropy/docs.astropy.org/en/stable/`.
    - set [index page](http://kapeli.com/docsets#settingindexpage) in Info.plist:
    	- `dashIndexFilePath: index.html`
    - [add icon](http://kapeli.com/docsets#addingicon).