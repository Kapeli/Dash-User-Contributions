#!/bin/bash

REPO="https://github.com/briannesbitt/Carbon"
#HTML="https://raw.githubusercontent.com/briannesbitt/Carbon/gh-pages/docs/index.html"
HTML="http://carbon.nesbot.com/docs/"
VERSION_TAG="$1"

DASHING="`which dashing`"
DOXYGEN="`which doxygen`"
GIT="`which git`"
WGET="`which wget`"
TEMPDIR="`mktemp -d`"

# Check input
if [[ -z $VERSION_TAG ]] || [[ $VERSION_TAG == '-h' ]] || [[ $VERSION_TAG == '--help' ]]; then
    echo "Usage: $0 <tag version>" >&2
    echo "Ex: $0 1.29.5" >&2
    exit 1
fi

# Check if dashing is available in $PATH
if [[ -z $DASHING ]]; then
    echo "Sorry but dashing isn't available in your PATH. I need it." >&2
    exit 1
fi

# Check if doxygen is available in $PATH
if [[ -z $DOXYGEN ]]; then
    echo "Sorry but doxygen isn't available in your PATH. I need it." >&2
    exit 1
fi

# Check if git is available in $PATH
if [[ -z $GIT ]]; then
    echo "Sorry but git isn't available in your PATH. I need it." >&2
    exit 1
fi

# Check if wget is available
if [[ -z $WGET ]]; then
    echo "Sorry but wget isn't available in your PATH. I need it." >&2
    exit 1
fi

# Download repo archive at given tag, and unzip it
echo -n "Downloading HTML docs... "
$WGET -q -kpHN -nH -P docs "$HTML"
# echo "Downloading repo at: $TEMPDIR"
# $WGET -q -O "$TEMPDIR/$(basename $REPO)-$VERSION_TAG.zip" "$REPO/archive/$VERSION_TAG.zip"
echo "Done !"

# Generate .docset and archive it
echo -n "Building .docset ... "
$DASHING build -s docs/ > /dev/null
tar --exclude='.DS_Store' -cvzf "$(basename $REPO)-$VERSION_TAG.tgz" Carbon.docset
echo "Done !"

# Clean directory
rm -rf Carbon.docset/
rm -rf docs/

echo
echo "Docset successfully generated !"
exit 0
