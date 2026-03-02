.. index:: continue

Continue
--------

**continue** [[ *file* :] *lineno* | *function* ]

Leave the debugger read-eval print loop and continue
execution. Subsequent entry to the debugger however may occur via
breakpoints or explicit calls, or exceptions.

If a line position or function is given, a temporary breakpoint is set at that
position before continuing.

Continue Examples:
++++++++++++++++++

::

    continue          # Continue execution
    continue 5        # Continue with a one-time breakpoint at line 5
    continue basename # Go to os.path.basename if we have basename imported
    continue /usr/lib/python2.7/posixpath.py:110 # Possibly the same as
                                                 # the above using file
                                                 # and line number

.. seealso::

   :ref:`step <step>` :ref:`jump <jump>`, :ref:`next <next>`, and :ref:`finish <finish>` provide other ways to progress execution.
