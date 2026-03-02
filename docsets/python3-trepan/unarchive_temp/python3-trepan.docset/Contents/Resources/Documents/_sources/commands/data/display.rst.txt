.. index:: display
.. _display:

Display (set display expression)
--------------------------------

**display** [ *format* ] *expression*

Print value of expression *expression* each time the program stops.
*format* may be used before *expression* and may be one of `/c` for
char, `/x` for hex, `/o` for octal, `/f` for float or `/s` for string.

For now, display expressions are only evaluated when in the same
code as the frame that was in effect when the display expression
was set.  This is a departure from *gdb*, and we may allow for more
flexibility in the future to specify whether this should be the
case or not.

With no argument, evaluate and display all currently requested
auto-display expressions.

.. seealso::

   :ref:`undisplay <undisplay>` to cancel display requests previously made.
