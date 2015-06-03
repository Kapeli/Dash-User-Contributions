#!/usr/bin/env python3

import os, re, sqlite3
from bs4 import BeautifulSoup, NavigableString, Tag
import sys
import os.path

res_dir = sys.argv[1]
doc_id = "orgmode"

db = sqlite3.connect("{}/docSet.dsidx".format(res_dir))
cur = db.cursor()

try:
  cur.execute('DROP TABLE searchIndex;')
except:
  pass
cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

# file-name-to-object-type mapping
pages = {
  "Key" : "Command",
  "Variable" : "Variable",
  "Command-and-Function" : "Function" }

sql = 'INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)'

doc_dir = "{}/Documents/{}/manual".format(res_dir, doc_id)

for page in pages.keys():
  soup = BeautifulSoup(open("{}/{}-Index.html".format(doc_dir, page)))
  for tag in soup.find_all('a'):
    for ct in tag.contents:
      if ct.name == "code":
        obj_name = ct.string
        path = doc_id + "/manual/" + tag['href']
        cur.execute(sql, (obj_name, pages[page], path))

# Main-Index.html has many types of objects
soup = BeautifulSoup(open("{}/Main-Index.html".format(doc_dir)))
for ul in soup.find_all('ul'):
  try:
    print(ul['class'])
  except KeyError:
    continue

  for li in ul.find_all('li'):
    a = li.find_all('a')
    obj_path = doc_id + '/manual/' + a[0]['href']
    ct0 = a[0].contents[0]
    prop = 'property, '
    prop_special = 'property, special, '
    if type(ct0) == NavigableString:
      if ct0[0] == '#':
        obj_type = 'Directive'
        obj_name = ct0
      elif ct0.startswith(prop_special):
        obj_type = "Property"
        obj_name = format(ct0[len(prop_special):])
      elif ct0.startswith(prop):
        obj_type = "Property"
        obj_name = format(ct0[len(prop):])
      else:
        continue
    elif type(ct0) == Tag:
      if ct0.name == 'code':
        obj_name = ct0.string
        if len(a[0].contents) > 1:
          if a[0].contents[1] == ', STARTUP keyword':
            obj_type = 'Keyword'
        else:
          if ct0.string.endswith('.el'):
            obj_type = 'Module'
          else:
            obj_type = 'Function'
      else:
        continue
    cur.execute(sql, (obj_name, obj_type, obj_path))

db.commit()
db.close()
