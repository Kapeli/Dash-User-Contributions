# Flask Classy

Documentation for the [Flask Classy](https://github.com/apiguy/flask-classy), is an extension that adds class-based views to Flask, as a [Dash](http://kapeli.com/dash) docset.
    
__Author:__ [Jasim Muhammed](http://jasimmk.ninja)

__Docs repository:__ [https://github.com/apiguy/flask-classy/tree/master/docs](https://github.com/apiguy/flask-classy/tree/master/docs)

## How to generate the docset

Install [doc2dash](https://github.com/hynek/doc2dash):
```bash
$ pip install doc2dash
```

Move to a directory of choice and execute the following commands:
```bash
$ git clone git@github.com:apiguy/flask-classy.git .
$ cd docs
$ make html
```
    
Which creates html files under `_build/html`
`Build finished. The HTML pages are in _build/html.`
```bash
$ cd _build
$ doc2dash --name Flask_Classy --verbose --destination . --index-page html/index.html html/
```
Which generates Flask_Classy.docset