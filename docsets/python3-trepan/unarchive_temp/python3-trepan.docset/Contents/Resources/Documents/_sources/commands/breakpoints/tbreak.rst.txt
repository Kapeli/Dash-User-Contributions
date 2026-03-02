.. index:: tbreak
.. _tbreak:

Tbreak (temporary breakpoint)
-----------------------------

**tbreak** [ *location* ] [**if** *condition*]

With a line number argument, set a break there in the current file.
With a function name, set a break at first executable line of that
function.  Without argument, set a breakpoint at current location.  If
a second argument is ``if``, subsequent arguments given an expression
which must evaluate to true before the breakpoint is honored.

The location line number may be prefixed with a filename or module
name and a colon. Files is searched for using *sys.path*, and the `.py`
suffix may be omitted in the file name.

Examples:
+++++++++

::

   tbreak     # Break where we are current stopped at
   tbreak 10  # Break on line 10 of the file we are currently stopped at
   tbreak os.path.join # Break in function os.path.join
   tbreak os.path:45   # Break on line 45 of os.path
   tbreak myfile.py:45 # Break on line 45 of myfile.py
   tbreak myfile:45    # Same as above.

.. seealso::

   :ref:`break <break>`.
