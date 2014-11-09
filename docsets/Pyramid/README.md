#Pyramid

Pyramid is a small, fast Python web framework.  It is developed as part of the [Pylons Project](http://www.pylonsproject.org/). It is licensed under a [BSD-like license](http://repoze.org/license.html).

##Author

Steve Piercy

* [https://github.com/stevepiercy](https://github.com/stevepiercy)
* [@steve_piercy](https://twitter.com/steve_piercy)

##Generate docset

To generate the Pyramid docset for Dash:

1. [Generate the docs for Pyramid using Sphinx](https://github.com/Pylons/pyramid/blob/master/HACKING.txt).
1. Follow the instructions for [Python, Sphinx or PyDoctor-Generated Documentation](http://kapeli.com/docsets). These instructions are general, so see the Tips below for additional help.

##Tips

It's assumed that you have built the docs for Pyramid, installed doc2dash, forked and cloned the `Dash-User-Contributions` repository, and are using Mac OS X.

###Add built Pyramid docs to Dash app

Add the built Pyramid docs as a docset to the Dash application. `-f` forces an overwrite. `-i` adds an icon to the docset.

```shell
/path/to/doc2dash -A -n Pyramid -d /path/to/cloned/repo/Dash-User-Contributions/docsets/Pyramid -f -i /path/to/cloned/repo/Dash-User-Contributions/docsets/Pyramid/icon.png /path/to/cloned/pyramid/repo/docs/_build/html
```

###Copy the larger icon to the Dash.docset

```shell
cp /path/to/cloned/repo/Dash-User-Contributions/docsets/Pyramid/icon@2x.png /Users/USERNAME/Library/Application\ Support/doc2dash/DocSets/Pyramid.docset/icon@2x.png
```

###tar up the docset for a pull request

```shell
tar --exclude='.DS_Store' -cvzf /path/to/cloned/repo/Dash-User-Contributions/docsets/Pyramid/Pyramid.tgz /Users/USERNAME/Library/Application\ Support/doc2dash/DocSets/Pyramid.docset
```

###Share the archive

Commit your changes, push to your repository, and submit a pull request.

##Bugs

[Report an issue on GitHub](https://github.com/Kapeli/Dash-User-Contributions/issues/new).

