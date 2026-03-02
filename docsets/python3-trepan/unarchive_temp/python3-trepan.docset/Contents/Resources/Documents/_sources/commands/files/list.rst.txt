.. index:: list
.. _list:

List (show me the code!)
------------------------

**list** [ *range* ]

**list**  **+** | **-** | **.**

List source code. See :ref:`help syntax range <syntax_range>` for what can go in a list range.

Without arguments, print lines centered around the current line. If
*num* is given that number of lines is shown.

Without arguments, print lines starting from where the last list left off
since the last entry to the debugger. We start off at the location indicated
by the current stack.

in addition you can also use:

  - a '.' for the location of the current frame
  - a '-' for the lines before the last list
  - a '+' for the lines after the last list

List Examples:
++++++++++++++

::

    list 5               # List starting from line 5 of current file
    list 5 ,             # Same as above.
    list , 5             # list listsize lines before and up to 5
    list foo.py:5        # List starting from line 5 of file foo.py
    list foo()           # List starting from function foo
    list os.path:5       # List starting from line 5 of module os.path
    list os.path:5, 6    # list lines 5 and 6 of os.path
    list os.path:5, +1   # Same as above. +1 is an offset
    list os.path:5, 1    # Same as above, since 1 < 5.
    list os.path:5, +6   # list lines 5-11
    list os.path.join()  # List lines centered around the os.join.path function.
    list .               # List lines centered from where we currently are stopped
    list -               # List lines previous to those just shown
    list                 # List continuing from where we last left off

.. seealso::

 :ref:`set listize <set_listsize>`, or :ref:`show listsize <show_listsize>` to see or set the number of source-code lines to list. :ref:`help syntax location <syntax_location>` for the specification of a location and :ref:`help syntax range <syntax_range>` for the specification of a range.
