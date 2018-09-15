Pandoc Docset
=============

Description
-----------
[Pandoc](http://pandoc.org/) is a universal document converter. You can also find [it on github](https://github.com/jgm/pandoc).

Authors
-------
- [Aziz Alto](https://github.com/iamaziz)
- [Bernhard Waldbrunner](https://github.com/vbwx)

How to generate the docset
--------------------------
- Run `Pandoc-to-dash.py`
- Delete unnecessary files in `Pandoc.docset/Contents/Resources/Documents`
- Run `fix-pages.pl`

Prerequisites
-------------
- [HTTrack](http://www.httrack.com)
- Python package BeautifulSoup
- Perl modules HTML::Strip, URI::Encode, String::Util
