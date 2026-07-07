# uv Dash Docset Generator

This script generates a [Dash](https://kapeli.com/dash) docset for the [uv](https://github.com/astral-sh/uv) package manager.

### Install Dependencies

Install `cairo`, `wget`, `libffi` and `python` with Homebrew. We need to use python installed by Homebrew [to access native libraries](https://gist.github.com/matangover/a34c31f7c832a6896795fc842ef26a1e).

```fish
# Install dependencies
brew install cairo libffi python wget
python3 -m venv .
source bin/activate
pip3 install requirements.txt
```

## Usage

Simply run the script to generate a fresh docset:

```fish
python3 generate_docset.py
```

The script will:
1. Download the latest documentation from docs.astral.sh/uv/
2. Create the docset structure
3. Copy and process the documentation
4. Remove redirect pages
5. Index all documentation with proper types
6. Apply visual refinements
7. Generate the icon

The generated docset will be in the `uv.docset` directory. Almost all the code was written by Google Jules and Claude Code. 
