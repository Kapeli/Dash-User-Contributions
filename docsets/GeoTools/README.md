# GeoTools Docset

Documentation for [GeoTools](http://www.geotools.org) library as a [Dash](http://kapeli.com/dash) docset.

**Author:** [Stephen Rudolph](https://github.com/stephenrudolph)

## How to generate the docset

#### Prerequisites
* [javadocset](https://github.com/Kapeli/javadocset), to convert the Javadoc to a Dash docset.

#### Available Versions
* 30.0
* 29.2
* 28.5
* 27.5
* 26.7
* 25.7
* 24.7
* 23.5
* 22.5
* 21.5
* 20.5
* 19.4
* 18.5
* 17.5
* 16.5
* 15.4
* 14.5
* 13.6

#### Generating
1. Download the GeoTools API documentation from http://docs.geotools.org. 
2. Unzip the downloaded docs
3. Convert to a Dash docset using javadocset (from https://github.com/Kapeli/javadocset, you may have to remove the quarantine on javadocset with `xattr -rd com.apple.quarantine ./javadocset`)

    ```bash
    $ javadocset GeoTools apidocs
    ```
4. Compress the docset using tar

    ```bash
    $ tar --exclude='.DS_Store' -cvzf GeoTools.tgz GeoTools.docset
    ```

