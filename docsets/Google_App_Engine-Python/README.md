Google App Engine - Python Docset
=======================

[GAE](https://github.com/GoogleCloudPlatform/google-cloud-python) Python API docset for [Dash](http://kapeli.com/dash).

 * Author: [HyShai](//github.com/hyshai) 
 
#### How to generate docset:

- clone repo and setup venv:

```sh
git clone https://github.com/GoogleCloudPlatform/google-cloud-python.git
cd google-cloud-python/
virtualenv venv
source venv/bin/activate
pip install -r docs/requirements.txt
python setup.py install
pip install -U sphinx
cd docs/
```

- apply this patch to `conf.py`: 
```
--- conf.old	2016-11-18 00:14:27.000000000 -0500
+++ conf.py	2016-11-18 00:17:06.000000000 -0500
@@ -119,9 +119,10 @@
 # The theme to use for HTML and HTML Help pages.  See the documentation for
 # a list of builtin themes.
 
-if not ON_READ_THE_DOCS:
-    html_theme = 'sphinx_rtd_theme'
-    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
+html_theme = 'basic'
+html_theme_options = {
+    'nosidebar' : True
+}
 
 # Theme options are theme-specific and customize the look and feel of a theme
 # further.  For a list of options available for each theme, see the
 
```

- then:
```sh
make html
cd ..
doc2dash -n "GAE-Python" -i docs/_static/images/gcp-logo-32x32.png -j -u https://googlecloudplatform.github.io/google-cloud-python/stable/ -f docs/_build/html/
```
