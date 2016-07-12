Pure
=======================

Author: [Jonathan Rehm](https://twitter.com/JonathanRehm)

Generation Steps:
- Install [Dashing](https://github.com/technosophos/dashing)
- Download docs from [Pure's website](http://purecss.io) using [SiteSucker](http://www.sitesucker.us/mac/mac.html)
- Navigate to the docs' directory
- Copy `dashing.json` from this repository into the root of the docs
- Run `dashing build pure.docset`
- Run `tar --exclude='.DS_Store' -cvzf Pure.tgz pure.docset`
- Follow [Dash's instructions](https://github.com/Kapeli/Dash-User-Contributions) on contributing the docset

Known Bugs:
- None

Originally contributed by [Alex LaFroscia](https://twitter.com/alexlafroscia)
