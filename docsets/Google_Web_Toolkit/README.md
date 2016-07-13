Google Web Toolkit
=======================

Docset for the Google Web Toolkit API.

Created by [Thomas Luff](https://github.com/hipyhop)

To create this docset:

1. Download and extract the latest GoogleWebToolkit SDK [from here](http://www.gwtproject.org/download.html).
2. Download Kapeli's javadocset tool [here](https://github.com/Kapeli/javadocset).
3. Run `./javadocset "Google Web Toolkit" gwt-2.6.1/doc/javadoc`
4. Change the value of `DocSetPlatformFamily` in GoogleWebToolkit.docset/Contents/Info.plist to 'gwt'. This is keyword to use in dash when searching this docset.
