Shapely Dash Docset
=======================

- __Docset Description__:
    - Manipulation and analysis of geometric objects in the Cartesian plane.

- __Author__:
    - [Sean Gillies](https://github.com/sgillies)

- __Docset repo__:
    - [https://github.com/Toblerity/Shapely](https://github.com/Toblerity/Shapely)

- __How to generate the docset:__

	- Clone origin [Shapely project](https://github.com/Toblerity/Shapely)
  - Generate html doc
  - `cd docs && make html`
  - Install [doc2dash](https://github.com/hynek/doc2dash):
	- `doc2dash -A html/ -n shapely`

	- Requirements:

		- [sphinx](http://www.sphinx-doc.org/en/stable/) must be installed.

Note:
> Generating the docsest is tested on Mac OS only. If anyone gets to try it on Windows, please let me know how it goes.
