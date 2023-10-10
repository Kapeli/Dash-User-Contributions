Blender Docset
=======================

Author:
* Yue Gao
    * [Github](https://www.github.com/hologerry)
    * [Website](https://yuegao.me)


* Alex Widener
    * [Github](https://www.github.com/alexwidener)
    * [Website](https://alexwidener.com)

Generating docsets for Blender in the future:

* Prerequisite:
[doc2dash](https://github.com/hynek/doc2dash/ "doc2dash")

    ```shell
    pip install doc2dash
    ```

* Blender documentation is generated through Sphinx.
* Clone the Blender Manual repo [blender-manual](https://projects.blender.org/blender/blender-manual.git)
* Make the html docs
    ```shell
    make
    ```
* Convert to docset
    ```shell
    doc2dash -n Blender build/html
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
