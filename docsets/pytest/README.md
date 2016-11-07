pytest Docset
=================

* Author: Dan Girellini (https://github.com/dangitall)
* Instructions:
 * clone https://github.com/pytest-dev/pytest
 * `cd pytest/doc`
 * Apply this patch:
 ```
diff --git a/doc/en/conf.py b/doc/en/conf.py
index f3b8d7d..e7660fd 100644
--- a/doc/en/conf.py
+++ b/doc/en/conf.py
@@ -110,13 +110,13 @@ html_theme_path = ['_themes']

 # The theme to use for HTML and HTML Help pages.  See the documentation for
 # a list of builtin themes.
-html_theme = 'flask'
+html_theme = 'basic'

 # Theme options are theme-specific and customize the look and feel of a theme
 # further.  For a list of options available for each theme, see the
 # documentation.
 html_theme_options = {
-  'index_logo': None
+    'nosidebar': True
 }

 # Add any paths that contain custom themes here, relative to this directory.
```
 * `sphinx-build en docbuild` (install sphinx via pip)
 * `cd docbuild``
 * `cp .../icon@2x.png .`
 * `cp .../dashing.json .`
 * `dashing build -s . -f dashing.json` (https://github.com/technosophos/dashing)
 * add this to the Contents/Info.plist dict:

```
   <key>DashDocSetFallbackURL</key>
   <string>https://hypothesis.readthedocs.io/en/latest/</string>
```
