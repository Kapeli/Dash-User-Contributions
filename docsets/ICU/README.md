ICU
=======================

Uploader: Erick Guan ([@fantasticfears](https://github.com/fantasticfears))

Instruction:

The list is how I packaged the docset. I believe it can be improved by tweaking more Doxygen parameters.

* Download source package from http://site.icu-project.org/download/59#TOC-ICU4C-Download.
* run `./configure` and `make doc`
* Edit `Doxyfile` as the instruction from Dash, Plus some editing:
```
# docset
GENERATE_DOCSET        = YES
DOCSET_FEEDNAME        = "ICU"
DOCSET_BUNDLE_ID       = org.icu-project.icu4c
```
* Run `doxygen Doxyfile && cd $ICU_DOC_PATH/doc/html && make`
* Edit `Info.plist` in the docset file. Change `CFBundleName` to `ICU` and `DocSetPlatformFamily` to `icu`.
* Copy `*.png` into the top directory level of docset.
* Rename `org.icu-project.icu4c.docset` to `ICU.docset`.
* Run `cd $ICU_DOC_PATH && tar --exclude='.DS_Store' -cvzf ICU.tgz ICU.docset`
* Adding the corresponding version in `docset.json`.

Related:

* The docset includes C/C++ ICU API. Nothing for ICU4j. I guess it's possible to get from Maven or anywhere else.
