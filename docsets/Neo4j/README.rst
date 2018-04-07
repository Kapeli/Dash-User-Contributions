Neo4j Docset
============

Author: http://github.com/guglielmo

Instructions 
------------

The steps needed to generate this docset.

1. clone the github/neo4j repository
2. cd into manual, and build the docs (java + maven required)::

    mvn clean install -DdocsBuild -e

3. cd into `manual/target/docbkx/webhelp/`
4. remove the `javadoc` directory, as we won't need it (yet)
5. use dashing (https://github.com/technosophos/dashing) to build the docset (go required)::

    dashing create
    > edit dashing.json (see below) 
    dashing build

6. the neo4j.docset 

The `dashing.json` file contains these instructions::

    {
        "name": "Neo4j",
        "package": "neo4j",
        "index": "index.html",
        "selectors": {
            "h1.title": "Guide",
            "h2.title": "Section"
        },
        "ignore": [
            "ABOUT"
        ],
        "icon32x32": "common/images/icon.png",
        "allowJS": true,
        "ExternalURL": ""
    }

Bugs
----

mvn build may complain about some dependencies, see https://github.com/neo4j/neo4j/tree/3.1/manual

