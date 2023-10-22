# NLTK docset

[NLTK](http://www.nltk.org/) is a Natural Language ToolKit using python.

## Authors

- [Aziz Alto](https://github.com/iamaziz)
- [Xavier Yang](https://github.com/ivaquero)

## Building Instruction

- Download the latest document from https://github.com/nltk/nltk.github.com
- Unzip the document
- Run the following commands

```bash
doc2dash -v -n NLTK -i nltk.github.com-master/_static/img/favicon-16x16.png -I nltk.github.com-master/index.html nltk.github.com-master
tar cvzf NLTK.tgz NLTK.docset
```
