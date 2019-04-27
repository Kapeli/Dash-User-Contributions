CQL 3.1 Docset
=======================

Author: Tim Heckman (http://github.com/theckman)

This docset was adapted from the CQL (3.3) docset peovided by [Ge
Bing](http://github.com/gebing), reusing the Python script they built for
generating the 3.3 docset.

Generation steps:

```
wget http://docs.datastax.com/en/cql/3.1/zip/cql31.zip
unzip cql31.zip -d cql31
./html2dash.py --name 'CQL_3.1' --key cql31 cql31
tar --exclude='.DS_Store' -cvzf 'CQL_3.1.tgz' CQL_3.1.docset
```

## Generation Script

The script to generate the files can be found here:

- https://github.com/gebing/dash-docsets
