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
DOCSET_BUNDLE_ID       = QGIS_3
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
cmake ../ -DWITH_APIDOC=TRUE -DWITH_3D=TRUE -WITH_SERVER=TRUE
make
make apidoc
```
Then, in *doc/api/html/Info.plist* remove *CFBundleVersion* (key and string value), and add the following two lines
```xml
<key>isDashDocset</key>
<true/>
```

Then generate docset (doxytag2zealdb can be installed with pip, but be aware that you may have to apply this [patch](https://github.com/vedvyas/doxytag2zealdb/pull/2)). 
```shell
# First command fail on docsetutil missing, nevermind!
cd doc/api/html && make
cd ../../../
doxytag2zealdb --tag doc/qgis.tag --db doc/api/html/QGIS_3.docset/Contents/Resources/docSet.dsidx  --include-parent-scopes --include-function-signatures
```

Finally, add icons and docset.json to `doc/api/html/QGIS_3.docset`

If you want to propose a PR to update this documentation, just zip it, share it (on Dropbox for instance) and give the URL in the PR.

To create the tar archive

```shell
cd doc/api/html && tar cvzf QGIS.tgz --exclude='.DS_Store' QGIS_3.docset
```
