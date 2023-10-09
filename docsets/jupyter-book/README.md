# Jupyter Book Docset

[Jupyter Book](https://github.com/executablebooks/jupyter-book) is an open-source tool for building publication-quality books and documents from computational material.

## Author

- Xavier Yang (https://github.com/ivaquero)

## Instructions

- Download the latest source codes from https://github.com/executablebooks/jupyter-book
- Install doc-building packages according to `docs/_config.yml`
- Run the following commands

```cmd
cd jupyter-book-master/docs && jupyter-book build .
rm -rf _downloads && rm -rf _sources
doj2dash -n jupyter-book -i _build/icon.png -f -I _build/html/index.html _build/html
tar cvzf jupyter-book.tgz jupyter-book.docset
```
