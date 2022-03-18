CQL Docset
=======================

Author: Ge Bing (http://github.com/gebing)

Generation steps:

```
wget http://docs.datastax.com/en/cql/3.3/zip/cql33.zip
unzip cql33.zip -d cql
./html2dash.py --name CQL --key cql cql
tar --exclude='.DS_Store' -cvzf CQL.tgz CQL.docset
```

Generation scripts:

Use my modified html2dash (https://github.com/gebing/dash-docsets)