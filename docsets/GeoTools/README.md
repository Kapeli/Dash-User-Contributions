# GeoTools Docset

Documentation for [GeoTools](http://www.geotools.org) library as a [Dash](http://kapeli.com/dash) docset.

**Author:** [Stephen Rudolph](https://github.com/stephenrudolph)

## How to generate the docset

#### Prerequisites
* [javadocset](https://github.com/Kapeli/javadocset), to convert the Javadoc to a Dash docset.

#### Available Versions
* 19.0
* 18.2
* 18.1
* 18.0
* 17.5
* 17.4
* 17.3
* 17.2
* 17.1
* 17.0
* 16.5
* 16.4
* 16.3
* 16.2
* 16.1
* 16.0
* 15.4
* 15.3
* 15.2
* 15.1
* 15.0
* 14.5
* 14.4
* 14.3
* 14.2
* 14.1
* 14.0
* 13.6
* 13.5
* 13.4
* 13.3
* 13.2

#### Generating
1. Download the GeoTools API documentation from http://docs.geotools.org. 
2. Convert to a Dash docset using javadocset

    ```bash
    $ javadocset GeoTools apidocs
    ```
3. Compress the docset using tar

    ```bash
    $ tar --exclude='.DS_Store' -cvzf GeoTools.tgz GeoTools.docset
    ```

