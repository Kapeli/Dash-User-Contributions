# Author: Ben CHEN
# Github: benbenbang
# Created Date: 2019-12-11
# Last Modified by: benbenbang
# Last Modified: 2019-12-11

mkdir target
git clone https://github.com/confluentinc/confluent-kafka-python.git ./target
cd target
export CONFLUENT_VERSION=$(cat setup.py | grep -o version=\'\\d.\\d.\\d\' | cut -d = -f 2 | grep -o \\d.\\d.\\d)
make docs
doc2dash -n confluent-kafka-python docs/_build/html --index-page index.html -d ../
cd -
rm -rf target
mkdir -p versions/$CONFLUENT_VERSION/
tar --exclude='.DS_Store' -czvf confluent-kafka-python.tgz confluent-kafka-python.docset
cp confluent-kafka-python.tgz versions/$CONFLUENT_VERSION/
mv confluent-kafka-python.tgz confluent-kafka-python.tgz.txt
mv ./versions/$CONFLUENT_VERSION/confluent-kafka-python.tgz ./versions/$CONFLUENT_VERSION/confluent-kafka-python.tgz.txt
rm -rf confluent-kafka-python.docset
