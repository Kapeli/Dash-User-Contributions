# MLflow Docset

Contributor: Gergely Imreh, `imrehg` on [GitHub](https://github.com/imrehg) and [Twitter](https://twitter.com/imrehg)

## Docset generation instructions

Clone the MLflow source code:
```
git clone https://github.com/mlflow/mlflow.git
cd mlflow
```

Install the pre-requisites:

* For the R docs, need to install [R](https://www.r-project.org/)
* For the Java docs, need a Java runtime and `maven`
* For Python docs, you need Python 3.7, then install the requirements:
```
pip install -r travis/small-requirements.txt
pip install tensorflow "sphinx<2.2" sphinx-click==2.3.0
```

You might need to check if the version number is correct in the source code, that
is in `mflow/version.py`, it should contain
```
...
VERSION = 'x.y.z'
```
where `x.y.z` is the correct version (which you can check with `git describe --tags` for example,
and do not include the `v` reported in that version). The same for the R docs at `mlflow/R/mlflow/DESCRIPTION`
```
...
Version: x.y.z
...
```
as well as for the Java sources, in all the `pom.xml` files, you can likely find the relevant files with:
```
$ find . -name "pom.xml"
./mlflow/java/pom.xml
./mlflow/java/scoring/pom.xml
./mlflow/java/client/pom.xml
./mlflow/java/spark/pom.xml
```
and these should wherever applicable contain the corret version as:
```
...
<version>x.y.z</version>
...
```
These should be correct in most releases, but it's worth checking.

Generate the docs:
```
cd docs
make html
```

Generate the icon from the shipped favicon. You'll need [ImageMagick](https://imagemagick.org/):
```
convert source/_static/favicon.ico mlflow.png
```
This will create two icons, `mlflow-0.png` (16x16px) and `mlflow-1.png` (32x32px).

Install `doc2dash` as well:
```
pip install doc2dash
```
and then generate the docset from the html docs with:
```
doc2dash --name MLflow \
  --icon mlflow-1.png \
  --force \
  --index-page index.html \
  --enable-js \
  --online-redirect-url https://www.mlflow.org/docs/latest/index.html \
  --add-to-dash \
  build/html
```
and package it up as usual as:
```
tar --exclude='.DS_Store' -cvzf MLflow.tgz MLflow.docset
```
