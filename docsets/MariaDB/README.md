# MariaDB Docset

This is a copy of the [MariaDB KnowledgeBase](https://mariadb.com/kb/en/), 
which serves as the documentation of MariaDB server, connectors and plugins. 
It is a living documentation and includes changes introduced for various MariaDB
versions. The data was fetch on 2025-05-23.

The MariaDB KnowledgeBase and it's various pages are usually licensed
under two licenses:

- The Creative Commons Attribution/ShareAlike 3.0 Unported license
(CC-BY-SA). 
- The Gnu FDL license (GFDL or FDL)

I refer you to the online version to get detailed information about the
license of the individual pages.

The Docset was generated with a website downloader and then generated
with Dash's Docset generator. The JavaScript for the generation is:

```js
const pageTitle = $("h1").text();
dashDoc.addEntry({name: pageTitle, type: "Guide"});

$('#top-nav').remove();
$('#sidebar-first').remove();
$('#navbar-bottom').remove();
$('footer').remove();
$('#comments').remove();
$('#subscribe').remove();
$('#backtotop').remove();
$('#subheader1').remove();
$('#content_disclaimer').remove();
$('h2:contains("Comments")').remove();
$('div.simple_section_nav').remove();

$("h2").each(function() {
    const entryName = $(this).text();
    
    var entryHash = $(this).attr('id');
    if(!entryHash)
    {
        entryHash = entryName.replace(/\W/g, '');
        $(this).attr('id', entryHash);
    }
    
    if (entryName !== 'Comments') {
        dashDoc.addEntry({name: entryName, type: "Section", hash: entryHash});
    }
});
```

Entries added to the `Info.plist` are:

```xml
<key>DashDocSetPlayURL</key>
<string>https://codapi.org/mariadb/</string>
<key>DashIndexFilePath</key>
<string>/en/library/index.html</string>
<key>DashDocSetFallbackURL</key>
<string>https://mariadb.com/kb/en/</string>
```

The Docset configuration is included in this repository.

For the purpose of usability, various unnecessary elements from the
pages have been removed (mostly navigation, sidebars etc). Those are not
needed as Dash provides excellent navigation facilities.

I tried to make sure that all links are local; however, there are
links to MariaDB's bug tracker and other websites (mysql.com) on various
pages, which have not been included in this Docset.

### Contact

This author of this Docset is [Louis Brauer](https://github.com/louis77). 
The copyright for the content of the Docset lies with the authors of the individual 
pages, MariaDB Foundation and/or MariaDB Corporation. I'm not affiliated with any of
those parties.
