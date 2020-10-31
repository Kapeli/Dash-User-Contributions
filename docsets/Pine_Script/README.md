Pine Script Docset
=======================

Author: [GenralD](https://github.com/GeneralD)

Generating docsets:

1. Clone [https://github.com/tradingview/pine_script_docs](https://github.com/tradingview/pine_script_docs)
2. Run in the directory:

```
make install_tools
make syncpackages
make html
doc2dash -i source/images/Pine_Script_logo_small.png --add-to-global build/html -n 'Pine Script 4'
```

