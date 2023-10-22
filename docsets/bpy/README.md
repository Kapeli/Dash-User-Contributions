Blender Python API Docset
=======================

Author:
* Yue Gao
    * [Github](https://www.github.com/hologerry)
    * [Website](https://yuegao.me)


Generating docsets for Blender in the future:

* Prerequisite:
[doc2dash](https://github.com/hynek/doc2dash/ "doc2dash")
    ```shell
    pip install doc2dash
    ```
* Blender binary is required to generate the docs [Blender](https://www.blender.org/download/ "Blender")
* Blender documentation is generated through Sphinx
* Download the Blender Manual repo
* Install Sphinx and the ReadTheDocs theme
    ```shell
    pip install sphinx sphinx-rtd-theme
    ```
* Install Sphinx and the ReadTheDocs theme
    ```shell
    pip install sphinx sphinx-rtd-theme
    ```
* Run this script from Blender's root path once you have compiled Blender
    ```shell
    blender --background --factory-startup -noaudio -python doc/python_api/sphinx_doc_gen.py
    ```
    This will generate python files in doc/python_api/sphinx-in/
    providing `blender` is or Links to the blender executable
* Generate html docs
    ```shell
    sphinx-build doc/python_api/sphinx-in doc/python_api/sphinx-out
    ```
* Convert to docset
    ```shell
    doc2dash -n bpy doc/python_api/sphinx-out
    ```
* Edit the fallback URL in the `Info.plist` to point to the Blender Manual
    ```shell
    <key>dashIndexFilePath</key>
    <string>index.html</string>
    <key>DashDocSetFallbackURL</key>
    <string>https://docs.blender.org/api/current/index.html</string>
    ```
* Convert to .tgz
    ```shell
    tar --exclude='.DS_Store' -cvzf bpy.tgz bpy.docset
    ```
* That's all!
