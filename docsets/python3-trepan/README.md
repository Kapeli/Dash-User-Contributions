python3-trepan Dash Docset
==========================

- __Docset Description__:
  - `python3-trepan` debugger documentation for Python.

- __Author__:
  - [sheikheddy](https://github.com/sheikheddy)

- __Upstream docs__:
  - [https://python3-trepan.readthedocs.io/en/latest/](https://python3-trepan.readthedocs.io/en/latest/)

- __How the docset was generated__:
  - Mirror docs HTML from Read the Docs.
  - Ensure `objects.inv` is present.
  - Build docset with `doc2dash` intersphinx parser.

Example commands:

```bash
wget --mirror --convert-links --adjust-extension --page-requisites --no-parent \
  https://python3-trepan.readthedocs.io/en/latest/ -P ./build

curl -fsSL https://python3-trepan.readthedocs.io/en/latest/objects.inv \
  -o ./build/python3-trepan.readthedocs.io/en/latest/objects.inv

uvx doc2dash --parser doc2dash.parsers.intersphinx.InterSphinxParser \
  -n python3-trepan -I index.html \
  ./build/python3-trepan.readthedocs.io/en/latest/

tar --exclude='.DS_Store' -cvzf python3-trepan.tgz python3-trepan.docset
```
