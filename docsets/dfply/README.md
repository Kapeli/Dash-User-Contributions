dfply docset
============

Author: Tony Duan, GitHub: [@tonyduan](http://github.com/tonyduan).

Library: [dfply](https://github.com/kieferk/dfply) by Kiefer Katovich, GitHub: [@kieferk](https://github.com/kieferk).

Generation: First convert the original repository's documentation from Markdown to HTML. The CSS theme is Sidre Sorhus' [GitHub markdown CSS](https://github.com/sindresorhus/github-markdown-css).

`pandoc --from markdown --to html --css theme.css --ascii README.md --output docs.html --standalone --metadata title="dfply documentation"`

Then create the SQLite database `docSet.dsidx` by running the SQL in this Gist: [dfply-dash-docset.sql](https://gist.github.com/tonyduan/8a41d115c5822fef8d3a84c8ece8011c). Note that I manually wrote this SQL from version 0.3.2 of the dfply documentation.
