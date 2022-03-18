GraphQL Specification Docset
============================


Docset author: [Leonid Shevtsov](https://leonid.shevtsov.me) / [@leonid-shevtsov](https://github.com/leonid-shevtsov)

Specification author: Facebook.

The online and up-to-date source for this docset is found at http://facebook.github.io/graphql/.

## Build script

Create these two files in a folder. Run `ruby build.rb`.

### build.rb

Requirements: Ruby, [Nokogiri](https://rubygems.org/gems/nokogiri), curl, ImageMagick, [Dashing](https://github.com/technosophos/dashing).

``` ruby
require 'nokogiri'

`curl http://facebook.github.io/graphql/ -o index.html`
`curl -O http://facebook.github.io/graphql/spec.css`
`curl -O http://facebook.github.io/graphql/highlight.css`
`curl -L https://github.com/facebook/graphql/raw/master/resources/GraphQL%20Logo.png >icon.png`
`convert icon.png -resize 32x32 icon.png`

doc = Nokogiri::HTML(File.read('index.html'))

doc.css('.spec-sidebar').remove
doc.css('.spec-sidebar-toggle').remove

File.open('index.html', 'w') { |f| f.puts doc.to_html }

`dashing build`

`tar --exclude='.DS_Store' -cvzf graphql.tgz graphql.docset`
```

### dashing.json

``` json
{
    "name": "GraphQL Specification",
    "package": "graphql",
    "index": "index.html",
    "selectors": {
        "h2": {
          "type": "Guide",
          "regexp": "([A-Z0-9.][0-9.]*)(.*)",
          "replacement": "$1 $2"
        },
        "h3": {
          "type": "Section",
          "regexp": "([A-Z0-9.][0-9.]*)(.*)",
          "replacement": "$1 $2"
        }
    },
    "icon32x32": "icon.png"
}
```
