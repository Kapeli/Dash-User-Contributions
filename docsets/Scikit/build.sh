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

# check prerequisites
python --version 2>&1 | grep -q 'Python 3' || (echo 'Require Python 3' >&2; exit 2)

originaldir=$(pwd)
workdir=$(mktemp -d -t sklearn2dashXXX)
trap "{ rm -rf $workdir; }" EXIT

# setup virtual environment
pip install -U pip
pip install virtualenv
python -m virtualenv $workdir/venv
source $workdir/venv/bin/activate

# build docs
cd $workdir

git clone --branch $tag https://github.com/scikit-learn/scikit-learn
cd scikit-learn/doc

pip install wheel numpy scipy cython
pip install sphinx sphinx-gallery numpydoc matplotlib Pillow pandas \
            scikit-image packaging seaborn sphinx-prompt \
            sphinxext-opengraph pytest
pip install doc2dash scikit-learn==$tag
NO_MATHJAX=1 make html
cd $workdir

# convert to dash
doc2dash --index-page documentation.html --enable-js -n scikit-learn scikit-learn/doc/_build/html/stable
tar --exclude='.DS_Store' -czvf scikit-learn.tgz scikit-learn.docset

# update Dash-User-Contributions
cd $originaldir
cp $workdir/scikit-learn.tgz .
# update docset.json
sed -ibak 's/"version": ".*,/"version": "'$tag'",/' docset.json
git add docset.json scikit-learn.tgz
