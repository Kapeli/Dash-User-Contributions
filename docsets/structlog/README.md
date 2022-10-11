# structlog

Maintained by [Hynek Schlawack](https://github.com/hynek/).

<https://www.structlog.org/>


## Building the Docset

### Requirements

- Python 3.10
- [*tox*](https://tox.wiki/)


### Building

1. Clone the [*structlog* repository](https://github.com/hynek/structlog).
2. Check out the tag you want to build.
3. `tox -e docset` will build the documentation and convert it into `structlog.docset` in one step.
