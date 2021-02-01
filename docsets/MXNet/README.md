MXNet Docset
=======================

- Docset Description:
    - [MXNet](http://mxnet.readthedocs.io) is a deep learning framework designed for both efficiency and flexibility.

- Author:
    - [Jie Yang](https://github.com/yangj1e)

- Instructions to generate the docset:
    - build MXNet:
        follow [instructions](http://mxnet.readthedocs.io/en/latest/how_to/build.html#build-mxnet-library)
    - [make html](https://github.com/dmlc/mxnet/tree/master/docs):
        - `cd docs && make html`
    - generate docset:
        - `doc2dash -v -n MXNet _build/html/`
    - set [Online Redirection](https://kapeli.com/docsets#onlineRedirection) in Info.plist:
        - `DashDocSetFallbackURL: http://mxnet.readthedocs.io/en/latest/`
    - (optional) enable [JavaScript](https://kapeli.com/docsets#enableJavascript) in Info.plist:
        - `isJavaScriptEnabled: true`
    - [add icon](http://kapeli.com/docsets#addingicon).
