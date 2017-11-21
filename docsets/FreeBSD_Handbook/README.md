FreeBSD Handbook
=======================

User Documentation for FreeBSD

* Docset author: Sebastian Schmidt (@publicarray)
* Documentation Source: https://download.freebsd.org/ftp/doc/
* prerequisites:
  * golang and dashing
  * recode

## How to build dockset

```bash
brew install golang recode
export $GOPATH=~/go

go get -u github.com/technosophos/dashing
wget https://download.freebsd.org/ftp/doc/en/books/handbook/book.html-split.tar.bz2
tar -xvf book.html-split.tar.bz2
recode iso-8859-1..utf8 *.html
dashing build
```
