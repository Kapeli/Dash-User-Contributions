# Kotlin

Author: Marcel Jackwerth ([@sirlantis](http://twitter.com/sirlantis))

Generation steps (see [GitHub repo](https://github.com/sirlantis/kotlin-docset)):

- Download docs via `wget --mirror -k -nH ...`.
- Add some CSS-overrides.
- Add each `.html` file as a `Guide` to index.

Where to get the docs:

- The official [Kotlin website](kotlinlang.org/docs).

Known Bugs:

- Doesn't include API documentation yet (they will [change them soon](http://kotlinlang.org/docs/api/index.html)).
- Some pages of the original Kotlin documentation are missing source code. Once they get this fixed we'll update the docset.