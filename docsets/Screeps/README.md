Screeps Dash Docset
=======================

* Docset Description:
  * _MMO sandbox game for programmers_. It's an open-source game for programmers, wherein the core mechanic is programming your units' AI. You control your colony by writing JavaScript.
* Docset Author:
  * Malte Poll ([Twitter](http://twitter.com/malt3), [GitHub](http://github.com/malt3))
* Installation:

1. Clone the [official Screeps documentation](https://github.com/screeps/docs) and build the static sites
```
git clone https://github.com/screeps/docs screeps-docs
cd screeps-docs
npm install
cd api
npm install
cd ..
npm run generate
cd api
npm run generate
cd ../..
```

2. Clone fixup script to repair some of the links
```
git clone https://github.com/malt3/screeps-dash-generator
cd screeps-dash-generator
python3 -m pip install --user beautifulsoup4
# copy static docs here before modifying them
cp -r ../screeps-docs/public .
# fixup links and do some cosmetic changes
python3 fixup-links.py --path public/
# Copy dashing configuration into the webroot
cp dashing.json public/
```

3. Install [dashing](https://github.com/technosophos/dashing) and build the docset
```
# first install go using your normal package manager, then
go get -u github.com/technosophos/dashing
# alternatively, on macos, you can also use brew:
# brew install dashing
# now build the docset:
cd public
dashing build Screeps
# The resulting docset is written to Screeps.docset
# (Optional: Copy Icon into the docset folder)
cp ../icon@2x.png Screeps.docset/icon.png
```
