# path.py Docset

Author: Rob Speed	 
https://robspeed.rocks


## Building Docset

Trimming the fat that Sphinx insists on creating is a bit involved, so I built a shell script to automate the process. It might be easier to just create my own theme.


### Project Directory

I recommend using a virtualenv.

```sh
virtualenv path.py-docset
cd path.py-docset
source bin/activate
```


### Dependencies

path.py needs to be installed as editable. The build script can be fetched from github.

```sh
pip install setuptools_scm rst.linker sphinx-readable-theme doc2dash jaraco.packaging
pip install -e git+https://github.com/jaraco/path.py.git#egg=path.py
curl -O https://raw.githubusercontent.com/Kapeli/Dash-User-Contributions/master/docsets/path.py/build.sh
```


### Build

The version number can be omitted, which will build the documentation in its current state.

```sh
bash build.sh 8.2.1
```


## Known Bugs

* Doesn't work in Windows. \*shrug\*
* Error messages reading "fatal: git checkout: --detach does not take a path argument" means that the requested version hasn't been tagged.
