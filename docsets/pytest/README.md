pytest Docset
=================

* Author: Dan Girellini (https://github.com/dangitall)
* Instructions:
 * clone https://github.com/pytest-dev/pytest
 * `cd pytest/doc`
 * Apply this patch:
 ```
 diff --git a/doc/en/conf.py b/doc/en/conf.py
index 5941716a..b91c3bf1 100644
--- a/doc/en/conf.py
+++ b/doc/en/conf.py
@@ -123,12 +123,12 @@ html_theme_path = ["_themes"]

 # The theme to use for HTML and HTML Help pages.  See the documentation for
 # a list of builtin themes.
-html_theme = "flask"
+html_theme = "basic"

 # Theme options are theme-specific and customize the look and feel of a theme
 # further.  For a list of options available for each theme, see the
 # documentation.
-html_theme_options = {"index_logo": None}
+html_theme_options = {"nosidebar": True}

 # Add any paths that contain custom themes here, relative to this directory.
 # html_theme_path = []
```
 * `tox -e docs` (install tox via pip)
 * `cd doc/en/_build`
 * `cp .../icon@2x.png .`
 * `doc2dash -A -n pytest --online-redirect-url https://docs.pytest.org/en/latest/contents.html -i icon@2x.png html/ -f`
