Concourse CI Docset
=======================

Author: Jeffrey Alvarez (github.com/kuritsu)

Generate the docset
-------------------

Follow the instructions of generating the doc [here](https://github.com/concourse/docs).

Clone the [docset repo](https://github.com/kuritsu/concourse-ci.docset).

Copy the contents of the concourse docs repo (after generating the doc) inside the
`concourse-ci.docset/Contents/Resources/Documents` folder of the docset repo
(including all html files, search_index.json and css, images, js folders).

Run the generateAll.sh script (which requires bash, tar, python).

As a result there will be created a concourse-ci.tgz in the root of the docset repo.
