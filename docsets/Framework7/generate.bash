#!/bin/bash

DOCSET="Framework7"
VERSION_TAG="$1"

DASHING="`which dashing`"
NPM="`which npm`"
WGET="`which wget`"

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

# Check if wget is available
if [[ -z $WGET ]]; then
    echo "Sorry but wget isn't available in your PATH. I need it." >&2
    exit 1
fi

# Download repo archive at given tag, and unzip it
echo -n "Downloading HTML docs... "
$WGET -q -rHpk -np -Dcdn.framework7.io,framework7.io --exclude-domains=blog.framework7.io,forum.framework7.io,v1.framework7.io -P html "https://framework7.io/docs/index.html" "https://framework7.io/react/index.html" "https://framework7.io/vue/index.html"
echo "Done !"

# Generate .docset and archive it
echo -n "Building .docset ... "
$DASHING build -s html > /dev/null 2>&1
tar --exclude='.DS_Store' -cvzf "$DOCSET-$VERSION_TAG.tgz" $DOCSET.docset > /dev/null 2>&1
echo "Done !"

echo
echo "Docset successfully generated !"
exit 0
