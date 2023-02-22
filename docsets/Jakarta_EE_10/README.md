# Jakarta EE 10

## About this docset

_Packager: Cameron Rodriguez ([@cam-rod](https://github.com/cam-rod), [camrod.me](https://camrod.me))_

This is an unofficial docset for [Jakarta EE 10](https://jakarta.ee/release/10/), the successor to Java Enterprise Edition (Java EE). Specifically, it's based on the Javadoc for Jakarta EE Platform 10, which contains all of the individual Jakarta specifications and profiles (i.e. Jakarta EE Web Profile, but _not_ MicroProfile).

## Building the docset

### Prerequisites

- Go
- [william8th/javadocset](https://github.com/william8th/javadocset)
- Javadoc JAR for Jakarta EE Platform 10 (from Maven package `jakarta.platform:jakarta-jakartaee-api:10.0.0`, [direct download link](https://repo1.maven.org/maven2/jakarta/platform/jakarta.jakartaee-api/10.0.0/jakarta.jakartaee-api-10.0.0-javadoc.jar))

### Instructions

1. Unpack the JAR (ex. change the extension to `.zip` and unzip the package)
2. Compile with javadocset. Assuming the extracted folder is not nested, and is called `jakarta.jakartaee-api-10.0.0-javadoc`:

```shell
javadocset 'Jakarta EE 10' jakarta.jakartaee-api-10.0.0-javadoc
```

3. Rename the generated docset folder to `Jakarta_EE_10.docset`. The folder `Jakarta_EE_10.docset/Contents/Resources/Documents/META-INF/` can be deleted.
4. The Javadoc built-in search function generates broken links due to [JDK-8215291](https://bugs.openjdk.org/browse/JDK-8215291). To patch this issue, open `Jakarta_EE_10.docset/Contents/Resources/Documents/search.js` and change line 53 to the following:

```js
                if (item.m && ui.item.p == item.l) {
```

5. Configure `Jakarta_EE_10.docset/Contents/Info.plist`:
    - Edit _CFBundleIdentifier_: `<string>jakarta-ee10</string>`
    - Edit _DocSetPlatformFamily_: `<string>jakarta-ee10</string>`
    - Edit _dashIndexFilePath_: `<string>index.html</string>`
    - Add _isJavaScriptEnabled_: `<true/>`
    - Add _isDashDocset_: `<true/>`
    - Add _DashDocSetFallbackURL_: `<string>https://jakarta.ee/specifications/platform/10/apidocs/</string>` (note that Javadoc search is not patched on the web version)
6. Optional [logo download](https://www.eclipse.org/org/artwork/zip_files/jakarta-logo.zip) (zip file, under `jakarta-logo/jakartaee_color/jakartaee_color-r/jakarta_ee_logo_schooner_color_stacked_default.svg`)
