# NetworkX Docset

[NetworkX](http://networkx.github.io/) is a Python language software package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks.

## Author

- [AllanLRH](https://github.com/AllanLRH)
- [Xavier Yang](https://github.com/ivaquero)

## Instructions

- Download the latest gh-pages files from https://github.com/networkx/networkx/tree/gh-pages
- Get an icon file (16×16) and rename it to `icon.png`, or just use the one in this repo
- Run the following commands

```cmd
doc2dash -n NetworkX -i networkx-gh-pages/icon.png -I networkx-gh-pages/index.html -f ./networkx-gh-pages
tar cvzf NetworkX.tgz NetworkX.docset
```
