Matrix
=======================

* Public page: https://docs.joinmastodon.org/
* Repository: https://github.com/mastodon/documentation

## Maintainers of the Dash Docset

* [Christian 'jaller94' Paul](https://chrpaul.de/about/)

## How to build

I'm building the Docset on GitLab CI. The files `.gitlab-ci.yml` and `generate.sh` contain most of the logic.

https://gitlab.com/jaller94/dash-mastodon-documentation/

### Manually
Requirements:

* Bash
* Hugo (static site generator)
* SQLite

```bash
git clone git@gitlab.com:jaller94/dash-mastodon-documentation.git
cd dash-matrix-spec
bash generate.sh
```

## Known issues

https://gitlab.com/jaller94/dash-mastodon-documentation/-/issues

## License of the Docset

The Mastodon Documentation is licensed under the GNU Free Documentation License. You can verify this information at https://github.com/mastodon/documentation/blob/master/LICENSE.
