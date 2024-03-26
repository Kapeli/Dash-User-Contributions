# Kotlin Docset

## Complete Instructions on how to generate the docset

* Clone docset generation script repo from
  [here](https://github.com/snowe2010/kotlin2docset)
* Follow the Readme file located inside repository to create `*.docset` file
* Replace `kotlin.tgz.txt` in this directory with a new gzipped
  tarball `kotlin.tgz` made from the directory the above script
  produced.

  ```bash
  tar --exclude='.DS_Store' -cvzf kotlin.tgz kotlin.docset
  ```
  
  Don't worry that file extensions are `*.tgz.txt` and `*.tgz`. Worker will replace tar file on repo with text file after it's processed.
* Alter `docset.json` in this directory as appropriate for your changes.
* Change this `README` if needed and submit a pull request with
  everything accomplished above!

## Version 1.9.20

[Tyler Thrailkill](https://github.com/snowe2010)

Large number of changes to generation script to add:

- Table of Contents on each page
- Kotlin Test capabilites
- automatic css changes and html modification

https://github.com/snowe2010/kotlin2docset

## Previous Versions:

**Original submitter:** Kevin Cianfarini, `kevincianfarini` on
Github/GitLab
https://github.com/kevincianfarini/kotlin2docset

**Previous Maintainers:**

https://github.com/kevincianfarini/kotlin2docset

- Alexander Ronald Altman, `pthariensflame` on Github/GitLab
- Igor Kurek, `ikurek` on Github/GitLab 
