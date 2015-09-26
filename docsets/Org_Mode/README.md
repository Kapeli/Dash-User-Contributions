Org Mode Docset
===============
* Name: [Peking Duck](https://github.com/pekingduck)
* Document source: http://orgmode.org/manual/index.html
* To generate the doc:

```
$ wget -c -L -r -k -np -i - <<LIST
http://orgmode.org/manual/index.html
http://orgmode.org/org-manual.css
http://orgmode.org/org-keys.js
LIST
$ mkdir -p Org_Mode.docset/Contents/Resources/Documents/
$ mv orgmode.org Org_Mode.docset/Contents/Resources/Documents/orgmode
# Python 3 w/ Beautifulsoup4 is required
$ $ pip install beautifulsoup4
$ python ./gen_org_doc.py Org_Mode.docset/Contents/Resources
$ tar --exclude='.DS_Store' -cvzf Org_Mode.tgz Org_Mode.docset
```
