#!/bin/bash

DASHING="`which dashing`"
DOXYGEN="`which doxygen`"
GIT="`which git`"
WGET="`which wget`"

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

# Request URL and download unique file (1.30.0)
mkdir -p docs/
$WGET -O docs/index.html https://raw.githubusercontent.com/briannesbitt/Carbon/39489dc5e3217c973a3299d87ef2300db5e64bb3/docs/index.html

# # Download HTML docs
# echo -n "Downloading HTML docs... "
# wget -kpHN -nH -P dashing --no-check-certificate -q http://carbon.nesbot.com/docs/
# echo "Done !"

# Generate .docset and archive it
echo -n "Building .docset ... "
$DASHING build -s docs/ > /dev/null
tar --exclude='.DS_Store' -cvzf Carbon-1.30.0.tgz Carbon.docset
echo "Done !"

# Clean directory
rm -rf Carbon.docset/
rm -rf docs/

echo
echo "Docset successfully generated !"
exit 0
