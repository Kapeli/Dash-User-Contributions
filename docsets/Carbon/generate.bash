#!/bin/bash

# Sami is available there: https://github.com/FriendsOfPHP/Sami#installation

REPO="https://github.com/briannesbitt/Carbon"
#HTML="https://raw.githubusercontent.com/briannesbitt/Carbon/gh-pages/docs/index.html"
HTML="http://carbon.nesbot.com/docs/"
VERSION_TAG="$1"

DASHING="`which dashing`"
SAMI="`dirname $0`/sami.phar"
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

# Check if git is available in $PATH
if [[ -z $GIT ]]; then
    echo "Sorry but git isn't available in your PATH. I need it." >&2
    exit 1
fi

# Check if sami.phar exists locally
if [[ -f $SAMI ]]; then
    echo "Sorry but sami doesn't exist locally. I need it." >&2
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

echo -n "Cleaning HTML docs... "
# remove trackers
sed -i .bak 's/\/\/www.google-analytics.com\/analytics.js//' docs/docs/index.html
sed -i .bak 's/\/\/piwik.selfbuild.fr\///' docs/docs/index.html
# remove ads
sed -i .bak 's/\.\.\/properties\/151\/funder\.js//' docs/docs/index.html
# remove non-functional search bars (sort of, this is a hack)
sed -i .bak 's/<input type="text" class="form-control" placeholder="Search".*$//' docs/docs/index.html
sed -i .bak 's/<i class="glyphicon glyphicon-search"><\/i>//' docs/docs/index.html
echo "Done !"

# Generate API doc with Sami
$SAMI update sami-config.php

# Generate .docset and archive it
echo -n "Building .docset ... "
$DASHING build --source docs/ > /dev/null
tar --exclude='.DS_Store' -cvzf "$(basename $REPO).tgz" Carbon.docset
echo "Done !"

# Copy main archive to specific version
cp "$(basename $REPO).tgz" "versions/$(basename $REPO)-$VERSION_TAG.tgz"

# Clean directory
rm -rf Carbon.docset/
rm -rf docs/

echo
echo "Docset successfully generated !"
exit 0
