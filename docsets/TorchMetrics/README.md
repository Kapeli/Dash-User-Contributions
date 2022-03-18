TorchMetrics Docset
=======================

#### Docset Description:

- [TorchMetrics](https://torchmetrics.readthedocs.io/en/latest/) is a collection of Machine learning metrics for distributed, scalable PyTorch models and an easy-to-use API to create custom metrics.

#### How to create:

- Run `make html` in the [torchmetrics docs](https://github.com/PyTorchLightning/metrics/tree/master/docs).
- Run python script below

```python
#!/usr/local/bin/python

import os, re, sqlite3
from bs4 import BeautifulSoup, NavigableString, Tag

import pdb

conn = sqlite3.connect('torchmetrics.docset/Contents/Resources/docSet.dsidx')
cur = conn.cursor()

try: cur.execute('DROP TABLE searchIndex;')
except: pass
cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

docpath = 'torchmetrics.docset/Contents/Resources/Documents'

# modules.html
rel_docpath = 'references/modules.html'
page = open(os.path.join(docpath, rel_docpath)).read()
soup = BeautifulSoup(page, features='html')

for h in soup.find_all('h3'):
    if h.findNextSibling('dl') is None:
        continue

    name = h.find(text=True, recursive=False)
    path = rel_docpath + h.find('a').attrs['href']

    cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, 'Module', path))
    print('name: %s, type: %s, path: %s' % (name, type, path))

# functional.html
rel_docpath = 'references/functional.html'
page = open(os.path.join(docpath, rel_docpath)).read()
soup = BeautifulSoup(page, features='html')

for h in soup.find_all('h3'):
    if h.findNextSibling('dl') is None:
        continue

    name = h.find(text=True, recursive=False)
    path = rel_docpath + h.find('a').attrs['href']

    cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, 'func', path))
    print('name: %s, type: %s, path: %s' % (name, type, path))

conn.commit()
conn.close()
```

#### Docset Author:

- [Seungjae Jung](https://github.com/seanexplode)
