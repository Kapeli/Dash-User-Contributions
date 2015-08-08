obspy Docset
============

- __Docset Description__:
    - [obspy](http://www.obspy.org/) is an open-source project dedicated to provide a Python framework for processing seismological data.

- __Author__:
    - [Tobias Megies](https://github.com/megies)

- __How to generate the docset__:
    - fetch and extract documentation: 
    	- `wget https://github.com/obspy/obspy/releases/download/0.10.2/obspy-0.10.2-documentation.tgz`
    	- `tar -xf obspy-0.10.2-documentation.tgz`
    - generate docset: 
    	- `doc2dash -v -n obspy obspy-0.10.2-documentation`
    - Set Info.plist to index page, add to Info.plist:
    	- "<key>dashIndexFilePath</key><string>index.html</string>"
    - Add icon:
        - `cp icon.png obspy.docset/`
    - Zip it:
        - `tar --exclude='.DS_Store' -cvzf obspy.tgz obspy.docset`
