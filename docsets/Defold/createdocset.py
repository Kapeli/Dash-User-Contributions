#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sqlite3
import shutil
import urllib
import json
import zipfile
from subprocess import call

INFO_PLIST = """<!DOCTYPE plist SYSTEM "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
<key>CFBundleIdentifier</key>
<string>defold</string>
<key>CFBundleName</key>
<string>Defold</string>
<key>DocSetPlatformFamily</key>
<string>defold</string>
<key>isDashDocset</key>
<true/>
<key>dashIndexFilePath</key>
<string>index.html</string>
<key>DashDocSetFamily</key>
<string>dashtoc</string>
</dict>
</plist>
"""

DOCSET_JSON = """{{
    "name": "Defold",
    "version": "{0}",
    "archive": "Defold.tgz",
    "author": {{
        "name": "Bjorn Ritzl",
        "link": "https://github.com/britzl"
    }},
    "aliases": [],
    "specific_versions": []
}}"""

# path definitions
docset_path = "defold.docset"
contents_path = os.path.join(docset_path, "Contents")
resources_path = os.path.join(contents_path, "Resources")
documents_path = os.path.join(resources_path, "Documents")
ref_path = os.path.join(documents_path, "ref")


DOC_ZIP = "ref-doc.zip"
JSON_PATH = "json"


def get_defold_sha1():
    info_url = "http://d.defold.com/stable/info.json"
    info_file = urllib.urlopen(info_url)
    info = json.loads(info_file.read())
    info_file.close()
    return info["sha1"]


def get_defold_version():
    info_url = "http://d.defold.com/stable/info.json"
    info_file = urllib.urlopen(info_url)
    info = json.loads(info_file.read())
    info_file.close()
    return info["version"]


def get_ref_doc():
    print("Downloading ref-doc.zip")
    sha1 = get_defold_sha1()
    if os.path.exists(DOC_ZIP):
        os.remove(DOC_ZIP)
    urllib.urlretrieve("http://d.defold.com/archive/" + sha1 + "/engine/share/ref-doc.zip", DOC_ZIP)


def cleanup():
    print("Performing cleanup")
    if os.path.exists(JSON_PATH):
        shutil.rmtree(JSON_PATH)
    if os.path.exists(DOC_ZIP):
        os.remove(DOC_ZIP)


def unzip_ref_doc():
    print("Unpacking ref-doc.zip")
    if os.path.exists(JSON_PATH):
        shutil.rmtree(JSON_PATH)

    with zipfile.ZipFile(DOC_ZIP) as zf:
        zf.extractall(JSON_PATH)


def convert_hrefs(s):
    return s.replace("<a href=\"/", "<a href=\"http://www.defold.com/")


