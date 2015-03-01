Wand Docset
=======================

Wand is a ctypes-based simple ImageMagick binding for Python.

* Author: [Hong Minhee](https://github.com/dahlia/wand)
* Docset by: [Joao](https://github.com/joaoponceleao)
* Instructions to generate docset:
    - Clone the Wand docset [fork](https://github.com/joaoponceleao/wand) (a fork is used to adjust the docs format for Dash).
    - Install [doc2dash](https://pypi.python.org/pypi/doc2dash) in a virtualenv
    - In the fork root directory:
        + `./makedoc.sh`
        + Done! It will ask if you want to open the docset in dash at the end or not (remember to delete any previous Wand docsets you may have installed). The docset itself will be saved to the root directory of the fork.
        + Note. JavaScript is enabled by default for the search functionality inside the docset (not needed for Dash's search). If you want to disable it, change line 21 (`if plutil ... -bool True ...`) to (`if plutil ... -bool False ...`) in the `makedoc.sh` script located in the root directory of the fork, before running the script.
