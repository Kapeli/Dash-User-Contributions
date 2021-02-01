Scrapy Dash Docset
=======================


### Docset Description
Scrapy is a fast high-level screen scraping and web crawling framework, used to crawl websites and extract structured data from their pages.

### Author
- [Monson Shao](https://github.com/holymonson)
- [Aziz Alto](https://github.com/iamaziz)


### How to generate the docset
```bash
make -C docs/ html
doc2dash docs/build/html/ -n Scrapy -u https://docs.scrapy.org/en/latest/ -I index.html -i tests/sample_data/test_site/files/images/scrapy.png -f
tar --exclude='.DS_Store' -czf Scrapy.tgz Scrapy.docset
cp Scrapy.tgz ../Dash-User-Contributions/docsets/Scrapy/

```

### Note
> Generating the docsest is tested on Mac OS only. If anyone gets to try it on Windows, please let me know how it goes.

> Scrapy maintains other wiki, code snippets, and tutorials on github. See: [https://github.com/scrapy/scrapy/wiki](https://github.com/scrapy/scrapy/wiki)
