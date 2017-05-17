Fiona Dash Docset
=======================

- __Docset Description__:
    - Fiona is OGR’s neat, nimble, no-nonsense API for Python programmers.

- __Author__:
    - [Sean Gillies](https://github.com/sgillies)

- __Docset repo__:
    - [https://github.com/Toblerity/Fiona](https://github.com/Toblerity/Fiona)

- __How to generate the docset:__

	- Clone origin [Fiona project](https://github.com/Toblerity/Fiona)
  - Generate html doc
  - `cd docs && make html`
  - Install [doc2dash](https://github.com/hynek/doc2dash):
	- `doc2dash -A html/ -n fiona`

	- Requirements:

		- [sphinx](http://www.sphinx-doc.org/en/stable/) must be installed.

Note:
> Generating the docsest is tested on Mac OS only. If anyone gets to try it on Windows, please let me know how it goes.
