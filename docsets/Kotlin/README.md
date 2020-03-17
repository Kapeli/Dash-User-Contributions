# Kotlin Docset

## Who are you

**Original submitter:** Kevin Cianfarini, `kevincianfarini` on
Github/GitLab

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
* Alter `docset.json` in this directory as appropriate for your changes.
* Change this `README` if needed and submit a pull request with
  everything accomplished above!
