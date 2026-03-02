.. index:: quit

Quit
----
**quit** [**unconditionally**]

Gently terminate the debugged program.

The program being debugged is aborted via a *DebuggerQuit*
exception.

When the debugger from the outside (e.g. via a `trepan` command), the
debugged program is contained inside a try block which handles the
*DebuggerQuit* exception.  However if you called the debugger was
started in the middle of a program, there might not be such an
exception handler; the debugged program still terminates but generally
with a traceback showing that exception.

If the debugged program is threaded, we raise an exception in each of
the threads ending with our own. However this might not quit the
program.

.. seealso::

   :ref:`kill <kill>` or `kill` for more forceful termination commands. :ref:`run <run>` and :ref:`restart <restart>` are other ways to restart the debugged program.
