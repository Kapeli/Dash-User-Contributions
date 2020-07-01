[Apache Beam](https://beam.apache.org/) Docset
=======================

Author: [Dmytro Sadovnychyi](https://github.com/sadovnychyi)

Generation steps:

## Icon
```bash
wget https://beam.apache.org/images/logos/full-color/nameless/beam-logo-full-color-nameless-100.png
convert beam-logo-full-color-nameless-100.png -resize 16x16 icon.png
convert beam-logo-full-color-nameless-100.png -resize 32x32 icon@2x.png
rm beam-logo-full-color-nameless-100.png
```

## Docset
```bash
git clone https://github.com/apache/beam.git --depth=1
pip install -e beam/sdks/python
pip intall doc2dash
# Replace sphinx_rtd_theme so we can hide sidebar and footer.
sed -i -e "s/html_theme = 'sphinx_rtd_theme'/html_theme = 'alabaster'; html_theme_options = {'nosidebar': True}; html_show_copyright = False; html_show_sphinx = False/" beam/sdks/python/scripts/generate_pydoc.sh
(cd beam/sdks/python && scripts/generate_pydoc.sh)
doc2dash beam/sdks/python/target/docs/_build --name="Apache Beam Python" --index-page=index.html --force --icon=icon.png
rm -rf beam
```

## Publishing
```bash
tar --exclude='.DS_Store' -cvzf Apache_Beam_Python.tgz "Apache Beam Python.docset"
```
