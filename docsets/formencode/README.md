# FormEncode

Documentation for the [FormEncode](http://www.formencode.org/en/latest/) validation and form generation package as a [Dash](http://kapeli.com/dash) docset.
    
__Author:__ [Jasim Muhammed](http://jasimmk.ninja)

__Docs repository:__ [https://github.com/formencode/formencode/tree/master/docs](https://github.com/formencode/formencode/tree/master/docs)

## How to generate the docset

Install [doc2dash](https://github.com/hynek/doc2dash):
```bash
$ pip install doc2dash
```

Move to a directory of choice and execute the following commands:
```bash
$ git clone git@github.com:formencode/formencode.git .
$ cd docs
$ make html
$ pip install sphinxjp.themes.basicstrap
```

Add these settings to the `docs/conf.py`

    extensions += ['sphinxjp.themes.basicstrap']
    html_theme = 'basicstrap'

Now you can run

    $ make html
    
which creates html files under `_build/html`
`Build finished. The HTML pages are in _build/html.`
```bash
$ cd _build
$ doc2dash --name formencode --verbose --destination . --index-page html/index.html html/
```
Which generates formencode.docset