#!/usr/bin/env python3

import os, re, sqlite3
from bs4 import BeautifulSoup, NavigableString, Tag
import sys
import os.path

res_dir = sys.argv[1]
doc_id = "guile"

db = sqlite3.connect("{}/docSet.dsidx".format(res_dir))
cur = db.cursor()

try: cur.execute('DROP TABLE searchIndex;')
except: pass
cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

pages = [ "Type", "Variable", "Procedure" ]

sql = 'INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)'

doc_dir = "{}/Documents/{}".format(res_dir, doc_id)

for page in pages:
  objs = set()
  soup = BeautifulSoup(open("{}/{}-Index.html".format(doc_dir, page)))
  for tag in soup.find_all('a'):
    for ct in tag.contents:
      if ct.name == "code":
        obj_name = ct.string
        # Sometimes an object appears more than once, we only index the first
        # one and ignore the rest.
        if obj_name not in objs:
          print("{}->{}".format(obj_name, tag['href']))
          path = doc_id + "/" + tag['href']
          cur.execute(sql, (obj_name, page, path))
          objs.add(obj_name)

db.commit()
db.close()
