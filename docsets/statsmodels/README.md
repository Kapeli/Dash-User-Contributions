statsmodels Docset
=======================

_statsmodels_ Docset


 - Author: Angelo Varlotta (http://github.com/capac/)
 - Documentation: downloaded from https://github.com/statsmodels/statsmodels and contained in the docs/ folder

General installation procedure:

```python
git clone https://github.com/statsmodels/statsmodels.git
git fetch --all --tags --prune
git checkout tags/v0.10.1 -b origin/master
cd statsmodels/docs
make html
```

To generate the documentation, you will need to download the following packages:

```python
alabaster==0.7.12
appnope==0.1.0
atomicwrites==1.3.0
attrs==19.1.0
Babel==2.7.0
backcall==0.1.0
beautifulsoup4==4.8.0
bleach==3.1.0
certifi==2019.6.16
cffi==1.12.3
chardet==3.0.4
Click==7.0
colorama==0.4.1
cycler==0.10.0
Cython==0.29.12
decorator==4.4.0
defusedxml==0.6.0
doc2dash==2.3.0
docutils==0.15
entrypoints==0.3
fuzzywuzzy==0.17.0
idna==2.8
imagesize==1.1.0
importlib-metadata==0.18
ipykernel==5.1.1
ipython==7.6.1
ipython-genutils==0.2.0
ipywidgets==7.5.0
jedi==0.14.1
Jinja2==2.10.1
jsonschema==3.0.1
jupyter==1.0.0
jupyter-client==5.3.1
jupyter-console==6.0.0
jupyter-core==4.5.0
kiwisolver==1.1.0
lxml==4.3.4
MarkupSafe==1.1.1
matplotlib==3.1.1
meson==0.51.1
mistune==0.8.4
more-itertools==7.2.0
nbconvert==5.5.0
nbformat==4.4.0
notebook==6.0.0
numpy==1.16.4
numpydoc==0.9.1
packaging==19.0
pandas==0.24.2
pandas-datareader==0.7.0
pandocfilters==1.4.2
parso==0.5.1
patsy==0.5.1
pexpect==4.7.0
pickleshare==0.7.5
pluggy==0.12.0
prometheus-client==0.7.1
prompt-toolkit==2.0.9
ptyprocess==0.6.0
py==1.8.0
pycparser==2.19
Pygments==2.4.2
pyparsing==2.4.1
pyrsistent==0.15.3
pytest==5.0.1
python-dateutil==2.8.0
pytz==2019.1
pyzmq==18.0.2
qtconsole==4.5.1
requests==2.22.0
rpy2==3.0.5
scipy==1.3.0
seaborn==0.9.0
Send2Trash==1.5.0
simplegeneric==0.8.1
six==1.12.0
snowballstemmer==1.9.0
soupsieve==1.9.2
Sphinx==2.1.2
sphinxcontrib-applehelp==1.0.1
sphinxcontrib-devhelp==1.0.1
sphinxcontrib-htmlhelp==1.0.2
sphinxcontrib-jsmath==1.0.1
sphinxcontrib-qthelp==1.0.2
sphinxcontrib-serializinghtml==1.1.3
terminado==0.8.2
testpath==0.4.2
tornado==6.0.3
traitlets==4.3.2
tzlocal==1.5.1
urllib3==1.25.3
wcwidth==0.1.7
webencodings==0.5.1
widgetsnbextension==3.5.0
wrapt==1.11.2
zipp==0.5.2
zope.interface==4.6.0
```

`pandas_datareader` doesn't seem to work currently with `pandas 0.25` so downgrade to `pandas 0.24.2` to make `pandas_datareader` work nicely.

The documentation build generates many warning messages about documents "not included in any toctree":

```bash
file_name.rst: WARNING: document isn't included in any toctree
```

To the best of my knowledge this doesn't seem to effect the documentation generation, but it likely warrants an inquiry into the matter.
