Python Developer's Guide
=======================

* Author: Long Tan (https://github.com/tanloong)
* Instructions:
  Prerequisites include having `git`, `doc2dash`, `uv` installed on your machine.
  Steps of building document (on Windows):
    1. git clone https://github.com/python/devguide
    2. $env:PYTHON="uv run python"; ./make.bat html # If you installed python with `uv` instead of the official Python Install Manager, set `PYTHON=uv run python` to let `make.bat` use that one instead of `py -3`.
    3. doc2dash --enable-js ./_build/html # If you don't have doc2dash installed, run `uv tool install doc2dash` first.
    4. mv '.\Python Developer''s Guide.docset\' PythonDevGuide.docset
    5. tar --exclude='.DS_Store' -cvzf  "./PythonDevGuide.tgz" './PythonDevGuide.docset'

