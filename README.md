Dash User Contributed Docsets
=======================

### Report a bug or request a docset
[Open an issue](https://github.com/Kapeli/Dash-User-Contributions/issues/new).

### Improve an existing docset

Navigate to the docset you want to fix in the `docsets` folder, improve it and submit [pull requests](https://github.com/Kapeli/Dash-User-Contributions/pulls).

You do not have to fix the existing generation script if it's too flawed or in a language you're not comfortable with, you can write a new generation script and completely take over the maintenance for that docset if you wish, just make sure you justify your reasons (i.e. how your improved docset is better) when submitting the pull request.

### Contribute a new docset

To contribute a docset, follow the steps below. If you get stuck at any point or have any questions, [open an issue](https://github.com/Kapeli/Dash-User-Contributions/issues). I'll help.

* Generate a docset by following the instructions at http://kapeli.com/docsets
    * Note: you can ignore the instructions regarding docset feeds. You won't need them if you plan to contribute to this repo
* Make sure your docset fulfils all the required criteria on the [Docset Contribution Checklist](https://github.com/Kapeli/Dash-User-Contributions/wiki/Docset-Contribution-Checklist) and as many of the optional ones as possible
* Check out the [Versioning Guidelines](https://github.com/Kapeli/Dash-User-Contributions/wiki/Docset-Versioning-Guidelines) to understand how docset versioning works in Dash
* Fork and clone this repo
* Set up your directory structure:
  * Copy the `Sample_Docset` folder into the `docsets` folder and rename it. Use the same name as your docset, but replace whitespaces with underscores. Note: don't add `_Docset` at the end of the name, just use the docset name (e.g. `ExtJS`) and nothing else.
  * Archive your docset using:
  ```bash
  tar --exclude='.DS_Store' -cvzf <docset name>.tgz <docset name>.docset
  ```
  * Copy your docset archive
    * Note: don't worry about this repo's size getting huge. As soon as your docset gets distributed to my CDN, it will get removed from the repo automatically. If your docset exceeds GitHub's file limit of 100 MB, open an issue and we'll figure out a different way to submit your docset
  * Include a `icon.png` and `icon@2x.png` with sizes `16x16` and `32x32` or simply delete the sample icon if you don't want an icon at all
  * Edit the docset.json file. Make sure to follow the same naming rules as the sample (i.e. your docset name should be the same as the archive name, but replace whitespaces with underscores)
  * Edit the README.md
* Submit a pull request

### How to use a user contributed docset you found here

To use a user contributed docset, go to Dash, click downloads, and click "User Contributed" under "Other docsets".
