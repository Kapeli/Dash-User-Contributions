# Bonobo Docset

Docset for [Bonobo](https://www.bonobo-project.org/).

Contributor: Gergely Imreh, `imrehg` on [GitHub](https://github.com/imrehg) and [Twitter](https://twitter.com/imrehg)

## Docset generation instructions

Clone the source code:

```shell
https://github.com/python-bonobo/bonobo.git
cd bonobo
```

You likely want to check out a version-tagged state with:

```shell
git checkout -b dash x.y.z
```

where `x.y.z` is a tag (for Bonobo corresponding to a version number), such as `0.6.4`.

Install the development requirements:

```shell
pip install -r requirements-dev.txt
```

Generate the docs:

```shell
cd docs
make html
```

Generate the icon from the shipped favicon. You'll need [ImageMagick](https://imagemagick.org/):

```shell
convert -resize 16x16 _static/bonobo.png icon.png
convert -resize 32x32 _static/bonobo.png icon@2x.png
```

Might also useful to use [`optipng`](http://optipng.sourceforge.net/) and compress the icons:

```
optipng -o 9 icon.png icon@2x.png
```

Install `doc2dash` too, to convert the HTML docs into a docset:

```shell
pip install doc2dash
```

Then generate the docset with:

```shell
doc2dash --name bonobo \
  --icon icon@2x.png \
  --force \
  --index-page index.html \
  --enable-js \
  --online-redirect-url https://docs.bonobo-project.org/en/master/ \
  --add-to-dash \
  _build/html
```

This command will also add it to your Dash installation (so it's easy to check it for correctness),
if you prefer not to, remove the `--add-to-dash` flag from above.

Finally, package it up as usual as:

```shell
tar --exclude='.DS_Store' -cvzf bonobo.tgz bonobo.docset
```
