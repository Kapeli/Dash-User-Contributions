Triton Language DocSet
=======================

Docset for the [Triton Launguage](https://triton-lang.org/main/index.html).

## Contributor
[@Zhenhuan Liu](https://github.com/Victarry)

### How to build:
1. Clone the repo
```
git clone https://github.com/triton-lang/triton.git
```
2. Install dependancies
```
pip3 install tabulate cmake sphinx matplotlib myst_parser sphinx-rtd-theme pandas pytest sphinx-gallery sphinx-multiversion
```
3. Build docs
```
cd docs
make html && doc2dash -n triton _build/html/main
```
