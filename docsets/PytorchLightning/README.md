Pytorch Lightning Dash Docset
=======================

- Docset Description:
    - From the Pytorch Lightning github: _The lightweight PyTorch wrapper for high-performance AI research. Scale your models, not the boilerplate._

 - Author:
    - [Mun Hou - GitHub](https://github.com/munhouiani/)

- Docset Generation:
    - Clone the Pytorch Lightning GitHub repository:
        - `git clone https://github.com/PyTorchLightning/pytorch-lightning.git`
        - `cd pytorch-lightning`
        - `git fetch --all --tags --prune`
        - `git checkout tags/1.0.8 -b 1.0.8`
    - Create a Conda environment:
        - `conda create -n pytorch-lightning-docs python=3.7 nodejs`
        - `conda activate pytorch-lightning-docs`
    - Install `pip` dependencies and `doc2dash`:
        - `python -m pip install doc2dash`
        - `python -m pip install sphinx recommonmark sphinx_autodoc_typehints sphinx_copybutton sphinx_paramlinks sphinx_togglebutton`
    - Install `pt_lightning_sphinx_theme`:
      - `git clone https://github.com/PyTorchLightning/lightning_sphinx_theme.git`
      - `cd lightning_sphinx_theme`
      - `python setup.py install`
      - `npm install`
    - Extra requirement:
        - `latex`
          - `brew cask install mactex` on Mac
          - Check https://www.latex-project.org/get/ for other distribution
    - Now go back to `pytorch-lightning/docs/`: 
        - build the docs
          - `make html`
        - build docset for dash
          - `doc2dash -n PytorchLightning -I index.html -v -j -u "https://pytorch-lightning.readthedocs.io/en/stable/" -a -f build/html`
    - The Pytorch Lightning Docset will install directly into Dash.
