Pebble SDK Docset
=======================

This is an unofficial Dash Docset for the official Pebble SDK docs. The Pebble SDK consists of a build toolchain and C libraries for the architecture of the Pebble smartwatch. Learn more at [developer.getpebble.com](http://developer.getpebble.com). It is my hope that one day the Pebble team provides an official docset; the implementation files are private so this docset is put together from Doxygen output.

Feel free to open issues in github or comment on the [Pebble forum topic](http://forums.getpebble.com/discussion/8270/sdk-documentation-in-dash-docset).

To build the docset from source, please see the README in the original PebbleSdkDocset repo, included as a submodule here or on [Github](//github.com/partlyhuman/PebbleSdkDocset/blob/master/README.md).

Prerequisites
----------------------------
* Ruby
* sqlite3

Sources
----------------------------
Download the official docs at [developer.getpebble.com](http://developer.getpebble.com).

Build
----------------------------
1. Clone the [PebbleSdkDocset](//github.com/partlyhuman/PebbleSdkDocset) repo.
2. Copy documentation from the official SDK into the Docset, e.g.

	`cp -r $PEBBLE_SDK/Documentation/pebble-api-reference/* ./Pebble.docset/Contents/Resources/Documents/`

3. The generate script echoes SQLite commands, pipe them through `sqlite3` to update the docset's database.

	`ruby generate-pebble-sdk-docset.rb | sqlite3 ./Pebble.docset/Contents/Resources/docSet.dsidx`
      
------------------------------------------------

Contact me: Roger Braunstein, @partlyhuman on [Twitter](//twitter.com/partlyhuman) [Github](//github.com/partlyhuman/)