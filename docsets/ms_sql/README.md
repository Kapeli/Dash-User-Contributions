MS SQL Server (Transact-SQL) Docset
=======================

* Author: [Andrew Zah](https://github.com/azah)

This project uses bash/pandoc to convert markdown->html and then bash/ruby to (roughly) categorize the files and insert them into the sqlite db.

# Building Locally

Requires `pandoc` + `ruby` and the `nokogiri` gem.

* Run `git submodule init` to get the docs submodule
* Run `git submodule update --recursive --remote` to update the docs submodule (if needed)
* Run `make genhtml` in the project root directory.
* Run `make gendocs` in the project root directory.

# Current Bugs
* Some media links are broken
* The expanded markdown from their custom [!INCLUDES] syntax gives broken links to media.
