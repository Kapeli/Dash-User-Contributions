# Kotlin Docset

## Who are you

**Original submitter:** Kevin Cianfarini, `kevincianfarini` on
Github/GitLab

<<<<<<< HEAD
**Current maintainer:** Alexander Ronald Altman,
`pthariensflame` on Github/GitLab

## Complete Instructions on how to generate the docset

* Clone Kevin's docset generation script repo from
  [here](https://github.com/kevincianfarini/kotlin2docset).
* Run `python kotlindoc2set.py` from there (you may need to install a
  newer Python version and/or install Beautiful Soup 4).
* Replace `kotlin.tgz.txt` in this directory with a new gzipped
  tarball `kotlin.tgz` made from the directory the above script
  produced.
=======
**Previous Maintainer:** Alexander Ronald Altman,
`pthariensflame` on Github/GitLab

**Current Maintainer:** Igor Kurek,
`ikurek` on Github/GitLab

## Complete Instructions on how to generate the docset

* Clone docset generation script repo from
  [here](https://github.com/ikurek/kotlin2docset) (fork of [kevincianfarini's repository](https://github.com/kevincianfarini/kotlin2docset))
* Follow the Readme file located inside repository do create `*.docset` file
* Apply CSS fixes described in Readme (or not, they're optional)
* Replace `kotlin.tgz.txt` in this directory with a new gzipped
  tarball `kotlin.tgz` made from the directory the above script
  produced.

  ```bash
  tar --exclude='.DS_Store' -cvzf kotlin.tgz kotlin.docset
  ```
  
  Don't worry that file extensions are `*.tgz.txt` and `*.tgz`. Worker will replace tar file on repo with text file after it's processed.
>>>>>>> daee4539969911937fd29e266d25f0735f5452d3
* Alter `docset.json` in this directory as appropriate for your changes.
* Change this `README` if needed and submit a pull request with
  everything accomplished above!
