# Conda Docset

[Conda](https://docs.conda.io/en/latest/) is an open source package management system and environment management system that runs on Windows, macOS, and Linux. Conda quickly installs, runs and updates packages and their dependencies. Conda easily creates, saves, loads and switches between environments on your local computer. It was created for Python programs, but it can package and distribute software for any language.

## How to build:

1. Install doc2dash:

```bash
pip install doc2dash
# or
conda install doc2dash
```

- Download the lastest document from https://github.com/conda/conda-docs
- Unpack the downloaded archive
- Comment out the `sphinx` related blocks in `source/conf.py`
- Execute the command

```bash
make file
doc2dash -n Conda -d Conda.docset -i source/conda-logo.png -I build/html/index.html -v build/html
tar cvzf Conda.tgz Conda.docset
```
