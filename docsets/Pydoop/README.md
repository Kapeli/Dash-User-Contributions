Pydoop docset
=======================

- __Docset Description__:
    - [Pydoop](http://pydoop.sourceforge.net/docs/) is a python API for Hadoop.

- __Author__:
    - [Aziz Alto](https://github.com/iamaziz)

- __How to generate the docset__:
    - fetch html: 
    	- `httrack "http://pydoop.sourceforge.net/docs/" -O "handjob" "+*pythonhosted.org/mrjob/*" -v`
    - generate docset: 
    	- `doc2dash -v -n Pydoop pydoop.sourceforge.net/docs/`
    - Set Info.plist to index page: 
    	- `dashIndexFilePath: index.html`
    - Add icon.
    
