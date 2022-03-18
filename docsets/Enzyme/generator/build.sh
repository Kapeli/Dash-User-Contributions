#!/usr/bin/env bash

SCRIPT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_PATH="$( dirname "${SCRIPT_PATH}" )/"
ENZYME_REPO_PATH=${ROOT_PATH}enzyme/
BUILT_DOCS_PATH=${ENZYME_REPO_PATH}_book/

# Clone the enzyme repo to build the docs
git clone git@github.com:airbnb/enzyme.git && cd enzyme

# Install enzyme's dependancies
npm install

# For some reason simply installing gitbook isn't enough.
# We have to manuall go and install it's dependancies
# Seems to be an issue with the version of gitbook-cli that enzyme uses.
# For now, we trigger `docs:prepare` which will install gitbook
# And we expect it to fail, so we hide the output.
npm run docs:prepare > /dev/null
# And then manually install gitbook's dependancies
# Install the gitbook dependancies
for dir in ~/.gitbook/versions/*/ ; do
    cd $dir && npm install
done

# Back to our enzyme repo
cd ${ENZYME_REPO_PATH}

# Build the gitbook docs
npm run docs:build

# Copy our files for dashing to use
cp ${ROOT_PATH}generator/dashing.json ${ROOT_PATH}generator/enzyme.png ${BUILT_DOCS_PATH}

# Let's go to where we can build our docset
cd ${BUILT_DOCS_PATH}

# Build that sucker
dashing build

# Tar up our docset
tar -X ${ROOT_PATH}generator/tar-exclusions -cvzf Enzyme.docset.tgz Enzyme.docset

# Move our docset to our root
mv ${BUILT_DOCS_PATH}Enzyme.docset.tgz ${ROOT_PATH}

# Delete the enzyme repo and all the extra files that we created
rm -rf ${ENZYME_REPO_PATH}

# Uncomment this if you'd like it to also remove gitbook
# rm -rf ~/.gitbook/
