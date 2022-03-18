# webextensions-docset

WebExtensions documentation set for [Dash](http://kapeli.com/dash), based on [MDN WebExtensions](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions) by @private_face.

## Building

### Prerequisites
* Node >= 14
* [Yarn](https://github.com/yarnpkg/yarn)

### Building
1. Clone the repo and install its dependencies:
```bash
git clone git@github.com:private-face/webextensions-docset.git
cd webextensions-docset
yarn install
```

2. Build the docset
```bash
yarn build

```

## Known issues
* Generation script will probably not work on Windows.
