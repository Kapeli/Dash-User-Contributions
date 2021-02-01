Airflow Docset 1.10.4
=======================

When you contribute a docset, you need to edit this README to include the following:
* Who are you: github @davydhong
* Complete instructions on how to generate the docset:
  * List of any prerequisites
    * prereq: sphinx and all the sphinx dependencies:
      * `pip3 install sphinx-rtd-theme sphinx-autoapi sphinxcontrib-httpdomain sphinx-argparse`
      * `sudo pip install doc2dash`
  * Where or how to download the initial HTML documentation for the docset
    * https://airflow.apache.org/
  * How to run the generation script
      * `$ git clone https://github.com/apache/airflow.git`
      * `$ cd docs`
      * change the makefile to
```
.PHONY: all default

default: all

all: build open

build:
	sphinx-build . _build

open:
	open _build/index.html
```
      $ make
      $ doc2dash -n Airflow --icon img/logos/airflow_64x64_emoji_transparent.png --add-to-dash -d ~/Library/Application\ Support/Dash/User\ Contributed/Airflow _build/

* List of any known bugs (links to GitHub issues)
  * Error loading airflow.gcp.operators.cloud_build module.
  * Error loading airflow.gcp.operators.natural_language module.
