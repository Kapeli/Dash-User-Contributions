Boto3 Docset
=======================
* Description: Boto3 is the Amazon Web Services (AWS) Software Development Kit (SDK) for Python, which allows Python developers to write software that makes use of services like Amazon S3 and Amazon EC2.

* Dash Docset: Updated by Randall Kahler

⋅⋅* Twitter: @angrychimp

⋅⋅* Homepage: https://angrychimp.net

⋅⋅* Github: https://github.com/angrychimp

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

* (Recommended) Download AWS Python SDK icons, and copy into docset
```
	$ cd ~/Library/Application Support/doc2dash/DocSets/boto3.docset/
	$ curl -O https://s3.amazonaws.com/angrychimp.net/dash/boto3.docset/icon.png
	$ curl -O https://s3.amazonaws.com/angrychimp.net/dash/boto3.docset/icon%402x.png
```

* Archive docset as per: https://github.com/Kapeli/Dash-User-Contributions#contribute-a-new-docset
	```
	cd ~/Library/Application Support/doc2dash/DocSets
	tar --exclude='.DS_Store' -cvzf /tmp/boto3.tgz boto3.docset
 	```

* Fork/clone this repo, update the `docset.json` file with new author/version/etc, and update this `README.md` file.

* Replace `boto3.tgz.txt` with `/tmp/boto3.tgz`.
	```
	cd /path-to-repo/Dash-User-Contributions/docsets/Boto3
	mv /tmp/boto3.tgz .
	rm boto3.tgz.txt
	```

* Commit and push to your forked repo.

* Issue a pull request.
