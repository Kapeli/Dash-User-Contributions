# WooCommerce Dash Docset

An unofficial Dash Docset for the [WooCommerce][1] plugin for [WordPress][2].

## Installation

To build the docset from source, you'll need the following prerequisites:

* [Xcode Developer Tools][3]
* [ApiGen][4]
* [ApiGen2Docset][5]

To install the dependencies, run the following command line instructions from your Terminal or shell:

**Install Xcode**

1. `xcode-select --install`

**Install ApiGen**

1. `cd /usr/local/src`
2. `curl -kLO http://cloud.github.com/downloads/apigen/apigen/ApiGen-2.8.0-standalone.zip`
3. `unzip ApiGen-2.8.0-standalone.zip`

**Install ApiGen2Docset**

1. `cd /usr/local/src`
2. `curl -kLo apigen2docset.tar.gz https://github.com/hugo187/apigen2docset/archive/master.tar.gz`
3. `tar -xzvf apigen2docset.tar.gz && mv apigen2docset-master apigen2docset && cd "$_"`
4. `chmod +x apigen2docset.sh && sudo cp "$_" /usr/local/bin/apigen2docset`

## Usage

To generate the PHP Docset from source, run `apigen.php` and point at to the location of your WooCommerce plugin directory:

`php -d memory_limit=512M /usr/local/src/apigen/apigen.php --groups "none" --title "WooCommerce" --template-config /usr/local/src/apigen/templates/bootstrap/config.neon -s ~/Sites/example.dev/wp-content/plugins/woocommerce -d ~/Desktop/WooCommerce`

To generate the Dash Docset, run `apigen2docset` and specify the location where you output the above PHP Docset:

`/usr/local/src/apigen2docset/apigen2docset.sh ~/Desktop/WooCommerce`

The resulting docset from ApiGen2Docset uses a generic bundle file template. I modify the original file, `~/Desktop/WooCommerce.docset/Contents/Info.plist`, to better suit Dash with the following:

```
<?xml version="1.0" encoding="UTF-8"?>

<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
	<dict>
		<key>CFBundleIdentifier</key>
		<string>woocommerce</string>
		
		<key>CFBundleName</key>
		<string>WooCommerce</string>
		
		<key>DocSetPlatformFamily</key>
		<string>woocommerce</string>
		
		<key>dashIndexFilePath</key>
		<string>package-WooCommerce.html</string>
		
		<key>isJavaScriptEnabled</key>
		<true />
	</dict>
</plist>
```

To build the final tar archive for consideration as a User-Contributed Docset for Dash, run the following:

`tar --exclude='.DS_Store' -cvzf WooCommerce.tgz WooCommerce.docset`

## Support

For support, please refer to the official [Github repository][6].

### Changelog

* 2.1.9 — 27 May 2014
* 2.1.8 — 30 April 2014

[1]: http://woothemes.com/woocommerce/
[2]: http://wordpress.org/
[3]: https://itunes.apple.com/us/app/xcode/id497799835
[4]: http://apigen.org/
[5]: https://github.com/hugo187/apigen2docset
[6]: https://github.com/ryanjbonnell/WooCommerce.docset