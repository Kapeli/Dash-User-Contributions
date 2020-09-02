LightGBM Docset
=======================

#### Docset description:
- [LightGBM](https://lightgbm.readthedocs.io/en/latest/) is a python gradient boosting framework that uses tree based learning algorithms.


#### How to build updates:

- Try this at first:
    ```sh
    sudo chmod +x doc_build.sh
    ./doc_build.sh
    ```
- If it is not working for you, try to build it like in [tutorial](https://github.com/microsoft/LightGBM/tree/master/docs) and than use [doc2dash](https://doc2dash.readthedocs.io/en/stable/usage.html):
    ```sh
    doc2dash -n LightGBM -i icon.png -A LightGBM/docs/_build/html
    ```


#### Docset Author:
 - [Kindulov M.](https://github.com/b0nce)
