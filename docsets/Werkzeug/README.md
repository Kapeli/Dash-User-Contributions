Werkzeug Docset
=======================

Author: [Byron Yi](https://github.com/byronyi)

First make sure the [doc2dash](https://doc2dash.readthedocs.org/)
tool is installed.
```shell
pip install doc2dash
```

To generate the docset, clone the Wergzeug [github
repository](https://github.com/mitsuhiko/werkzeug),
and then use the following script.
```shell
git clone https://github.com/mitsuhiko/werkzeug.git
cd werkzeug/docs
make html
cd _build/html
doc2dash -n Werkzeug -i _static/werkzeug.png --index-page index.html -a .
```
