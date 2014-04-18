# Scrapy settings for sawfishDocset project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
import os,sqlite3
BOT_NAME = 'sawfishDocset'

SPIDER_MODULES = ['sawfishDocset.spiders']
NEWSPIDER_MODULE = 'sawfishDocset.spiders'

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

BASE_PATH=os.path.join(
            PROJECT_ROOT,
            "output",
            "sawfish.docset/Contents/Resources")

DOC_PATH=os.path.join(BASE_PATH,"Documents")

if not os.path.exists(DOC_PATH):
    os.makedirs(DOC_PATH)

_db=sqlite3.connect(os.path.join(BASE_PATH,"docSet.dsidx"))

def getDb():
    return _db

def getCursor():
    return _db.cursor()

def closeDb():
    _db.close()

#USER_AGENT = 'sawfishDocset (+http://www.yourdomain.com)'
