Zabbix 2.2 Docset
=======================

# Zabbix 2.2 Docset creation
Here are the steps used to generate and test this docset.

First, let's install some packages from brew:
```bash
brew install fdupes bash wget
```

Open https://www.zabbix.com/documentation in your browser (tested in chrome), open developer console and run the following script:
```JavaScript
dTreeNodes = document.getElementsByClassName('dTreeNode');
for (var i=0; i<dTreeNodes.length; i++)
{
    links=dTreeNodes[i].getElementsByTagName('a');
    if (links.length == 2)
        {
            console.log(links[0].href);
            links[0].click();
        }
}
```
You should now see the directory structure on the left completely unfolded. Save the page. Go to the directory you used to save the page in terminal and run the following command:
```bash
python -m SimpleHTTPServer
```
Now you should be able to open http://127.0.0.1:8000/ in you browser.

Open another terminal window or tab and wget the documentation. Assume you've used the documentation_unfolded.html name in the previous step.
```bash
d=documentation; time wget -P docset_prepare -rc -l 10 -p -E -k -H -nc -D www.zabbix.com --include $d/2.2/,$d/lib,$d/_media,$d/_export,$d/_detail http://127.0.0.1:8000/documentation_unfolded.html
```
It should take about 27 minutes and about 350 MB of your disk space.

Let's keep only the printed versions of html files:
```bash
find ./docset_prepare/www.zabbix.com/documentation/2.2/ -type f -not -name "*export_html.html" -exec rm '{}' \;
```

And rename them to .html:
```bash
find ./docset_prepare/www.zabbix.com/documentation/2.2/ -type f -name "*export_html.html"| while read file; do mv -v "${file}" "${file%\?*}.html"; done
```

We've told wget not to add '.1' suffixes to any files but it did for some of them (if there's a folder and a file with the same name and the folder is downloaded first and that's wget adding a file extension, the file will have a suffix). So for these files we now have invalid links, let's fix:
```bash
grep -rl '\.1\.html' docset_prepare/|while read file; do sed -i '' 's/.1.html/.html/g' "$file"; done
```

And there're some links for printed versions inside, let's update them:
```bash
find ./docset_prepare/www.zabbix.com/documentation/2.2/ -type f -name "*.html"| while read file; do sed -i '' 's/%3Fdo=export_html//g' "$file"; done
```

Generate the docset:
```bash
docset=zabbix
rm -rf $docset.docset
mkdir -vp $docset.docset/Contents/Resources/Documents/
cp -rp docset_prepare/www.zabbix.com/documentation/* $docset.docset/Contents/Resources/Documents/
tee $docset.docset/Contents/Info.plist<<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleIdentifier</key>
    <string>$docset</string>
    <key>CFBundleName</key>
    <string>$(bash -c "d=$docset; echo \${d^*}")</string>
    <key>DocSetPlatformFamily</key>
    <string>$docset</string>
    <key>isDashDocset</key>
    <true/>
</dict>
</plist>
EOF

touch $docset.docset/Contents/Resources/docSet.dsidx
pushd $docset.docset/Contents/Resources/Documents
sqlite3 ../docSet.dsidx "DROP TABLE IF EXISTS searchIndex;"
sqlite3 ../docSet.dsidx "CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);"
sqlite3 ../docSet.dsidx "CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);"

find 2.2 -name *.html| {
    while read file
    do
        filename=${file##*/}
        path=${file%/$filename}
        name=${path##*/}:${filename%.html}
        name="$(echo $path|tr '/' ':'|sed 's/2.2://'):${filename%.html}"
        name=${name/2.2:/}
        echo $name
        sqlite3 ../docSet.dsidx "INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('$name', 'func', '$file');"
    done
}

sqlite3 ../docSet.dsidx "select * from searchIndex where id < 3;"
popd
```

