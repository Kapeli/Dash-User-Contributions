Dask Dash Docset
=====

- Docset Description:
    - "Versatile parallel programming with task scheduling".

- Docset Author:
    - [Angelo Varlotta - GitHub](https://github.com/capac)
    
- Installation:
    - Clone Dask GitHub repository and switch to 2.25.0 tag.
        - `git clone https://github.com/dask/dask.git`.
        - `git fetch --all --tags --prune`
        - `git checkout tags/2.25.0 -b 2.25.0` (you may remove the branch once done)
    - Create an environment for compiling the docs using Anaconda:
      - `conda create -n dask_docs -c conda-forge --file docs/requirements-docs.txt`.
    - `cd dask/docs`
    - `make html`
    - Install `doc2dash` with `pip install doc2dash`, will also install the additional packages `colorama, soupsieve, beautifulsoup4, attrs, zope.interface`.
    - Run `doc2dash` command with option parameters. Mine was: 
    ```doc2dash -n "Dask 2.25.0" -d "/Users/angelo/Library/ApplicationSupport/doc2dash/DocSets/dask/2-25-0" -i "/Users/angelo/Pictures/Icons/dash/dask/icon@2x.png" -v -j -u "https://docs.dask.org/en/latest/" -I "index.html" ./ -a -f```
    - Dask package will install directly in Dash.
