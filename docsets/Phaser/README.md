Phaser Docset
==================

Created by [Colin Ray](https://github.com/rcolinray).

## Generation

To generate the docset, clone [phaser-dash-docset](https://github.com/rcolinray/phaser-dash-docset) and execute the following commands:

```
git submodule init
git submodule update
cabal sandbox init
cabal install --only-dependencies
cabal configure
cabal build
cabal run
```

## Dependencies

- GHC
- Cabal