Let's replace duplicated files with symlinks:
```bash
pushd $docset.docset/Contents/Resources/Documents
# let's count how much space we could free by deduping
fdupes -1 -r ./|{ s=0; while read file files; do n=$(echo $files|tr ' ' '\n'|wc -l); s=$(( $s + ( $(ls -la "$file" |awk {'print $5'}) ) * n )); p="$((s / 1024)) KB"; printf "\b\b\b\b\b\b\b\b\b\b$p"; done; echo ""; echo "$(echo "scale=4; $s / 1024/1024"|bc) MB";  }

fdupes -1 -r ./|{
    s=0
    while read file files
    do
        fname="${file##*/}"
        fpath="${file%/$fname}"
        # echo "$fpath"
        i=0; farr=''; for pathc in ${fpath//\// }; do farr[$((i++))]=$pathc; done
        #echo "${farr[4]}"
        fdepth=$(($i-1))
        for dup in $files
        do
            dname="${dup##*/}"
            dpath="${dup%/$dname}"
            if test "$dpath" == "$fpath"
                then
                link="$fname"
            else
                i=0; darr=''; for pathc in ${dpath//\// }; do darr[$((i++))]=$pathc; done
                ddepth=$(($i-1))
                test $ddepth -gt $fdepth && li=$ddepth || li=$fdepth 
                # compare path components:
                si=0
                for i in $(seq 0 $li)
                do
                    # echo "$i ${farr[i]} ${darr[i]}"
                    si=$i
                    test "${darr[i]}" == "${farr[i]}" || break
                done
                rdpath=$( seq -f '' -s '../' $si $ddepth)
                rfpath=$(for i in $( seq $si $fdepth); do printf "${farr[i]}/"; done)
                link="$rdpath$rfpath$fname"
            fi
            rm -v "$dup"
            ln -vs "$link" "$dup"
        done
    done
}

# check for dups once again:
fdupes -1 -r ./
popd
```

Now let's create an icon. If you have 32x32 png (you'll find it in this repo), name it as logo.png and run the following commands:
```bash
sips -Z 32 logo.png --out icon@2x.png
sips -Z 16 logo.png --out icon.png
tiffutil -cathidpicheck icon.png icon@2x.png -out icon.tiff
rm -v icon@2x.png icon.png
cp -v icon.tiff zabbix.2.2.docset/icon.png
```

Your docset should be ready now!

# Preparing zabbix documentation for offline usage
As dash doesn't support tree structures you might want to use the native documentation. So save the page in a way described earlier, run an http server in it and wget the documentation:
```bash
time wget -P manual_wget_unfolded -rc -l 1 -p -E -k -H -nc -D www.zabbix.com --include documentation/2.2,documentation/lib http://127.0.0.1:8000/documentation_unfolded.html
```
And we should also download some additional images that were hidden from wget by javascript variables:
```bash
mkdir -vp manual_wget_unfolded/www.zabbix.com/documentation/lib/plugins/indexmenu/images/default/
for img in base empty folderh folderhopen folderopen join joinbottom line minus minusbottom page plus plusbottom folder
do
    wget -cq -P manual_wget_unfolded/www.zabbix.com/documentation/lib/plugins/indexmenu/images/default/ www.zabbix.com/documentation/lib/plugins/indexmenu/images/default/$img.gif
done
```

Now stop the http server, change directory to manual_wget_unfolded/www.zabbix.com and run it here. You should now be able to browse zabbix 2.2 documentation at http://127.0.0.1:8000/.

# Bash script to create an SQLite index based on html files and there paths
If you are working on your own docset and got confused with sqlite database steps you might find the following instructions useful. This script creates an index, it will just put all the html files into the database using path components separated by ‘:' as names:
```
docset=STM32
touch $docset.docset/Contents/Resources/docSet.dsidx
pushd $docset.docset/Contents/Resources/Documents
sqlite3 ../docSet.dsidx "DROP TABLE IF EXISTS searchIndex;"
sqlite3 ../docSet.dsidx "CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);"
sqlite3 ../docSet.dsidx "CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);”

find . -name *.html| {
    while read file
    do
        file=${file/.\//}
        filename=${file##*/}
        path=${file%/$filename}
        name=${path##*/}:${filename%.html}
        name="$(echo $path|tr '/' ':'):${filename%.html}"
        echo "$name $file"
        sqlite3 ../docSet.dsidx "INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('$name', 'func', '$file');"
    done
}

sqlite3 ../docSet.dsidx "select * from searchIndex where id < 3;”
popd
```