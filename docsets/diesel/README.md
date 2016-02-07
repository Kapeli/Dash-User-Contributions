Diesel Docset
=======================

This Docset was created by [Luís Zamith](https://github.com/zamith)

The Docset was generated with
[Dashing](https://github.com/technosophos/dashing), using the following
configuration file:

```json
{
    "name": "Diesel",
    "package": "diesel",
    "index": "index.html",
    "selectors": {
        ".methods .fnname": {
           "type":"Function",
           "matchpath":"diesel/.*\\.html"
        },
        "h1 .trait": {
          "type":"Trait",
           "matchpath":"diesel/.*\\.html"
        },
        "h1 .macro": {
          "type":"Macro",
           "matchpath":"diesel/.*\\.html"
        }
    },
    "ignore": [
        "ABOUT"
    ],
    "icon32x32": "logo.png",
    "allowJS": false,
    "ExternalURL": "http://sgrif.github.io/diesel/diesel/index.html"
}
```

The documentation came from the [official API
documentation](http://sgrif.github.io/diesel/diesel/index.html).

The documentation is valid for Diesel `0.5.0`.

For more information about Diesel, visit http://diesel.rs/
