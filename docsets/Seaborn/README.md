# Seaborn docset

## Authors

- [Paulo S. Costa](https://github.com/paw-lu)
- [Xavier Yang](https://github.com/ivaquero)

## Building Method 1

This docset is automatically generated via [paw-lu/seaborn-dash-docset](https://github.com/paw-lu/seaborn-dash-docset).

### Requirements

- [git](https://git-scm.com/)
- [GitHub CLI (gh)](https://cli.github.com/)
- [GNU Make](https://www.gnu.org/software/make/)
- [GNU Tar](https://www.gnu.org/software/tar/)
- [ImageMagick](https://imagemagick.org/index.php)
- [Nox](https://nox.thea.codes/en/stable/)
- [Python 3](https://www.python.org/)

### Build directions

To build the docs, run:

```bash
gh repo clone paw-lu/seaborn-dash-docset
cd seaborn-dash-docset
nox --tags build
```

## Building Method 2

- download the latest document from https://github.com/seaborn/seaborn.github.io
- comment some blocks like `intersphinx_mapping` in `conf.py`
- `cd seaborn.github.io-master && make html`
- remove `_sources` and `archive`
- run the following commands

```bash
doc2dash -v -n seaborn -i seaborn.github.io-master/_static/logo-tall-lightbg.png -I seaborn.github.io-master/index.html seaborn.github.io-master
tar cvzf seaborn.tgz seaborn.docset
```
