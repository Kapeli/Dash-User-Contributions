Laravel Zero Docset
=======================

## Bug reports

You can contact me at [@godbout](https://twitter.com/godbout), on [GitHub](https://github.com/godbout) or by email at guill@sleeplessmind.com.mo.

## Docset build

I built my own builder in PHP, available here: https://github.com/godbout/dash-docset-builder

To build this docset:
```php
// Install the PHP dependencies
composer install

// Download the docs, package, and archive them
php dash-docset build laravel-zero
```

If you just want to download the docs, you can run `php dash-docset grab laravel-zero`, if you already have the docs but just want to build the package, run `php dash-docset build laravel-zero`.

The docset information (where to download the doc, which file is the index, where to get the icons, what CSS to update, etc...) is defined in a Docset class of the builder app. You could add any other doc and build it, although currently the builder is in alpha and changes might occur periodically.
