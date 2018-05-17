Julia Docset
=======================

This is a Dash docset for Julia (version 0.7 nightly, pre-alpha)

Assembled by: [cormullion](https://github.com/cormullion)

To generate this, you can run this Julia script:

```julia
# a Julia script to output a Dash (kapeli.com) docset of the Julia HTML documentation
#   It uses the JavaScript search index of the HTML docs to build the SQLite index
#   Set these and run:

tempworkingdir = "/tmp"
docset = "Julia"
sourcedir = "/Applications/Julia-0.7.app/Contents/Resources/julia/share/doc/julia/html/en/"
bundlename = "Julia"

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

using SQLite

# 1 Create docset folder and structure in $(tempworkingdir):

    if !isdir("$(tempworkingdir)/$(docset).docset")
        mkdir("$(tempworkingdir)/$(docset).docset")
    end

    cd("$(tempworkingdir)/$(docset).docset")

    if !isdir("Contents/Resources/Documents/")
        mkpath("Contents/Resources/Documents/")
    end

    cd("Contents/Resources/Documents/")

# 2 Copy the Julia HTML Documentation:

    run(`cp -R $sourcedir .`)

# 3 Create the Info.plist file:

    cd("$(tempworkingdir)/$(docset).docset/Contents/")
    let
        bundleidentifier = "$(docset)"
        bundlename = "$bundlename"
        docsetplatformfamily = "julia" # what is this?
        infoplist = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
    	<key>CFBundleIdentifier</key>
    	   <string>$(bundleidentifier)</string>
    	<key>CFBundleName</key>
    	   <string>$(bundlename)</string>
    	<key>DocSetPlatformFamily</key>
    	   <string>$(docsetplatformfamily)</string>
    	<key>isDashDocset</key>
    	   <true/>
        <key>isJavaScriptEnabled</key>
            <true/>
        <key>DashDocSetFallbackURL</key>
            <string>https://docs.julialang.org/en/latest/</string>
        <key>dashIndexFilePath</key>
            <string>index.html</string>
    </dict>
    </plist>"""

    open("Info.plist", "w") do f
    	    write(f, infoplist)
    	end
    end #let

# 4 Create the SQLite Index

    cd("$(tempworkingdir)/$(docset).docset/Contents/Resources")
    if isfile("docSet.dsidx")
        rm("docSet.dsidx")
    end
    db = SQLite.DB("docSet.dsidx")
    SQLite.query(db, "CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT)")
    SQLite.query(db, "CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path)")

# 5 Populate the SQLite Index

    sourcefile = "$(tempworkingdir)/$(docset).docset/Contents/Resources/Documents/search_index.js"
    f = open(sourcefile)
    fcontents = readlines(f)
    close(f)

    function sqlanitize(s)
        s = replace(s, "\\'", "''") # replace a single quote with two
        s = replace(s, "\\\"", "\"") # don't need to escape double quote now
        return s
    end

    counter = 1
    location = page = title = category = ""
    for l in fcontents
        ln = replace(l, r"^\s+", "")
        if startswith(ln, "\"location\"")
            # regex upto and including ",", for nested quotations
            location = replace(ln, r"\"location\": \"(.*?)\",.*$", s"\1")
        elseif startswith(ln, "\"page\"")
            page = replace(ln, r"\"page\": \"(.*?)\",.*$", s"\1")
        elseif startswith(ln, "\"title\"")
            title = replace(ln, r"\"title\": \"(.*?)\",.*$", s"\1")
        elseif startswith(ln, "\"category\"")
            category = replace(ln, r"\"category\": \"(.*?)\",.*$", s"\1")
        elseif startswith(ln, "\"text\"")
            println(outputfile, "  $counter $location $page $title $category")
            # not sure what to do about pages and sections. For now, include both as 'sections', mark the titles of pages with ":"
            if category == "page"
                category = "section"
                title = "[" * lpad(string(counter), 4) * "]¶ " * title
            elseif category == "section"
                title = "[" * lpad(string(counter), 4) * "]  " * title
            end
            # sometimes titles are empty
            if title == ""
                title = section
            end
            category = titlecase(category)

            SQLite.query(db, "INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('$(sqlanitize(title))', '$(sqlanitize(category))', '$(sqlanitize(location))')")
            location = page = title = category = ""
            counter += 1
            counter % 200 == 0 && println("... done $counter elements ...")
         end
    end

# 6 add icon

  run(`cp $(@__DIR__)/icon.png "$(tempworkingdir)/$(docset).docset/icon.png"`)

# That's all folks!
```

