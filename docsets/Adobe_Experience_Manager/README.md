Adobe Experience Manager Docset
=======================

This docset is maintained by Ignacio Bergmann (https://github.com/nachocual). It was generated from the javadocs hosted by Adobe.

How it was generated:
* Download the index-all from the online documentation using wget:
 `wget http://docs.adobe.com/docs/en/aem/6-1/ref/javadoc/index-all.html --page-requisites`
* Clean it up as it is probably pretty broken and the docset generation tool will have trouble parsing it. I used the `tidy` command for this
* Now that the index-all is in good shape, download the rest of the documentation using wget: `wget --no-parent --recursive --level=0 --page-requisites --no-clobber --reject-regex='index.html\?(.*)' http://docs.adobe.com/docs/en/aem/6-1/ref/javadoc/`
* Create the docset using the `javadocset` tool
* The docset will be missing the JCR API documentation which is pretty useful, so it order to add it download the javadoc JAR from http://search.maven.org/#artifactdetails%7Cjavax.jcr%7Cjcr%7C2.0%7Cjar and expand in using the unzip command
* Create a JCR docset using the `javadocset` tool
* Inside the `Documents` folder of your AEM docset, create a folder called `jcr` and copy all the JCR javadoc html files in it.
* Connect to your AEM docset's database
* In the sql console, attach the JCR docset's database `attach '/path/to/JCR.docset/Contents/Resources/docSet.dsidx' as jcr;`
* Add all the entries from the JCR docset to the AEM one `Add the entries from the JCR docset:
"insert into searchIndex(name, type, path) select name, type, 'jcr/' || path from jcr.searchIndex;`
* Clean up the titles of all the html files, removing the name of the library so it follows the docset guidelines
