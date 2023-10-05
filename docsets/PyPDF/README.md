# PyPDF Docset

[PyPDF](https://github.com/py-pdf/pypdf) is a free and open-source pure-python PDF library capable of splitting, merging, cropping, and transforming the pages of PDF files. It can also add custom data, viewing options, and passwords to PDF files. PyPDF can retrieve text and metadata from PDFs as well.

## Author

- Xavier Yang (https://github.com/ivaquero)

## Instructions

- download the latest document from https://github.com/py-pdf/pypdf
- unpack the zip file
- `cd pypdf-main/docs`
- run the following commands

```cmd
make html
doc2dash -v -n PyPDF -i pypdf-main/docs/_build/html/_static/logo.png -I pypdf-main/docs/_build/html/index.html pypdf-main/docs/_build/html
tar cvzf PyPDF.tgz PyPDF.docset
```
