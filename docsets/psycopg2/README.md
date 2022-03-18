Psycopg 2 Docset
==============

PostgreSQL database adapter for Python


## How to generate docset

- Download the desired release from [psycopg2 Github releases](https://github.com/psycopg/psycopg2/releases)
- Install requirements:
  ```bash
  pip install virtualenv doc2dash
  ```
- Run these commands from psycopg2 directory:
  ```bash
  # Create virtualenv
  make env

  # Generate html documentations
  make docs
  ```
- Generate docset:
  ```bash
  doc2dash -n psycopg2 -j -I index.html -u 'http://initd.org/psycopg/docs/' doc/html
  ```
- Copy `icon.png` and `icon@2x.png` to `psycopg2.docset` directory (right click, then choose `Show Package Contents`)
- Archive docset:
  ```bash
  tar --exclude='.DS_Store' -cvzf psycopg2.tgz psycopg2.docset
  ```
- Update docset version in `docset.json`


---
Docset author: [Rifa'i M. Hanif](https://github.com/hanreev)
