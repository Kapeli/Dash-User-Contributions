from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.item import Item
from sdldoc.items import SdlDocItem, SdlCategoryItem
import re

class FuncSpider(CrawlSpider):
    """
    crawl sdl2 doc
    """
    name = "func"
    allowed_domains= ["wiki.libsdl.org"]
    download_delay = 10
    COOKIES_DEBUG = True
    start_urls= [
        "http://wiki.libsdl.org/CategoryAPI",
        "http://wiki.libsdl.org/APIByCategory"
        ] 
    rules=(
        Rule(SgmlLinkExtractor(allow=(r"/SDL_[^?]+\?highlight=.+")),callback='parse_item'),
        Rule(SgmlLinkExtractor(allow=(r"/Category[^?]+")),callback='parse_category'),
        )

    def parse_item(self,resp):        
        sel = Selector(resp)
        pattern=re.compile(r"http://wiki\.libsdl\.org/([^?]+).*")
        matches=pattern.match(resp.url)
        item=SdlDocItem()
        item['name']=sel.xpath('//div[@id="page"]//h1/text()').extract()
        item['link']=matches.groups(1) if matches else resp.url
        item['category']=sel.xpath('(//div[@id="page"]/div//p)[last()]/a//text()').extract()
        item['content']=sel.xpath('//div[@id="page"]//div[@id="content"]').extract()
        return item
    
    def parse_category(self,resp):
        sel=Selector(resp)
        item=SdlCategoryItem()
        item['link']=re.split("/",resp.url)[-1:][0]
        item['name']=sel.xpath('//div[@id="page"]//h1/text()').extract()
        item['content']=sel.xpath('//div[@id="page"]//div[@id="content"]').extract()
        return item



