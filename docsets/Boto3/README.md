Boto3 Docset
=======================
* Description: Boto3 is the Amazon Web Services (AWS) Software Development Kit (SDK) for Python, which allows Python developers to write software that makes use of services like Amazon S3 and Amazon EC2. 

* Dash Docset: Created by Shane Kirk

⋅⋅* Twitter: @shanek1rk

⋅⋅* Homepage: http://shanekirk.me

⋅⋅* Github: https://github.com/shanedroid

=======================

How to generate:

* Clone the boto3 repo from here: https://github.com/boto/boto3

* Generate local docs as per: https://github.com/boto/boto3#generating-documentation
	```
    $ pip install -r requirements-docs.txt
	$ cd docs
	$ make html
 	```

* Import docset into dash:
	```
	doc2dash -A boto3/docs/build/html --name boto3
 	```

* Archive docset as per: https://github.com/Kapeli/Dash-User-Contributions#contribute-a-new-docset
	```
	cd ~/Library/Application Support/doc2dash/DocSets
	tar --exclude='.DS_Store' -cvzf boto3.tgz boto3.docset
 	```

* Add icon, etc...
=======================
