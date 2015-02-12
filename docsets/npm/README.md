# npm Docset

## Author

(note: I'm not the author of the npm documentation, I just generated the npm docset.)

#### François Massart

- Twitter: [@FrancoisMassart](https://twitter.com/FrancoisMassart)
- GitHub: [FrancoisMassart](https://github.com/FrancoisMassart)

## Building the Docset

Here is how I built the docset.
- I followed the [instructions](http://kapeli.com/docsets) on Kapeli website.
- I used [SiteSucker](http://ricks-apps.com/osx/sitesucker/index.html) to download the [docs.npmjs.com](https://docs.npmjs.com/)
- Then I opened my local copy of the html docs and I used jQuery snippets in Firefox's console to generate SQL queries like
```javascript
var str='';
$('#getting-started>.pageColumns>li>a').each(function(i,e) {
    str += "INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES ";
    str += "('Getting Started - "+$(e).text()+"', 'Guide', '"+$(e).attr('href')+"');\n";
});
console.log(str);
```
- I adapted each code to slightly change the title of the page or the type of index... (Guide, Command, etc.)
- Using the generated queries inside [SQLPro for SQLLite](http://sqlitepro.com) to create the file `docSet.dsidx` (renamed from the extension `.db`)
- Due to a bug of Dash with YouTube videos, I replaced the html markup of YouTube videos by links "Open in YouTube"

## Bugs & Enhancements

If you have problems with this documentation set, or you would like to suggest
improvements, feel free to contact me.

## Known Issues

- The Dash application currently does not allow embedded videos, I replaced them by regular links. This should be fixed in the next release of Dash.
