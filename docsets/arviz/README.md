# arviz

## Who am I

[Paulo S. Costa](https://github.com/paw-lu)

## How to generate docset

This docset is automatically generated via [paw-lu/arviz-dash-docset](https://github.com/paw-lu/arviz-dash-docset).

### Requirements

- [git](https://git-scm.com/)
- [GitHub CLI (`gh`)](https://cli.github.com/)
- [GNU Make](https://www.gnu.org/software/make/)
- [GNU Tar](https://www.gnu.org/software/tar/)
- [ImageMagick](https://imagemagick.org/index.php)
- [Nox](https://nox.thea.codes/en/stable/)
- [Python 3.10](https://www.python.org/)

### Build directions

To build the docs, run:

```console
$ gh repo clone paw-lu/arviz-dash-docset

$ cd arviz-dash-docset

$ nox --tags build
```

## Credits

This project was generated from [Cookiecutter Dash docset](https://github.com/paw-lu/cookiecutter-dash-docset).
