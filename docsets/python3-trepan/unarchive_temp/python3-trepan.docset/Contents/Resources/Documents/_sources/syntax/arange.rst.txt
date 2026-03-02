.. index:: syntax; arange
.. _syntax_arange:

Syntax for Address Ranges
=========================

Address ranges are used in the :ref:`disassemble <disassemble>` command. It is like a
range, but we allow addresses.

An address range is in one of the following forms:

::

    location       # starting line only
    first, last    # starting and ending line
    , last         # ending line only


See :ref:` location <location>` for a full description of a location.

*first* and *last* can also be line specifications (:ref:`linespec
<linespec>`), but they also may be a number or address
(bytecode offset). And finally, *last* can be a (line number) offset.

A number is just a decimal number. An offset is a number prefaced with "+" and
indicates the number to increment the line number found in *first*.

Address-Range Examples
----------------------

::

  *5                 # start from bytecode offset 5 of the current file
  *5 ,               # Same as above.
  foo.py:*5          # start from bytecode offset 5 of file foo.py


.. seealso::

 :ref:`location <syntax_location>`, :ref:`linespec <linespec>`
