.. index:: next
.. _next:

Next (step over)
----------------

**next** [ **+** | **-** ] [ *count* ]

Step one statement ignoring steps into function calls at this level.

With an integer argument, perform `next` that many times. However if
an exception occurs at this level, or we *return*, *yield* or the
thread changes, we stop regardless of count.

A suffix of `+` on the command or an alias to the command forces to
move to another line, while a suffix of `-` does the opposite and
disables the requiring a move to a new line. If no suffix is given,
the debugger setting 'different-line' determines this behavior.

.. seealso::

   :ref:`stepi <stepi>`, ref:`skip <step>`, :ref:`jump <jump>`, :ref:`continue <continue>`, and
   :ref:`finish <finish>` provide other ways to progress execution.
