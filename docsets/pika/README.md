pika Docset
=================

* Author: Dan Girellini (https://github.com/dangitall)
* Instructions:
 * clone https://github.com/pika/pika.git
 * `cd pika`
 * Apply this patch:
 ```
diff --git a/docs/conf.py b/docs/conf.py
index 0de2264..3623d0b 100644
--- a/docs/conf.py
+++ b/docs/conf.py
@@ -29,6 +29,7 @@ add_module_names = True
 show_authors = True
 pygments_style = 'sphinx'
 modindex_common_prefix = ['pika']
-html_theme = 'default'
+html_theme = 'basic'
+html_theme_options = {'nosidebar': True}
 html_static_path = ['_static']
 htmlhelp_basename = 'pikadoc'
```
 * `sphinx-build doc docbuild` (install sphinx via pip)
 * `cd docbuild``
 * `cp .../dashing.json .`
 * `dashing build -s . -f dashing.json` (https://github.com/technosophos/dashing)
 * add this to the Contents/Info.plist dict:

```
   <key>DashDocSetFallbackURL</key>
   <string>http://pika.readthedocs.io</string>
```
