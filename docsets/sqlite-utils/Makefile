DOC2DASH ?= doc2dash
DOC2DASH_OPTS ?=
GIT ?= git

GITHUB_USER ?= simonw
GITHUB_REPO ?= sqlite-utils
VERSION ?= 3.35.2

PYTHON ?= $(shell which python3)
PIP = $(PYTHON) -m pip

HTML_DIR = $(GITHUB_REPO)/docs/_build/html
DOCSET_DEST_DIR = versions/$(VERSION)
DOCSET_FILE = $(DOCSET_DEST_DIR)/$(GITHUB_REPO).docset
DOCSET_ARCHIVE = $(DOCSET_DEST_DIR)/$(GITHUB_REPO).tgz

$(DOCSET_ARCHIVE):
	- mkdir -p $(DOCSET_DEST_DIR)
	$(GIT) clone "git@github.com:$(GITHUB_USER)/$(GITHUB_REPO).git" && \
	$(PIP) install "furo" "sphinx-autobuild" "codespell" "sphinx-copybutton"  "beanbag-docutils>=2.0" "pygments-csv-lexer"

	cd $(GITHUB_REPO) && $(GIT) checkout $(VERSION)

	cd $(GITHUB_REPO)/docs && \
	echo 'html_theme_options = {"nosidebar": "true"}' >> conf.py && \
	make html

	$(DOC2DASH) $(DOC2DASH_OPTS) -d $(DOCSET_DEST_DIR) $(HTML_DIR)

	tar --exclude='.DS_Store' -cvzf $(DOCSET_ARCHIVE) $(DOCSET_FILE)
	- rm -rf $(DOCSET_FILE)

all: $(DOCSET_ARCHIVE)

.phony: all
.default: all

clean:
	-rm -rf $(GITHUB_REPO)

uninstall:
	-rm -rf $(GITHUB_REPO) "/Users/$$USER/Library/Application Support/doc2dash/DocSets/$(GITHUB_REPO).docset"
