.. index:: break
.. _break:

Break (set a breakpoint)
------------------------

**break** [*location*] [if *condition*]]

Sets a breakpoint, i.e. stopping point just before the
execution of the instruction specified by *location*.

Without arguments or an empty *location*, the breakpoint is set at the
current stopped location.

See `help syntax location` for detailed information on a location.

If the word `if` is given after *location*, subsequent arguments given
Without arguments or an empty *location*, the breakpoint is set
the current stopped location.

Normally we only allow stopping at lines that we think are
stoppable. If the command has a `!` suffix, force the breakpoint anyway.

Examples
++++++++

::

   break                # Break where we are current stopped at
   break if i < j       # Break at current line if i < j
   break 10             # Break on line 10 of the file we are
                        # currently stopped at
   break! 10            # Break where we are current stopped at, even if
                        # we don't think line 10 is stoppable
   break os.path.join() # Break in function os.path.join
   break x[i].fn()      # break in function specified by x[i].fn
   break x[i].fn() if x # break in function specified by x[i].fn
                        # if x is set
   break os.path:45     # Break on line 45 file holding module os.path
   break myfile.py:2    # Break on line 2 of myfile.py
   break myfile.py:2 if i < j # Same as above but only if i < j
   break "foo's.py":1"  # One way to specify path with a quote
   break 'c:\\foo.bat':1      # One way to specify a Windows file name,
   break '/My Docs/foo.py':1  # One way to specify path with blanks in it

.. seealso::

   :ref:`info break <info_break>`, :ref:`tbreak <tbreak>`, :ref:`condition <condition>`, and :ref:`help syntax location <syntax_location>`.
