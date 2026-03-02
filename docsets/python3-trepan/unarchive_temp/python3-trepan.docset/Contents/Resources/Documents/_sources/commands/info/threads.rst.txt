.. index:: info; threads
.. _info_threads:

Info Threads
------------
**info threads** [ *thread-name* | *thread-number* ] [ **terse** | **verbose** ]

List all currently-known thread name(s).

If no thread name is given, we list info for all threads. Unless a
terse listing, for each thread we give:

* the class, thread name, and status as *Class(Thread-n, status)*
* the top-most call-stack information for that thread.

Generally the top-most calls into the debugger and dispatcher are
omitted unless set dbg_trepan is *True*.

If 'verbose' appended to the end of the command, then the entire stack
trace is given for each frame.  If 'terse' is appended we just list
the thread name and thread id.

To get the full stack trace for a specific thread pass in the thread name.
