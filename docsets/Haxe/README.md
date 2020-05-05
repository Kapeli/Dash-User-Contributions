Haxe Docset
=======================

[Haxe](http://haxe.org/) API docset for [Dash](http://kapeli.com/dash).

By [Dmitrii Maganov](https://github.com/vonagam).

Instructions how to reproduce the build (using version 4.0.5 as an example):

- Install [Dashing](https://github.com/technosophos/dashing) (`brew install dashing` on mac).

- Download documentation files from https://github.com/HaxeFoundation/api.haxe.org/tree/gh-pages/v/4.0.5

- Move into documentation folder.

- Optionally copy provided here `icon@2x.png`.

- Run this to setup selectors for dashing:

```bash
htmls=$(find . -name '*.html')
sed -i '' -E 's|(<h3 class="section">([^<]+)</h3><div) (class="fields">)|\1 data-type="\2" \3|g' $htmls
sed -i '' -E 's|(<h1)(><small>([^<]+)</small>)|\1 data-type="\3"\2|g' $htmls
```

- Create `dashing.json`:

```json
{
  "name": "Haxe",
  "package": "haxe",
  "index":"index.html",
  "icon32x32": "icon@2x.png",
  "allowJS": true,
  "ExternalURL": "https://api.haxe.org/v/4.0.5",
  "selectors": {
    "h1[data-type='class']": {
      "type": "Class",
      "regexp": "^class ",
      "replacement": ""
    },
    "h1[data-type='abstract']": {
      "type": "Class",
      "regexp": "^abstract ",
      "replacement": ""
    },
    "h1[data-type='enum']": {
      "type": "Enum",
      "regexp": "^enum ",
      "replacement": ""
    },
    "h1[data-type='interface']": {
      "type": "Interface",
      "regexp": "^interface ",
      "replacement": ""
    },
    "h1[data-type='package']": {
      "type": "Package",
      "regexp": "^package ",
      "replacement": ""
    },
    "h1[data-type='typedef']": {
      "type": "Type",
      "regexp": "^typedef ",
      "replacement": ""
    },
    "h3 + .fields[data-type='Constructor'] .identifier": "Constructor",
    "h3 + .fields[data-type='Variables'] .identifier": "Variable",
    "h3 + .fields[data-type='Static variables'] .identifier": "Variable",
    "h3 + .fields[data-type='Methods'] .identifier": "Method",
    "h3 + .fields[data-type='Static methods'] .identifier": "Method",
    "h3 + .fields[data-type='Fields'] .identifier": "Field",
    "h3 + .fields[data-type='Values'] .identifier": "Value"
  }
}
```

- Run `dashing build` to create docset.
