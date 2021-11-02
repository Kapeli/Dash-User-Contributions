#!/bin/bash

set -e

MAJOR_VERSION="8"
ODOO_VERSION="$MAJOR_VERSION.0"

git clone https://github.com/odoo/odoo.git --depth=1 --branch=$ODOO_VERSION

virtualenv env
source env/bin/activate

pip install \
    --requirement odoo/requirements.txt \
    --requirement odoo/doc/requirements.txt
# sphinx-patchqueue > 0.4.0 is required to fix this issue:
# https://github.com/sphinx-doc/sphinx/issues/1888
pip install --upgrade sphinx-patchqueue 
pip install doc2dash

make --directory=odoo/doc html

doc2dash \
    --force \
    --name "Odoo $MAJOR_VERSION" \
    --online-redirect-url "https://www.odoo.com/documentation/$ODOO_VERSION/" \
    --icon icon.png \
    --index-page index.html \
    odoo/doc/_build/html/ 

tar --exclude='.DS_Store' -cvzf "Odoo_$MAJOR_VERSION.tgz" "Odoo $MAJOR_VERSION.docset"
