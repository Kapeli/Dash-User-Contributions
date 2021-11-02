aiohttp Dash Docset
=======================

#### Docset Description
Asynchronous HTTP Client/Server for asyncio and Python.

#### Generation Steps
1. To remove the sidebar totally, you need to build the HTML documentation from source. And you wanna download the [source of aiohttp](https://github.com/aio-libs/aiohttp/) firstly.
2. Edit `docs/conf.py` to suppress generate of sidebar and other decorations. Just append the configuration items below into the end of Python dict `html_theme_options` in `docs/conf.py`. Remember to remove the items conflicted with items below in `conf.py`.

```python
    "nosidebar": True,
    "show_powered_by": True,
    "show_related": False,
    "show_relbars": False,
    "github_button": False,
    "github_banner": False,
```

3. Build HTML doc by running `make html` within the `docs/` directory.
4. Add custom styles for the HTML files. Cause you wanna reduce side margins of main contents and code blocks. The snippet below is borrowed from Dash docset Flask, which is an official docset.

```css
/* copy and paste the content below into
 * docs/_build/html/_static/custom.css
 */
div.footer {width:auto; max-width:940px} div.document {max-width:none; width: auto} div.related {display:none;} div.sphinxsidebar {display:none;} a.headerlink {display:none;} div.bodywrapper {margin: 0 0 0 0px;}
div.body {max-width:none !important;}

pre {padding: 7px 10px !important;margin: 15px 0 !important;overflow:auto;}
div.admonition {margin:20px 0; padding:10px 10px;}
```

5. Repeat the steps above to build HTML doc for [aiohttp-demos](https://github.com/aio-libs/aiohttp-demos). Put doc files of aiohttp-demos into a sub-folder, such as `aiohttp-demos`, under HTML doc folder of aiohttp. Combine them together by replacing `href` attributes below as correct relative path values:

```
# replace texts below with "aiohttp-demos/" (without quotes)
https://aiohttp-demos.readthedocs.io/en/latest/

# replace texts below with "../" (without quotes)
http://aiohttp.readthedocs.io/en/stable/
```

6. Build the docset with [doc2dash](https://github.com/hynek/doc2dash).


```shell
doc2dash -jv -n aiohttp -I index.html -u https://aiohttp.readthedocs.io/en/stable/ <path to HTML doc folder of aiohttp>
```

7. Compress the docset as a tarball as what's told id in [the guide of this repo](https://github.com/Kapeli/Dash-User-Contributions):

```shell
tar --exclude='.DS_Store' -cvzf aiohttp.tgz aiohttp.docset
```

8. Verify the compress doc with the command from [.travis.yml](https://github.com/Kapeli/Dash-User-Contributions/blob/master/.travis.yml):

```shell
# run the command at the root of this repo
wget http://kapeli.com/feeds/zzz/docsetcontrib.tgz && tar -xzf docsetcontrib.tgz && ./docsetcontrib --verify
```

9. Make a commit and
submit a pull request if no error occurred.

#### Contributors
- [abogushov](https://github.com/abogushov)
    - `0.22.5`, initial
    - `1.0.1`
    - `2.0.7`
    - `2.3.1`
- [AllanLRH](https://github.com/AllanLRH)
    - `3.1.0`
- [laggardkernel](https://github.com/laggardkernel)
    - `3.4.4`
