[Apache RocketMQ][1] Docset
================

Author: [Daniel CYR][2]

#### Generation steps:

```
rm -rf rocketmq-docset
mkdir rocketmq-docset rocketmq-docset/src rocketmq-docset/tools rocketmq-docset/generated

cd rocketmq-docset
cd tools
wget --quiet http://kapeli.com/javadocset.zip
unzip javadocset.zip
cd ../src/
git clone https://github.com/apache/incubator-rocketmq
cd ../generated
javadoc -sourcepath ../src/incubator-rocketmq/client/src/main/java -subpackages org.apache.rocketmq -d ./javadocs
mkdir docset
cd docset
../../tools/javadocset Apache_RocketMQ ../javadocs
tar --exclude='.DS_Store' -czf Apache_RocketMQ.tgz
Apache_RocketMQ.docset

cd ..
echo -e "\n"
echo -e "Generated javadocs are in ./rocketmq-docset/generated/javadocs"
echo -e "Generated docset is ./rocketmq-docset/generated/docset/Apache_RocketMQ.docset"
echo -e "Targzipped docset is ./rocketmq-docset/generated/docset/Apache_RocketMQ.tgz"
echo -e "\n"
```

You can paste those commands in a terminal or just run the script that
will do all the commands for you:

```
scripts/generate-docset.sh
```

[1]: https://rocketmq.apache.org/
[2]: https://github.com/danielccyr

