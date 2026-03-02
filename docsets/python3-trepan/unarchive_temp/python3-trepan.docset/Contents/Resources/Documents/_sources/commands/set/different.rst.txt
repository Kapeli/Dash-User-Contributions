.. index:: set; different
.. _set_different:

Set Different
-------------

**set** **different** [ **on** | **off** ]

Set consecutive stops must be on different file/line positions.

By default, the debugger traces all events possible including line,
exceptions, call and return events. Just this alone may mean that for
any given source line several consecutive stops at a given line may
occur. Independent of this, Python allows one to put several commands in
a single source line of code. When a programmer does this, it might be
because the programmer thinks of the line as one unit.

One of the challenges of debugging is getting the granualarity of
stepping comfortable. Because of the above, stepping all events can
often be too fine-grained and annoying. By setting different on you can
set a more coarse-level of stepping which often still is small enough
that you won't miss anything important.

Note that the `step` and `next` debugger commands have '+' and '-'
suffixes if you wan to override this setting on a per-command basis.

.. seealso::

   :ref:`set trace <set_trace>` to change what events you want to filter.
   :ref:`show trace <show_trace>`.
