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

# Archive the DocSet
cd build/doc/html
tar --exclude='.DS_Store' -cvzf ~/Downloads/Elektra.tgz org.libelektra.docset
```
