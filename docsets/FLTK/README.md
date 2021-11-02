# FLTK Docset

## Author

Edward Rudd

## Building the docset

1) Download the FLTK source distribution and build the project via CMake
2) Do some slight modifications to the generated Doxygen file created by FLTK's CMake scripts.
    ```
    DOCSET_FEEDNAME        = "FLTK Programming Manual"
    DOCSET_BUNDLE_ID       = org.fltk.FLTK
    DOCSET_PUBLISHER_ID = org.fltk.FLTK
    DOCSET_PUBLISHER_NAME = FLTK
    DISABLE_INDEX = YES
    GENERATE_TREEVIEW      = NO
    ```

3) Build the doxygen docs with cmake.
4) Run "make" in the generated html folder
5) Edit the produced Info.plist with the following changes
    ```
    <key>DashDocSetFamily</key>
    <string>fltk</string>
    <key>DocSetPlatformFamily</key>
    <string>fltk</string>
    <key>DashDocSetFallbackURL</key>
    <string>http://www.fltk.org/doc-1.3/</string>
    <key>dashIndexFilePath</key>
    <string>index.html</string>
    ```

## Bugs & Enhancements

If you have problems with this documentation set, or you would like to suggest
improvements, feel free to report them on the
[FLTK Docset Issue Tracker](https://github.com/urkle/Dash-User-Contributions/issues).
