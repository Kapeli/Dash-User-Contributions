# pytest Docset

- Author: Dan Girellini (https://github.com/dangitall)
- Instructions:
- clone https://github.com/pytest-dev/pytest
- `cd pytest`
- Apply this patch:

```diff
diff --git a/doc/en/conf.py b/doc/en/conf.py
index 9558a75f9..ed87be7d0 100644
--- a/doc/en/conf.py
+++ b/doc/en/conf.py
@@ -149,8 +149,8 @@ linkcheck_workers = 5
 # -- Options for HTML output ----------------------------------------------------------
 # https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

-html_theme = "furo"
-html_theme_options = {"sidebar_hide_name": True}
+html_theme = "basic"
+html_theme_options = {"nosidebar": True}

 html_static_path = ["_static"]
 html_css_files = [
diff --git a/doc/en/requirements.txt b/doc/en/requirements.txt
index 0637c967b..942c3c361 100644
--- a/doc/en/requirements.txt
+++ b/doc/en/requirements.txt
@@ -11,3 +11,4 @@ packaging
 furo
 sphinxcontrib-towncrier
 sphinx-issues
+towncrier<24.7
diff --git a/tox.ini b/tox.ini
index 61563ca2c..94bb88fa9 100644
--- a/tox.ini
+++ b/tox.ini
@@ -119,6 +119,7 @@ commands =
 setenv =
     # Sphinx is not clean of this warning.
     PYTHONWARNDEFAULTENCODING=
+    LC_ALL=C

 [testenv:docs-checklinks]
 description =
```

- `tox -e docs` (install tox via pip)
- `cd doc/en/`
- `doc2dash -n pytest --online-redirect-url https://docs.pytest.org/en/stable -i _static/pytest1.png html/ -f`
- `tar cvzf pytest.tgz pytest.docset`
