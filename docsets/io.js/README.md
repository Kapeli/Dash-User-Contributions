# io.js

* Author: Fangdun Cai
* Twitter: [@_fundon](https://twitter.com/_fundon)
* GitHub: https://github.com/fundon

## Generation Steps:

```
# change to io.js project
$ cd io.js

$ git clone git@github.com:fundon/iojs-docset.git dash
$ cp dash/template.html doc/template.html

# generate io.js API docs
$ make doc

$ rm -rf dash/io.js.docset/Contents/Resources/Documents/iojs.org/api/
$ cp -R out/doc/api/* dash/io.js.docset/Contents/Resources/Documents/iojs.org/api/
# generate io.js docset
$ cd dash
$ make
```

## Or see https://github.com/fundon/iojs-docset
