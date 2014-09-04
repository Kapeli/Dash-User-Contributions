# Jinja2 Docset

Documentation for the [Jinja2](http://jinja.pocoo.org) template engine as a [Dash](http://kapeli.com/dash) docset.
    
__Author:__ [Giacomo Comitti](https://github.com/gcmt)

__Docset repository:__ [https://github.com/gcmt/jinja2-docset](https://github.com/gcmt/jinja2-docset)

## How to generate the docset

Install [doc2dash](https://github.com/hynek/doc2dash):
```bash
$ pip install doc2dash
```

Move to a directory of choice and execute the following commands:
```bash
$ git clone https://github.com/gcmt/jinja2-docset.git
$ cd jinja2-docset
$ ./generate.sh
```

Once generated, the Jinja2 docset can be found under the `dist` folder. To install the docset, execute the following command:
```bash
$ ./install.sh
```