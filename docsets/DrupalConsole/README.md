Drupal Console Docset
=======================

Drupal Console Website: http://drupalconsole.com
Drupal Console Dash repository: https://github.com/hechoendrupal/Dash-User-Contributions


* How to setup environment to contribute to Drupal Console Dash documentation.
  * Fork repository: https://github.com/hechoendrupal/Dash-User-Contributions
  * Clone your fork in your machine: git clone https://github.com/<YOUR-USER>/Dash-User-Contributions ~/DrupalConsoleDash
  
* Updating DrupalConsole Docset
  * Using latest version of Drupal Console or using a dev version execute the following command
  	$ drupal generate:doc:dash --path ~/DrupalConsoleDash/docsets/DrupalConsole
  * Move current version into a new version folder
  * Archive docset using the following command
    tar --exclude='.DS_Store' -cvzf DrupalConsole.tgz DrupalConsole.docset
  * Update docset.json to include new version folder  
