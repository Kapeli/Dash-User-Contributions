Kornia docset
=============

__Docset description:__
	[Kornia](https://kornia.readthedocs.io), is a differentiable computer vision library for PyTorch

__Author:__
    [Yue Gao](https://github.com/hologerry)

__How to generate the docset:__

- Download the desired release from GitHub
  [kornia releases](https://github.com/kornia/kornia/releases)
- Run `make doc` in the kornia directory (install the required packages first)
- Run [doc2dash](https://pypi.python.org/pypi/doc2dash/) on the
  `html` directory inside `docs/build/`: `doc2dash -n kornia html`
- Archive the docset:
  ```
  tar --exclude='.DS_Store' -cvzf kornia.tgz kornia.docset
  ```
- Update the version in `docset.json`
- Icon from https://github.com/kornia/kornia/blob/master/docs/source/_static/img/kornia_logo_only.png
