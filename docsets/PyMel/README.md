PyMel Docset
=======================

Author:

* Alex Widener
    * [Github](http://www.github.com/alexwidener)
    * [Twitter](http://www.twitter.com/globalproctd)
    * [Website](http://alexwidener.com)

Generating docsets for PyMel in the future:

Prerequisite(OSX):
[doc2dash](https://github.com/hynek/doc2dash/ "doc2dash")

    pip install --user doc2dash

* PyMel documentation is generated through Sphinx.
* Used Windows web scraper [WinHTTrack Website Copier](http://www.httrack.com/page/2/)
* Point it to the [base URL for PyMel documentation](http://help.autodesk.com/cloudhelp/2016/ENU/Maya-Tech-Docs/PyMel/ "PyMel docs")
* Give it about 30 minutes. It took a while on an SSD & 100Meg down internet connection.
* Once it's done, it doesn't have the Sphinx searchtools.js file so [download it from here](http://sphinx-doc.org/_static/searchtools.js "searchtools.js")
* Put searchtools.js into the _static folder.
* Copy folders back to OS X
* Terminal: cd to the PyMel directory that holds genindex.html
* Terminal: doc2dash PyMel
* That's all!

No known bugs, works fine.
PyMel doesn't have an icon. Sorry.

