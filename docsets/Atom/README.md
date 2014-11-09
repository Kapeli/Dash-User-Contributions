Atom
=======================

Author: Ben Booth ([@bkbooth11][1])

#### Generation Steps:
* Download the original documentation from [atom.io/docs/api][2] using
[httrack][3] or similar
* Clone [github.com/bkbooth/dash-atom-docs][4] and copy the downloaded
documentation into `Atom.docset/Contents/Resources/Documents/`
* Make sure you have [node.js][8] installed then inside the cloned repository
run `npm install` then `node index` to populate the sqlite3 database

#### Known Bugs:
* None, submit any you find [here][5]

#### Planned Improvements:
* Find and unlink broken links (currently shows a 'Not Found' message)
* Improve the page titles
* (Maybe) add Table of Contents support
* (Maybe) automate building or scraping the docs using [grunt][6] or [gulp][7]

[1]: https://twitter.com/bkbooth11
[2]: https://atom.io/docs/api
[3]: http://www.httrack.com
[4]: https://github.com/bkbooth/dash-atom-docs
[5]: https://github.com/bkbooth/dash-atom-docs/issues
[6]: http://gruntjs.com/
[7]: http://gulpjs.com/
[8]: http://nodejs.org/
