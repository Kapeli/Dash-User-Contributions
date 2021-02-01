Papermill Dash Docset
=======================

- Docset Description:
    - [Papermill](https://papermill.readthedocs.io/en/latest/#) is a tool for parameterizing and executing Jupyter Notebooks.

- Author:
    - [Angelo Varlotta](https://github.com/capac)

- Docset Generation:
    - Clone the Papermill GitHub repository:
        - `git clone https://github.com/nteract/papermill.git`
        - `git fetch --all --tags`
        - `git checkout tags/2.1.1 -b 2.1.1`
    - Create an environment for compiling the docs using Anaconda:
      - `conda create -n papermill-docs -c conda-forge --file docs/requirements-doc.txt python=3.7`
    - `pip install requirements-azure.txt`
    - `cd papermill/docs`
    - `make html`
      - **NOTICE**: If `make` fails, you may need to install other Python packages, just use `pip install <package_name>`.
    - Install `doc2dash` with `pip install doc2dash`.
    - Run `doc2dash` command with option parameters. Mine was: 
    ```doc2dash -n "papermill" -d "/Users/angelo/Library/ApplicationSupport/doc2dash/DocSets/papermill/2-1-1" -i "/Users/angelo/Pictures/Icons/dash/papermill/icon@2x.png" -v -j -u "https://papermill.readthedocs.io/en/latest/" -I "index.html" ./ -a -f```
    - The Papermill package will install directly into Dash.