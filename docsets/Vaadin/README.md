Vaadin Framework Docset for Dash
================================

Reference documentation for use with [Dash](http://kapeli.com/dash), an API Documentation Browser by [@kapeli](https://twitter.com/kapeli)

## About Vaadin

> Vaadin: thinking of U and I

> Vaadin is a Java framework for building modern web applications that look great, perform well and make you and your users happy.

Visit [https://vaadin.com/]() for more information about the project.

This is a compilation of the Javadoc API documentation available for download from Vaadin's website.

## About this Docset

This Dash docset was compiled by [Eric W. Wallace](https://twitter.com/ewall) and is available on [Github](https://github.com/ewall/Dash-User-Contributions/tree/master/docsets/Vaadin).

### Available Versions

* 8.20.3
* 8.20.2
* 8.20.1
* 8.20.0
* 8.19.0
* 8.18.0
* 8.17.0
* 8.16.1
* 8.16.0
* 8.15.1
* 8.15.0
* 8.14.3
* 8.14.2
* 8.14.1
* 8.14.0
* 8.13.3
* 8.13.2
* 8.13.1
* 8.13.0
* 8.12.4
* 8.12.3
* 8.12.2
* 8.12.1
* 8.12.0
* 8.11.3
* 8.11.2
* 8.11.1
* 8.11.0
* 8.10.5
* 8.10.4
* 8.10.3
* 8.10.2
* 8.10.1
* 8.10.0
* 8.9.4
* 8.9.3
* 8.9.2
* 8.9.1
* 8.9.0
* 8.8.6
* 8.8.5
* 8.8.3
* 8.8.2
* 8.8.1
* 8.8.0
* 8.7.2
* 8.7.1
* 8.7.0
* 8.6.4
* 8.6.3
* 8.6.2
* 8.6.0
* 8.5.2
* 8.5.1
* 8.5.0
* 8.4.5
* 8.4.4
* 8.4.3
* 8.4.2
* 8.4.1
* 8.4.0
* 8.3.3
* 8.3.2
* 8.3.1
* 8.1.4
* 8.1.3
* 8.1.2
* 8.1.1
* 8.1.0
* 8.0.7
* 8.0.6
* 8.0.5
* 8.0.3
* 8.0.2
* 8.0.1
* 8.0.0
* 7.7.7
* 7.7.6
* 7.7.5
* 7.7.4
* 7.7.3
* 7.7.2
* 7.7.1
* 7.7.0
* 7.6.8
* 7.6.7
* 7.6.6
* 7.6.5
* 7.6.4
* 7.6.3
* 7.6.2
* 7.6.1
* 7.6.0
* 7.5.10
* 7.5.9
* 7.5.8
* 7.4.8
* 7.3.10
* 6.8.15

### Generating this Docset

1. Download Javadoc jar for the latest Vaadin release from [https://vaadin.com/releases](), and extract the files.
2. Use [javadocset](https://github.com/Kapeli/javadocset) to compile the Docset, e.g. `./javadocset Vaadin <path to extracted Javadoc folder>`
3. Add the icon and enable JavaScript per [these instructions](http://kapeli.com/docsets).
4. Test the new docset in Dash to ensure it's working as expected.
5. Wrap up the files with `tar --exclude='.DS_Store' -cvzf Vaadin.tgz Vaadin.docset`, create version folder, and move the archive into it.
6. Don't forget to update `docset.json` and `README.md` files!
