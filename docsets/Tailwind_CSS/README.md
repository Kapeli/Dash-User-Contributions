**Please note that different versions of this Docset have been made by different people. Please contact the right person for your relevant Docset.**

[Tailwind CSS 1.x][1] Docset
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
php dash-docset build tailwindcss
```

If you just want to download the docs, you can run `php dash-docset grab tailwindcss`, if you already have the docs but just want to build the package, run `php dash-docset build tailwindcss`.

The docset information (where to download the doc, which file is the index, where to get the icons, what CSS to update, etc...) is defined in a Docset class of the builder app. You could add any other doc and build it, although currently the builder is in alpha and changes might occur periodically.

# [Tailwind CSS 0.7.4][1] Docset

Author: Ben Booth ([@bkbooth11][2])

## Generation steps

- Clone [github.com/bkbooth/dash-tailwindcss-docs][6] and `cd` into cloned directory
- Run `yarn` (or `npm install`)
- Run `yarn build` (or `npm run build`)

## Prequisites

- [Node.js][3] >= v8.0.0
- [Yarn][4] (preferred, can use `npm`)
- [Wget][5]

## Known Bugs

- None, please submit any you find [here][7]

## Planned Improvements

- (Maybe) add Table of Contents support

[1]: https://tailwindcss.com/
[2]: https://twitter.com/bkbooth11
[3]: https://nodejs.org/
[4]: https://yarnpkg.com/
[5]: https://www.gnu.org/software/wget/
[6]: https://github.com/bkbooth/dash-tailwindcss-docs
[7]: https://github.com/bkbooth/dash-tailwindcss-docs/issues
