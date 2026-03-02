.. index:: info; lines
.. _info_lines:

Info Lines
-----------

**info lines** [**-n** *function-or-module*]

Show line - function/offset information.
Use **-n** *function-or-module* to filter results.


Info Lines Examples
++++++++++++++++++++

::

    (trepan3k) info lines
    Line - (fn, start offset) table for test/example/gcd.py
      10: <module> @0         21: check_args() @84     36: gcd() @30
      11: <module> @4         22: check_args() @106    37: gcd() @50
      13: <module> @12        23: check_args() @116    38: gcd() @54
      14: check_args() @0     24: check_args() @122    40: <module> @28
      16: check_args() @14    26: <module> @20         41: <module> @36
      17: check_args() @22    30: gcd() @0             43: <module> @42
      18: check_args() @36    31: gcd() @8             44: <module> @60
      19: check_args() @38    34: gcd() @18            45: <module> @84
      20: check_args() @70    35: gcd() @26
    (trepan3k) info lines -n <module>
      10: <module> @0    11: <module> @4   13: <module> @12
      40: <module> @28   26: <module> @20  41: <module> @36
      43: <module> @42   44: <module> @60  45: <module> @84
    (trepan3k) info lines -n gcd
      30: gcd() @0   31: gcd() @8   34: gcd() @18
      35: gcd() @26  36: gcd() @30  37: gcd() @50
      38: gcd() @54

.. seealso::

   :ref:`info program <info_line>`, :ref:`info program <info_program>`, :ref:`info pc <info_pc>`, :ref:`info frame <info_frame>`
