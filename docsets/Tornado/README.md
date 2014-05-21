Tornado Dash Docset
===================

Building the Docset
-------------------

Check out stable tornado docs:

    git clone https://github.com/tornadoweb/tornado.git
    cd tornado/docs
    git checkout stable
    make sphinx

Build the docset:

    doc2dash --name=Tornado tornado/docs/build/html
    cp icon.png icon@2x.png Tornado.docset

Enable javascript and set an index page by adding the following to ``Tornado.docset/Contents/Info.plist``:

    <key>dashIndexFilePath</key>
    <string>index.html</string>
    <key>isJavaScriptEnabled</key>
    <true/>

Package the docset:

    tar --exclude='.DS_Store' -cvzf Tornado.tgz Tornado.docset

