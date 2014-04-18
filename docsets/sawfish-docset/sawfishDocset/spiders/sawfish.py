from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.item import Item
from sawfishDocset import settings
import re,os,sqlite3

class SawfishCrawler(CrawlSpider):
    """
    crawl sawfish documentation
    """
    name = "sawfish"
    allowed_domains= ["sawfish.tuxfamily.org"]
#    download_delay = 5
    COOKIES_DEBUG = True
    start_urls=[
        "http://sawfish.tuxfamily.org/sawfish.html/"
        ]
    rules=(
        Rule(SgmlLinkExtractor(
                allow=(r"Concept-Index\.html")
                )
             ,callback="parse_content",follow=True),
        Rule(SgmlLinkExtractor(
                allow=(r"Function-Index\.html")
                )
             ,callback="parse_function",follow=True),
        Rule(SgmlLinkExtractor(
                allow=(r"Variable-Index\.html")
                )
             ,callback="parse_variable",follow=True),
        Rule(SgmlLinkExtractor(allow=(r".*")),callback="saveFile",follow=True),
        )
    
    def fileName(self,url):
        pattern=re.compile(r"/([^/]*)\.html$")
        match= pattern.search(url)
        if match:
            return match.group(1)

    def saveFile(self,resp):
        link=self.fileName(resp.url)
        if link:
            file=open(os.path.join(settings.DOC_PATH,link+".html"),'wb')
            file.write(unicode(resp.body,errors='ignore'))
            file.close()
            print link
    
    def parse_content(self,resp):
        self.saveFile(resp)
        #Category
        sel=Selector(resp)
        links=sel.xpath('//div[@class="contents"]//a')
        for idx,link in enumerate(links):
            name=link.xpath('text()').extract()
            if re.match(r"^\d*\.\d*(.+)$",name[0]) is not None:
                continue # skip subcategories
            else:
                match=re.match(r"^\d+(.*)$",name[0])
                self.insert([match.group(1).strip() if match is not None else name[0]],
                            link.xpath('@href').extract(),
                            "Category")
        
        
    def parse_function(self,resp):
        self.saveFile(resp)      
        self.parse_internal(resp,"Function")  

    def parse_variable(self,resp):
        self.saveFile(resp)
        self.parse_internal(resp,"Variable")
        
        
    def parse_internal(self,resp,category):
        sel=Selector(resp)
        links=sel.xpath('//table[@class="index-{0}"]//a[code]'.format("fn" if category == "Function" else "vr"))
        for idx,link in enumerate(links):
            self.insert(link.xpath('code/text()').extract(),link.xpath('@href').extract(),category)

        
    def insert(self,name,link,t):
        print "inserting: %s %s %s" % (name[0],t,link[0])
        db=settings.getDb()
        cur=settings.getCursor()
        cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', 
                        (name[0], 
                         t, 
                         link[0]))
        db.commit()

