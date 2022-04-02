[Deno](https://deno.land) API Docset
=======================

Author: Yuto Oguchi([@aiotter](https://github.com/aiotter))

## Contents
* [Deno API (stable)](https://doc.deno.land/deno/stable)
* [Deno API (unstable)](https://doc.deno.land/deno/unstable)

## Generation steps
```bash
# Generate docset for newest available deno
$ deno run --allow-net --allow-write=deno.docset --allow-read=. --no-check "https://raw.githubusercontent.com/aiotter/deno_api_docset/master/main.ts"

# Generate docset for deno 1.20.2
$ deno run --allow-net --allow-write=deno.docset --allow-read=. --no-check "https://raw.githubusercontent.com/aiotter/deno_api_docset/master/main.ts" v1.20.2
```

## Docset versioning
`Deno version`+`deno_api_docset hash`
(e.g. `1.20.2+702568c`)

Follow Semantic Versioning.
Set the build identifier to a SHA-1 hash of the commit of deno_api_docset you used.

## Bug reports
Please report bugs at <https://github.com/aiotter/deno_api_docset>
