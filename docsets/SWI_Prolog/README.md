SWI Prolog Docset
=======================
* Author: Lorenz Köhl
* Github: https://github.com/mye/Dash-User-Contributions
* How to generate the docset:
	* Install https://github.com/technosophos/dashing using go get
	* Copy dashing.json and favicon.ico (from swi-prolog.org) into the doc/Manual subdirectory from your SWI Prolog installation
	* run `cp -i packages/* Manual` in the doc/ directory of the installation (select "n" for index.html)
	* Run `dashing build` inside this directory

