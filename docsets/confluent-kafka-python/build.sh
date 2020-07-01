# @Author: benbenbang
# @Date:   2020-12-11
# @Last Modified by:   benbenbang
# @Last Modified time: 2020-06-29

mkdir target
git clone https://github.com/confluentinc/confluent-kafka-python.git ./target
cd target
export CONFLUENT_VERSION=$(cat setup.py | grep -o version=\'\\d.\\d.\\d\' | cut -d = -f 2 | grep -o \\d.\\d.\\d)
git checkout v$CONFLUENT_VERSION
make docs
doc2dash -n confluent-kafka-python docs/_build/html --index-page index.html -d ../
cd -
rm -rf target
mkdir -p versions/$CONFLUENT_VERSION/
tar --exclude='.DS_Store' -czvf confluent-kafka-python.tgz confluent-kafka-python.docset
cp confluent-kafka-python.tgz versions/$CONFLUENT_VERSION/
rm -rf confluent-kafka-python.docset
mv versions/$CONFLUENT_VERSION/confluent-kafka-python.tgz versions/$CONFLUENT_VERSION/confluent-kafka-python.tgz
