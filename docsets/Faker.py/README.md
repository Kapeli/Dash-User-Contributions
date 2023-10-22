# Faker Docset

[Faker](https://github.com/joke2k/faker) is a Python package that generates fake data for you. Whether you need to bootstrap your database, create good-looking XML documents, fill-in your persistence to stress test it, or anonymize data taken from a production service, Faker is for you.

Faker is heavily inspired by PHP Faker, Perl Faker, and by Ruby Faker.

## Author

- [Xavier Yang](https://github.com/ivaquero)

## How to build:

- Install doc2dash

```bash
pip install doc2dash
# or
conda install doc2dash
```

- Download the lastest document from https://github.com/joke2k/faker
- Unpack the downloaded archive
- Install doc-building packages selectively according to `docs/conf.py`
- Edit `docs/conf.py` and replace corresponding sections with the following

```python
extensions = ['autoapi.extension']
autoapi_dirs = ["../../faker-master"]

html_theme = "alabaster"

html_theme_options = dict(
    logo_only=True,
    nosidebar=True,
)
```

- Execute the command

```bash
cd faker-master/docs && make file
rm -rf faker-master/docs/html/_sources
doc2dash -v -n Faker -I _build/html/index.html _build/html
tar cvzf Faker.tgz Faker.docset
```
