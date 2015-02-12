# io.js

Author: Fangdun Cai   
Twitter: [@_fundon](https://twitter.com/_fundon)   
GitHub: https://github.com/fundon

## Generation Steps:

```
$ git clone git@github.com:fundon/doc-tool.git
$ cd doc-tool
$ git checkout dash-docset
$ iojs dash.js $(find iojs.org/api/*.json)
$ cp -r io.js/api/* io.js.docset/Contents/Resources/Documents/iojs.org/api
$ tar --exclude='.DS_Store' -cvzf io.js.tgz io.js.docset
```
