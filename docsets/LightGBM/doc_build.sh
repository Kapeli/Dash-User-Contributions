#!/bin/bash

git clone https://github.com/microsoft/LightGBM.git
python3 -m venv build_lgbm_docs
source $(pwd)/build_lgbm_docs/bin/activate
pip install -r LightGBM/docs/requirements_base.txt
(
 cd LightGBM/docs &&
 export C_API=NO || set C_API=NO &&
 make -j $(nproc) html
)
pip install doc2dash
doc2dash -n LightGBM -i $(pwd)/icon.png -A LightGBM/docs/_build/html
deactivate
rm -rf build_lgbm_docs
rm -rf LightGBM
