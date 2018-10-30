lxml Dash Docset
=======================

#### Docset Description

[lxml](http://lxml.de/) is the most feature-rich and easy-to-use library for processing XML and HTML in the Python language.

Also check out its [github](https://github.com/lxml/lxml) repo.

#### Generation Steps

Building lxml docset with `doc2dash` is impossible because it couldn't be recognized as a known documentation format. Here is the method to build it manually:

1. Compile the documentation from [source](https://github.com/lxml/lxml), or just scrape it from [lxml website](http://lxml.de/) if you're as lazy as me([laggardkernel](https://github.com/laggardkernel)).
    - Note: Only website files, api folder and s5 folder should be used later. You don't want a docset containing all the old versions and released packages.
2. Make a docset folder with correct structure. See [Docset Generation Guide](https://kapeli.com/docsets) if you don't know what I'm saying.
    - No need to populate the SQLite index cause there's nothing we can do with it.

```
# an example
 ❯ tree lxml.docset
lxml.docset
├── Contents
│   ├── Info.plist
│   └── Resources
│       ├── Documents
│       └── docSet.dsidx
└── icon.png
```

3. Copy the documentation files into `lxml.docset/Contents/Resources/Documents`.
4. Do [other things needed](https://github.com/Kapeli/Dash-User-Contributions/blob/master/README.md) before submitting a pull request.

#### Docset Makers
- [laggardkernel](https://github.com/laggardkernel): `4.2.5`
- [iamaziz](https://github.com/iamaziz): `3.4.1`
- [Aziz Alto](https://github.com/iamaziz): the creator of lxml
