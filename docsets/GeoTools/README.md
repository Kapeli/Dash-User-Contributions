# GeoTools Docset

Documentation for [GeoTools](http://www.geotools.org) library as a [Dash](http://kapeli.com/dash) docset.

**Author:** [Stephen Rudolph](https://github.com/stephenrudolph)

## How to generate the docset

#### Prerequisites
* [javadocset](https://github.com/Kapeli/javadocset), to convert the Javadoc to a Dash docset.

#### Available Versions
<<<<<<< HEAD
* 23.0
=======
* 24.1
* 24.0
* 23.3
* 23.2
* 23.1
* 23.0
* 22.5
* 22.4
>>>>>>> daee4539969911937fd29e266d25f0735f5452d3
* 22.3
* 22.2
* 22.1
* 22.0
* 21.5
* 21.4
* 21.3
* 21.2
* 21.1
* 21.0
* 20.5
* 20.4
* 20.3
* 20.2
* 20.1
* 20.0
* 19.4
* 19.3
* 19.2
* 19.1
* 19.0
* 18.5
* 18.4
* 18.3
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
2. Unzip the downloaded docs
3. Convert to a Dash docset using javadocset (from https://github.com/Kapeli/javadocset, you may have to remove the quarantine on javadocset with `xattr -rd com.apple.quarantine ./javadocset`)

    ```bash
    $ javadocset GeoTools apidocs
    ```
4. Compress the docset using tar

    ```bash
    $ tar --exclude='.DS_Store' -cvzf GeoTools.tgz GeoTools.docset
    ```

