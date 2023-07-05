.PHONY: all build fetch docs import archive update version

all: fetch build version
build: docs import archive update

BOTO3_SRC ?= $(HOME)/src/boto3
DOCSET ?= $(shell pwd)

fetch:
	cd $(BOTO3_SRC) && \
		git fetch
	cd $(BOTO3_SRC) && \
		git checkout "$$(cd $(BOTO3_SRC) && git tag | sort -V | tail -n1 )"

docs:
	cd $(BOTO3_SRC) && \
		source .venv/bin/activate && \
		pip install -U pip && \
		pip install -U -r requirements-docs.txt && \
		pip install -U . && \
		cd docs && \
			ulimit -n 512 && \
			make html

import:
	rm -rf "$(HOME)/Library/Application Support/doc2dash/DocSets/boto3.docset"
	cd $(BOTO3_SRC)/docs && \
		doc2dash -A build/html --name boto3

archive:
	rm -f /tmp/boto3.tgz
	cd "$(HOME)/Library/Application Support/doc2dash/DocSets" && \
		tar --exclude='.DS_Store' -czf /tmp/boto3.tgz boto3.docset

update:
	yes | cp /tmp/boto3.tgz .
	if [[ -e boto3.tgz.txt ]]; then git rm boto3.tgz.txt; fi

version:
	VERSION=$(shell cd $(BOTO3_SRC) && git describe --tags) && \
			jq '.version = "'$$VERSION'"' < docset.json > docset.json.tmp && \
			mv docset.json.tmp docset.json && \
			sed -E -i .bak "s/Boto3 Version: .+/Boto3 Version: $$VERSION/" README.md && \
			rm -f README.md.bak

upload:
	VERSION=$(shell cd $(BOTO3_SRC) && git describe --tags) && \
			aws s3 cp boto3.tgz s3://$(BOTO3_BUCKET)/$$VERSION/boto3.tgz && \
			curl --fail --silent --head https://$(BOTO3_CF)/$$VERSION/boto3.tgz && \
			echo https://$(BOTO3_CF)/$$VERSION/boto3.tgz
