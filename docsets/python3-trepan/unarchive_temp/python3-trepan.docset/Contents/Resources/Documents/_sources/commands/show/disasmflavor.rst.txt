.. index:: show; disasmflavor
.. _show_disasmflavor:

Show DisasmFlavor
-----------------

**show disasmflavor**

 Show the disassembly format style used in the ``disassemble`` command.

The style of style to use in disassembly:

``classic``:
  fields: line, marker offset, opcode operand

``extended``:
  like above, but we try harder to get operand information from previous instructions

``bytes``:
   like classic but we show the instruction bytes after the offset

``extended-bytes``:
   ``bytes`` format along with *extended* format

Show disasmflavor Example:
++++++++++++++++++++++++++

::

   set disasmflavor

.. seealso::

   :ref:`set_disasmflavor <set_disasmflavor>`
