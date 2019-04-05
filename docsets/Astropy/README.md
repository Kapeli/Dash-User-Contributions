Astropy Dash Docset
=======================

- __Docset Description__:
    - [Astropy](http://www.astropy.org/) is a community python library for Astronomy.

- Authors:
    - [Aziz Alto](https://github.com/iamaziz) Original version
    - [William Henney](https://github.com/deprecated) Update to version 1.2. Generate HTML docs from source instead of mirroring from readthedocs
    - [Simon Conseil](https://github.com/saimn) Update to version 1.3, 2.0, 3.1.

- Instructions to generate the docset:
	- Download Astropy source to a temporary folder `SRCDIR`
	  - `cd $SRCDIR; git clone https://github.com/astropy/astropy.git`
    - Build the html documentation:
	  - `cd $SRCDIR/astropy; python setup.py build_docs`
    - Generate docset:
      - `doc2dash -v -n Astropy -I index.html -u http://docs.astropy.org/en/stable/ $SRCDIR/astropy/docs/_build/html`.
    - [Add icon](http://kapeli.com/docsets#addingicon):
	  - `cp icon*.png Astropy.docset`
	- Edit metadata (version) in `docset.json`.
    - To avoid a file name conflicts for case-insensitive system, it may be
      needed to rename some files:
      - `mv Astropy.docset/Contents/Resources/Documents/api/astropy.units.function.logarithmic.{m_bol,m_bol_renamed}.html`
      - `sqlite3 ./Astropy.docset/Contents/Resources/docSet.dsidx "UPDATE searchIndex SET path = 'api/astropy.units.function.logarithmic.m_bol_renamed.html#astropy.units.function.logarithmic.m_bol' WHERE name = 'astropy.units.function.logarithmic.m_bol' ;"`
    - Create archive:
      - `tar --exclude='.DS_Store' -cvzf Astropy.tgz Astropy.docset`
