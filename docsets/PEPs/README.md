# PEPs Docset

This docset contains all PEPs from the Python Software Foundation.

## Building the docset

1. Clone the [PEPs repository](https://github.com/python/peps)
2. Follow the build instructions. As of 2023.01.28, you need to 
   `pip install -r requirements.txt` and `make render`.
3. Install [`doc2dash`](https://pypi.org/project/doc2dash/).
4. Build Docset from built HTML:

```bash
doc2dash --index-page index.html --icon build/_static/py.png --online-redirect-url https://peps.python.org/ build
```

## Hiccups

The [`:pep:` Sphinx role typically generates a hyperlink to the PEPs website](https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-pep), 
but when buliding the PEPs documentation locally we'd like it to link to relative
pages. Indeed, the PEP repository overrides this role to provide this behaviour,
but until [PR #2972](https://github.com/python/peps/pull/2972) it was linking to
an absolute path which broke internal links when browsing locally.