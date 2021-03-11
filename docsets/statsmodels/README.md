<<<<<<< HEAD
statsmodels Docset
=======================

_statsmodels_ Docset


 - Author: Angelo Varlotta (http://github.com/capac/)
 - Documentation: downloaded from the v0.11.1 folder from the repository at https://github.com/statsmodels/statsmodels.github.io/.

I just downloaded the v0.11.1 folder, which you can do by using SVN:

```
svn checkout https://github.com/statsmodels/statsmodels.github.io/trunk/v0.11.1
```

Basically place `trunk` in place of `tree/master` in the URL for the v0.11.1 folder. The docs folder with the HTML files will be present once you run the command above, and there you can run the `doc2dash` command.
=======
Statsmodels Dash Docset
=======================

- Docset Description:
    - From the statsmodels website: _[statsmodels](https://www.statsmodels.org/stable/about.html#about-statsmodels) is a Python module that provides classes and functions for the estimation of many different statistical models, as well as for conducting statistical tests, and statistical data exploration. An extensive list of result statistics are available for each estimator. The results are tested against existing statistical packages to ensure that they are correct. The package is released under the open source Modified BSD (3-clause) license. The online documentation is hosted at [statsmodels.org](https://www.statsmodels.org/)._

- Author:
    - [Angelo Varlotta - GitHub](https://github.com/capac)

- Docset Generation:
    - Read the `README.md` file in the `docs` directory. From the file:
      - _We use a combination of sphinx and Jupyter notebooks for the documentation. Jupyter notebooks should be used for longer, self-contained examples demonstrating a topic. Sphinx is nice because we get the tables of contents and API documentation._
    - Clone the statsmodels GitHub repository and switch to the 0.12.0 tag.
        - `git clone https://github.com/statsmodels/statsmodels.git`
        - `git fetch --all --tags --prune`
        - `git checkout tags/0.12.0 -b 0.12.0` (you may remove branch when done).
    - Create an environment for compiling the docs using Anaconda.
      - `conda create -n statsmodels-docs -c conda-forge`
    - Go into `cd statsmodels`.
    - Run `python -m pip install -e .[docs]` to install Python packages contained in the `requirement.txt` files in the `docs/` folder.
    - I needed to install several additional Python packages not contained in the `requirements.txt` file:
        - `colorama`
        - `theano`
        - `pytest`
        - `seaborn`
        - `arviz`
        - `pymc3`
        - `PyYaml`
        - `sphinx_material`
        - `nbsphinx`
    - Compile the docs with `make html`.
    - Install `doc2dash` with `python -m pip install doc2dash` (will also install: `zope.interface`, `soupsieve`, `beautifulsoup4`, `colorama`, `click`).
    - Go to `cd _build/html`.
    - Run `doc2dash` command with option parameters. Mine was: 
    ```doc2dash -n "statsmodels 0.12.0" -d "~/Library/ApplicationSupport/doc2dash/DocSets/statsmodels/0-12-0" -i "~/Pictures/Icons/dash/statsmodels/icon@2x.png" -v -j -u "https://www.statsmodels.org/" -I "index.html" ./ -a -f```
    - The statsmodels package will install directly into Dash.
>>>>>>> daee4539969911937fd29e266d25f0735f5452d3
