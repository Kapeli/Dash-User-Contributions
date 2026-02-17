Boto3 Docset
=======================
Boto3 is the Amazon Web Services (AWS) Software Development Kit (SDK) for Python, which allows Python developers to write software that makes use of services like Amazon S3 and Amazon EC2.
http://boto3.readthedocs.io/en/latest/

* Boto3 Version: 1.42.49
* Dash Docset: Updated by James Seward
* Twitter: @jamesoff
* Mastodon: @jamesoff@mastodon.jamesoff.net
* Github: https://github.com/jamesoff

=======================

How to generate this docset:

* Clone the boto3 repo from here: https://github.com/boto/boto3

**Automated build**

* Set `BOTO3_SRC` in your environment to the directory the boto3 repo is checked out to
* If you are uploading to an S3 bucket + CF distribution (to host for the PR), set `BOTO3_BUCKET` and `BOTO3_CF`, and arrange for suitable AWS credentials to be available
* Fetch `master` from upstream and check out a new branch
* `make all` will perform the entire build and update this file and the JSON specificiation with the new version numbers
* Commit
* If hosting the tgz file in S3, `make upload` will upload, check the URL, then print it

**Step-by-step instructions**

* Generate local docs as per: https://github.com/boto/boto3#generating-documentation
	```
	pip install -r requirements-docs.txt
	pip install --upgrade boto3
	cd docs
	make html
	```

* Import docset into dash:
	```
	# Removes previous compilation if it exists
	[[ -e ~/Library/Application\ Support/doc2dash/DocSets/boto3.docset ]] && rm -r ~/Library/Application\ Support/doc2dash/DocSets/boto3.docset
	doc2dash -A build/html --name boto3
	```

* Archive docset as per: https://github.com/Kapeli/Dash-User-Contributions#contribute-a-new-docset
	```
	cd ~/Library/Application\ Support/doc2dash/DocSets
	tar --exclude='.DS_Store' -cvzf /tmp/boto3.tgz boto3.docset
	```

* Fork/clone the source Kapeli repo, update the `docset.json` file with new author/version/etc, and update this `README.md` file as necessary.

* Replace `boto3.tgz.txt` with `/tmp/boto3.tgz`.
	```
	cd /path-to-repo/Dash-User-Contributions/docsets/Boto3
	mv /tmp/boto3.tgz .
	[[ -e boto3.tgz.txt ]] && git rm boto3.tgz.txt
	```

* (Recommended) Download AWS Python SDK icons, and copy into docset
	```
	cd /path-to-repo/Dash-User-Contributions/docsets/Boto3/
	curl -O https://s3.amazonaws.com/angrychimp.net/dash/boto3.docset/icon.png
	curl -O https://s3.amazonaws.com/angrychimp.net/dash/boto3.docset/icon%402x.png
	```

* Commit and push to your forked repo.

* Issue a pull request.
