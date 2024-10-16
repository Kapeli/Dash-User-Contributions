pyspark Docset
==============

* Author: Rahul Iyer (https://twitter.com/rahuliyer95) - versions: 3.4.0, 3.5.2
* Author: Tomas Kunka (https://twitter.com/TomasKunka) - versions: 3.0.0, 2.4.0
* Author: Ronert Obst (https://twitter.com/ronert_obst) - versions: 2.1.0, 1.6.1, 1.5.1
* Instructions
  * Clone the Apache Spark [repo](https://github.com/apache/spark)
  * Checkout the release branch for the version you are building the docs
  * Modify `spark/python/docs/conf.py` and add `html_theme_options = {"nosidebar": "true"}`
  * Export the following environment variables
    * `export GIT_HASH="$(git rev-parse HEAD | cut -c 1-12)"`
    * `export VERSION="<spark-version>"` e.g `VERSION="3.5.2"`
  * Run `make html`
    * Optionally `export SPHINXOPTS="-j auto --keep-going"`
  * Then run [doc2dash](https://github.com/hynek/doc2dash)
