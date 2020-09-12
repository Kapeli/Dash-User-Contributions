XGBoost  Dash Docset
=======================

- Docset Description:
    - From the XGBoost Documentation web page: _[XGBoost](https://xgboost.readthedocs.io/en/latest/index.html) is an optimized distributed gradient boosting library designed to be highly efficient, flexible and portable. It implements machine learning algorithms under the [Gradient Boosting](https://en.wikipedia.org/wiki/Gradient_boosting) framework. XGBoost provides a parallel tree boosting (also known as GBDT, GBM) that solve many data science problems in a fast and accurate way. The same code runs on major distributed environment (Hadoop, SGE, MPI) and can solve problems beyond billions of examples._

 - Author:
    - [Angelo Varlotta - GitHub](http://github.com/capac/)

- Docset Generation:
    - Clone the XGBoost GitHub repository:
        - `git clone https://github.com/dmlc/xgboost.git`
        - `cd xgboost`
        - `git fetch --all --tags --prune`
        - `git checkout tags/v1.2.0 -b v1.2.0`
    - Create a Conda environment:
        - `conda create -n xgboost-docs -c conda-forge python=3.7`
    - Install `pip` dependencies and `doc2dash`:
        - `cd doc`
        - `python -m pip install -r requirements.txt`
        - `python -m pip install doc2dash`
    - Extra required modules:
        - `recommonmark`
        - To avoid the error message: _make sure the Graphviz executables are on your systems' PATH_, install:
            - `conda install -c conda-forge python-graphviz`
    - Now run: 
        - `cd _build/html`
        - `doc2dash -n "XGBoost 1.2.0" -d "/Users/angelo/Library/ApplicationSupport/doc2dash/DocSets/xgboost/1-2-0" -i "/Users/angelo/Pictures/Icons/dash/xgboost/icon@2x.png" -v -j -u "https://xgboost.readthedocs.io/en/stable/" -I "index.html" ./ -a -f`
    - The XGBoost package will install directly into Dash.
