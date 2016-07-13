Parse iOS SDK Docset
======================

[Parse](https://parse.com) iOS SDK docset for Dash. Check out the [Parse iOS Guide](https://parse.com/docs/ios_guide) for an in-depth look at Parse's API.

* Author: Héctor Ramos [github](https://github.com/hramos)

Sources
-------
Official docs: [HTML](https://parse.com/docs/ios), [docset feed](https://www.parse.com/docs/ios/com.parse.Parse-iOS-SDK.atom).

Build
-----

1. Download the latest xar from the [Parse-iOS-SDK docset feed](https://www.parse.com/docs/ios/com.parse.Parse-iOS-SDK.atom).
2. Extract the xar and package it into a tar using
   `tar --exclude='.DS_Store' -cvzf Parse-iOS-SDK.tgz Parse-iOS-SDK-<docset version>.docset`
3. Fork this repo, copy the new tar, and update `docset.json`.
4. Submit a pull request.
