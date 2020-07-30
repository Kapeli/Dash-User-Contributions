# Elektra DocSet

This folder contains a DocSet for [Elektra](https://libelektra.org).

## Maintainer

René Schwaiger ([sanssecours](https://github.com/sanssecours))

## Prerequisites

- [CMake](https://cmake.org)
- [Git](https://git-scm.com)

## How to Build

```sh
# Clone Elektra’s repository
git clone https://github.com/ElektraInitiative/libelektra.git

# Change working directory to repository root
cd libelektra

# Build the DocSet
cmake -DBUILD_DOCSET=ON -DBUILD_FULL=OFF -DBUILD_SHARED=OFF \
      -DBUILD_STATIC=OFF -DBUILD_TESTING=OFF -Bbuild
cmake --build build

# If the command before failed, then please edit `build/doc/html/Makefile`
# and change the variable `XCODE_INSTALL` to the root of your
# installation of `docsetutil`. For example, if you store `docsetutil` at
# `~/Documents/Development/Applications/DocSetUtil/Developer`, then
# change the variable to
# `$(HOME)/Documents/Development/Applications/DocSetUtil/Developer`.
# See also: https://github.com/Kapeli/Dash-User-Contributions/pull/1884

# Only use the following four commands, if your version of Xcode
# does not include `docsetutil` and you store `docsetutil` at
# `~/Documents/Development/Applications/DocSetUtil/Developer/usr/bin`.
cd build/doc/html
sed -i'' -E 's~XCODE_INSTALL=.*~XCODE_INSTALL="$(HOME)/Documents/Development/Applications/DocSetUtil/Developer"~' Makefile
make
cd ../../..

# Archive the DocSet
cd build/doc/html
tar --exclude='.DS_Store' -cvzf ~/Downloads/Elektra.tgz org.libelektra.docset
```
