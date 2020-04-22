Bokeh Dash Docset
=====

- Docset Description:
    - "Bokeh is a Python interactive visualization library that targets modern web browsers for presentation".

- Docset Author:
    - [Angelo Varlotta](https://github.com/capac)

- Installation:

For this version of bokeh, I cloned the GitHub repository and checked out the 2.0.1 tag, went into the `sphinx` directory and ran `make html` (run `make help` to see the available options):

```
git clone https://github.com/bokeh/bokeh.git
git checkout tags/2.0.1 -b 2.0.1
cd sphinx
make html
```

`make` will abort if certain Python modules are missing, so just install them. Another issue I had was this error:

```
Set GOOGLE_API_KEY to a valid API key, or set bokeh_missing_google_api_key_ok=True in conf.py to build anyway (with broken GMaps)
```

The `conf.py` file is located under `sphinx` in the `source` directory. Change the variable to True.