# pymc

## Authors

- [Paulo S. Costa](https://github.com/paw-lu)
- [Xavier Yang]

## Building Method 1

This docset is automatically generated via [paw-lu/pymc-dash-docset](https://github.com/paw-lu/pymc-dash-docset).

#### Requirements

- [git](https://git-scm.com/)
- [GitHub CLI (`gh`)](https://cli.github.com/)
- [GNU Make](https://www.gnu.org/software/make/)
- [GNU Tar](https://www.gnu.org/software/tar/)
- [ImageMagick](https://imagemagick.org/index.php)
- [Nox](https://nox.thea.codes/en/stable/)
- [Python 3.10](https://www.python.org/)

#### Build directions

To build the docs, run:

```bash
gh repo clone paw-lu/pymc-dash-docset
cd pymc-dash-docset
nox --tags build
```

### Credits

This project was generated from [Cookiecutter Dash docset](https://github.com/paw-lu/cookiecutter-dash-docset).

## Building Method 2

- download the latest document from https://github.com/pymc-devs/pymc.io
- unpack the archive file
- `cd pymc.io-main && make html`
- remove `_source` in `_build`
- run the following commands

```bash
doc2dash -v -n pymc -i icon.png -I pymc.io-main/_build/index.html pymc.io-main/_build
tar cvzf pymc.tgz pymc.docset
```
