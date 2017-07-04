#!/bin/bash

DOCSET_ID=Emacs-CL
SQL_FILE=final.sql
BASEDIR=$DOCSET_ID.docset
CONDIR=$BASEDIR/Contents/
RESDIR=$CONDIR/Resources
DOCDIR=$RESDIR/Documents
VENVDIR=venv

# Make sure we start clean
rm -rf $BASEDIR $SQL_FILE $VENVDIR *.tgz
mkdir -p $DOCDIR

# Create a virtual env and install the appropriate packages
${VENVBIN:-virtualenv} $VENVDIR
source $VENVDIR/bin/activate
pip install beautifulsoup4 git+https://github.com/hylang/hy.git

# Download the HTML pages
if [ ! -d www.gnu.org ]; then
    wget -q -H -c -r -k -p -np -nv -E -D www.gnu.org https://www.gnu.org/software/emacs/manual/html_node/cl/index.html
else
    echo ---------HTML already fetched-----------
fi

# gendash.hy extracts data from the HTML pages and print out
# the corresponding INSERT statements.
cp db.sql $SQL_FILE
find . -name *.html | ./gendash.hy >> $SQL_FILE
sqlite3 $RESDIR/docSet.dsidx < $SQL_FILE

# Copy relevant files into the DOCSET directory
cp info.plist $CONDIR
cp *.png $BASEDIR
cp -rp www.gnu.org $DOCDIR

tar --exclude='.DS_Store' -cvzf $DOCSET_ID.tgz $DOCSET_ID.docset
