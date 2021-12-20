Optuna Docset
==================

## Docset description

- [Optuna](https://optuna.org/) is an automatic hyperparameter optimization software framework, particularly designed for machine learning.

## How to create docset
- The following scripts are executed on Github Actions. 
- See https://github.com/29Takuya/dash-docset-optuna/blob/main/.github/workflows/docset.yml for more information.

### Build document from source

```
# Python 3.7
git clone https://github.com/29Takuya/dash-docset-optuna.git && cd dash-docset-optuna
git clone https://github.com/optuna/optuna.git && cd optuna
pip install -U ".[document]"
cd docs && make html
cd ../..
```

### Convert to docset with doc2dash

```
# (optional) Switch to Python 3.8 to use the latest doc2dash release
pip install doc2dash
doc2dash \
  --name Optuna \
  --destination . \
  --force \
  --index-page index.html \
  --online-redirect-url https://optuna.readthedocs.io \
  ./optuna/docs/build/html
cp ./icon/*.png Optuna.docset/
tar --exclude='.DS_Store' -cvzf Optuna.tgz Optuna.docset
```

## Docset maintainer

- Takuya Shimada, https://github.com/29Takuya