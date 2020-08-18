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
  - Install [doc2dash](https://github.com/hynek/doc2dash) and [spinx](http://www.sphinx-doc.org/en/stable/)
  - Generate html doc:
		- `cd docs && make html`
	- `doc2dash -A html/ -n shapely`

Note:
> Generating the docsest is tested on Mac OS & Linux only. If anyone gets to try it on Windows, please let me know how it goes.
