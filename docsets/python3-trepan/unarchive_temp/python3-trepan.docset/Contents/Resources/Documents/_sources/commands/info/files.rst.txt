.. index:: info; files
.. _info_files:

Info Files
----------

**info files** [ *filename* [ **all** | **brkpts** | **sha1** | **size** ]]

Show information about the current file. If no filename is given and
the program is running then the current file associated with the
current stack entry is used. Sub options which can be shown about a file are:

:brkpts:
   Line numbers where there are statement boundaries. These lines can be used in breakpoint commands.
:sha1:
   A SHA1 hash of the source text. This may be useful in comparing source code
:size:
   The number of lines in the file.
:all:
   All of the above information.
