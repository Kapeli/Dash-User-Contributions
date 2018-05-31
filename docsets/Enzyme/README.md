# Enzyme

## Author

Jason Weir

* GitHub: [@gidgidonihah](http://github.com/gidgidonihah)
* Twitter: [@gidgidonihah](http://twitter.com/@gidgidonihah)

## Building the Docset

This docset was build using the generate.sh script.
for the script to succeed, there are some prerequisites.

You must have [node](http://nodejs.org), and [dashing](https://github.com/technosophos/dashing#readme) installed.

Dashing has not been kept up to date, so the latest compiled release will not work. It must be built from source.
To do that, you must have [Go](https://golang.org) installed. Follow the
[`go get`](https://github.com/technosophos/dashing#install) installation instructions

For the sake of these instructions we will presume that this repo was cloned to `~/Dash-User-Contributions`.

The generation script will take the following steps.

1. Clone the enzyme repo
2. npm install the enzyme dependencies
3. install the gitbook dependancies in `~/.gitbook/version/{VERSION}/`
4. Build the docset
5. tar the docset and move it to the root of this repo
6. remove the enzyme repo and all dependancies

Note, this will leave gitbook (`~/.gitbook/`) and it's dependancies installed.
You will have to manually remove that if you wish.

### To run the build script:

clone this repo and cd into it, then simply:
```
./generator/build.sh
```

## Update the versions

At this point you should be able to simply update the version in `docset.json`, commit and open a pull request.
Also, it would be nice to add it do the versions folder and the `docset.json` to either replace the minor version
or create a new major version.

NOTE: the script doesn't currently update docset.json for versions, or move the enzyme.tgz into the versions folder,
but could certainly be updated to remove that manual step as well.
