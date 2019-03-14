openFrameworks Docset
=======================

Docset for openFrameworks 0.10.1

Created by [Yi donghoon](https://github.com/icq4ever), [@icq4ever](https://twitter.com/icq4ever)

To create this docset 


in `_OF_DIR_/libs/openFrameworksCompiled/project/doxygen` directory

1. set `GENERATE_DOCSET` to `YES` in `libs/openFrameworksCompiled/project/doxygen/Doxyfile`
2. set `DISABLE_INDEX` to `YES` in `libs/openFrameworksCompiled/project/doxygen/Doxyfile`
3. set `GENERATE_TAGFILE` value = `openFrameworks.tag` in `libs/openFrameworksCompiled/project/doxygen/Doxyfile`
4. run `doxgen`
5. run `make` in the generated `build/html` directory
6. generate index with [doxytag2zealdb](https://github.com/vedvyas/doxytag2zealdb) in `_OF_DIR_/libs/openFrameworksCompiled/project/doxygen` directory, with terminal command below.
    ```
    $ doxytag2zealdb --tag ./openFrameworks.tag --db ./build/html/org.doxygen.Project.docset/Contents/Resources/docSet.dsidx --include-parent-scopes --include-function-signatures
    ```
7. set icon 
8. update plist
9. rename `.docset` folder.
10. archive `.docset` folder to `.tgz` and pull request.

---

Docset for openFrameworks 0.10.0

Created by [Yi donghoon](https://github.com/icq4ever), [@icq4ever](https://twitter.com/icq4ever)
---

Docset for openFrameworks 0.9.8

Created by [Yi donghoon](https://github.com/icq4ever), [@icq4ever](https://twitter.com/icq4ever)

---

Docset for openFrameworks 0.9.3 

Created by [Yi donghoon](https://github.com/icq4ever), [@icq4ever](https://twitter.com/icq4ever)

---

Docset for openFrameworks 0.8.4 

Created by [Marcus Ficner](https://github.com/mficner), [@marcusficner](https://twitter.com/marcusficner)
