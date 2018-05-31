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

# Create the build folder
cd libelektra
mkdir build
cd build

# Build the DocSet
cmake .. -DBUILD_DOCSET=ON -DBUILD_FULL=OFF -DBUILD_SHARED=OFF \
         -DBUILD_STATIC=OFF -DBUILD_TESTING=OFF
make

# Archive the DocSet
cd doc/html
tar --exclude='.DS_Store' -cvzf ~/Downloads/Elektra.tgz org.libelektra.docset
```
