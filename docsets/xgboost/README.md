XGBoost Docset
=======================

_XGBoost_ Docset


 - Author: Angelo Varlotta (http://github.com/capac/)
 - Documentation: downloaded and compiled int he `doc` subdirectory from the 1.0.2 tag at the XGBoost GitHub repository.


Package requirements:

```
alabaster==0.7.12
altair==3.2.0
appdirs==1.4.3
appnope==0.1.0
asn1crypto==1.3.0
attrs==19.3.0
Babel==2.8.0
backcall==0.1.0
beautifulsoup4==4.8.1
black==19.3b0
bleach==3.1.0
breathe==4.14.1
certifi==2019.11.28
cffi==1.14.0
chardet==3.0.4
Click==7.0
cloudpickle==1.3.0
colorama==0.4.3
commonmark==0.9.1
cryptography==2.8
css-html-js-minify==2.5.5
cycler==0.10.0
cytoolz==0.10.1
dask==2.13.0
decorator==4.4.2
defusedxml==0.6.0
doc2dash==2.3.0
docutils==0.16
entrypoints==0.3
future==0.18.2
graphviz==0.13.2
guzzle-sphinx-theme==0.7.11
idna==2.9
imageio==2.8.0
imagesize==1.2.0
importlib-metadata==1.5.0
ipykernel==5.1.4
ipython==7.13.0
ipython-genutils==0.2.0
ipywidgets==7.5.1
jedi==0.16.0
Jinja2==2.11.1
joblib==0.14.1
jsonschema==3.2.0
jupyter==1.0.0
jupyter-client==6.1.0
jupyter-console==6.1.0
jupyter-core==4.6.1
kiwisolver==1.1.0
lxml==4.4.1
MarkupSafe==1.1.1
matplotlib==3.1.3
mistune==0.8.4
mkl-fft==1.0.15
mkl-random==1.1.0
mkl-service==2.3.0
mock==4.0.1
more-itertools==8.2.0
nbconvert==5.6.1
nbformat==5.0.4
nbsphinx==0.5.0
networkx==2.4
notebook==6.0.3
numpy==1.18.1
numpydoc==0.9.2
olefile==0.46
packaging==20.3
pandas==1.0.3
pandas-datareader==0.8.1
pandocfilters==1.4.2
parso==0.6.2
patsy==0.5.1
pexpect==4.8.0
pickleshare==0.7.5
Pillow==7.0.0
pluggy==0.13.1
prometheus-client==0.7.1
prompt-toolkit==3.0.4
ptyprocess==0.6.0
py==1.8.1
pycparser==2.20
Pygments==2.6.1
pyOpenSSL==19.1.0
pyparsing==2.4.6
pyrsistent==0.15.7
PySocks==1.7.1
pytest==5.4.1
python-dateutil==2.8.1
pytz==2019.3
PyWavelets==1.1.1
pyzmq==18.1.1
qtconsole==4.7.2
QtPy==1.9.0
recommonmark==0.6.0
requests==2.23.0
rpy2==2.9.4
scikit-image==0.16.2
scikit-learn==0.22.1
scipy==1.4.1
seaborn==0.10.0
selenium==3.141.0
Send2Trash==1.5.0
sh==1.12.14
simplegeneric==0.8.1
six==1.14.0
snowballstemmer==2.0.0
soupsieve==1.9.5
Sphinx==2.4.4
sphinx-gallery==0.5.0
sphinx-material==0.0.16
sphinx-rtd-theme==0.4.3
sphinxcontrib-applehelp==1.0.2
sphinxcontrib-devhelp==1.0.2
sphinxcontrib-htmlhelp==1.0.3
sphinxcontrib-jsmath==1.0.1
sphinxcontrib-qthelp==1.0.3
sphinxcontrib-serializinghtml==1.1.4
sphinxcontrib-websupport==1.2.1
statsmodels==0.11.0
terminado==0.8.3
testpath==0.4.4
toml==0.10.0
toolz==0.10.0
tornado==6.0.4
traitlets==4.3.3
tzlocal==2.0.0
Unidecode==1.0.23
urllib3==1.25.8
vega==2.6.0
vega-datasets==0.7.0
wcwidth==0.1.8
webencodings==0.5.1
widgetsnbextension==3.5.1
zipp==2.2.0
zope.interface==4.7.2
```

Run the following commands:

```
git clone https://github.com/dmlc/xgboost.git -tag v1.0.2
cd doc
make html
```

After this, you can run the `doc2dash` command in the directory:

```
doc2dash -n "xgboost" -d "$HOME/Library/ApplicationSupport/doc2dash/DocSets/xgboost/1-0-2" -i "$HOME/Pictures/Icons/dash/xgboost/icon@2x.png" -v -j -u "https://xgboost.readthedocs.io/en/stable/" -I "index.html" ./ -a -f
```