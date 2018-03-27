# Requests-HTML Docset

Docset build by [AllanLRH](https://github.com/AllanLRH)

## Build-instructions

* Grab the source for the project at the [Github repo](https://github.com/kennethreitz/requests-html)
* Build the HTML source (`make html`)
* Build the docs with doc2dash. I used this command: `doc2dash --name "Requests-html 0.9.0" --destination . --icon ./icon@2x.png --online-redirect-url http://html.python-requests.org --enable-js docs/build/html`, executed from within the doc2dash source folder.
* Rename _Requests-html 0.9.0.docset_ to _requests-html.docset_
* The Docset-file isreally justa folder — go edit this file: _requests-html.docset/Contents/Info.plist_ with a text editor:
    * Remove the version information from the tag `CFBundleName`
    * Add the following lines:
    ```
    <key>dashIndexFilePath</key>
    <string>index.html</string>
    ```
