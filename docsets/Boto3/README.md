Boto3 Docset
=======================
Boto3 is the Amazon Web Services (AWS) Software Development Kit (SDK) for Python, which allows Python developers to write software that makes use of services like Amazon S3 and Amazon EC2.
http://boto3.readthedocs.io/en/latest/

* Boto3 Version: 1.4.7
* Dash Docset: Updated by Randall Kahler
* Twitter: @angrychimp
* Homepage: https://angrychimp.net
* Github: https://github.com/angrychimp

=======================

How to generate this docset:

* Clone the boto3 repo from here: https://github.com/boto/boto3

* Generate local docs as per: https://github.com/boto/boto3#generating-documentation
	```
	pip install -r requirements-docs.txt
	cd docs
	make html
	```

* Import docset into dash:
	```
	doc2dash -A boto3/docs/build/html --name boto3
	```

* Archive docset as per: https://github.com/Kapeli/Dash-User-Contributions#contribute-a-new-docset
	```
	cd ~/Library/Application Support/doc2dash/DocSets
	tar --exclude='.DS_Store' -cvzf /tmp/boto3.tgz boto3.docset
	```

* Fork/clone the source Kapeli repo, update the `docset.json` file with new author/version/etc, and update this `README.md` file as necessary.

* Replace `boto3.tgz.txt` with `/tmp/boto3.tgz`.
	```
	cd /path-to-repo/Dash-User-Contributions/docsets/Boto3
	mv /tmp/boto3.tgz .
	```

* (Recommended) Download AWS Python SDK icons, and copy into docset
	```
	cd /path-to-repo/Dash-User-Contributions/docsets/Boto3/
	curl -O https://s3.amazonaws.com/angrychimp.net/dash/boto3.docset/icon.png
	curl -O https://s3.amazonaws.com/angrychimp.net/dash/boto3.docset/icon%402x.png
	```

* Commit and push to your forked repo.

* Issue a pull request.
