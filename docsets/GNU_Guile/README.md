GNU Guile Docset
================
* Name: [Peking Duck](https://github.com/pekingduck)
* Document source: http://www.gnu.org/software/guile/manual/ (HTML compressed with one web page per node)
* To generate the doc:
  * Download and uncompress the .tgz file into ```GNU_Guile.docset/Contents/Resources/Documents/guile```
  * Run the accompanying Python script (Python 3 and BeautifulSoup required) to generate the index:
  
```
$ pip install beautifulsoup4
$ python3 gen_guile_doc.py GNU_Guile.docset/Contents/Resources
```
  
  * Manually edit index.html and remove "Previous: (dir), Up: (dir) " from the
file.
