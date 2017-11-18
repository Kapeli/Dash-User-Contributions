Wagtail docset
=============

__Docset description:__
	[Wagtail](http://docs.wagtail.io) is a content management system built on Django.

__Author:__
    [153957](https://github.com/153957)

__How to generate the docset:__

- Download the desired release from GitHub
  [Wagtail releases](https://github.com/wagtail/wagtail/releases)
- Install the package (in a virtualenv) and install the testing and docs
  requirements.
- Run `make html` in the `docs` directory.
- Run [doc2dash](https://pypi.python.org/pypi/doc2dash/) on the
  `html` directory inside `docs/_build/`: `doc2dash -n Wagtail html`
- Edit the Info.plist in the docset, adding the following keys:

        <key>dashIndexFilePath</key>
        <string>index.html</string>
        <key>DashDocSetFallbackURL</key>
        <string>http://docs.wagtail.io/en/[version]/</string>

- Archive the docset:

        tar --exclude='.DS_Store' -cvzf Wagtail.tgz Wagtail.docset

- Copy the archived docset `Wagtail.tgz` to two locations (keep the filename the same):
    1. `specific_versions` folder within a sub-folder with the version name
    2. main `docsets/Wagtail` folder

- Update the version in `docset.json`

__Icon:__

- Icon from http://docs.wagtail.io/en/latest/_static/logo.png
