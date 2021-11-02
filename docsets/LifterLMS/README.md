LifterLMS Dash Docset
=====================

Official docset for the [LifterLMS](https://lifterlms.com) WordPress plugin.

### Generate the Docset

1. Clone the docset repo from https://github.com/gocodebox/LifterLMS-Dash-Docset.
2. Install node dependencies: `npm install`
3. Install [Dashing](https://github.com/technosophos/dashing): `brew install dashing`
4. Scrape the docs from https://developer.lifterlms.com: `node index.js` (this takes a while)
5. Generate the docset with Dashing: `npm run-script dashing`
6. Package the docset for contribution as a User-Contributed Docset: `tar --exclude='.DS_Store' -cvzf LifterLMS.tgz LifterLMS.docset`

### Issues and Support

+ Please post an issue in the official GitHub repository at https://github.com/gocodebox/LifterLMS-Dash-Docset

### Changelog

+ Version 3.29.4 - 2019-03-14