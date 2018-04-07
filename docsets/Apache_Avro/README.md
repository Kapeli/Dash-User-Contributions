[Apache Avro][1] Docset
================

Author: [Daniel CYR][2]

#### Generation steps:

```
rm -rf avro-docset
mkdir avro-docset avro-docset/src avro-docset/tools avro-docset/generated

cd avro-docset/tools
wget --quiet http://kapeli.com/javadocset.zip
unzip javadocset.zip
cd ../src/ 
wget --quiet http://www-eu.apache.org/dist/avro/avro-1.8.2/avro-doc-1.8.2.tar.gz
tar xfz avro-doc-1.8.2.tar.gz
cd ../generated
../tools/javadocset Avro ../src/avro-doc-1.8.2/api/java
tar --exclude='.DS_Store' -czf Avro.tgz Avro.docset
```

You can paste those commands in a terminal or just run the script that
will do all the commands for you:

```
scripts/generate-docset.sh
```

[1]: https://avro.apache.org/
[2]: https://github.com/danielccyr

