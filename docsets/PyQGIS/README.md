QGIS
=======================

## Author

This docset is maintained by [Julien Cabieces](https://github.com/troopa81)

## Building

First, get QGIS
```shell
git clone https://github.com/qgis/QGIS.git
```

Build it
```shell
mkdir build
cd build
cmake ../ -DWITH_3D=TRUE -WITH_SERVER=TRUE
make
```

Then, clone PyQGIS

```shell
git clone https://github.com/qgis/pyqgis.git
```

Copy `pyqgis.patch` in pyqgis directory and apply patch

```shell
patch -ruN  < pyqgis.patch
```

Build docset

```shell
./scripts/build-docs.sh
doc2dash -n PyQGIS_3 build/master/html/
```
Finally, add icons and docset.json to `PyQGIS_3.docset`

If you want to propose a PR to update this documentation, just zip it, share it (on Dropbox for instance) and give the URL in the PR.

To create the tar archive

```shell
tar cvzf PyQGIS.tgz --exclude='.DS_Store' PyQGIS_3.docset
```
