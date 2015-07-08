# /bin/sh
# download & create docset
# require wget, pup

NAME=CypherReference
VERSION=stable

# create dir
rm -rf ${NAME}.docset/
mkdir -p ${NAME}.docset/Contents/Resources/Documents/

# download
wget -r -p -nv -nH -np -k --cut-dirs=3 -q \
	-P ${NAME}.docset/Contents/Resources/Documents/ \
	http://neo4j.com/docs/${VERSION}/cypher-refcard/

# create info.plist
cat << EOF > ${NAME}.docset/Contents/Info.plist 
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleIdentifier</key>
	<string>cypher</string>
	<key>CFBundleName</key>
	<string>Cypher Reference</string>
	<key>DocSetPlatformFamily</key>
	<string>cypher</string>
	<key>isDashDocset</key>
	<true/>
	<key>dashIndexFilePath</key>
	<string>index.html</string>
</dict>
</plist>
EOF

# create index
SQL="""
CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);
CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);
"""

## extract keywords
#pup "th a text{}" < ${NAME}.docset/Contents/Resources/Documents/index.html > words
#
## make SQL
#cat words | xargs -n1 -I_ echo "INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ('alles', '_', 'index.html');" > sql

# write one entry into it
sqlite3 --cmd "$SQL" ${NAME}.docset/Contents/Resources/docSet.dsidx <<EOF
INSERT OR IGNORE INTO searchIndex(name, type, path) \
  VALUES ('Cypher Reference Card', 'Guide', 'index.html');
EOF

# create tgz
tar -cvzf ${NAME}.tgz ${NAME}.docset/

# cleanup
rm -rf ${NAME}.docset/
