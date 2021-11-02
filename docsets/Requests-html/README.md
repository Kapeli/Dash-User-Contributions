# Requests-HTML Docset

Docset build by [AllanLRH](https://github.com/AllanLRH)

## Build-instructions

* Grab the source for the project at the [Github repo](https://github.com/kennethreitz/requests-html)
* Build the HTML source (`make html`)
* Build the docs with doc2dash. I used this command: `doc2dash --name "Requests-html" --destination . --icon ./icon@2x.png --online-redirect-url http://html.python-requests.org --enable-js docs/build/html`, executed from within the doc2dash source folder.
* Rename docset to _requests-html.docset_
* The Docset-file is really justa folder — go edit this file: _requests-html.docset/Contents/Info.plist_ with a text editor and add the following lines:

```
<key>dashIndexFilePath</key>
<string>index.html</string>
```
