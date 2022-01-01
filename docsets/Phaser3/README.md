# [Phaser 3](https://www.phaser.io/) docs for [Dash](https://kapeli.com/dash)

By [Oliver Kletzmayr](https://github.com/okletzmayr)

## Generation:

To generate the docset, clone
[phaser3-dash-docset](https://github.com/okletzmayr/phaser3-dash-docset).

Requirements:

- [dashing](https://github.com/technosophos/dashing)
- node v14 (currently v16 won't work with `node-gyp` in `phaser3-docs`)

Run the `make.sh` script to generate the docset from the git submodules.
Please feel free to have a look at the script yourself, but here's a summary
of what it does:

- checks for dashing
- checks if the submodules exist
- installs `phaser3-docs` deps with `npm`
- build the Phaser docs locally
- runs dashing to generate the docset
- gets the git tag from the `phaser` submodule
- creates a `.tgz` in `./docset/versions/<version tag>/`

Alternatively, if you prefer to do all of that yourself, and just run the
dashing config:

```shell
dashing build --source ./phaser3-docs/out
```

