OpenGL Mathematics Extensions for Dash
=======================

Author: @pavelzw

Generation of the docset:

Have the files `glm-icon-16x16.png`, `glm-icon-32x32.png`, `glm-Info.plist`, `generate-glm.sh` in your CWD.

Prerequisites:

You must have the following installed: `make`, `doxygen`, `docsetutil`, `gsed`.
```
brew install make
brew install doxygen
brew install swiftdocorg/formulae/docsetutil
brew install gsed
```
`generate-glm.sh`
<details>

```shell
#!/bin/bash

GLM_VERSION='0.9.9.8'

rm -rf glm
rm -rf glm.docset
git clone https://github.com/g-truc/glm.git --branch $GLM_VERSION --depth 1 -c advice.detachedHead=false

# modify doxygen config
# https://kapeli.com/docsets#doxygen
cd glm/doc
gsed -i -e 's/GENERATE_DOCSET[[:space:]]*= NO/GENERATE_DOCSET = YES/g' man.doxy
gsed -i -e 's/DISABLE_INDEX[[:space:]]*= NO/DISABLE_INDEX = YES/g' man.doxy
gsed -i -e 's/SEARCHENGINE[[:space:]]*= YES/SEARCHENGINE = NO/g' man.doxy
# GENERATE_TREEVIEW is already set to NO

doxygen man.doxy
cd html
# replace xcode docsetutil with homebrew docsetutil
gsed -i 's/$(XCODE_INSTALL)\/usr\/bin\/docsetutil/docsetutil/g' Makefile
make
mv org.doxygen.Project.docset ../../../glm.docset

cd ../../..
cp glm-Info.plist glm.docset/Contents/Info.plist
cp glm/doc/manual.pdf glm.docset/Contents/Resources/Documents/manual.pdf
gsed -i 's/https:\/\/github.com\/g-truc\/glm\/blob\/master\/manual.md/manual.pdf/g' glm.docset/Contents/Resources/Documents/index.html

cp glm-icon-16x16.png glm.docset/icon.png
cp glm-icon-32x32.png glm.docset/icon@2x.png
```

</details>

`glm-Info.plist`
<details>

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN"
"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
     <key>CFBundleIdentifier</key>
     <string>glm</string>
     <key>CFBundleName</key>
     <string>OpenGL Mathematics</string>
     <key>DashDocSetFallbackURL</key>
	<string>https://glm.g-truc.net/0.9.9/api/</string>
     <key>DashDocSetFamily</key>
     <string>doxy</string>
     <key>DashDocSetKeyword</key>
	<string>glm</string>
	<key>DashDocSetPluginKeyword</key>
	<string>glm</string>
	<key>DashWebSearchKeyword</key>
	<string>glm</string>
     <key>DocSetPlatformFamily</key>
	<string>usercontribGLM</string>
     <key>dashIndexFilePath</key>
     <string>index.html</string>
     <key>isDashDocset</key>
	<false/>
     <key>isJavaScriptEnabled</key>
	<false/>
</dict>
</plist>
```

</details>

To generate the docset, execute `generate-glm.sh`.