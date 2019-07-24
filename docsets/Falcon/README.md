# Falcon Docset

## Project Information:
- Author: Falcon Maintainers (https://github.com/falconry)
- Homepage: https://github.com/falconry/falcon
- Issue Tracker: https://github.com/falconry/falcon/issues

## Prerequisites:
- Python 3.7

## Instructions:
- Clone Falcon Repository: `git clone https://github.com/falconry/falcon.git`
- Switch to desired branch: `git checkout <version_branch>`
- Install tox `pip install tox`
- Run tox job to generate the documentation and package `tox -e dash`
- The generated docs will be located in `./dash/`
