# Odin docset

[Odin](https://odin-lang.org/) programming language, the data-oriented language for sane software development.


## Author

[Daniel Margarido](https://github.com/drmargarido)


## Generate docset

1. Install Dependencies
```sh
pip3 install bs4
pip3 install lxml
```

2. Run the following scripts from this [repository](https://github.com/drmargarido/odin-docset)
```sh
bash download_pkgs_docs.sh
python3 generate_odin_docset.py
```

## Notes

* The odin version is the current `<year>.<month>.0`
