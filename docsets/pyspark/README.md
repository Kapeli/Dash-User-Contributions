pyspark Docset
=======================

* Author: Tomas Kunka (https://twitter.com/TomasKunka) - versions: 2.4.0
* Author: Ronert Obst (https://twitter.com/ronert_obst) - versions: 2.1.0, 1.6.1, 1.5.1
* Instructions
  * Clone the Apache Spark repo
  * Modify spark/python/docs/conf.py and add `html_theme_options = {"nosidebar": "true"}` under `html_theme = 'nature'`
  * Run make html
  * Then run doc2dash
added docset for pyspark version 2.4.0
moved author of previous versions Ronert Obst to specific_versions section in dockset.json (not sure if that is ok)
