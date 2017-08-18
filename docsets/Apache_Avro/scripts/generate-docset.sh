rm -rf avro-docset
mkdir avro-docset avro-docset/src avro-docset/tools avro-docset/generated

cd avro-docset
cd tools
wget --quiet http://kapeli.com/javadocset.zip
unzip javadocset.zip
cd ../src/
wget --quiet http://www-eu.apache.org/dist/avro/avro-1.8.2/avro-doc-1.8.2.tar.gz
tar xfz avro-doc-1.8.2.tar.gz
cd ../generated
../tools/javadocset Avro ../src/avro-doc-1.8.2/api/java
tar --exclude='.DS_Store' -czf Avro.tgz Avro.docset

cd ..
echo -e "\n"
echo -e "Generated docset is ./avro-docset/generated/Avro.docset"
echo -e "Targzipped docset is ./avro-docset/generated/Avro.tgz"
echo -e "\n"