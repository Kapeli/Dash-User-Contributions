Google Apps Script Docset
=======================

This docset is created by [Alexander Maiburg](http://github.com/almai). It contains the complete reference for all [Google Apps Script Services](https://developers.google.com/apps-script/reference/).

You can download the docset file and use it immediately in [Kapelis Dash](https://kapeli.com) or generate it from source.

Generating the docset:

``` bash
# Install go. On MacOS execute...
~ brew install go
# Install Dashing.
~ go get -u github.com/technosophos/dashing
# Clone files for Docset.
~ git clone git@github.com:almai/gas-docset.git
# Change into folder.
~ cd gas-docset
# Edit dashing.json or leave the defaults. (For further information please visit https://github.com/technosophos/dashing).
~ vim dashing.json
# Start generation (depending on the install path of Dashing).
~ ~/go/bin/dashing build googleAppsScript
```

After generation, you can import the docset into the Dash app.
