.. index:: backtrace
.. _backtrace:

Backtrace (show call-stack)
---------------------------

**backtrace** [*options*] [*count*]

Print backtrace of all stack frames, or innermost *count* frames.

With a negative argument, print outermost -*count* frames.

An arrow indicates the 'current frame'. The current frame determines
the context used for many debugger commands such as expression
evaluation or source-line listing.

*opts* are:

   -d | --deparse - show deparsed call position
   -s | --source  - show source code line
   -f | --full    - locals of each frame
   -h | --help    - give this help


Backtrace Examples:
+++++++++++++++++++

::

   backtrace      # Print a full stack trace
   backtrace 2    # Print only the top two entries
   backtrace -1   # Print a stack trace except the initial (least recent) call.
   backtrace -s   # show source lines in listing
   backtrace -d   # show deparsed source lines in listing
   backtrace -f   # show with locals
   backtrace -df  # show with deparsed calls and locals
   backtrace --deparse --full   # same as above

.. seealso::

   :ref:`frame <frame>`, :ref:`info locals <info_locals>`, :ref:`deparse <deparse>` and :ref:`list <list>`.
