Docset for pysam
================
This is a Dash docset for [pysam](http://pysam.readthedocs.io/).

* Author: Vimalkumar Velayudhan
  ([github](https://github.com/vimalkvn), [website](https://vimal.io))

* Related Github issue: Kapeli/Dash-User-Contributions#1482

## Instructions to generate this docset

Create a directory for this project:

	mkdir ~/Workspace/zeal/pysam
	cd ~/Workspace/zeal/pysam

Create virtualenv, install latest release of pysam and doc2dash
(for building docset):

	python3 -m venv venv
	source venv/bin/activate
	pip install pysam doc2dash

Clone pysam repository, checkout release corresponding to the
PyPI version (`pip show pysam`):

	git clone --depth 1 https://github.com/pysam-developers/pysam/
	cd pysam
	git fetch --tags
	git checkout v0.15.1

Build documentation:

	cd doc
	make SPHINXOPTS="-D html_theme_options.nosidebar=true" html
	cd ../..

Generate docset:

	doc2dash -n pysam -u https://pysam.readthedocs.io/en/stable/ \
	pysam/doc/_build/html

Docset will be saved as pysam.docset.
