[Atom][1] Docset
================

Author: Ben Booth ([@bkbooth11][2])

Previous Author: GyuYong Jung([@Obliviscence][3])


#### Generation steps:

* Clone [github.com/bkbooth/dash-atom-docs][7] and `cd` into cloned directory
* Run `yarn` (or `npm install`)
* Set the desired API version with `atom_version` in _package.json_
* Run `yarn build` (or `npm run build`)

[@Obliviscence][3]'s generation script available here: [github.com/Ephemera/atom-docset-generator][9]


#### Prequisites:

* [Node.js][5] >= v6.0.0
* [httrack][4]
* [Yarn][6] (preferred, can use `npm`)


#### Known Bugs:

* None, submit any you find [here][8]


#### Planned Improvements:

* (Maybe) add Table of Contents support



[1]: https://atom.io/
[2]: https://twitter.com/bkbooth11
[3]: https://twitter.com/Obliviscence
[4]: https://www.httrack.com/
[5]: https://nodejs.org/
[6]: https://yarnpkg.com/
[7]: https://github.com/bkbooth/dash-atom-docs
[8]: https://github.com/bkbooth/dash-atom-docs/issues
[9]: https://github.com/Ephemera/atom-docset-generator
