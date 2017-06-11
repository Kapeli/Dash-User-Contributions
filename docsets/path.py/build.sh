#!env bash

# Automatically exit on error
set -e

VERSION="${1}"
REPO="https://github.com/jaraco/path.py.git"
WORK_DIR="${PWD}"
SRC_DIR="${WORK_DIR}/src/path.py"
BUILD_DIR="${WORK_DIR}/build"
DIST_DIR="${WORK_DIR}/dist"

# Sphinx needs this
THEME_PATH=$(python -c "import sphinx_readable_theme as theme; print(theme.__path__[0])")

# Prep the build and distribution directories
mkdir -p build dist src


echo "Building documentation for path.py"
echo ""


# Prepare the path.py source code


echo "Updating source repo…"

cd "${SRC_DIR}";

# Make sure we're in the master branch
git checkout -q master

# Update!
git pull -q --rebase origin master

# The version is optional
if [ -n "${VERSION}" ]; then
	git checkout -q --detach "${VERSION}"
fi

# Make sure we're using the version currently checked out
pip install -q -e .


# Generate the HTML documentanion


echo "Building HTML documentation…"

cd "${SRC_DIR}/docs"

# Use Sphinx to build the docs using the "readable" theme
sphinx-build -Q -a -E -D html_theme="readable" -D html_theme_path="${THEME_PATH}" . "${BUILD_DIR}"

# Return to the master branch
git checkout -q master


# Reformat the documentation


echo "Preparing documentation for docset conversion…"

cd "${BUILD_DIR}"

# Don't need any images
rm _static/*.png _static/*.gif

# Remove the search page
rm search.html searchindex.js
sed -i ".bkp" '/<li>.*Search Page.*<\/li>/d' *.html

# Get rid of javascript
sed -i ".bkp" '/<script .*<\/script>/d' *.html
rm _static/*.js

# Remove the sidebars
sed -i ".bkp" '/<div class="sphinxsidebar"/,/<div class="clearer"><\/div>/d' *.html

# Fix page titles
sed -i ".bkp" "s@<title>\(.*\) &mdash;.*</title>@<title>\1</title>@" *.html

# Use a fluid layout
cat >> _static/basic.css << EOF
body div.document, body div.bodywrapper, body div.documentwrapper {
	margin: 0;
  width: 100%;
	max-width: none;
	float: none;
}

body div.footer {
	box-sizing: border-box;
	width: 100%;
	margin: 20px 0 10px;
	padding: 0 10px;
}
EOF

# Remove the sed backups
rm *.bkp


# Generate the docset from the HTML documentation


echo "Generating docset…"

cd "${WORK_DIR}"

# Convert the documentation to a docset
doc2dash -q -f -n path.py -I api.html --destination "${DIST_DIR}" "${BUILD_DIR}"

# Create compressed archive
tar --exclude=".DS_Store" -C "${DIST_DIR}" -czf "${DIST_DIR}/path.py.tgz" path.py.docset


# Finish up


echo "Cleaning up…"

# Remove the build directory
rm -rf "${BUILD_DIR}"


# Success!


echo "Docset successfully generated in ${DIST_DIR}"
