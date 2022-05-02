# dash-docset-swift-language-guide

A Bash script to generate a [Dash docset](https://github.com/Kapeli/Dash-User-Contributions) for the [Swift language guide](https://docs.swift.org/swift-book/LanguageGuide/TheBasics.html). Includes a table of contents.

Install directly from Dash, or build from source.

## Building from Source

1. If you’re using macOS 12.3.1, the only requirement is `wget` (`brew install wget`).
2. `git clone https://github.com/roeybiran/dash-docset-swift-language-guide`
3. `cd dash-docset-swift-language-guide && ./main.sh`.

### Artifacts

- `.build` should contain the `.docset` bundle.
- `.dist` should contain the compressed docset along with some required assets.
