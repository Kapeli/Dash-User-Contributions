NLTK docset
=======================

- __Docset Description__:
    - [NLTK](http://www.nltk.org/) is a Natural Language ToolKit using python.

- __Author__:
    - [Aziz Alto](https://github.com/iamaziz)

- __How to generate the docset__:
    - fetch html: 
    	- `httrack "http://www.nltk.org/" -O "NLTK" "+*www.nltk.org/*" -v`
    - generate docset: 
    	- `doc2dash -v -n NLTK NLTK/www.nltk.org/`
    - Set Info.plist to index page: 
    	- `dashIndexFilePath: index.html`
    - Add icon.
    
