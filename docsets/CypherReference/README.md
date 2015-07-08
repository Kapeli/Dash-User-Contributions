Cypher Reference Card
=====================

This docset is created by Jelle Herold

- github/[`wires`](https://github.com/wires)
- twitter/[`statebox`](https://twitter.com/statebox)

The documentation is downloaded from neoj4.com using `wget`.

	wget -r -p -nv -nc -nH -np -k --cut-dirs=3 \
          -P cypher-refcard-stable \
          http://neo4j.com/docs/stable/cypher-refcard/

For more info look at [`mkDocset.sh`](mkDocset.sh).

There is currently only one entry in the search index, this could be improved.
For instance, we can extract some keywords from the html using `pup`.

	pup "th a text{}" < index.html
