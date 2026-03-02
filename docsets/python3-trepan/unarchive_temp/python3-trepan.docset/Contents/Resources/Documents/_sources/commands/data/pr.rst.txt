.. index:: pr
.. _pr:

Pr (print expression)
---------------------

**pr** *expression*

Print the value of the expression. Variables accessible are those of the
environment of the selected stack frame, plus globals.

The expression may be preceded with */fmt* where *fmt* is one of the
format letters 'c', 'x', 'o', 'f', or 's' for chr, hex, oct,
float or str respectively.

If the length output string large, the first part of the value is
shown and `...` indicates it has been truncated.

.. seealso::

   :ref:`pp <pp>` and :ref:`examine <examine>` for commands which do more
   in the way of formatting;
