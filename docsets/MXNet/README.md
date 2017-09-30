MXNet Docset
=======================
- This docset refers greatly to the one made by Yang Jie (https://github.com/yangj1e)

- Docset Description:
    - [MXNet](https://mxnet.incubator.apache.org)(incubating) is a deep learning framework designed for both efficiency and flexibility. It allows you to mix symbolic and imperative programming to maximize efficiency and productivity. At its core, MXNet contains a dynamic dependency scheduler that automatically parallelizes both symbolic and imperative operations on the fly. A graph optimization layer on top of that makes symbolic execution fast and memory efficient. MXNet is portable and lightweight, scaling effectively to multiple GPUs and multiple machines.

MXNet is also more than a deep learning project. It is also a collection of blue prints and guidelines for building deep learning systems, and interesting insights of DL systems for hackers.

- Author:
    - [Yafeng Zhou](https://github.com/yafz)

- Instructions to generate the docset:
    - build MXNet doc:
        follow [instructions](https://github.com/apache/incubator-mxnet/tree/master/docs)
    - generate docset:
        - `doc2dash -v -n MXNet _build/html/`
    - enable [JavaScript](https://kapeli.com/docsets#enableJavascript) in Info.plist:
        - `isJavaScriptEnabled: true`
    - [add icon](http://kapeli.com/docsets#addingicon).
