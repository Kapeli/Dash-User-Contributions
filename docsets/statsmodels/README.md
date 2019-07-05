statsmodels Docset
=======================

_statsmodels_ Docset


 - Author: Angelo Varlotta (http://github.com/capac/)
 - Documentation: downloaded from https://github.com/statsmodels/statsmodels and contained in the docs/ folder

General installation procedure:

```python
git clone https://github.com/statsmodels/statsmodels.git
cd statsmodels/docs
make html
```

To generate the documentation, you will need to download the packages in the `requirements.txt` file. The documentation build generates many warning messages about documents "not included in any toctree":

```bash
file_name.rst: WARNING: document isn't included in any toctree
```

To the best of my knowledge this doesn't seem to effect the dcumentation generation, but likely warrants a inquiry into the matter.