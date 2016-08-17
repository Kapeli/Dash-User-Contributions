Pillow docset
=============

__Docset description:__
	[Pillow](http://python-pillow.github.io), the friendly PIL fork. PIL
	is the [Python Imaging
	Library](https://en.wikipedia.org/wiki/Python_Imaging_Library).

__Author:__
    [153957](https://github.com/153957)

__How to generate the docset:__

- Download the desired release from GitHub
  [Pillow releases](https://github.com/python-pillow/Pillow/releases)
- Run `make html` in the `docs` directory (if you are missing some
  requried packages run `python setup.py develop` in the root dir first)
- Run [doc2dash](https://pypi.python.org/pypi/doc2dash/) on the
  `html` directory inside `docs/_build/`: `doc2dash -n Pillow html`
- Edit the Info.plist in the docset, adding the following keys:

        <key>dashIndexFilePath</key>
        <string>index.html</string>
        <key>DashDocSetFallbackURL</key>
        <string>http://pillow.readthedocs.org</string>

- Archive the docset:

        tar --exclude='.DS_Store' -cvzf Pillow.tgz Pillow.docset

- Update the version in `docset.json`
- Icon from https://github.com/python-pillow/python-pillow.github.io
