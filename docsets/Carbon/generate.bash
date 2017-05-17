#!/bin/bash

DASHING=
WGET=wget

# Check if wget is available
if [[ -z `which wget` ]]; then
    (>&2 echo "Sorry but wget isn't available in your PATH. I need it.")
    exit 1
fi

# Check if dashing is available in $PATH, download it otherwise
if [[ -n `which dashing` ]]; then
    DASHING=`which dashing`
else
    echo -n "Dashing isn't available on your system. Downloading it... "
    wget --no-check-certificate -q https://github.com/technosophos/dashing/releases/download/0.3.0/dashing
    DASHING=./dashing
    echo "Done !"
fi

# Download HTML docs
echo -n "Downloading HTML docs... "
wget -kpHN -nH -P dashing --no-check-certificate -q http://carbon.nesbot.com/docs/
echo "Done !"

# Generate .docset and archive it
echo -n "Building .docset ... "
$DASHING build -s dashing > /dev/null
echo "Done !"

echo
echo "Docset successfully generated !"
exit 0
