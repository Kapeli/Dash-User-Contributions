Geb
=======================

Documentation for [Geb](http://www.gebish.org) library as a [Dash](http://kapeli.com/dash) docset. 

**Author:** [Patrick Double](https://github.com/double16)

## How to generate the docset

#### Prerequisites
* [homebrew](https://brew.sh), to install dependencies

#### Available Versions
* 2.1

#### Generating
1. Clone https://github.com/double16/geb-dash-docset.git
2. Convert to a Dash docset by running `./generate.sh`

    ```bash
    $ ./generate.sh
    ```
3. Docsets will be in `build/manual/{version}`
4. Compress the docset using tar

    ```bash
    $ tar --exclude='.DS_Store' -cvzf Geb.tgz build/manual/2.1/Geb.docset
    ```
