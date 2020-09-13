Airflow Dash Docset
=======================

- Docset Description:
    - [Airflow](https://airflow.apache.org) is a platform created by the community to programmatically author, schedule and monitor workflows.

- Author:
    - [Angelo Varlotta - GitHub](https://github.com/capac)

- Docset Generation:
    - Clone the Airflow GitHub repository.
        - `git clone git clone https://github.com/apache/airflow.git`
    - Go into `cd airflow` and switch to the 1.10.12 tag.
        - `git checkout tags/1.10.12 -b 1-10-12` (you may remove the branch when done).
    - Create an environment for compiling the docs using Anaconda.
        - `conda create -n airflow-docs -c conda-forge python=3.7`
    - I needed to install several additional Python packages. Just run `python -m pip install <package_name>`.
        - `apache-airflow`
        - `sphinx_rtd_theme`
        - `sphinx-autoapi`
        - `sphinx-jinja`
        - `sphinx-copybutton`
        - `sphinx-argparse`
        - `sphinxcontrib-httpdomain`
        - `doc2dash`
    - Go to `cd docs/`.
    - Compile the docs with `python build`.
    - Go to `cd _build/html`.
    - Run `doc2dash` command with option parameters. Mine was: 
    `doc2dash -n "Airflow 1.10.12" -d "/Users/angelo/Library/ApplicationSupport/doc2dash/DocSets/airflow/1-10-12" -i "/Users/angelo/Pictures/Icons/dash/airflow/icon@2x.png" -v -j -u "https://airflow.readthedocs.io/en/latest/" -I "index.html" ./ -a -f`
    - The Airflow package will install directly into Dash.
