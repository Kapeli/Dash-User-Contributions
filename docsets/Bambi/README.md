# Bambi Docset

[Bambi](https://bambinos.github.io/bambi/) is a high-level Bayesian model-building interface written in Python. It's built on top of the PyMC probabilistic programming framework, and is designed to make it extremely easy to fit mixed-effects models common in social sciences settings using a Bayesian approach.

## How to build:

1. Install doc2dash:

```bash
pip install doc2dash
# or
conda install doc2dash
```

- Download the lastest document from https://github.com/bambinos/bambi/tree/gh-pages
- Unpack the downloaded archive
- remove `.doctrees` and `_source` to reduce the size
- Execute the following commands

```bash
doc2dash -n Bambi -i bambi-gh-pages/logos/favicon.png -I bambi-gh-pages/index.html -v bambi-gh-pages
tar cvzf Bambi.tgz Bambi.docset
```
