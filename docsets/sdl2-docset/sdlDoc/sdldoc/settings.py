import os,sqlite3
BOT_NAME = 'sdldoc'

SPIDER_MODULES = ['sdldoc.spiders']
NEWSPIDER_MODULE = 'sdldoc.spiders'

ITEM_PIPELINES = [
    "sdldoc.pipelines.SdldocPipeline"
]

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

BASE_PATH=os.path.join(
            PROJECT_ROOT,
            "output",
            "sdl2.docset/Contents/Resources")

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

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'sdlDoc (+http://www.yourdomain.com)'

