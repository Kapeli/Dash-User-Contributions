import os
import sqlite3
import shutil
import subprocess
import urllib.parse
from bs4 import BeautifulSoup
import cairosvg

import os

homebrew_lib_dir = "/opt/homebrew/lib"
existing_lib_path = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = homebrew_lib_dir + ":" + existing_lib_path

DOCSET_NAME = "uv.docset"
DOCUMENTS_PATH = os.path.join(DOCSET_NAME, "Contents/Resources/Documents")
SQLITE_DB_PATH = os.path.join(DOCSET_NAME, "Contents/Resources/docSet.dsidx")
INFO_PLIST_PATH = os.path.join(DOCSET_NAME, "Contents/Info.plist")
DOWNLOAD_DIR = "downloaded_docs"
SOURCE_DOCS = os.path.join(DOWNLOAD_DIR, "uv")

def download_docs():
    """Download fresh documentation from docs.astral.sh/uv/"""
    print("Downloading documentation from https://docs.astral.sh/uv/...")
    
    # Clean up any existing download directory
    if os.path.exists(DOWNLOAD_DIR):
        shutil.rmtree(DOWNLOAD_DIR)
    
    # Use wget to mirror the entire uv documentation subdomain
    # -r: recursive
    # -np: don't ascend to parent directory
    # -k: convert links for local viewing
    # -p: download all page requisites (images, css, js)
    # -E: add .html extension to files without it
    # --adjust-extension: add proper extensions
    # --restrict-file-names=windows: avoid special characters in filenames
    # -nH: don't create host directory
    # --level=inf: infinite recursion depth
    # -P: prefix/directory to save to
    # -q: quiet mode (less verbose output)
    try:
        result = subprocess.run(
            [
                "wget",
                "-r",           # recursive download
                "-np",          # no parent
                "-k",           # convert links
                "-p",           # get page requisites
                "-E",           # add extensions
                "--adjust-extension",
                "--restrict-file-names=windows",
                "-nH",          # no host directory
                "--level=inf",  # infinite depth
                "-q",           # quiet mode
                "-P", DOWNLOAD_DIR,
                "https://docs.astral.sh/uv/"
            ],
            check=True,
            capture_output=True,
            text=True
        )
        print("Documentation downloaded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading documentation: {e}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        raise
    except FileNotFoundError:
        print("Error: wget not found. Please install wget:")
        print("  Ubuntu/Debian: sudo apt-get install wget")
        print("  macOS: brew install wget")
        raise

def setup_structure():
    if os.path.exists(DOCSET_NAME):
        shutil.rmtree(DOCSET_NAME)
    os.makedirs(DOCUMENTS_PATH)

def copy_docs():
    """Copy documentation from download directory and remove redirect pages"""
    for item in os.listdir(SOURCE_DOCS):
        s = os.path.join(SOURCE_DOCS, item)
        d = os.path.join(DOCUMENTS_PATH, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)
    
    # Remove redirect pages (these are HTML files that just redirect to another location)
    # When docs are freshly downloaded with wget, these won't exist because wget follows redirects
    # But we clean them up here in case any exist in the source
    redirect_files = []
    for root, dirs, files in os.walk(DOCUMENTS_PATH):
        for file in files:
            if file.endswith(".html"):
                abspath = os.path.join(root, file)
                try:
                    with open(abspath, "r") as f:
                        content = f.read(500)  # Read first 500 chars
                        if '<title>Redirecting...</title>' in content:
                            redirect_files.append(abspath)
                except Exception:
                    pass
    
    for redirect_file in redirect_files:
        relpath = os.path.relpath(redirect_file, DOCUMENTS_PATH)
        print(f"Removing redirect page: {relpath}")
        os.remove(redirect_file)

def create_plist():
    plist_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleIdentifier</key>
	<string>uv</string>
	<key>CFBundleName</key>
	<string>uv</string>
	<key>DocSetPlatformFamily</key>
	<string>uv</string>
	<key>isDashDocset</key>
	<true/>
	<key>dashIndexFilePath</key>
	<string>index.html</string>
    <key>DashDocSetFamily</key>
    <string>dashtoc</string>
    <key>isJavaScriptEnabled</key>
    <true/>
    <key>DashDocSetFallbackURL</key>
    <string>https://docs.astral.sh/uv/</string>
</dict>
</plist>
"""
    with open(INFO_PLIST_PATH, "w") as f:
        f.write(plist_content)

def index_docs():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cur = conn.cursor()
    cur.execute("CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);")
    cur.execute("CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);")

    for root, dirs, files in os.walk(DOCUMENTS_PATH):
        for file in files:
            if file.endswith(".html"):
                if file == "404.html":
                    continue

                abspath = os.path.join(root, file)
                relpath = os.path.relpath(abspath, DOCUMENTS_PATH)

                with open(abspath, "r") as f:
                    soup = BeautifulSoup(f, "html.parser")

                title_tag = soup.find("title")
                title = title_tag.get_text() if title_tag else relpath
                if title:
                    title = title.split("|")[0].strip()

                # Skip redirect pages (they have "Redirecting..." as title)
                if title == "Redirecting...":
                    print(f"Skipping redirect page: {relpath}")
                    continue

                # Determine the appropriate entry type based on the path
                # Reference and configuration pages are marked as 'Section'
                # All other pages (getting-started, concepts, guides, pip, etc.) default to 'Guide'
                entry_type = 'Guide'
                if relpath.startswith('reference/') or relpath.startswith('configuration/'):
                    entry_type = 'Section'
                
                cur.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?)", (title, entry_type, relpath))

                # Special handling for reference pages
                if "reference/cli" in relpath:
                    # Commands
                    for h in soup.find_all(['h2', 'h3']):
                        hid = h.get('id')
                        if hid and (hid.startswith('uv') or hid == 'cli-reference'):
                            if hid == 'cli-reference': continue
                            name = h.get_text().strip()
                            if not name: continue
                            path = f"{relpath}#{hid}"
                            cur.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?)", (name, 'Command', path))
                            add_dash_anchor(h, 'Command', name)

                elif "reference/settings" in relpath:
                    # Settings
                    for h in soup.find_all(['h3']):
                        hid = h.get('id')
                        if hid:
                            name = h.get_text().strip()
                            if not name: continue
                            path = f"{relpath}#{hid}"
                            cur.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?)", (name, 'Setting', path))
                            add_dash_anchor(h, 'Setting', name)

                elif "reference/environment" in relpath:
                    # Environment Variables
                    for h in soup.find_all(['h3']):
                        hid = h.get('id')
                        if hid and hid.startswith('uv_'):
                            name = h.get_text().strip()
                            if not name: continue
                            path = f"{relpath}#{hid}"
                            cur.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?, ?, ?)", (name, 'Environment', path))
                            add_dash_anchor(h, 'Environment', name)

                # General sections for TOC
                for h in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                    hid = h.get('id')
                    if hid and not h.find('a', class_='dashAnchor'):
                        name = h.get_text().strip()
                        if name:
                            add_dash_anchor(h, 'Section', name)

                with open(abspath, "w") as f:
                    f.write(str(soup))

    conn.commit()
    conn.close()

def add_dash_anchor(tag, type, name):
    # <a name="//apple_ref/cpp/Entry Type/Entry Name" class="dashAnchor"></a>
    safe_name = urllib.parse.quote(name, safe='')
    anchor_name = f"//apple_ref/cpp/{type}/{safe_name}"
    # Use BeautifulSoup to create the tag
    anchor = BeautifulSoup(f'<a name="{anchor_name}" class="dashAnchor"></a>', "html.parser").a
    tag.insert(0, anchor)

def apply_visual_refinements():
    css_path = os.path.join(DOCUMENTS_PATH, "stylesheets/extra.css")
    dash_css = """
/* Dash docset refinements */
.md-header,
.md-sidebar--primary,
.md-sidebar--secondary,
.md-footer,
.md-search {
  display: none !important;
}

.md-main__inner {
  margin-top: 0 !important;
}

.md-content {
  margin-left: 0 !important;
  margin-right: 0 !important;
}

.md-container {
  padding-top: 0 !important;
}

@media screen and (min-width: 76.25em) {
  .md-main {
    min-height: auto !important;
  }
}
"""
    if os.path.exists(css_path):
        # Check if the CSS has already been added to avoid duplication
        with open(css_path, "r") as f:
            existing_content = f.read()
        
        if "/* Dash docset refinements */" not in existing_content:
            with open(css_path, "a") as f:
                f.write(dash_css)
    else:
        # Fallback: inject into HTML files if extra.css is missing
        pass

def copy_icon():
    """Convert SVG logo to 200x200 PNG icon using cairosvg"""
    icon_svg = os.path.join(DOCUMENTS_PATH, "assets/logo-letter.svg")
    icon_dst = os.path.join(DOCSET_NAME, "icon.png")
    
    if os.path.exists(icon_svg):
        for output_size in [16, 32]:
            try:
                if output_size==32:
                    icon_dst = icon_dst[:-4]+"@2x.png"
                # Use cairosvg to convert SVG to PNG
                cairosvg.svg2png(
                    url=icon_svg,
                    write_to=icon_dst,
                    output_width=output_size,
                    output_height=output_size
                )
                print(f"Icon created from {icon_svg}")
            except Exception as e:
                print(f"Failed to convert icon: {e}")
    else:
        print(f"Warning: Icon source not found at {icon_svg}")

if __name__ == "__main__":
    print("Downloading fresh documentation...")
    download_docs()
    print("Setting up docset structure...")
    setup_structure()
    print("Copying documentation...")
    copy_docs()
    print("Creating Info.plist...")
    create_plist()
    print("Indexing documentation and adding anchors...")
    index_docs()
    print("Applying visual refinements...")
    apply_visual_refinements()
    print("Copying icon...")
    copy_icon()
    print("Done!")
