#!/usr/local/bin/python

import os, re, sqlite3
from bs4 import BeautifulSoup, NavigableString, Tag 

db = sqlite3.connect('glut.docset/Contents/Resources/docSet.dsidx')
cur = db.cursor()

try: cur.execute('DROP TABLE searchIndex;')
except: pass
cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

docpath = 'glut.docset/Contents/Resources/Documents'

page = open(os.path.join(docpath,'www.opengl.org/resources/libraries/glut/spec3/spec3.html')).read()
soup = BeautifulSoup(page)

any = re.compile('.*')
for tag in soup.find_all('a', {'href':any}):
    name = tag.text.strip()
    func = re.compile(r"\d\.\d\s(glut.+)");
    if len(name) > 0:
        path = tag.attrs['href'].strip()
        fname = func.search(name)
        if fname:
            cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (fname.group(1), 'func', os.path.join('www.opengl.org/resources/libraries/glut/spec3/',path)))
            print 'name: %s, path: %s' % (name, os.path.join('www.opengl.org/resources/libraries/glut/spec3/',path))

db.commit()
db.close()
