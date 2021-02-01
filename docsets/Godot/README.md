Godot Docset
=======================

[Godot](https://godotengine.org/) docset for [Dash](http://kapeli.com/dash).

By [Dmitrii Maganov](https://github.com/vonagam).

Instructions how to reproduce the build (using version 3.2 as an example):

- Install [Dashing](https://github.com/technosophos/dashing) (`brew install dashing` on mac).

- Download documentation sources from https://github.com/godotengine/godot-docs/tree/3.2

- Build documentation with `pip install -r requirements.txt` and `make html`.

- Move into built documentation folder (`_build/html`).

- Optionally copy provided here `icon@2x.png`.

- Create `dashing.json`:

```json
{
  "name": "Godot",
  "package": "godot",
  "index":"index.html",
  "icon32x32": "icon@2x.png",
  "allowJS": true,
  "ExternalURL": "https://docs.godotengine.org/en/3.2",
  "selectors": {
    "span[id^=doc-] + h1": {
      "type": "Guide",
      "regexp": "¶$",
      "replacement": ""
    },
    "span[id^=class-] + h1": {
      "type": "Class",
      "regexp": "¶$",
      "replacement": ""
    },
    ".section#signals > ul[id^=class-] > li > strong:first-of-type": "Event",
    ".section#enumerations > p[id^=class-] > strong:first-of-type": "Enum",
    ".section#enumerations > p[id^=class-] + ul > li > strong:first-of-type": "Value",
    ".section#constants > ul[id^=class-] > li > strong:first-of-type": "Constant",
    ".section#method-descriptions > ul[id^=class-] > li > strong:first-of-type": "Method",
    ".section#property-descriptions > ul[id^=class-] > li > strong:first-of-type": "Property"
  },
  "ignore": [
    "@C#¶"
  ]
}
```

- Run `dashing build` to create docset.
