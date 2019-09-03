Nim Docset
==========

* [Who am I?](https://github.com/genotrance)
* Complete instructions on how to generate the docset:
  * Ensure a working GCC install
  * Install Go lang and `go get -u github.com/technosophos/dashing`
  * Download and extract the latest release build of Nim with prebuilt binaries from the [official website](https://nim-lang.org/install.html)
  * `cd nim-$version`
  * Get git $hash from `bin/nim -v`
  * Generate docs with `koch docs --git.commit=$hash`
  * `cd web/upload/$version`
  * Copy `dashing.json` and `logo.jpg` from https://github.com/niv/nim-docset
  * Edit `dashing.json`, replacing `nim-lang.org/docs/manual.html` with `overview.html`
  * Run `dashing build nim`
  * `tar cvzf nim.docset.tgz nim.docset`