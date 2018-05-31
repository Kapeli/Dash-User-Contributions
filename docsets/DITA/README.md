DITA
=======================

# Author

Maintained by Paul Mazaitis, https://github.com/pmazaitis

# Docset Source

This docset is pulled from the online specification for the Darwin Information Typing Architecture (DITA) maintained by OASIS:

    http://docs.oasis-open.org/dita/dita/v1.3/dita-v1.3-part3-all-inclusive.html

# Generating the Docset

## Prerequisites

This docset requires a script to generate the index:

    dita_docset_indexer.py

The script is intended to be run from the same directory as the DITA.docset bundle.  It takes no arguments.

## Updating the Local Copy

To update the local copy of the docset run the following in the source directory:

    wget -k -r -p -np --ignore "*.pdf" --ignore "*.zip" http://docs.oasis-open.org/dita/dita/v1.3/errata01/os/complete/part3-all-inclusive/dita-v1.3-errata01-os-part3-all-inclusive-complete.html

Neither the PDF version so the document nor the zip file archives of the specification are appropriate for including in this docset.

# Notes

I have included the subsections of section 2 in the specifications as guides; one caveat to how the indexing script handles this is that it checks for hardcoded file names during the process run to index these files: not the most robust solution! I couldn't find any kind of markup or hierarchical  that helps me determine useful guides systematically, so this was the best I could come up with. Given that there are a limited number of these, and the specification shouldn't change that often, I'm hoping this won't be so bad.

# Bugs

None known, but there will be, and critique is always welcome.
