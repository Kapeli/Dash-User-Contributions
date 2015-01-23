# pouchdb-docset

Documentation for the [PouchDB](http://pouchdb.com/) in-browser JavaScript database in the Dash [docset](http://kapeli.com/docsets) format for offline reading and searching.

Created by [Buck Doyle](https://github.com/backspace).

## Generating the docset

Requirements:

* ruby
* wget
* imagemagick

```
git clone https://github.com/backspace/pouchdb-docset
cd pouchdb-docset
bundle install
rake
```

The docset will be generated at `dist/PouchDB.docset`.

## Known issues

All API headings are marked as methods. The initial fetch of the documentation manually ignores the `2014` directory because I couldn’t get `wget`’s `--exclude-directories` to use wildcards.
