.. index:: set; autopc
.. _set_autopc:

Autorun Info PC
---------------

**set autopc** [ **on** | **off** ]

Run the :ref:`info pc <info_pc>` command every time you stop in the
debugger.

With this, you will get output like:

::

   (trepan3k) set autopc on
   Run `info pc` on debugger entry is on.
   (trepan3k) **step**
   (/tmp/raise.py:2): bug
   -- 2     x = 5
   PC offset is 0.
      2-->     0 LOAD_CONST          1          5
               2 STORE_FAST          1          x

      3        4 LOAD_FAST           1          x
               6 LOAD_FAST           0          y
               8 BINARY_TRUE_DIVIDE  None
              10 POP_TOP             None
   (trepan3k) step
   (/tmp/raise.py:3 @4): bug
   -- 3     x / y
   PC offset is 4.
      2        0 LOAD_CONST          1          5
               2 STORE_FAST          1          x

      3-->     4 LOAD_FAST           1          x
               6 LOAD_FAST           0          y
               8 BINARY_TRUE_DIVIDE  None
              10 POP_TOP             None
              12 LOAD_CONST          0          None
              14 RETURN_VALUE        None
   (trepan3k) step
   (/tmp/raise.py:3 @8): bug
   !! 3     x / y
   R=> (<class 'ZeroDivisionError'>, ZeroDivisionError('division by zero'), <traceback object at 0x7f22d4f521e0>)
   PC offset is 8.
      2        0 LOAD_CONST          1          5
               2 STORE_FAST          1          x

      3        4 LOAD_FAST           1          x
               6 LOAD_FAST           0          y
       -->     8 BINARY_TRUE_DIVIDE  None
              10 POP_TOP             None
              12 LOAD_CONST          0          None
              14 RETURN_VALUE        None


You may also want to put this this in your debugger startup file.

.. seealso::

   :ref:`show autopc <show_autopc>`
