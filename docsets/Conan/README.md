# Conan Docset

[Conan](https://github.com/conan-io/conan) is an open source package Conan is a package manager for C and C++ developers

## Author

- [Xavier Yang](https://github.com/ivaquero)

## How to build:

1. Install doc2dash:

```bash
pip install doc2dash
# or
conda install doc2dash
```

- Download the lastest document from https://github.com/conan-io/docs/tree/develop2
- Unpack the downloaded archive
- Install doc-building packages selectively according to `conf.py`
- Disable the sidebar by modifying this line in `conf.py`

```python
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "nosidebar": True,
    "logo_only": True,
}
```

- Execute the following commands

```bash
cd docs-develop2 && make file
doc2dash -n Conan -i _build/html/_static/conan-favicon.png -I _build/html/index.html -v _build/html
tar cvzf Conan.tgz Conan.docset
```
