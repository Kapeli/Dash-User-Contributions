Seaborn Dash Docset
=======================

- Docset Description:
    - [Seaborn](http://seaborn.pydata.org/) is a Python data visualization library based on matplotlib. It provides a high-level interface for drawing attractive and informative statistical graphics.

- Author:
    - [Angelo Varlotta - GitHub](https://github.com/capac)

- Docset Generation:
    - Read the README.md file. From the file:
      - _The build process involves conversion of Jupyter notebooks to `rst` files. To facilitate this, you may need to set `NB_KERNEL` environment variable to the name of a kernel on your machine (e.g. `export NB_KERNEL="python3"`). To get a list of available Python kernels, run `jupyter kernelspec list`._
    - Clone the Seaborn GitHub repository and switch to the 0.11.0 tag.
        - `git clone https://github.com/mwaskom/seaborn.git`
        - `git fetch --all --tags --prune`
        - `git checkout tags/0.11.0 -b 0.11.0` (you can remove branch when done).
    - Create an environment for compiling the docs using Anaconda.
      - Go to `cd seaborn/docs`.
      - `conda create -n seaborn-docs -c conda-forge --file requirements.txt`
    - I needed to install several additional Python packages not contained in the `requirements.txt` file:
        - `numpy`
        - `matplotlib`
        - `seaborn`
    - Compile the docs with `make notebooks html`.
    - Install `doc2dash` with `python -m pip install doc2dash` (will also install: `zope.interface`, `soupsieve`, `beautifulsoup4`, `colorama`, `click`).
    - Go to `cd _build/html`.
    - Run `doc2dash` command with option parameters. Mine was: 
    ```doc2dash -n "seaborn 0.11.0" -d "/Users/angelo/Library/ApplicationSupport/doc2dash/DocSets/seaborn/0-11-0" -i "/Users/angelo/Pictures/Icons/dash/seaborn/icon@2x.png" -v -j -u "http://seaborn.pydata.org/" -I "index.html" ./ -a -f```
    - The Seaborn package will install directly into Dash.
