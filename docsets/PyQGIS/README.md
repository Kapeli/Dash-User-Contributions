PyQGIS
=======================

## Author

This docset is maintained by [Julien Cabieces](https://github.com/troopa81) and [Jacky Volpes](https://github.com/Djedouas)

## Building

First, get QGIS
```shell
git clone https://github.com/qgis/QGIS.git
```

Build it
```shell
mkdir build
cd build
cmake ../ -DWITH_3D=TRUE -DWITH_SERVER=TRUE
make
```

Then, clone PyQGIS

```shell
git clone https://github.com/qgis/pyqgis.git  --depth=1
```

Copy `pyqgis.patch` in pyqgis directory and apply patch

```shell
patch -ruN  < pyqgis.patch
```

Build docset (prerequisites with pip are sphinx, python-docs-theme, doc2dash, pyaml, sphinxcontrib-jquery)

```shell
./scripts/build-docs.sh
doc2dash -n PyQGIS_3 build/master/
```
Finally, add icons and docset.json to `PyQGIS_3.docset`

To create the tar archive

```shell
tar cvzf PyQGIS.tgz --exclude='.DS_Store' PyQGIS_3.docset
```
