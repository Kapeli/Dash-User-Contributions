# libuv docset

[libuv](https://libuv.org/) docset for Dash.

Author: [Timothée Sterle](https://github.com/nanotee)

## Prerequisites

You need the following Python packages in order to generate the docset:

- [Sphinx](https://pypi.org/project/Sphinx/)
- [doc2dash](https://pypi.org/project/doc2dash/)

## How to generate the docset

- Clone the libuv project with `git clone https://github.com/libuv/libuv`
- `cd libuv/docs`
- Checkout the latest stable version (e.g. `git checkout v1.41.0`)
- `make html SPHINXOPTS="-D html_title='' -D html_theme_options.nosidebar=True"`
- `doc2dash -n "libuv" -I "index.html" -u "http://docs.libuv.org/en/stable/" "build/html"`
