Astropy Dash Docset
=======================

- __Docset Description__:
    - [Astropy](http://www.astropy.org/) is a community python library for Astronomy.

- Authors:
    - [Aziz Alto](https://github.com/iamaziz) Original version
    - [William Henney](https://github.com/deprecated) Update to version 1.2. Generate HTML docs from source instead of mirroring from readthedocs
    - [Simon Conseil](https://github.com/saimn) Update to version 1.3, 2.0.

- Instructions to generate the docset:
	- Download Astropy source to a temporary folder `SRCDIR`
	  - `(cd $SRCDIR; git clone https://github.com/astropy/astropy.git)`
    - Build the html documentation:
	  - `(cd $SRCDIR/astropy; python setup.py build_docs)`
    - Generate docset:
      - `doc2dash -v -n Astropy $SRCDIR/astropy/docs/_build/html/`.
    - Set [index page](http://kapeli.com/docsets#settingindexpage) and support for online redirection in `Astropy.docset/Contents/Info.plist`. Add the following keys:

			 <key>dashIndexFilePath</key>
			 <string>index.html</string>
			 <key>DashDocSetFallbackURL</key>
			 <string>http://docs.astropy.org/en/stable/</string>

    - [Add icon](http://kapeli.com/docsets#addingicon):
	  - `cp icon*.png Astropy.docset`
	- Edit metadata in `docset.json`

