Boto Docset
=======================
* Description: Boto is a Python package that provides interfaces to Amazon Web Services. Currently, all features work with Python 2.6 and 2.7.

* Dash Docset: Created by Shane Kirk

⋅⋅* Twitter: @shanek1rk

⋅⋅* Homepage: http://shanekirk.me

⋅⋅* Github: https://github.com/shanedroid

=======================

How to generate:

* Install sphinx and dash2doc:

	```
    $ pip install sphinx dash2doc
 	```
* Clone the boto repo from here: https://github.com/boto/boto

* Edit the file boto/docs/source/conf.py to include:
	```
     html_use_index = True
 	```

* Use sphinx to build:
	```
    $ mkdir boto/docs/html
    $ sphinx-build source boto/docs/html
 	```

* Import docset into dash:
	```
	$ doc2dash -A boto/docs/html --name boto
 	```

* Archive docset as per: https://github.com/Kapeli/Dash-User-Contributions#contribute-a-new-docset
	```
	$ cd ~/Library/Application Support/doc2dash/DocSets
	$ tar --exclude='.DS_Store' -cvzf boto.tgz boto.docset
 	```
 	
* Add icon, etc...
=======================
