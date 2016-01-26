jBASE Docset
=======================

This Docset was created by [Lucian Fratila](https://www.bnksys.com) using contents from [a fork](https://github.com/lucianf/jbc-language) of the [jBASE Programmer's Guide](https://github.com/temenostech/jbc-language).

In short, the process consists in:
- splitting the original file into three files (jBC, System Variables, Categories)
- raising markdown level by one (e.g. ## -> #) in each file
- jBC: using a mapping file (originally generated from the jBASE 3 index page) to tag each section with the appropriate type (function/statement)
- System Variables, Categories: tagging accordingly (variable/category)
- glueing the three files together and using pandoc to create an Epub with TOC
- extracting the Epub, removing the unneeded meta files, setting the correct TOC title and converting the tags into class attributes
- using dashing to convert the HTML structure into a docset

Detailed instructions on how to reassemble the data (markdown->epub->docset) along with the script I used are provided in [this repo](https://github.com/lucianf/dash-docset-jbase).  Alternatively, please [contact me](https://github.com/lucianf).
