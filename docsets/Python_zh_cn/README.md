# Python Chinese docset

---

* Author: bokix (https://github.com/bokix) and [destroy314](https://github.com/destroy314)
* Instructions:
  Chinese API document for Python.
  You can download initial document at:
  https://docs.python.org/
  just make search index from "genindex-all.html"

To generate docset, install [doc2dash](https://doc2dash.hynek.me/en/stable/installation/), download HTML format documentation from [https://docs.python.org/zh-cn/3/download.html](https://docs.python.org/zh-cn/3/download.html) and run:

    doc2dash -n Python_zh_cn -I index.html -u https://docs.python.org/zh-cn/3.x/ -j python-3.x.x-docs-html

Copy two icons into `Python_zh_cn.docset`, then change the value of `<key>CFBundleName</key>` in `Info.plist` to `<string>Python 3.x</string>`.