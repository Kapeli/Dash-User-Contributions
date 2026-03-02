.. index:: syntax; range
.. _syntax_range:

Syntax for List Ranges
======================

List ranges are used in the `list` and `disassemble` commands.

A list range is in one of the following forms:

    location       # starting line only
    first, last    # starting and ending line
    , last         # ending line only


A *location* is described elsewhere. *first* and *last* can also be
locations, but they may also be a number. And finally, *last* can be a (line number)
offset.

A number is just a decimal number. An offset is a number prefaced with "+" and
indicates the number to increment the line number found in *first*.

List Range Examples
--------------------

::

    5                    # start from line 5 of the current file
    5 ,                  # Same as above.
    , 5                 # listsize lines before and up to 5
    foo.py:5             # start from line 5 of file foo.py
    foo()                # start from function foo
    os.path:5            # start from line 5 of module os.path
    os.path:5            # Same as above.
    os.path:5, 6         # list lines 5 and 6 of os.path
    os.path:5, +1        # Same as above. +1 is an offset
    os.path:5, 1         # Same as above, since 1 < 5.
    os.path:5, +6        # lines 5-11
    os.path.join()       # lines starting with the os.join.path function.
    "c:\foo.py":10,      # listsize lines starting from line 10 of c:\foo.py
    , 'My Doc/foo.py':20 # listsize lines ending at line 20 of file: My Doc/foo.py


.. seealso::

 :ref:`help syntax location <syntax_location>`
