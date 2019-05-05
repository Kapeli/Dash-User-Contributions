Ada 2012 Standard Docset
=======================

Author: Bartek Jasicki (https://github.com/thindil)

Prerequisites: Python, Sqlite3, Unzip

1. Download Ada Standard from:
   http://www.ada-auth.org/standards/rm12_w_tc1/RM-12_w_TC1-Html.zip
2. Take all needed files from Git repository:
   https://github.com/thindil/ada-docset
2. Make docset directory: `mkdir -p Ada.docset/Contents/Resources/Documents`
3. Unzip them to the docset directory:
   `unzip RM-12_w_TC1-Html.zip -d Ada.docset/Contents/Resources/Documents`
4. Run generating script: `./adadocset.py`
5. Copy both icons and JSON file to docset: `cp *.png docset.json Ada.docset/`

Legal information: Ada Standard may be copied, in whole or in part, in any
form or by any means, as is, or with alterations, provided that:
1. Alterations are clearly marked as alterations.
2. Copyright notice inside document is included unmodified in any copy.
