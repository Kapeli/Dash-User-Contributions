# Guava Docset

Documentation for Google's [Guava](https://code.google.com/p/guava-libraries/) library as a [Dash](http://kapeli.com/dash) docset.

**Author:** [Dylan Scott](https://github.com/dylanscott)

## How to generate the docset

#### Prerequisites
* [Apache Maven](http://maven.apache.org/), to generate the Javadoc
* [javadocset](https://github.com/Kapeli/javadocset), to convert the Javadoc to a Dash docset.

#### Generating
1. Clone and navigate to the Guava repository

    ```bash
    $ git clone https://code.google.com/p/guava-libraries/
    $ cd guava-libraries
    ```

2. Checkout the desired revision/tag.
3. Generate the Javadoc using Maven.

    ```bash
    $ mvn javadoc:javadoc
    ```

4. Convert to a Dash docset using javadocset

    ```bash
    $ javadocset Guava guava/target/site/apidocs
    ```
