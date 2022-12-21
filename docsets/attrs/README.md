# attrs

<https://www.attrs.org/>

Maintained by [Hynek Schlawack](https://github.com/hynek/).


## Building the Docset

### Requirements

- recent Python 3
- [*tox*](https://tox.wiki/)


### Building

1. Clone the [*attrs* repository](https://github.com/python-attrs/attrs).
2. Check out the tag you want to build.
3. `tox -e docset` will build the documentation and convert it into `attrs.docset` in one step.
