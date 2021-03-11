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

git clone --branch $tag https://github.com/scikit-learn/scikit-learn
cd scikit-learn/doc
git fetch https://github.com/jnothman/scikit-learn 0.20sphinxrename
git cherry-pick FETCH_HEAD  # patch sphinx to avoid overwriting generated files with different case
###git fetch https://github.com/thomasjpfan/scikit-learn examples_njobs_fix
###git cherry-pick FETCH_HEAD  # n_jobs=1

pip install -U pip
<<<<<<< HEAD
pip install numpy scipy cython nose coverage matplotlib==2.* sphinx==2.1.2 pillow sphinx-gallery numpydoc scikit-image seaborn joblib pandas pytest
=======
pip install numpy scipy cython nose coverage matplotlib==2.* sphinx==2.1.2 pillow sphinx-gallery numpydoc scikit-image seaborn joblib pandas pytest sphinx-prompt
>>>>>>> daee4539969911937fd29e266d25f0735f5452d3
pip install doc2dash scikit-learn==$tag
NO_MATHJAX=1 make html optipng
cd $workdir

# convert to dash
export PYTHONPATH=$workdir # adds userguide to python path
doc2dash --index-page documentation.html --parser userguide.ScikitLearnDocs --enable-js -n scikit-learn scikit-learn/doc/_build/html/stable
tar --exclude='.DS_Store' -czvf scikit-learn.tgz scikit-learn.docset

# update Dash-User-Contributions
cd $originaldir
cp $workdir/scikit-learn.tgz .
# update docset.json
sed -ibak 's/"version": ".*,/"version": "'$tag'",/' docset.json
git add docset.json scikit-learn.tgz
