.. index:: frame
.. _frame:

Frame (absolute frame positioning)
----------------------------------

**frame** [ *thread-name* | *thread-number* ] [ *frame-number* ]

Change the current frame to frame *frame-number* if specified, or the
current frame, 0, if no frame number specified.

If a thread name or thread number is given, change the current frame
to a frame in that thread. Dot (.) can be used to indicate the name of
the current frame the debugger is stopped in.

A negative number indicates the position from the other or
least-recently-entered end.  So `frame -1` moves to the oldest frame,
and `frame 0` moves to the newest frame. Any variable or expression
that evaluates to a number can be used as a position, however due to
parsing limitations, the position expression has to be seen as a single
blank-delimited parameter. That is, the expression `(5*3)-1` is okay
while `(5 * 3) - 1)` isn't.

Frame Examples:
+++++++++++++++

::

   frame     # Set current frame at the current stopping point
   frame 0   # Same as above
   frame 5-5 # Same as above. Note: no spaces allowed in expression 5-5
   frame .   # Same as above. "current thread" is explicit.
   frame . 0 # Same as above.
   frame 1   # Move to frame 1. Same as: frame 0; up
   frame -1  # The least-recent frame
   frame MainThread 0 # Switch to frame 0 of thread MainThread
   frame MainThread   # Same as above
   frame -2434343 0   # Use a thread number instead of name

.. seealso::

   :ref:`down <down>`, :ref:`up <up>`, :ref:`backtrace <backtrace>`, and
   :ref:`info threads <info_threads>`.
