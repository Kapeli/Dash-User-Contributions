.. index:: info; signals
.. _info_signals:

Info Signals
------------
**info signals** [*signal-name*]

**info signals** \*

Show information about how debugger treats signals to the program.
Here are the boolean actions we can take:

* Stop: enter the debugger when the signal is sent to the debugged program
* Print: print that the signal was received
* Stack: show a call stack
* Pass: pass the signal onto the program

If *signal-name* is not given, we the above show information for all
signals. If '*' is given we just give a list of signals.
