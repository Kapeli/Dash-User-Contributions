# CanJS Dash Docset

The Official Docset for the [CanJS JavaScript Library][canjs].

## Installation

- To build the docsets, you'll need the following:
	- [CanJS][canjs] *
	- [Git][git]
	- [NodeJS][nodejs]
	- [DocumentJS][documentjs] *
	- [Grunt][npm]
	- [NPM][npm] 

**Note**: Items with `*` are submodules of the canjs.com repository. 

## Generating Docs

**Clone the canjs.com repository**

Once cloned, checkout the `gh-pages` branch:

	git clone https://github.com/bitovi/canjs.com.git
	cd canjs.com
	git checkout gh-pages

**Setup Submodules**

	git submodule init
	git submodule update

**Install NPM packages**

	npm install

**Generate the Docs**

Once all prerequisites, submodules, and packages are installed, run the following:

	grunt docjs

This will set up the docset for the current version of CanJS, and will appear in the appropriate subdirectory (e.g., `2.1`). Once generated, you can archive the docset by running:
	
	cd 2.1 # or whichever directory is the latest major.minor version of CanJS
	tar --exclude='.DS_Store' -cvzf CanJS.tgz CanJS.docset

To generate the docs for any legacy version, you can change the CanJS submodule. For example, to generate the latest 2.0.x docs for that version of CanJS:

	cd /path/to/canjs.com/can
	git checkout v2.0.7 # or another tagged version number
	cd ..
	grunt docjs

**Note**: at the time of this writing, there is a small bug with the 1.1.x tagged versions of CanJS in a support file `.jshintrc`. The fix is to remove the single-line comments from this file, then re-run:
	
	grunt docjs
 
## Support

Fixes and support for any documentation bugs in [CanJS][canjs] should be submitted to the [CanJS Github Repository](https://github.com/bitovi/canjs/).

# About

- Changelog for CanJS can be viewed [here](https://github.com/bitovi/canjs/blob/master/changelog.md).

[canjs]: http://canjs.com
[documentjs]: http://javascriptmvc.com/docs/DocumentJS.html
[git]: http://git-scm.com
[nodejs]: http://nodejs.org
[grunt]: http://gruntjs.com
[npm]: https://www.npmjs.org
