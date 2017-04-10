Chainer
=======================

This is a Dash Docset for [Chainer](http://chainer.org/), a deep learning framework.
This Docset is maintained by [mitmul](https://github.com/mitmul).

## How to craete the docset

- Clone Chainer repo (https://github.com/pfnet/chainer)
- Install Chainer (`python setup.py install`)
- Move to `docs` dir and `make html`
- Get the icon image from http://chainer.org/images/chainer_icon_red.png
- Run `doc2dash`: `doc2dash -n Chainer -i chainer_icon_red.png -j build/html`
