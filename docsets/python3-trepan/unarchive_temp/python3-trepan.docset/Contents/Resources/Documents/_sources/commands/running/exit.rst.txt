.. index:: exit

Exit
----

**exit** [*exitcode*]

Hard exit of the debugged program.

The program being debugged is exited via *sys.exit()*. If a return code
is given, that is the return code passed to *sys.exit()*, the
return code that will be passed back to the OS.

.. seealso::

   :ref:`quit <quit>` and :ref:`kill <kill>`
