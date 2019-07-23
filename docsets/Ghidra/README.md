Ghidra Docset
=============

This docset was created by [Ryan Govostes](https://github.com/rgov) from the [Ghidra](https://ghidra-sre.org) Javadoc-generated documentation.

To generate this docset, launch Ghidra and open the CodeBrowser tool. From the Help menu, choose "Ghidra API Help." This will invoke Javadoc and open the browser to the generated HTML files.

The browser URL will look something like this:

    file:///private/var/folders/.../GhidraAPI_javadoc/9.0.4/api/ghidra/app/script/GhidraScript.html
           ^--------------------...----------------------------^

Copy the highlighted portion. Then run the [javadocset](https://github.com/Kapeli/javadocset) tool with that path:

    javadocset Ghidra "/private/var/folders/.../GhidraAPI_javadoc/9.0.4/api/"

This will place the Ghidra.docset in the current directory.

Edit the docset's Info.plist file to change the `dashIndexFilePath` to `ghidra/app/script/GhidraScript.html`.

The Ghidra icon is located [here](https://raw.githubusercontent.com/NationalSecurityAgency/ghidra/master/Ghidra/RuntimeScripts/Windows/support/ghidra.ico) or in `support/ghidra.ico`. This file contains the icon at multiple resolutions. The [redketchup.io Icon Editor](https://redketchup.io/icon-editor) is one tool that can be used to extract the icon.


Known Issues
------------

`javadocset` outputs many warnings ([#11](https://github.com/Kapeli/javadocset/issues/11)).
