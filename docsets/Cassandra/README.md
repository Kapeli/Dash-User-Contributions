Cassandra Docset
=======================

Author: Ge Bing (http://github.com/gebing)

Generation steps:

```
wget http://docs.datastax.com/en/cassandra/3.0/zip/cassandra30.zip
unzip cassandra30.zip -d cassandra
./html2dash.py --name Cassandra --key cassandra cassandra
tar --exclude='.DS_Store' -cvzf Cassandra.tgz Cassandra.docset
```

Generation scripts:

Use my modified html2dash (https://github.com/gebing/dash-docsets)