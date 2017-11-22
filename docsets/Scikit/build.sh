#!/bin/bash
set -ex
set -o pipefail

if [ $# -gt 1 ]
then
	echo Usage $0 [GIT-TAG] >&2
	exit 1
fi

tag=$1

if [ -z "$tag" ]
then
	tag=$(curl 'https://api.github.com/repos/scikit-learn/scikit-learn/releases?per_page=1' | python -c 'import json, sys; print(json.load(sys.stdin)[0]["tag_name"])')
fi

originaldir=$(pwd)
workdir=$(mktemp -d -t sklearn2dash)
trap "{ rm -rf $workdir; }" EXIT

# setup virtual environment
virtualenv $workdir/venv
source $workdir/venv/bin/activate
cp userguide.py $workdir

# build docs
# XXX: alternatively we could just download from scikit-learn.github.io assuming versions are matched
cd $workdir
# TODO: perhaps scikit-learn should provide an environment.yml and this script should use conda-env...
pip install numpy scipy cython nose coverage matplotlib sphinx pillow sphinx-gallery numpydoc
pip install doc2dash scikit-learn==$tag
git clone --depth 1 --branch $tag https://github.com/scikit-learn/scikit-learn
cd scikit-learn/doc
make html
cd $workdir

# convert to dash
doc2dash --index-page documentation.html --parser userguide.ScikitLearnDocs -n scikit-learn scikit-learn/doc/_build/html/stable
tar --exclude='.DS_Store' -czvf scikit-learn.tgz scikit-learn.docset

# update Dash-User-Contributions
cd $originaldir
cp $workdir/scikit-learn.tgz .
# update docset.json
sed -i bak 's/"version": ".*,/"version": "'$tag'",/' docset.json
git add docset.json scikit-learn.tgz
