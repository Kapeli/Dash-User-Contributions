Hypothesis Docset
=================

* Author: Dan Girellini (https://github.com/dangitall)
* Instructions:
 * clone https://github.com/HypothesisWorks/hypothesis-python.git
 * `cd hypothesis-python`
 * Apply this patch:
 ```
 diff --git a/docs/conf.py b/docs/conf.py
index b705f57..2831c4a 100644
--- a/docs/conf.py
+++ b/docs/conf.py
@@ -68,9 +68,10 @@ intersphinx_mapping = {
 # -- Options for HTML output ----------------------------------------------

 if not on_rtd:  # only import and set the theme if we're building docs locally
-    import sphinx_rtd_theme
-    html_theme = 'sphinx_rtd_theme'
-    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
+    html_theme = 'basic'
+    html_theme_options = {
+        'nosidebar': True
+    }

 html_static_path = ['_static']
```
 * `sphinx-build docs docbuild` (install sphinx via pip)
 * `cd docbuild``
 * create dashing.json:

````
{
    "name": "Hypothesis",
    "package": "hypothesis",
    "index": "index.html",
    "selectors": {
        "dl.function code.descname": "Method",
        "dl.attribute code.descname": "Attribute",
        "div.section h1": {
            "type": "Category",
            "regexp": "¶",
            "replacement": ""
        },
        "div.section h2": {
            "type": "Section",
            "matchpath": "examples|data|details|development|django|healthchecks|index|packaging|quick|settings|stateful|usage",
            "regexp": "¶",
            "replacement": ""
        }
    },
    "ignore": [
        "ABOUT"
    ],
    "icon32x32": "",
    "allowJS": false,
    "ExternalURL": ""
}
````
 * `dashing build -s . -f dashing.json` (https://github.com/technosophos/dashing)
 * add this to the Contents/Info.plist dict:

````
   <key>DashDocSetFallbackURL</key>
   <string>https://hypothesis.readthedocs.io/en/latest/</string>
````
