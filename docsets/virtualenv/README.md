virtualenv Docset
=======================

* Author: Dan Girellini (https://github.com/dangitall)
* Instructions:
 * clone https://github.com/pypa/virtualenv.git
 * `cd virtualenv`
 * apply this patch:

```
diff --git a/docs/conf.py b/docs/conf.py
index 9332aa1..43f1e3d 100644
--- a/docs/conf.py
+++ b/docs/conf.py
@@ -87,14 +87,10 @@ extlinks = {
 # given in html_static_path.
 #html_style = 'default.css'

-html_theme = 'default'
-if not on_rtd:
-    try:
-        import sphinx_rtd_theme
-        html_theme = 'sphinx_rtd_theme'
-        html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
-    except ImportError:
-        pass
+html_theme = 'basic'
+html_theme_options = {
+    'nosidebar': True
+}
```
 * `sphinx-build docs docbuild`
 * Copy dashing.json to docbuild
 * `dashing build`
 * add this to the Contents/Info.plist dict:

````
   <key>DashDocSetFallbackURL</key>
   <string>https://virtualenv.pypa.io/en/stable/</string>
````