def create_docset():
    print("Creating docset")
    # remove old docset
    if os.path.exists(docset_path):
        shutil.rmtree(docset_path)

    # create all paths
    if os.path.exists(ref_path):
        shutil.rmtree(ref_path)
    os.makedirs(ref_path)

    # create Info.plist
    with open(os.path.join(contents_path, "Info.plist"), "w") as file:
        file.write(INFO_PLIST)

    # copy icon
    shutil.copyfile("icon.png", os.path.join(docset_path, "icon.png"))

    # copy css
    shutil.copyfile("defold.css", os.path.join(documents_path, "defold.css"))

    # create sqlite db
    with sqlite3.connect(os.path.join(resources_path, "docSet.dsidx")) as db:
        cursor = db.cursor()

        try: cursor.execute('DROP TABLE searchIndex;')
        except: pass

        # create db table
        cursor.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
        # make sure duplicates are ignored
        # cursor.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

        index_html = ""
        for root, dir, files in os.walk(JSON_PATH):
            for file in files:
                with open(os.path.join(root, file), "r") as fh:
                    if file.endswith(".json"):
                        print("  Parsing " + file)
                        class_name = file.replace("_doc.json", "")
                        class_path = class_name + ".html"
                        class_doc = ""
                        parsed_json = json.load(fh)
                        info = parsed_json["info"]
                        class_doc = class_doc + "<h1>" + info["name"] + "</h1>\n"
                        class_doc = class_doc + "<p>" + info["description"] + "</p>\n"
                        index_html = index_html + "<a class='index' href='ref/" + class_path + "'>" + class_name + "</a>" + info["brief"] + "</br>"
                        for element in parsed_json["elements"]:
                            function_name = element["name"]
                            if function_name != "":
                                entry_type = "Function"
                                if element["type"] == "VARIABLE":
                                    entry_type = "Variable"
                                elif element["type"] == "MESSAGE":
                                    entry_type = "Command"
                                elif element["type"] == "PROPERTY":
                                    entry_type = "Property"
                                elif element["type"] == "MACRO":
                                    entry_type = "Macro"
                                elif element["type"] == "TYPEDEF":
                                    entry_type = "Type"
                                elif element["type"] == "ENUM":
                                    entry_type = "Enum"

                                function_path = class_path + "#" + function_name
                                class_doc = class_doc + "<h1><a name='//apple_ref/cpp/" + entry_type + "/" + function_name + "' class='dashAnchor'></a><a class='entry' name='" + function_name + "'>" + function_name + ("()" if entry_type == "Function" else "") + "</a></h1>"
                                class_doc = class_doc + "<div class='brief'>" + element["brief"] + "</div>"
                                if element.get("description", "") != "":
                                    class_doc = class_doc + "<p>" + element["description"] + "</p>"
                                if element.get("note", "") != "":
                                    class_doc = class_doc + "<p>Note: " + element["note"] + "</p>"
                                if len(element["parameters"]) > 0:
                                    class_doc = class_doc + "<h3>PARAMETERS</h3>"
                                    class_doc = class_doc + "<div class='params'>"
                                    for parameter in element["parameters"]:
                                        class_doc = class_doc + "<p class='param'>" + parameter["name"] + " - " + parameter["doc"] + "</p>"
                                    class_doc = class_doc + "</div>"
                                if len(element["members"]) > 0:
                                    class_doc = class_doc + "<h3>MEMBERS</h3>"
                                    class_doc = class_doc + "<div class='params'>"
                                    for member in element["members"]:
                                        class_doc = class_doc + "<p class='param'>" + member["name"] + " - " + member["doc"] + "</p>"
                                    class_doc = class_doc + "</div>"
                                if len(element["returnvalues"]) > 0:
                                    class_doc = class_doc + "<h3>RETURN</h3>"
                                    class_doc = class_doc + "<div class='return'>"
                                    for returnvalue in element["returnvalues"]:
                                        class_doc = class_doc + "<p>" + returnvalue["name"] + " - " + returnvalue["doc"] + "</p>"
                                    class_doc = class_doc + "</div>"
                                if element.get("examples", "") != "":
                                    class_doc = class_doc + "<h3>EXAMPLES</h3>"
                                    class_doc = class_doc + "<div class='examples'>"
                                    class_doc = class_doc + "<p>" + element["examples"] + "</p>"
                                    class_doc = class_doc + "</div>"

                                class_doc = class_doc + "<hr/>"
                                cursor.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (function_name, entry_type, "ref/" + function_path))

                        with open(os.path.join(ref_path, class_path), "w") as out:
                            out.write("<html><head><link rel='stylesheet' type='text/css' href='../defold.css'></head><body>")
                            out.write(convert_hrefs(class_doc))
                            out.write("</body></html>")

                        cursor.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (class_name, 'Module', "ref/" + class_path))

        with open(os.path.join(documents_path, "index.html"), "w") as out:
            out.write("<html><head><link rel='stylesheet' type='text/css' href='defold.css'></head>")
            out.write("<body><p>Welcome to the documentation for <a href='http://www.defold.com'>Defold</a>, the free game engine by <a href='http://www.king.com'>King</a>.</p>")
            out.write(index_html)
            out.write("</body></html>")


def archive_docset():
    print("Creating Defold.tgz")
    if os.path.exists("Defold.tgz"):
        os.remove("Defold.tgz")

    call(["tar", "--exclude='.DS_Store'", "-cvzf", "Defold.tgz", docset_path])
    shutil.rmtree(docset_path)

    print("Creating docset.json")
    with open("docset.json", "w") as out:
        out.write(DOCSET_JSON.format(get_defold_version()))


get_ref_doc()
unzip_ref_doc()
create_docset()
archive_docset()
cleanup()
print("Done!")
