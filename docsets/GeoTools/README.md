# GeoTools Docset

Documentation for [GeoTools](http://www.geotools.org) library as a [Dash](http://kapeli.com/dash) docset.

**Author:** [Stephen Rudolph](https://github.com/stephenrudolph)

## How to generate the docset

#### Prerequisites
* [javadocset](https://github.com/Kapeli/javadocset), to convert the Javadoc to a Dash docset.

#### Generating
1. Download the GeoTools API documentation from http://docs.geotools.org. 
2. Convert to a Dash docset using javadocset

    ```bash
    $ javadocset GeoTools apidocs
    ```
