cvxpy Docset
=======================

Ben Dichter (https://github.com/bendichter)

## To generate

```
git clone https://github.com/cvxgrp/cvxpy.git
cd cvxpy/doc
```
Using python 2:

```
make html
```

Download all of the externally hosted notebooks and convert to html:

```python
import os
from glob import glob
import re
import urllib.request
from requests import get
import bs4 as soup
from tqdm import tqdm
            
html_dir = '.../cvxpy/doc/build/html'
nbv_addresses = []
names = []
for filename in glob(os.path.join(html_dir, '**/*.html'), recursive=True):
    with open(filename, 'r') as content_file:
        content = content_file.read()
    nbv_inds = [m.start() for m in re.finditer('http://nbviewer.ipython.org', content)]
    content_out = content
    if nbv_inds:
        for nbv_ind in tqdm(nbv_inds, desc='downloading and converting notebooks from ' + filename):
            nbv_address = content[nbv_ind:content.find('"', nbv_ind)]
            
            dest = os.path.split(filename)[0]
            name = nbv_address[nbv_address.rfind('/') + 1:]
            nb_fname = name.replace('.ipynb','.html')
            
            # download notebook
            dl_address = nbv_address.replace('nbviewer.ipython.org/github', 'raw.githubusercontent.com')
            dl_address = dl_address.replace('blob/','')
            response = get(dl_address)
                
            # write ipnb file
            nb_fullpath = os.path.join(dest, name)
            with open(nb_fullpath, "wb") as file:
                file.write(response.content)
            
            #convert notebook
            os.system('jupyter nbconvert --to html -y --output-dir ' + dest + ' ' + nb_fullpath)
            os.remove(nb_fullpath)
            
            content_out = content_out.replace(nbv_address, nb_fname)
        
        # write file with new paths
        with open(filename, 'w') as content_file:
            content_file.write(content_out)
```
in terminal:

```
doc2dash -n cvxpy html
```

And then go through and remove "CVXPY DOCUMENTATION" for all of the titles.

## Known bugs:
* I couldn't get the index page to work.
