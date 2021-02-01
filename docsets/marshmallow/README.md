Marshmallow Docset
=======================

Marshmallow is an ORM/ODM framework used for converting datatypes and validation.
* Jonathan Revah (https://github.com/heyoni/)
* Steps for generating the docset:
  * Clone repo: https://github.com/marshmallow-code/marshmallow/
  * Create a virtual environment following the `README`
  * Modify `docs/conf.py` to have `"nosidebar": True` inside the `html_theme_options` function
  * Inside marshmallow's repo, build the documentation using `tox -e watch-docs`
  * Run the following command: `doc2dash -A --name marshmallow -i docs/_static/marshmallow-logo.png -I index.html -u https://marshmallow.readthedocs.io/ docs/_build`
  * The documentation will be added to Dash and can be extracted from there!
