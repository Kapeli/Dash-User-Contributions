Bokeh Dash Docset
=====

- Docset Description:
    - From the Bokeh web site: "Bokeh is a Python interactive visualization library that targets modern web browsers for presentation. It provides elegant, concise construction of versatile graphics, and affords high-performance interactivity over large or streaming datasets. Bokeh can help anyone who would like to quickly and easily make interactive plots, dashboards, and data applications."

- Docset Author:
    - [Angelo Varlotta - GitHub](https://github.com/capac)

- Installation:

For this version of Bokeh, I cloned the GitHub repository and checked out the 2.0.2 tag, went into the `sphinx` directory and ran `make html` (run `make help` to see the available options):

```
git clone https://github.com/bokeh/bokeh.git
git checkout tags/2.0.2 -b 2.0.2
cd sphinx
make html
```

`make` will abort if certain Python modules are missing, so just install them. The packages I needed to install were:

```
sphinx==3.0.3
pandas==1.0.3
scipy==1.4.1
colorcet==2.0.2
bokeh==2.0.2
nodejs==10.13.0
networkx==2.4
```

Another issue I had was this error:

```
Set GOOGLE_API_KEY to a valid API key, or set bokeh_missing_google_api_key_ok=True in conf.py to build anyway (with broken GMaps)
```

The `conf.py` file is located under `sphinx` in the `source` directory. Just change the variable to `True` and run make again.