.. index:: info; break
.. _info_break:

Info Break
----------

**info breakpoints** [ *bp-number...* ]

Show the status of specified breakpoints (or all user-settable
breakpoints if no argument).

The **Disp** column contains one of `keep`, or `del`, to indicate the
disposition of the breakpoint after it gets hit.  `del` means that the
breakpoint will be deleted.  The **Enb** column indicates if the
breakpoint is enabled. The **Where** column indicates the file/line
number of the breakpoint.

Also shown are the number of times the breakpoint has been hit,
when that count is at least one, and any conditions the breakpoint
has.

Example:
++++++++

::

    (trepan3k) info break
    Num Type          Disp Enb    Where
    1   breakpoint    del  n   at /tmp/fib.py:9
    2   breakpoint    keep y   at /tmp/fib.py:4
            breakpoint already hit 1 time
    3   breakpoint    keep y   at /tmp/fib.py:6
            stop only if x > 0

.. seealso::

   :ref:`break <break>`, :ref:`delete <delete>` :ref:`enable <enable>`, :ref:`disable`, :ref:`condition <condition>`
