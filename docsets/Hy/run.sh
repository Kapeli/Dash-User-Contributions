#!/bin/bash

DOCSET_ID=Hy
SQL_FILE=db.sql
BASEDIR=$DOCSET_ID.docset
CONDIR=$BASEDIR/Contents/
RESDIR=$CONDIR/Resources
DOCDIR=$RESDIR/Documents
VENVDIR=venv
HYDIR=hy
CSVFILE=data.csv
DBFILE=$RESDIR/docSet.dsidx

function extract_objs {
    # $1 - pattern, $2 - type, $3 - in-file, $4 relative path of $3
    grep $1 $3 | perl -e "while(<STDIN>) {if (/href=\"([^\"]+)\">([^>]+)</) {print \"\$2,$2,$4\$1\n\" if length(\$2) < 30;}}"
}

# Make sure we start clean
rm -rf $BASEDIR $CSVFILE $DBFILE $VENVDIR *.tgz
mkdir -p $DOCDIR

# Create a virtual env and install the appropriate packages
${VENVBIN:-virtualenv} $VENVDIR
source $VENVDIR/bin/activate
pip install sphinx sphinx_rtd_theme
if [ ! -d $HYDIR ]; then
    git clone https://github.com/hylang/hy
fi
(cd $HYDIR/docs; make html; cp -rp _build/html/* ../../$DOCDIR)

# Use perl to extract objects
extract_objs toctree-l4 Macro hy/docs/_build/html/language/api.html language/api.html > $CSVFILE

extract_objs toctree-l3 Macro hy/docs/_build/html/extra/anaphoric.html extra/anaphoric.html >> $CSVFILE

extract_objs toctree-l4 Function hy/docs/_build/html/language/core.html language/core.html >> $CSVFILE

extract_objs toctree-l3 Command hy/docs/_build/html/language/cli.html language/cli.html >> $CSVFILE

extract_objs toctree-l3 Function hy/docs/_build/html/extra/reserved.html extra/reserved.html >> $CSVFILE

extract_objs toctree-l4 Macro hy/docs/_build/html/contrib/loop.html contrib/loop.html >> $CSVFILE

extract_objs toctree-l3 Macro hy/docs/_build/html/contrib/multi.html contrib/multi.html >> $CSVFILE

extract_objs toctree-l4 Macro hy/docs/_build/html/contrib/profile.html contrib/profile.html >> $CSVFILE

extract_objs toctree-l3 Macro hy/docs/_build/html/contrib/sequences.html contrib/sequences.html >> $CSVFILE

extract_objs toctree-l4 Function hy/docs/_build/html/contrib/walk.html contrib/walk.html >> $CSVFILE

extract_objs toctree-l3 Function hy/docs/_build/html/contrib/hy_repr.html contrib/hy_repr.html >> $CSVFILE

sqlite3 $DBFILE < $SQL_FILE

# Copy relevant files into the DOCSET directory
cp Info.plist $CONDIR
cp *.png $BASEDIR
tar --exclude='.DS_Store' -cvzf $DOCSET_ID.tgz $DOCSET_ID.docset
