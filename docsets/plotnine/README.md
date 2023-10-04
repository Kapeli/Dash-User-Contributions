# plotnine Docset

## Author

- Xavier Yang (https://github.com/ivaquero)

## How to build:

1. Install doc2dash:

```bash
pip install doc2dash
# or
conda install doc2dash
```

- Download the lastest document from https://github.com/has2k1/plotnine
- Unpack the downloaded archive
- Install doc-building packages selectively according to `source/conf.py`
- Execute the command

```bash
doc2dash -n plotnine -i plotnine-gh-pages/images/logo-540.png -I /Users/integzz/Documents/plotnine-gh-pages/index.html -v plotnine-gh-pages/
tar cvzf plotnine.tgz plotnine.docset
```
