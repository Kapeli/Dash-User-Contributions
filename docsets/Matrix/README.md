Matrix
=======================

* Public page: https://spec.matrix.org/
* Repository: https://github.com/matrix-org/matrix-spec

## Maintainers of the Dash Docset

* [Christian 'jaller94' Paul](https://chrpaul.de/about/)

## How to build

I'm building the Docset on GitLab CI. The files `.gitlab-ci.yml` and `generate.sh` contain most of the logic.

https://gitlab.com/jaller94/dash-matrix-spec/

### Manually
Requirements:

* Bash
* Hugo (static site generator)
* SQLite

```bash
git clone git@gitlab.com:jaller94/dash-matrix-spec.git
cd dash-matrix-spec
bash generate.sh
```

## Known issues

https://gitlab.com/jaller94/dash-matrix-spec/-/issues

## License of the Docset

The Matrix specification is licensed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0). You can verify this information at https://spec.matrix.org/latest/#license or https://github.com/matrix-org/matrix-spec/blob/main/LICENSE.
