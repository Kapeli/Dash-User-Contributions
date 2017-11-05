Ramda Docset
=======================

## Author

Akronix

 - Github: [akronix](https://github.com/akronix)


## Building the Docset

Install [dashing](https://github.com/technosophos/dashing), if you haven't already.

Clone [my fork](https://github.com/Akronix) of the ramda.js documentation and checkout to the ['dash-docs' branch.](https://github.com/Akronix/ramda.github.io/tree/dash-docs)

Go to the current version docs folder: `cd ramda.github.io/0.25.0/docs`

Run `dashing build Ramda`

Open with any SQLite Client the generated database located in Ramda.docset/Contents/Resources/docSet.dsidx
Remove the duplicated element `__`, with unique id=2, which I haven't managed yet to not get it generated twice both as Method and as Property. You can use this SQL statement for this:
`delete from searchIndex where id=2;`

## Bugs & Enhancements

If you have problems with this documentation set, you would like to suggest improvements,
or you would like to contribute, feel free to contact me to my personal e-mail: akronix5@gmail.com
or submit an issue in the [Dash User Contributions repo](https://github.com/Kapeli/Dash-User-Contributions/issues).


When you contribute a docset, you need to edit this README to include the following:
* Who are you (GitHub and/or Twitter username)
* Complete instructions on how to generate the docset, including:
  * List of any prerequisites (especially your docset generation script!)
  * Where or how to download the initial HTML documentation for the docset
  * How to run the generation script
  * Any other notes that might be useful
* List of any known bugs (links to GitHub issues)
* Anything else you think is relevant
