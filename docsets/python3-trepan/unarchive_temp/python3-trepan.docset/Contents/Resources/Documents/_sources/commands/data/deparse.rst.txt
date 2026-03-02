.. index:: deparse
.. _deparse:

Deparse (CPython bytecode deparser)
-----------------------------------

**deparse** [options] [.]

Options are:

::

    -p | --parent        show parent node
    -P | --pretty        show pretty output
    -A | --tree | --AST  show parse tree
    -o | --offset [num]  show deparse of offset NUM
    -h | --help          give this help

deparse around where the program is currently stopped. If no offset is given,
we use the current frame offset. If `-p` is given, include parent information.

If an '.' argument is given, deparse the entire function or main
program you are in.  The `-P` parameter determines whether to show the
prettified as you would find in source code, or in a form that more
closely matches a literal reading of the bytecode with hidden (often
extraneous) instructions added. In some cases this may even result in
invalid Python code.

Output is colorized the same as source listing. Use ``set highlight plain`` to turn
that off.

Deparse Examples:
+++++++++++++++++

::

       deparse             # deparse current location
       deparse --parent    # deparse current location enclosing context
       deparse .           # deparse current function or main
       deparse --offset 6  # deparse starting at offset 6
       deparse --offsets   # show all exact deparsing offsets
       deparse --tree      # deparse and show parse tree

.. seealso::

 :ref:`disassemble <disassemble>`, :ref:`list <list>`, and :ref:`set highlight <set_highlight>`
