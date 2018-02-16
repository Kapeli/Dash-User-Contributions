[Kafka][1] Docset
================

Author: [Daniel CYR][2]

#### Generation steps:

```
mkdir kafka-docset
cd kafka-docset
wget http://kapeli.com/javadocset.zip
unzip javadocset.zip
git clone https://github.com/confluentinc/kafka.git
cd kafka
gradle
./gradlew aggregatedJavadoc
cd ..
./javadocset Kafka ./kafka/build/docs/javadoc/

```




[1]: https://kafka.apache.org/
[2]: https://github.com/danielccyr

