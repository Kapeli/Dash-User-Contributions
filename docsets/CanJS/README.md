# TODO

- look at the instructions for other projects to see how their docs are generated
- add any details needed where appropriate

# CanJS

- Preamble for what CanJS is, etc. 
- By Bitovi (with link to corp site and canjs.com)
- Link to Bitovi Repo. for CanJS

# Prerequisites for Generating Docs

- Mention Repo for canjs (gh-pages branch)
- Mention dependencies (DocumentJS, Grunt, etc.)
	- Appropriate links to each project in the MD file
- Mention other submodules, initializing them, etc.

# Generating Docs

- Mention command `grunt docjs` (to generate the *.docset file for master)
- Mention instructions for generating docs for each tag version
	- go to the `can` subdirectory, and `git checkout vx.y.z` where x.y.z is the tag you want to generate docs for
	- get the *.docset file from the appropriate subdirectories
	- mention the oddities for CanJS v1.1 (fix with the .jshintrc directory) (known bug)

# About

- include any licensing and other infornation here
- include any copyright and other legal stuff here