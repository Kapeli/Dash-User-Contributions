# Docset for Mediawiki

Upstream docs:

* master: https://doc.wikimedia.org/mediawiki-core/master/php/


## Clone this repo

```
git clone https://github.com/inductiveload/mediawiki_docset
```

## Generate the docset

Choose a branch (only master works for now: `master`)

```
./generate.sh master
```

This will:

* Construct a set of Docker containers for MediaWiki and run them up
* Build a version of doxygen with a huge buffer size that can handle MediaWiki's docs
* Fetch and install doxygen2docset
* Patch the MW Doxyfile to generate docset tag files
* Build the doxygen docs and create the docset
* Archive the docset
