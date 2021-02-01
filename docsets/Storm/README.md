Storm
=======================

* [Andrew Jorgensen](https://github.com/ajorgensen) ([@ajorgensen](https://twitter.com/ajorgensen))

## Docset Generation ##

1. Clone the javadocset generation [repository](git@github.com:Kapeli/javadocset.git): ```git clone git@github.com:Kapeli/javadocset.git```

2. Download the appropriate source from [apache storm](http://storm.incubator.apache.org/downloads.html)

3. Unzip the downloaded tarball and cd into the directory

4. Run maven javadoc command ```mvn javadocs:javadocs```

5. Generate the docset (syntax is javadocset <docset name> <javadoc api folder>): ```javadocset storm ./storm-core/target/site/apidocs```
