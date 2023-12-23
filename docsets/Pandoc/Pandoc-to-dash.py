# quick-and-dirty script to generate Pandoc docset for Dash.app

#----------------------------------
# built-in packages
import sqlite3
import os
import urllib
import plistlib

#----------------------------------
# third party packages + httrack 
import requests
from bs4 import BeautifulSoup as bs


# download html documentation
def get_html(docname, url, download_html=False):
  
  cmd_command = """
  rm -rf {0} &&
  mkdir -p {0}/Contents/Resources/Documents &&
  cd {0} &&
  httrack -%v2 -T60 -R99 --sockets=7 -%c1000 -c10 -A999999999 -%N0 --disable-security-limits -F 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.19 (KHTML, like Gecko) Ubuntu/11.10 Chromium/18.0.1025.168' --mirror --keep-alive --robots=0 "{1}" -n -* +*.css +*css.php +*.ico +*/fonts/* +*.svg +*.ttf +fonts.googleapis.com* +*.woff +*.eot +*.png +*.jpg +*.gif +*.jpeg +*.js +{1}* -github.com* +raw.github.com* &&
  rm -rf hts-* &&
  mkdir -p Contents/Resources/Documents &&
  mv -f *.* Contents/Resources/Documents/
  """.format(docname, url)
  
  if download_html:
    os.system(cmd_command)

def update_db(name, typ, path):
  try:
    cur.execute("SELECT rowid FROM searchIndex WHERE path = ?", (path,))
    dbpath = cur.fetchone()
    cur.execute("SELECT rowid FROM searchIndex WHERE name = ?", (name,))
    dbname = cur.fetchone()

    if dbpath is None and dbname is None:
        cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, typ, path))
        print('DB add >> name: {0} | type: {1} | path: {2}'.format(name, typ, path))
    else:
        print("record exists")
  except:
    pass
  
def add_infoplist(base_page):

  index_file = base_page.split("//")[1]
  name = docset_name.split('.')[0]
  
  plist_path = os.path.join(docset_name, "Contents", "Info.plist")
  plist_cfg = {
      'CFBundleIdentifier': name,
      'CFBundleName': name,
      'DocSetPlatformFamily': name.lower(),
      'DashDocSetFamily': 'python',
      'isDashDocset': True,
      'dashIndexFilePath': index_file
  }
  plistlib.writePlist(plist_cfg, plist_path)

def add_urls(pages):

  # loop through index pages:
  for p in pages:

    # setup paths
    page_name = pages[p].split('/')[-1]
    base_path = pages[p].split("//")[1]

    # soup each index page
    html = requests.get(pages[p]).text
    soup = bs(html)

    for a in soup.findAll('a'):
      name = a.text.strip()
      path = a.get('href')
      name = " ".join(name.split())

      if path is not None and not path.startswith("http"):
        path = base_path + path
        update_db(name, p, path)

def main():
  # docset settings
  global docset_name
  docset_name = 'Pandoc.docset'
  output = f'{docset_name}/Contents/Resources/Documents/'

  # docset directory
  if not os.path.exists(output):
      os.makedirs(output)

  # docset icon
  icon = 'http://kirkstrobeck.github.io/whatismarkdown.com/img/markdown.png'
  urllib.urlretrieve(icon, f"{docset_name}/icon.png")

  # index pages
  base_page = 'http://pandoc.org/'
  pages = {
        'Guide'   : base_page,
        'Sample'  : 'http://pandoc.org/demo/example9/',
        }

  # download html
  get_html(docset_name, base_page, True)

  # create and connect to SQLite
  db = sqlite3.connect(f'{docset_name}/Contents/Resources/docSet.dsidx')
  global cur
  cur = db.cursor()
  cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
  cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

  # docset entries
  add_urls(pages)
  add_infoplist(base_page)

  # report num of entries
  cur.execute('Select count(*) from searchIndex;')
  entry = cur.fetchone()
  print(f"{entry} entry.")

  # commit and close db
  db.commit()
  db.close()

if __name__ == '__main__':
  main()

