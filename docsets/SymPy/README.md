# SymPy Dash Docset

**Docset Description**:

[SymPy](http://sympy.org/en/index.html) is a Python library for symbolic mathematics. It aims to become a full-featured computer algebra system (CAS) while keeping the code as simple as possible in order to be comprehensible and easily extensible.

## How to build:

1. Install doc2dash:

```cmd
pip install doc2dash
```

1. Download doc file for SymPy from https://github.com/sympy/sympy/releases

2. Unpack the downloaded archive.

3. Execute the command

```cmd
doc2dash -n SymPy -d SymPy.docset.X.Y --enable-js -i "sympy-docs-html-X.Y/_static/sympylogo.png" -uhttp://docs.sympy.org/latest/index.html -v sympy-docs-html-X.Y
```

where `X.Y` has to be replaced by the current version number

for example

```cmd
doc2dash -n SymPy -d SymPy.docset.1.12 --enable-js -i "sympy-docs-html-1.12/_static/sympylogo.png" -uhttp://docs.sympy.org/latest/index.html -v sympy-docs-html-1.12
```

4. Change into the created directory `SymPy-X.Y.docset`

5. Pack the content:

```cmd
tar cvzf SymPy.tgz SymPy.docset
```

6. Adapt the `docset.json` file and put `SymPy.tgz` into a newly created directory `X.Y` in the versions directory.
