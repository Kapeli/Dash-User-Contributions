.. index:: set; disasmflavor
.. _set_disasmflavor:

Set DisasmFlavor
----------------

**set disasmflavor** {**classic** | **extended** | **bytes** | **extended-bytes**}

Set the style of format to use in disassembly:

``classic``:
    has fields: *line* *marker* *offset*, and *opcode operand*

``extended``:
    like ``classic``, but we try harder to get operand information from previous instructions

``bytes``:
    like classic but we show the instruction bytes after the offset

``extended-bytes``
   ``bytes`` format along with *extended* format


Set disasmflavor Examples:
++++++++++++++++++++++++++

::
    set asmfmt extended # this is the default
    set asmfmt classic  # no highlight

.. seealso::

   :ref:`show disasmflavor <show_disasmflavor>`
