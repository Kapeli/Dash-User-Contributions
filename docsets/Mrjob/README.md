mrjob docset
=======================

- __Docset Description__:
    - [mrjob](https://pythonhosted.org/mrjob/) for writing MapReduce in Python.

- __Author__:
    - [Aziz Alto](https://github.com/iamaziz)

- __How to generate the docset__:
    - fetch html: 
    	- `httrack "https://pythonhosted.org/mrjob/" -O "mrjob" "+*pythonhosted.org/mrjob/*" -v`
    - generate docset: 
    	- `doc2dash -v -n Mrjob mrjob/pythonhosted.org/mrjob/`
    - Set Info.plist to index page: 
    	- `dashIndexFilePath: index.html`
    - Add icon.
    
