JUnit
=======================

* [Andrew Jorgensen](https://github.com/ajorgensen) ([@ajorgensen](https://twitter.com/ajorgensen))

## Docset Generation ##

1. Clone the javadocset generation [repository](git@github.com:Kapeli/javadocset.git): ```git clone git@github.com:Kapeli/javadocset.git```

2. Clone the JUnit repository on [github](https://github.com/junit-team/junit).

3. Run maven javadoc command ```mvn javadoc:javadoc```. NOTE: For older versions you will need to run ```ant javadoc```

5. Generate the docset (syntax is javadocset <docset name> <javadoc api folder>): ```javadocset junit ./target/site/apidocs```
