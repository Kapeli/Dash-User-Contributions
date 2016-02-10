# Crystal Docset

Documentation for the [Crystal Language](http://crystal-lang.org/) as a [Dash](http://kapeli.com/dash) docset.

**Author:** [Chris F. Ravenscroft](https://github.com/fusion)

## Limitations

Many, I am sure. The main one being that the api pages use the same CSS to define 
class and modules so everyting ends up clumped under "classes."

## How to generate the docset

This is the script file I use to generate this docset, including salient comments:

    #!/bin/bash
    
    # 1. Run a site capture such as SiteSucker or a glorious Curl command.
    #    (Select parent directory as target)
    # 2. Capture everything under http://crystal-lang.org/docs/
    #    (SiteSucker will also pull in /api/...if not do it youself)
    # 3. Edit the variable below to point to your forked docset repository
    # 4. Then run this script
    TARGET=/Volumes/Fasty/Projects/CRYSTAL/Dash-User-Contributions/docsets/Crystal
    
    dashing build crystal-lang
    
    DB=crystal.docset/Contents/Resources/docSet.dsidx
    newlined=$(echo "select id from searchIndex where name like '%
    %';" | sqlite3 $DB)
    for id in $newlined; do
        name=$(echo "select name from searchIndex where id=${id};" | sqlite3 $DB)
        newname=$(echo $name | awk '{ print $1 }')
        echo "update searchIndex set name='${newname}' where id=${id};" | sqlite3 $DB
    done
    
    sed  -ibck -e 's/https*\:\/\/crystal-lang.org\///g' \
        crystal.docset/Contents/Resources/Documents/api/index.html && \
        rm -f crystal.docset/Contents/Resources/Documents/api/index.htmlbck
    
    tar --exclude='.DS_Store' -cvzf Crystal.tgz crystal.docset
    mv Crystal.tgz "$TARGET/"
    cp crystallogo16x16.png "$TARGET/icon.png"
    cp crystallogo32x32.png "$TARGET/icon@2x.png"

And this is my dashing.json profile:

    {
        "name": "Crystal",
        "package": "crystal",
        "index": "index.html",
        "selectors": {
            "h1.type-name": { 
                "type": "Class",
                "regexp": "(^.*class |^.*module |^.*struct |^.*alias )",
                "replacement": ""
            },
            "div.signature": { 
                "type": "Method",
                "regexp": "(^.*def |\\s*abstract\\s*|[\\r\\n#])",
                "replacement": ""
            },
            "dt.entry-const": { 
                "type": "Constant",
                "regexp": "(=.+)",
                "replacement": ""
            },
            "section.normal > h1": { 
                "type": "Guide"
            }
        },
        "ignore": [
            "ABOUT"
        ],
        "icon16x16": "crystallogo16x16.png",
        "icon32x32": "crystallogo32x32.png",
        "allowJS": true,
        "ExternalURL": "http://crystal-lang.org/api/"
    }
