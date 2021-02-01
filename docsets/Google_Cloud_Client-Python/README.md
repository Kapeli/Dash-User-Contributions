Google Cloud Python APi Docset 0.34.0
=======================

 When you contribute a docset, you need to edit this README to include the following:
* Who are you: github @davydhong
* Complete instructions on how to generate the docset:
  * List of any prerequisites
    * prereq: sphinx and all the sphinx dependencies:
      * `pip3 install recommonmark sphinx-rtd-theme sphinx-autoapi sphinxcontrib-httpdomain sphinx-argparse`
      * `sudo pip install doc2dash`
  * Where or how to download the initial HTML documentation for the docset
    * https://airflow.apache.org/
  * How to run the generation script
      * `$ git clone https://github.com/googleapis/google-cloud-python.git`
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
      $ doc2dash -n Google\ Cloud\ Python --add-to-dash -d ~/Library/Application\ Support/Dash/User\ Contributed/Google\ Cloud\ Python _build/

