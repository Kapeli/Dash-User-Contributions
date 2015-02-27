EMF XSD SDK (Eclipse Modeling Framework API)
============================================

When you contribute a docset, you need to edit this README to include the
following:
* Who are you (GitHub and/or Twitter username)

GitHub: tsdh
Twitter: tsdh80

* Complete instructions on how to generate the docset, including:
  * List of any prerequisites (especially your docset generation script!)

I have a project for repackaging the EMF XSD SDK releases and pushing them to
Clojars so that you can get them via Maven:

  https://github.com/tsdh/emf-xsd-sdk

That contains a ZSH script `make-zeal-docs.zsh` which generates the docset.
You need ZSH, a recent GNU grep, sed, and javadoc.

  * Where or how to download the initial HTML documentation for the docset

I didn't.  I generated it myself.  The script above does that, too.

  * How to run the generation script

./make-zeal-docs.zsh

  * Any other notes that might be useful

No, I don't think so.

* List of any known bugs (links to GitHub issues)

No known bug.  I hope that doesn't change. :-)

* Anything else you think is relevant

No.
