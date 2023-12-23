#!/usr/bin/env python3
# Script to populate the index for the DITA docset for Dash
# Paul Mazaitis, https://github.com/pmazaitis
#
# Intended to be run in the same directory as the docset under development; 
# paths may be fragile! 
#
import os
import re
import sqlite3
from bs4 import BeautifulSoup

if __name__ == '__main__':
 
    # Setup
    root_dir = 'DITA.docset/Contents/Resources/'
    content_dir = os.path.join(root_dir,'Documents/docs.oasis-open.org/')
    conn = sqlite3.connect(os.path.join(root_dir,'docSet.dsidx'))
    cur = conn.cursor()

    try: cur.execute('DROP TABLE searchIndex;')
    except: pass
    cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
    cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')


    # The DITA documentation set doesn't have any clearly delineated content 
    # like a guide, but I figured the subsections of section 2 might be useful
    # for quick access, so I process them as guides.
    guide_files = ['introduction-to-dita.html',
                    'ditamarkup.html',
                    'ditaaddressing.html',
                    'behaviors.html',
                    'configuration-specialization-and-constraints.html',
                    'coding-requirements.html',
                    'technical-content-specializations.html'
                    ]

    # The two primary indexable components of this docset are the sets of
    # elements (enclosed in angle brackets) and attributes (prefixed with an
    # at-symbol).
    for dir_name, subdir_list, file_list in os.walk(content_dir):
        for fname in file_list:
            path = os.path.join(dir_name,fname)
            shortpath = os.path.join(*(path.split(os.path.sep)[4:]))
            if re.search('.html$', path):
                page = open(path).read()
                soup = BeautifulSoup(page, "lxml")

                if fname in guide_files:
                    rawname = soup.title
                    name = rawname.string
                    cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, "Guide", shortpath))
                    print(f'Found Guide: {name}')

                if re.search('langRef', dir_name):
                    itemtype = None
                    if rawname := soup.body.h1.code:
                        name = rawname.string
                        if re.match('@',name):
                            itemtype = "Attribute"
                        elif re.match('<',name):
                            itemtype = "Element"

                    if itemtype:
                        cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, itemtype, shortpath))
                        print(f'Found {itemtype}: {name}')
                conn.commit()    
            
