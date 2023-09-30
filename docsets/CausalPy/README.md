# CausalPy Docset

[CausalPy](https://github.com/pymc-labs/CausalPy) is a Python package focussing on causal inference in quasi-experimental settings. The package allows for sophisticated Bayesian model fitting methods to be used in addition to traditional OLS.

## Author

- [Xavier Yang](https://github.com/ivaquero)

## How to build:

1. Install doc2dash:

```bash
pip install doc2dash
# or
conda install doc2dash
```

- Download the lastest document from https://github.com/pymc-labs/CausalPy
- Unpack the downloaded archive
- Comment out the `sphinx` related blocks in `docs/source/conf.py`
- Execute the command

```bash
make file
doc2dash -n CausalPy -i source/_static/logo.png -I build/html/index.html -v build/html
tar cvzf CausalPy.tgz CausalPy.docset
```
