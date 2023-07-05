Statsmodels Dash Docset
=======================

- Docset Description:
    - From the statsmodels website: _[statsmodels](https://www.statsmodels.org/stable/about.html#about-statsmodels) is a Python module that provides classes and functions for the estimation of many different statistical models, as well as for conducting statistical tests, and statistical data exploration. An extensive list of result statistics are available for each estimator. The results are tested against existing statistical packages to ensure that they are correct. The package is released under the open source Modified BSD (3-clause) license. The online documentation is hosted at [statsmodels.org](https://www.statsmodels.org/)._

- Author:
    - [Angelo Varlotta - GitHub](https://github.com/capac)

- Docset Generation:
    - Read the `README.md` file in the main and `docs` directory.
    - Create an environment for compiling the docs using Anaconda.
      - `conda create -n statsmodels-docs -c conda-forge`
    - Clone from the statsmodels GitHub repository the v0.14.0 branch and switch to the directory.
        - `git clone --branch=v0.14.0 https://github.com/statsmodels/statsmodels`
    - Run `python -m pip install -f requirement.txt` and `python -m pip install -f requirement-doc.txt` to install required Python packages.
    - You may need to install several additional Python packages not contained in the requirements file. Just run `python -m pip install <package-name>` or `conda install -c conda-forge <package-name>`.
    - Go to `cd docs/`
    - Compile the docs with `make html`.
    - Install `doc2dash` with `python -m pip install doc2dash` (will also install extra packages).
    - Go to `cd _build/html`.
    - Run `doc2dash` command with option parameters. My command was: 
    ```doc2dash -n "statsmodels 0.14.0" -d "~/Library/ApplicationSupport/doc2dash/DocSets/statsmodels/0-14-0" -i "~/Pictures/Icons/dash/statsmodels/icon@2x.png" -v -j -u "https://www.statsmodels.org/" -I "index.html" ./ -a -f```
    - The statsmodels package will install directly into Dash.
