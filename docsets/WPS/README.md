WPS Dash Docset
===============

Unofficial Dash Docset for [wemake-python-styleguide](https://wemake-python-stylegui.de/en/latest/)

* Author: @snmishra (GitHub)

* Instructions on how to generate the docset:
  * `git clone https://github.com/wemake-services/wemake-python-styleguide`
  * `cd wemake-python-styleguide`
  * `python -m virtualenv ~/.virtualenvs/wps && . ~/.virtualenvs/wps/bin/activate`
  * `pip install -r docs/requirements.txt; pip install doc2dash; make -C docs html` 
  * `doc2dash -n WPS -i docs/_static/logo.png docs/_build/html/`
  * `tar -czf WPS.tgz WPS.docset`
