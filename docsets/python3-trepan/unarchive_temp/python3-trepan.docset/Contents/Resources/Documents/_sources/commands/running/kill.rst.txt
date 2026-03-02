.. index:: kill

Kill
----

**kill** [ *signal-number* ] [unconditional]

Send this process a POSIX signal ('9' for 'SIGKILL' or 'kill -SIGKILL')

9 is a non-maskable interrupt that terminates the program. If program
is threaded it may be expedient to use this command to terminate the program.

However other signals, such as those that allow for the debugged to
handle them can be sent.

Giving a negative number is the same as using its
positive value.

Kill Examples:
++++++++++++++

::

    kill                # non-interuptable, nonmaskable kill
    kill 9              # same as above
    kill -9             # same as above
    kill!               # same as above, but no confirmation
    kill unconditional  # same as above
    kill 15             # nicer, maskable TERM signal
    kill! 15            # same as above, but no confirmation

.. seealso::

   :ref:`quit <quit>` for less a forceful termination command; `exit` for another way to force termination.
   :ref:`run <run>` and :ref:`restart <restart>` are ways to restart the debugged program.
