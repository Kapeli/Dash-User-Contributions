Robot Framework
=======================

## Author

This docset is maintained by @deiga, you can find me at:
* deiga@iki.fi
* https://github.com/deiga
* https://twitter.com/deiga

### Instructions

  * Clone Robot Framework repository: `git clone https://github.com/robotframework/robotframework`
  * Enter docs directory: `cd doc/api`
  * Generate html docs with `Sphinx`: `make html`
    * Install `Sphinx` if needed: `pip install sphinx`
  * Generate `docset` with `doc2dash`: `doc2dash _build/html -A -j -u http://robot-framework.readthedocs.org/en/3.0 -f -n "Robot Framework"`
    * Install `doc2dash` if needed: `pip install doc2dash`
