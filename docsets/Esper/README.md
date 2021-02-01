# Esper Docset

Documentation for EsperTech's [Esper](http://www.espertech.com/products/esper.php).

**Author:** [fish748](https://github.com/fish748)

## How to generate the docset

1. Download and extract Esper source file [from here](http://dist.codehaus.org/esper/)
2. Generate the Javadoc using Eclipse.
3. Convert to docset using Kapeli's [javadocset](https://github.com/Kapeli/javadocset#readme) like this: 
```
./javadocset <any docset name you want> <path to Javadoc-generated API folder>
```
