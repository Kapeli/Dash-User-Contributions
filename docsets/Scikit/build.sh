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
which optipng || (echo 'Require optipng' >&2; exit 2)

originaldir=$(pwd)
workdir=$(mktemp -d -t sklearn2dashXXX)
trap "{ rm -rf $workdir; }" EXIT

# setup virtual environment
python -m virtualenv $workdir/venv
source $workdir/venv/bin/activate
cp userguide.py $workdir

# build docs
# XXX: alternatively we could just download from scikit-learn.github.io assuming versions are matched
cd $workdir
# TODO: perhaps scikit-learn should provide an environment.yml and this script should use conda-env...
pip install -U pip
pip install numpy==1.15 scipy cython nose coverage matplotlib sphinx pillow sphinx-gallery numpydoc scikit-image joblib pandas
pip install doc2dash scikit-learn==$tag
git clone --branch $tag https://github.com/scikit-learn/scikit-learn
cd scikit-learn/doc
git fetch https://github.com/jnothman/scikit-learn 0.20sphinxrename
git cherry-pick FETCH_HEAD  # patch sphinx to avoid overwriting generated files with different case
NO_MATHJAX=1 make html optipng
cd $workdir

# convert to dash
doc2dash --index-page documentation.html --parser userguide.ScikitLearnDocs -n scikit-learn scikit-learn/doc/_build/html/stable
tar --exclude='.DS_Store' -czvf scikit-learn.tgz scikit-learn.docset

# update Dash-User-Contributions
cd $originaldir
cp $workdir/scikit-learn.tgz .
# update docset.json
sed -ibak 's/"version": ".*,/"version": "'$tag'",/' docset.json
git add docset.json scikit-learn.tgz
