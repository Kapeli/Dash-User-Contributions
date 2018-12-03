QGIS
=======================

## Author

This docset is maintained by [Julien Cabieces](https://github.com/troopa81)

## Building

First, get QGIS
```shell
git clone https://github.com/qgis/QGIS.git
```

Then edit Doxyfile template file *cmake_templates/Doxyfile.in* and modify these values
```
GENERATE_DOCSET        = YES
DOCSET_FEEDNAME        = "QGIS"
DOCSET_BUNDLE_ID       = QGIS_3.docset
DOCSET_PUBLISHER_ID    = com.QGIS
DOCSET_PUBLISHER_NAME  = QGIS
DISABLE_INDEX          = YES
SEARCHENGINE           = NO
GENERATE_TAGFILE       = qgis.tag
```

Build it
```shell
mkdir build
cd build
cmake ../ -DWITH_APIDOC=TRUE -DWITH_3D=TRUE
make
```

Then generate docset (doxytag2zealdb can be installed with pip)
```shell
# First command fail on docsetutil missing, nevermind!
cd doc/api/html && make
doxytag2zealdb --tag doc/qgis.tag --db doc/api/html/QGIS_3.docset/Contents/Resources/docSet.dsidx  --include-parent-scopes --include-function-signatures
```

Finally, add icons and meta.json
