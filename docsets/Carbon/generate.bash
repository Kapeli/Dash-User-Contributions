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
if [[ ! -f $SAMI ]]; then
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
$WGET -q -kpHN -nH -P docs/html_docs "$HTML"
echo "Done !"

echo -n "Cleaning HTML docs... "
# remove trackers
LC_ALL=C sed -i .bak 's/\/\/www.google-analytics.com\/analytics.js//' docs/html_docs/docs/index.html
LC_ALL=C sed -i .bak 's/\/\/piwik.selfbuild.fr\///' docs/html_docs/docs/index.html
# remove ads
LC_ALL=C sed -i .bak 's/\.\.\/properties\/151\/funder\.js//' docs/html_docs/docs/index.html
# remove non-functional search bars (sort of, this is a hack)
LC_ALL=C sed -i .bak 's/<input type="text" class="form-control" placeholder="Search".*$//' docs/html_docs/docs/index.html
LC_ALL=C sed -i .bak 's/<i class="glyphicon glyphicon-search"><\/i>//' docs/html_docs/docs/index.html
echo "Done !"

echo -n "Downloading repo... "
$GIT clone -q $REPO
echo "Done !"

# Generate API doc with Sami
echo -n "Generating API docs from repo... "
export VERSION_TAG
php $SAMI update sami-config.php
echo "Done !"

echo -n "Cleaning API docs... "
# always hide the left column
LC_ALL=C sed -i .bak 's/max-width: 991px/min-width: 0px/' docs/api_docs/css/sami.css
echo "Done !"

# Generate .docset and archive it
echo -n "Building .docset ... "
$DASHING build --source docs/ > /dev/null
tar --exclude='.DS_Store' -czf "$(basename $REPO).tgz" Carbon.docset
echo "Done !"

# Copy main archive to specific version
cp "$(basename $REPO).tgz" "versions/$(basename $REPO)-$VERSION_TAG.tgz"

# Clean directory
rm -rf Carbon.docset/
rm -rf docs/
rm -rf Carbon/

echo
echo "Docset successfully generated !"
exit 0
