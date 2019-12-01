Altair Docset
=======================

I had to install many Python packages in order for the `MakeFile` to compile properly. Here is the list from `pip freeze`:

```bash
conda create -n myenv python=3.7.5  # if the environment isn't in place
conda activate docs
git clone https://github.com/altair-viz/altair.git
git fetch --all --tags --prune
git checkout tags/v3.2.0 -b origin/master
cd doc/
make help  # gives a list of make commands that can be used
make html
```

List of prerequisites:

```bash
alabaster==0.7.12
altair==3.2.0
appnope==0.1.0
asn1crypto==1.2.0
attrs==19.3.0
Babel==2.7.0
backcall==0.1.0
bleach==3.1.0
certifi==2019.9.11
cffi==1.13.2
chardet==3.0.4
commonmark==0.9.1
cryptography==2.8
decorator==4.4.1
defusedxml==0.6.0
docutils==0.15.2
entrypoints==0.3
future==0.18.2
idna==2.8
imagesize==1.1.0
importlib-metadata==0.23
ipykernel==5.1.3
ipython==7.9.0
ipython-genutils==0.2.0
ipywidgets==7.5.1
jedi==0.15.1
Jinja2==2.10.3
jsonschema==3.2.0
jupyter-client==5.3.4
jupyter-console==6.0.0
jupyter-core==4.6.1
MarkupSafe==1.1.1
mistune==0.8.4
mkl-fft==1.0.15
mkl-random==1.1.0
mkl-service==2.3.0
more-itertools==7.2.0
nbconvert==5.6.1
nbformat==4.4.0
notebook==6.0.2
numpy==1.17.3
numpydoc==0.9.1
olefile==0.46
packaging==19.2
pandas==0.25.3
pandocfilters==1.4.2
parso==0.5.1
pexpect==4.7.0
pickleshare==0.7.5
Pillow==6.2.1
prometheus-client==0.7.1
prompt-toolkit==2.0.10
ptyprocess==0.6.0
pycparser==2.19
pygame==1.9.5
Pygments==2.4.2
pyOpenSSL==19.1.0
pyparsing==2.4.5
pyrsistent==0.15.5
PySocks==1.7.1
python-dateutil==2.8.1
python-slugify==3.0.2
pytz==2019.3
pyzmq==18.1.0
qtconsole==4.6.0
recommonmark==0.6.0
requests==2.22.0
selenium==3.141.0
Send2Trash==1.5.0
six==1.13.0
snowballstemmer==2.0.0
Sphinx==2.2.1
sphinx-rtd-theme==0.4.3
sphinxcontrib-applehelp==1.0.1
sphinxcontrib-devhelp==1.0.1
sphinxcontrib-htmlhelp==1.0.2
sphinxcontrib-jsmath==1.0.1
sphinxcontrib-qthelp==1.0.2
sphinxcontrib-serializinghtml==1.1.3
sphinxcontrib-websupport==1.1.2
terminado==0.8.3
testpath==0.4.4
text-unidecode==1.2
toolz==0.10.0
tornado==6.0.3
traitlets==4.3.3
urllib3==1.24.2
vega==2.6.0
vega-datasets==0.7.0
wcwidth==0.1.7
webencodings==0.5.1
widgetsnbextension==3.5.1
zipp==0.6.0
```

Also you will need to place the `ChromeDriver` binary in your path and install Google Chrome in the Applications folder ("a directory that the `make` file expects Chrome to be located in"). You can download the driver from ['ChromeDriver - WebDriver for Chrome'](https://sites.google.com/a/chromium.org/chromedriver/home).

I had an error message about deprecated use of `script_files`, which I removed by making use of the code modification from ['readthedocs/sphinx_rtd_theme - sphinx_rtd_theme/search.html'](https://github.com/readthedocs/sphinx_rtd_theme/commit/a49a812c8821123091166fae1897d702cdc2d627#diff-b3d4a9c32d5abd89b9214dcfbb2ece79).

IMPORTANT: Thre are two index files which don't have the correct URL to display thumbnail images. They are the `index.html` in `altair/doc/_build/html/index.html` and the `index.html` file in `altair/doc/_build/html/gallery/index.html`. For the first file, one needs to change `/_static` to `_static`, while in the second file `/_static` to `../_static`.

There are still many `docstring` warning messages about "Unexpected indentation", "Bullet list ends without a blank line; unexpected unindent" or "Block quote ends without a blank line; unexpected unindent" but these seem to be innocuous.
