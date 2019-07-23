Ghidra Docset
=============

This docset was created by [Ryan Govostes](https://github.com/rgov) from the [Ghidra](https://ghidra-sre.org) Javadoc-generated documentation.

To generate this docset, launch Ghidra and open the CodeBrowser tool. From the Help menu, choose "Ghidra API Help." This will invoke Javadoc and open the browser to the generated HTML files.

The browser URL will look something like this:

    file:///private/var/folders/.../GhidraAPI_javadoc/9.0.4/api/ghidra/app/script/GhidraScript.html
           ^--------------------...----------------------------^

Copy the highlighted portion. Then run the [javadocset](https://github.com/Kapeli/javadocset#readme) tool with that path:

    javadocset Ghidra "/private/var/folders/.../GhidraAPI_javadoc/9.0.4/api/"

This will place the Ghidra.docset in the current directory.

Edit the docset's Info.plist file to change the `dashIndexFilePath` to `ghidra/app/script/GhidraScript.html`.


Known Issues
------------

`javadocset` outputs many "could not determine type" warnings.
