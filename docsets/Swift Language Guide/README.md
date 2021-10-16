# dash-docset-swift-language-guide

Applicable to Swift version **5.5**.

[Dash docset](https://github.com/Kapeli/Dash-User-Contributions) generation script for the [Swift language guide](https://docs.swift.org/swift-book/LanguageGuide/). Includes a table of contents.

Install directly from Dash, or build from source.

## Building from Source

1. The only dependency is [wget](https://www.gnu.org/software/wget/) (`brew install wget`). Other utilities used in the script should be available if you’re running a recent version of macOS.
2. Clone this repo.
3. Run ./main.sh, the script will fetch the documentation from the Swift homepage, prepare it for Dash.
4. The ./build folder should now contain the docset bundle, ready to be added to Dash. Additionally, an archived version of the docset (along with the files necessary to distribution) will be produced.
