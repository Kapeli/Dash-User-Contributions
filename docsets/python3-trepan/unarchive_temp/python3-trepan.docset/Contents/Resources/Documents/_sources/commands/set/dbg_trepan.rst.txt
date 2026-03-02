.. index:: set; dbg_trepan
.. _set_dbg_trepan:

Set Dbg_trepan
--------------

**set dbg_trepan** [ **on** | **off** ]

Set the ability to debug the debugger.

Setting this allows visibility and access to some of the debugger's
internals. Specifically variable "frame" contains the current frame and
variable "debugger" contains the top-level debugger object.

.. seealso::

   :ref:`show dbg_trepan <show_dbg_trepan>`
