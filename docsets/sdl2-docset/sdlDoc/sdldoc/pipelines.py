from sdldoc.items import SdlDocItem, SdlCategoryItem
from sdldoc import settings
import os,re,sqlite3

class SdldocPipeline(object):
    
    def __init__(self):        
        self.db=settings.getDb()
        self.cur=settings.getCursor()

    def process_item(self, item, spider):
        content=self.renderItem(item)
        if content is not None:
            name=item['name'][0]
            link=item['link'] if type(item['link']) is str else item['link'][0]
            t='Category'
            file=open(os.path.join(settings.DOC_PATH,link+".html"),'wb')
            file.write(content)
            file.close()
            
            if type(item) is SdlDocItem:
                if 'CategoryEnum' in item['category']:
                    t='Enum'
                elif 'CategoryDefine' in item['category']:
                    t='Define'
                elif 'CategoryStruct' in item['category']:
                    t='Struct'
                else:
                    t='Function'
            self.cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', 
                        (name, 
                         t, 
                         link+".html"))
            print 'name: %s, type: %s, path: %s.html' % (name,t,link)
            self.db.commit()
        return item

    def renderItem(self,item):
        filename=os.path.join(settings.PROJECT_ROOT,"templates");
        if type(item) is SdlDocItem:
            filename=os.path.join(filename,"item.tpl")            
        elif type(item) is SdlCategoryItem:
            filename=os.path.join(filename,"cat.tpl")

        with open(filename,'r') as file:
            content=file.read()
            keys=item.keys()
            for key in keys:
                val=item[key]
                content=re.sub("{"+key+"}",val[0].encode('utf-8','ignore') if val else "",content)
            return content
        return None
        
    
        
