Hypothesis Docset
=================

* Author: Dan Girellini (https://github.com/dangitall)
* Instructions:
 * clone https://github.com/HypothesisWorks/hypothesis-python.git
 * `cd hypothesis-python`
 * `sphinx-build docs docbuild` (install sphinx via pip)
 * `cd docbuild``
 * create dashing.json:

````
{
    "name": "Hypothesis",
    "package": "hypothesis",
    "index": "index.html",
    "selectors": {
        "dl.function code.descname": "Method",
        "dl.attribute code.descname": "Attribute",
        "div.section h1": {
            "type": "Category",
            "regexp": "¶",
            "replacement": ""
        },
        "div.section h2": {
            "type": "Section",
            "matchpath": "examples|data|details|development|django|healthchecks|index|packaging|quick|settings|stateful|usage",
            "regexp": "¶",
            "replacement": ""
        }
    },
    "ignore": [
        "ABOUT"
    ],
    "icon32x32": "",
    "allowJS": false,
    "ExternalURL": ""
}
````
 * `dashing build -s . -f dashing.json` (https://github.com/technosophos/dashing)
 * add this to the Contents/Info.plist dict:

````
   <key>DashDocSetFallbackURL</key>
   <string>https://hypothesis.readthedocs.io/en/latest/</string>
````
