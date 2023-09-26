# NetworkX Docset

[NetworkX](http://networkx.github.io/) is a Python language software package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks.

## Author

- [AllanLRH](https://github.com/AllanLRH)
- [ivaquero](https://github.com/ivaquero)

## Instructions

- Download source code of the latest release
- `cd doc`
- Modify `conf.py`, comment the `sphinx_gallery` related blocks or the size of docset will be too large.
- Get a png file for the icon
- Run the following command

```cmd
make html
doc2dash -n NetworkX -i icon.png -f -I index.html -v build/html && tar cvzf NetworkX.tgz NetworkX.docset
```
