more_itertools Docset
=================

* Author: Dan Girellini (https://github.com/dangitall)
* Instructions:
 * clone https://github.com/erikrose/more-itertools.git
 * `cd pytest/doc`
 * Apply this patch:
 ```
diff --git a/docs/conf.py b/docs/conf.py
index 8adf15f..36f62fc 100644
--- a/docs/conf.py
+++ b/docs/conf.py
@@ -13,7 +13,7 @@
 
 import sys, os
 
-import sphinx_rtd_theme
+# import sphinx_rtd_theme
 
 # If extensions (or modules to document with autodoc) are in another directory,
 # add these directories to sys.path here. If the directory is relative to the
@@ -93,7 +93,7 @@ pygments_style = 'sphinx'
 
 # The theme to use for HTML and HTML Help pages.  See the documentation for
 # a list of builtin themes.
-html_theme = 'sphinx_rtd_theme'
+html_theme = 'basic'
 
 # Theme options are theme-specific and customize the look and feel of a theme
 # further.  For a list of options available for each theme, see the
@@ -101,7 +101,7 @@ html_theme = 'sphinx_rtd_theme'
 #html_theme_options = {}
 
 # Add any paths that contain custom themes here, relative to this directory.
-html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
+# html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
 
 # The name for this set of Sphinx documents.  If None, it defaults to
 # "<project> v<release> documentation".
```
 * `sphinx-build docs docbuild` (install sphinx via pip)
 * `cd docbuild``
 * `cp .../dashing.json .`
 * `dashing build -s . -f dashing.json` (https://github.com/technosophos/dashing)
 * add this to the Contents/Info.plist dict:

```
   <key>DashDocSetFallbackURL</key>
   <string>https://hypothesis.readthedocs.io/en/latest/</string>
```
