# Yii2 Dash Docset

An unofficial Dash Docset for the [Yii2][1].

## Installation

To build the docset from source, you'll need the following prerequisites:

* [Dash Docset Generator for Yii2][2]

To install the dependencies, run the following command line instructions from your Terminal or shell:

**Install "Dash Docset Generator for Yii2"**

1. `git clone --progress https://github.com/stepanselyuk/dash-docset-yii2`

## Usage

To generate the PHP Docset from source, run `./_update` (need PHP >= 5.4, also you can specify path to PHP in config.sh):

`sh ./_update`

You will see Yii2.docset and Yii2.tgz in repository folder.

```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleIdentifier</key>
	<string>yii2</string>
	<key>CFBundleName</key>
	<string>Yii 2</string>
	<key>DocSetPlatformFamily</key>
	<string>yii2</string>
	<key>isDashDocset</key>
	<true/>
	<key>dashIndexFilePath</key>
	<string>index.html</string>
	<key>isJavaScriptEnabled</key><true/>
</dict>
</plist>
```

## Support

For support, please refer to the official [Github repository][2].

### Changelog

* 2.0.0 Beta — 22 July 2014

[1]: http://yiiframework.com/
[2]: https://github.com/stepanselyuk/dash-docset-yii2
