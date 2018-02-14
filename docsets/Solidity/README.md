solidity-dash
=======================

A script utility to generate the latest documentation of [Solidity](https://github.com/ethereum/solidity) on the popular documentation app Dash.

This repository is the result of a personal quest for offline knowledge + the [unattended and much needed request](https://github.com/Kapeli/Dash-User-Contributions/issues/1685).

### How to

- Clone the repo and cd into it
- Doing `bash setup.sh` will:
	- Try to install dependencies (see below)
	- Fetch the **ethereum** repo
	- Go to docs dir and make them into html
	- Copy them to **solidity.docset**
	- Copy info.plist, dsidx and icon.svg into **solidity.docset**
	- Run `populate.py` to iterate through the htmls and fill the db.

### Dependencies

- [Sphinx](www.sphinx-doc.org), ethereum docs engine
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), to extract html tags.
- svgexport, since icon is in svg format.

### To do

- Improve the html tag search
- Generate the docset for the last 3 versions 
	- 0.4.19
	- 0.4.18
	- 0.4.17


### By [oschvr](http://twitter.com/oschvr)
