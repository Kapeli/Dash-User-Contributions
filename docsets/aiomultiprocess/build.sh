# @Author: benbenbang
# @Date:   2020-06-21
# @Last Modified by:   benbenbang
# @Last Modified time: 2020-06-29

mkdir target
git clone https://github.com/omnilib/aiomultiprocess.git ./target
cd target
export AIOMULTIPROCESS_VERSION=$(cat aiomultiprocess/__init__.py | grep -o "__version__ = \"\\d.\\d.\\d\""  | cut -d = -f 2 | grep -o \\d.\\d.\\d)
make html
doc2dash -n aiomultiprocess html/ --index-page index.html -d ../
cd -
rm -rf target
mkdir -p versions/$AIOMULTIPROCESS_VERSION/
tar --exclude='.DS_Store' -czvf aiomultiprocess.tgz aiomultiprocess.docset
cp aiomultiprocess.tgz versions/$AIOMULTIPROCESS_VERSION/
rm -rf aiomultiprocess.docset
mv versions/$AIOMULTIPROCESS_VERSION/aiomultiprocess.tgz versions/$AIOMULTIPROCESS_VERSION/aiomultiprocess.tgz
