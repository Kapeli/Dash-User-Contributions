# dash-docset-swift-language-guide

Applicable to: **Swift 5.4**

[Dash docset](https://github.com/Kapeli/Dash-User-Contributions) generation script for the [Swift Language Guide](https://docs.swift.org/swift-book/LanguageGuide/).

This script will fetch the documentation from the Swift homepage, prepare it for Dash, and put everything in a `.build` folder in the same directory the script has been executed in.

## Features

- Includes entries for each 'chapter' and its sub-sections.
- Tables of contents for sub-sections.

## Dependencies

- Python 3.8+. Should be provided by your Mac if you're running Catalina or newer.
- [html5lib](https://pypi.org/project/html5lib/) (`pip3 install html5lib`)
- [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/) (`pip3 install beautifulsoup4`)
- [wget](https://www.gnu.org/software/wget/) (`brew install wget`)

## Issues

- The "On This Page" jump menu as originally seen in the Swift website has been hidden due to some visual glitches it was causing. The Dash table of contents should offer a similar functionality.