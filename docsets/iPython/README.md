iPython Dash Docset
=======================

- Docset Description:
    - [iPython](https://ipython.org/) provides a rich toolkit to help you make the most of using Python interactively. Its main components are: 
       - A powerful interactive Python shell,
       - A Jupyter kernel to work with Python code in Jupyter notebooks and other interactive frontends.

- Author:
    - [Angelo Varlotta - GitHub](https://github.com/capac)

- Installation:
    - Clone iPython GitHub repository and switch to 7.14.0 tag.
        - `https://github.com/ipython/ipython.git`
        - `git fetch --all --tags`
        - `git checkout tags/7.14.0 -b 7.14.0`
        - `cd ipython`
    - Create an environment for compiling the docs using Anaconda:
      - `conda create -n ipython-docs -c conda-forge`.
    - Follow the instructions in `README.rst` in the `ipython/docs` directory, like running `pip install -U -r docs/requirements.txt` in the `ipython` directory.
    - `cd docs`
    - `make html`
      - You should install with `pip` or `conda` the `graphviz` package to avoid a warning message that occurs during compile time.
    - Install `doc2dash` with `pip install doc2dash`.
    - Run `doc2dash` command with option parameters. Mine was: 
    ```doc2dash -n "iPython" -d "/Users/angelo/Library/ApplicationSupport/doc2dash/DocSets/ipython/7-14-0" -i "/Users/angelo/Pictures/Icons/dash/ipython/ipython-text/icon@2x.png" -v -j -u "https://ipython.readthedocs.io/en/stable/" -I "index.html" ./ -a -f```
    - iPython package will install directly in Dash.