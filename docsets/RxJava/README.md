RxJava Docset
=======================

## How I generate this docset

1. Download and unzip the original `javadoc.jar` from [maven](http://search.maven.org/#search%7Cga%7C1%7Cio.reactivex.rxjava)
2. [Generate](https://github.com/Kapeli/javadocset) a `.docset` package from it
3. Run this [script](offline-images) (with [NodeJS](https://nodejs.org)) to download and replace all images for offline usage

    ```sh
    node offline-images RxJava.docset
    ```

4. Follow the rest of the steps [here](https://github.com/Kapeli/Dash-User-Contributions#contribute-a-new-docset)
5. Done
