# PyMC3

When you contribute a docset, you need to edit this README to include the following:

## Who am I

[Paulo S. Costa](https://github.com/paw-lu)

## Generating the docset

Assuming you have [Python](https://www.python.org/),
[gh](https://github.com/cli/cli),
[fd](https://github.com/sharkdp/fd),
[parallel](https://www.gnu.org/software/parallel/),
and [doc2dash](https://github.com/hynek/doc2dash) installed.

```sh
% gh repo clone pymc-devs/pymc3 -- --recurse-submodules

% cd pymc3

% python -m venv .venv

% source .venv/bin/activate

(venv)% python -m pip install .

(venv)% python -m pip install -r requirements-dev.txt

(venv)% latesttag=$(git describe --tags `git rev-list --tags --max-count=1`)

(venv)% git checkout ${latesttag)

(venv)% git submodule update --remote

(venv)% cd docs/source

(venv)% make html

(venv)% cd ..

(venv)% doc2dash --icon logos/PyMC3.png --enable-js --online-redirect-url='https://docs.pymc.io/' --name='PyMC3' --index-page source/_build/html/index.html source/_build/html

(venv)% cd PyMC3.docset

(venv)% fd --extension=ipynb | parallel trash

(venv)% fd --extension=ipynb.txt | parallel trash

(venv)% fd 'pymc-examples*' PyMC3.docset/Contents/Resources/Documents/_images | parallel trash
```

## Bugs and known issues

The generated docset is very large
and the notebook components will not render correctly.
To save space, the notebook components are deleted.
