# MLflow Docset

Contributor: Gergely Imreh, `imrehg` on [GitHub](https://github.com/imrehg) and [Twitter](https://twitter.com/imrehg)

## Docset generation instructions

Clone the MLflow source code:

```shell
git clone https://github.com/mlflow/mlflow.git
cd mlflow
```

You likely want to check out a version-tagged state with:

```shell
git checkout vX.Y.Z
```

where `X.Y.Z` is a tag (for MLFlow corresponding to a version number), such as `1.7.2`.

Install the pre-requisites:

* For the R docs, need to install [R](https://www.r-project.org/), and `libgit2`
* For the Java docs, need a Java runtime and `maven`
* Will need to have `pandoc` installed as well
* For Python docs, you need Python 3.7, then install the requirements:

```shell
pip install -r dev/small-requirements.txt
pip install -r dev/extra-ml-requirements.txt
pip install -r dev-requirements.txt
```

You might need to check if the version number is correct in the source code, that
is in `mlflow/version.py`, it should contain

```python
...
VERSION = 'X.Y.Z'
```

where `X.Y.Z` is the correct version (which you can check with `git describe --tags` for example,
and do not include the `v` reported in that version). The same for the R docs at `mlflow/R/mlflow/DESCRIPTION`

```rst
...
Version: X.Y.Z
...
```

as well as for the Java sources, in all the `pom.xml` files, you can likely find the relevant files with:

```shell
$ find . -name "pom.xml"
./mlflow/java/pom.xml
./mlflow/java/scoring/pom.xml
./mlflow/java/client/pom.xml
./mlflow/java/spark/pom.xml
```

and these should wherever applicable contain the correct version as:

```xml
...
<version>X.Y.Z</version>
...
```

These should be correct in most releases, but it's worth checking.

Generate the docs:

```shell
cd docs
```

Currently also need to comment out some Ubuntu-specific docs building steps,
thus in `build-rdoc.sh` have to comment out the install lines lines at the top,
such as these (basically all with a `sudo` step)

```shell
sudo add-apt-repository ppa:cran/libgit2
sudo apt-get update
sudo apt-get install --yes libssh2-1-dev libgit2-dev
```

Also ensure that you've installed `libgit2` (e.g. through `brew`).

```shell
make html
```

Generate the icon from the shipped favicon. You'll need [ImageMagick](https://imagemagick.org/):

```shell
convert source/_static/favicon.ico mlflow.png
```

This will create two icons, `mlflow-0.png` (16x16px) and `mlflow-1.png` (32x32px).

Install `doc2dash` as well:

```shell
pip install doc2dash
```

and then generate the docset from the html docs with:

```shell
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

```shell
tar --exclude='.DS_Store' -cvzf MLflow.tgz MLflow.docset
```
