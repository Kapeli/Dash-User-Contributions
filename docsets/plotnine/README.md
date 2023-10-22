# plotnine Docset

## Author

- Xavier Yang (https://github.com/ivaquero)

## Instructions

Install doc2dash:

```bash
pip install doc2dash
# or
conda install doc2dash
```

- download the lastest document from https://github.com/has2k1/plotnine
- unpack the downloaded archive
- comment the plotnine_example-related blocks `source/conf.py`
- run the following commands

```bash
make html
doc2dash -n plotnine -i plotnine-main/doc/_build/html/_static/logo-32.png -I plotnine-main/doc/_build/html/index.html plotnine-main/doc/_build/html
tar cvzf plotnine.tgz plotnine.docset
```
