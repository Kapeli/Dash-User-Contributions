Dask Dash Docset
=====

- Docset Description:
    - "Versatile parallel programming with task scheduling".

- Docset Author:
    - [Angelo Varlotta](https://github.com/capac)
    
- Installation:
    - Clone Dask GitHub repository and switch to 2.15.0 tag
        - `git clone https://github.com/dask/dask.git`
        - `git fetch --all --tags`
        - `git checkout tags/2.15.0 -b 2.15.0`
    - Create an environment for compiling the docs using Anaconda:
      - `conda create -n dask_docs -c conda-forge --file requirements-docs.txt`, the `requirement-docs.txt` file is in the `dask/docs` directory.
    - `cd dask/docs`
    - `make html`
    - Install `doc2dash` with `pip install doc2dash`. Also install additional packages `colorama, soupsieve, beautifulsoup4, attrs, zope.interface`.
    - Run `doc2dash` command with option parameters. Mine was: 
    ```doc2dash -n "dask" -d "/Users/angelo/Library/ApplicationSupport/doc2dash/DocSets/dask/2-15-0" -i "/Users/angelo/Pictures/Icons/dash/dask/icon@2x.png" -v -j -u "https://docs.dask.org/en/latest/" -I "index.html" ./ -a -f```
    - Dask package will install directly in Dash.