# imbalanced-learn Docset

## Author

- Xavier Yang (https://github.com/ivaquero)

## How to build:

1. Install doc2dash:

```bash
pip install doc2dash
# or
conda install doc2dash
```

- Download the lastest document from https://github.com/scikit-learn-contrib/imbalanced-learn
- Unpack the downloaded archive
- Execute the command

```bash
make file
doc2dash -n imbalanced-learn -i imbalanced-learn-master/doc/_static/img/logo.png -I imbalanced-learn-master/doc/_build/html/index.html -v imbalanced-learn-master/doc/_build/html
tar cvzf imbalanced-learn.tgz imbalanced-learn.docset
```
