Zsh Docset
==========

This docset is maintained by [Zhiming Wang](https://github.com/zmwangx),
updated for 5.9 by [Kevin Turner](https://github.com/keturn).

Build instructions
------------------

To generate the docset from the upstream doc distribution, download the generation script
from <https://github.com/keturn/gen-zsh-docset>,
and run

```zsh
uv run gen-zsh-docset 5.9
```

Or if you have a recent (v7+) `texinfo` and want more bells and whistles,

```zsh
git submodule update
cd vendor/zsh
Util/preconfig && ./configure && make html && make tarxz-doc
cd ../..
ln vendor/zsh/zsh-*-doc.tar.xz .
uv run gen-zsh-docset --no-download 5.9
```
