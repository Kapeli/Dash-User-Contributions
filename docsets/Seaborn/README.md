Seaborn Dash Docset
=======================

- Docset Description:
    - [Seaborn](http://seaborn.pydata.org/) is a Python data visualization library based on matplotlib. It provides a high-level interface for drawing attractive and informative statistical graphics.

- Author:
    - [Angelo Varlotta](https://github.com/capac)

- Docset Generation:
    - Clone Seaborn GitHub repository and switch to 0.10.1 tag
        - `git clone https://github.com/mwaskom/seaborn.git`
        - `git fetch --all --tags`
        - `git checkout tags/0.10.1 -b 0.10.1`
    - Create an environment for compiling the docs using Anaconda:
      - `conda create -n seaborn-docs -c conda-forge --file requirements.txt`, the `requirements.txt` file is in the `seaborn/docs` directory.
    - `cd seaborn/docs`
    - install several Python packages:
        - `matplotlib`
        - `scipy`
        - `pandas`
        - `numpydoc`
        - `statsmodels`
    - `make html`
    - Install `doc2dash` with `pip install doc2dash`.
    - Run `doc2dash` command with option parameters. Mine was: 
    ```doc2dash -n "seaborn" -d "/Users/angelo/Library/ApplicationSupport/doc2dash/DocSets/seaborn/0-10-1" -i "/Users/angelo/Pictures/Icons/dash/seaborn/icon@2x.png" -v -j -u "http://seaborn.pydata.org/" -I "index.html" ./ -a -f```
    - Seaborn package will install directly in Dash.
