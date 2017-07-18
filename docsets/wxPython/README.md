wxWidgets Docset
=======================

- __Docset Description:__
    - wxPython is a GUI toolkit for the Python programming language. It allows Python programmers to create programs with a robust, highly functional graphical user interface, simply and easily. It is implemented as a Python extension module (native code) that wraps the popular wxWidgets cross platform GUI library, which is written in C++.

- __Author:__
    - [Aditya Panchal](https://github.com/bastula)

- Instructions to generate the docset:
    - Fetch the latest wxPython generated documentation from: [https://sourceforge.net/projects/wxpython/files/wxPython4/extras/](https://sourceforge.net/projects/wxpython/files/wxPython4/extras/)
    - Install doc2dash: [https://doc2dash.readthedocs.io](https://doc2dash.readthedocs.io) 
    - Run the doc2dash command in a local copy of this folder: `doc2dash -n wxPython -i icon@2x.png -i index.html -u http://docs.wxpython.org`
    - Compress the resulting docset: `tar --exclude='.DS_Store' -cvzf wxPython.tgz wxPython.docset`
    - Update the version number in docset.json
