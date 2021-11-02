# dash-docset-swift-language-guide

Applicable to Swift version **5.5**.

A Bash script to generate a [Dash docset](https://github.com/Kapeli/Dash-User-Contributions) for the [Swift language guide](https://docs.swift.org/swift-book/LanguageGuide/). Includes a table of contents.

Install directly from Dash, or build from source.

## Building from Source

1. The only external dependency is [wget](https://www.gnu.org/software/wget/) (`brew install wget`). Other utilities used in the script are already available to you if you’re running a recent version of macOS.
2. Clone this repo.
3. `cd` to the project's root and run `./main.sh`. The script will fetch the documentation from the [Swift language guide’s](https://docs.swift.org/swift-book/LanguageGuide/) homepage, and prepare it for Dash.
4. Inside ./.build you'll find the docset bundle, ready to be added to Dash.
5. Plus, ./.dist will now contain what’s needed to publish the docset to Dash — the compressed docset bundle along with some required assets.
