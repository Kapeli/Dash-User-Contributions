#!/usr/local/bin/python
#scrapy runner
from sdldoc import settings
import os,sqlite3


if __name__ == "__main__":
    db=sqlite3.connect(os.path.join(settings.BASE_PATH,"docSet.dsidx"))
    cur=db.cursor()
    #init db
    try: cur.execute('DROP TABLE searchIndex;')
    except: pass
    cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
    cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')
    db.commit()
    db.close()
    os.system("scrapy crawl func --nolog")
    settings.closeDb()
