# Celery: Distributed Task Queue, Dash Documentation

Updated by [James M. Allen](https://github.com/jamesmallen)

## How to generate the docset

Clone celery from https://github.com/celery/celery.

Install prereqs:
```console
$ pip install -U -r requirements/docs.txt
$ pip install doc2dash
# Sphinx version gets reverted by doc2dash - this updates it again
$ pip install -U sphinx>=1.7.1
```

Add the following lines inside `docs/conf.py` `build_config(`:
```python
globals().update(conf.build_config(
    html_theme_options={
        'nosidebar': True,
    },
    html_title='',
```
Run the following from within the `docs` folder:

```bash
#!/usr/bin/env bash
# optional:
# make clean

make html

# ensure dash CSS overrides are included
if ! grep -q '/*dash*/' _build/html/_static/celery.css; then
    cat << EOF >> _build/html/_static/celery.css
    /*dash*/
    div.related {
        width: auto !important;
    }

    div.document {
        width: auto !important;
    }

    div.body {
        min-width: auto !important;
        max-width: auto !important;
    }

    div.footer {
        width: auto !important;
    }
EOF
fi

# generate Dash docset and install it in global location
doc2dash -Afj -nCelery -Iindex.html -uhttp://docs.celeryproject.org/en/v4.1.0/ _build/html

# create tarball
cd ~/Library/Application\ Support/doc2dash/DocSets
tar --exclude='.DS_Store' -cvzf Celery.tgz Celery.docset

```
