Blender Docset
=======================

Author:

* Alex Widener
    * [Github](http://www.github.com/alexwidener)
    * [Twitter](http://www.twitter.com/globalproctd)
    * [Website](http://alexwidener.com)

Generating docsets for Blender in the future:

Prerequisite(OSX):
[doc2dash](https://github.com/hynek/doc2dash/ "doc2dash")

    pip install --user doc2dash

* Blender documentation is generated through Sphinx.
* Used Windows web scraper [WinHTTrack Website Copier](http://www.httrack.com/page/2/)
* Point it to the [base URL for Blender documentation](http://www.blender.org/api/blender_python_api_2_75_1/ "Blender docs")
* Once it's done, it doesn't have the Sphinx searchtools.js file so [download it from here](http://sphinx-doc.org/_static/searchtools.js "searchtools.js")
* Put searchtools.js into the _static folder.
* Copy folders back to OS X
* Terminal: cd to the Blender directory that holds genindex.html
* Terminal: doc2dash Blender
* That's all!

Updated to add the latest version currently, 2.77.1
