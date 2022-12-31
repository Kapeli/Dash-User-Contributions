PyTorch-Geometric Docset
=======================

### Docset Description:

- [PyTorch-Geometric](https://pytorch-geometric.readthedocs.io/en/latest/) is a geometric deep learning extension library for [PyTorch](http://pytorch.org/).

### How to create:

1.  Follow description of [main documentation page](https://github.com/rusty1s/pytorch_geometric/tree/master/docs) create the original docs.
2.  Using [doc2dash](https://github.com/hynek/doc2dash) to create the docset.
    ```shell
    doc2dash --icon ./html/icon@2x.png --name Pytorch-Geometric ./html
    ```
3. Modify the `Info.plist` file to change the `DocSetPlatformFamily` key.
    ```xml
	<key>DocSetPlatformFamily</key>
	<string>pyg</string>
    ```

### Contributions:

#### Docset for Pytorch-Geometric 1.7.0
- Created by [Seungjae Jung](https://github.com/seanexplode)

#### Docset for Pytorch-Geometric 2.2.0
- Created by [Dark-Existed](https://github.com/Dark-Existed)