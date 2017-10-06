Nightwatch.js
=======================

* Made by [Eric Schaefer](https://github.com/eschaefer)
* To generate the docset:
  * Scraped HTML from [http://nightwatchjs.org](http://nightwatchjs.org) using `HTTrack` commandline tool.
  * Used [Dashing](https://github.com/technosophos/dashing#readme) to generate docset, with this config:

```
{
  "name": "Nightwatch.js",
  "package": "nightwatch.js",
  "index": "nightwatchjs.org/api/index.html",
  "selectors": {
    ".apimethod h3": [
      { "type": "Method", "matchpath": "nightwatchjs.org/api/index.html" }
    ],
    ".docs-section .page-header h2": [
      {
        "type": "Style",
        "requiretext": "(Assert)|(Expect)",
        "matchpath": "nightwatchjs.org/api/index.html"
      }
    ],
    ".docs-section .page-header h2": [
      {
        "type": "Guide",
        "requiretext":
          "(Using Nightwatch)|(Running Tests)|(Working with Page Objects)|(Extending Nightwatch)|(Unit Testing with Nightwatch)",
        "matchpath": "nightwatchjs.org/guide/index.html"
      }
    ]
  },
  "icon32x32": "logo-nightwatch.png",
  "allowJS": true
}

```
