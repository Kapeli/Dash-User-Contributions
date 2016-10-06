Standard ML Docset
=======================

**Author:** [Ethan Lee](https://github.com/Luminoid)

## How to generate the docset
### Prerequisites
* [Dashing](https://github.com/technosophos/dashing)
* `dashing.json`
```json
{
    "name": "Standard_ML",
    "package": "Standard_ML",
    "index": "manpages.html",
    "selectors": {
        "H2 CODE": "Section"
    },
    "ignore": [
        "ABOUT"
    ],
    "icon32x32": "",
    "allowJS": false,
    "ExternalURL": "http://sml-family.org/Basis"
}
```
### initial HTML documentation
* http://sml-family.org/Basis/manpages.html
### How to run the generation script
```bash
$ cd Standard_ML
$ dashing create
# Now you can edit dashing.json. See below.
$ dashing build Standard_ML
```
