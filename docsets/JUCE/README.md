JUCE Dash Docset
=======================

* Description: JUCE is GUI and C++ Class Library
* Author: Julian Storer
* Dash Docset: Created by deanan@gmail.com
* Docset repo: https://github.com/deanand/Dash-User-Contributions/docsets/JUCE

Instructions to generate the docset:

* Get JUCE here: https://github.com/julianstorer/JUCE
* Get the JUCE API docs here: https://github.com/julianstorer/JUCE-API-Documentation
* Place the two directories in the same directory.
* Inside the api docs directory:
  * Change juce_api_config:
  * 
    ```
        GENERATE_DOCSET   = YES
        DISABLE_INDEX     = YES 
        SEARCHENGINE      = NO
        GENERATE_TREEVIEW = NO
    ```

  * run `run_doxygen`
  * cd api
  * make
* Go into the docset bundle and fix the title pages:

     ```
     find . -type f -name "*.html" -exec perl -0777 -pi -w -e "s/<title>JUCE: /<title>/sg" "{}" \;
     ```
* Add icon, etc...
