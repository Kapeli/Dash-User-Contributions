[Powershell modules][1] Docset
================

Author: [lucasg][2]

#### Generation steps:

`posh-to-dash.py` is written for Python 3, and has been tested on Windows and Linux. 

```
pip install selenium requests bs4

python posh-to-dash.py --verbose --temporary --output=Powershell/versions/6/Powershell.tgz --version=6
python posh-to-dash.py --verbose --temporary --output=Powershell/versions/5.1/Powershell.tgz --version=5.1
python posh-to-dash.py --verbose --temporary --output=Powershell/versions/5.0/Powershell.tgz --version=5.0
python posh-to-dash.py --verbose --temporary --output=Powershell/versions/4.0/Powershell.tgz --version=4.0
python posh-to-dash.py --verbose --temporary --output=Powershell/versions/3.0/Powershell.tgz --version=3.0

cp static/icon.PNG Powershell/icon.png
cp static/icon@2x.PNG Powershell/icon@2x.png
cp Powershell/versions/6/Powershell.tgz Powershell/Powershell.tgz

```

Otherwise, look at the `.travis` generation script for an up to date build recipe : `https://github.com/lucasg/powershell-docset/blob/master/.travis.yml`


[1]: https://docs.microsoft.com/en-us/powershell/module/
[2]: https://github.com/lucasg