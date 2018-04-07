Blender Docset
=======================

Author:

* Alex Widener
    * [Github](http://www.github.com/alexwidener)
    * [Website](http://alexwidener.com)

Generating docsets for Blender in the future:

Prerequisite(MacOS):
[doc2dash](https://github.com/hynek/doc2dash/ "doc2dash")

    pip install --user doc2dash

* Blender documentation is generated through Sphinx.
* Download the link on the Blender Python API page that says "This site can be downloaded for offline use"
* If it doesn't have the Sphinx searchtools.js file [download it from here](http://sphinx-doc.org/_static/searchtools.js "searchtools.js")
* Put searchtools.js into the _static folder. (if it doesn't exist. Newer versions appear to have this file)
* Terminal: cd to the Blender directory that holds genindex.html
* Terminal: doc2dash Blender
* That's all!

Updated to add the latest version currently, 2.79
