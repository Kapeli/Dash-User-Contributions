.. index:: info; line
.. _info_line:

Info Line
---------

**info line** [*location*]

Show line information for location *location*.

If no location is given, use the the current stopped line.

Info Line Examples
++++++++++++++++++

::

    (trepan3k) info line
    Line 3 of "/tmp/python3-trepan/test/example/multi-line.py"
        starts at offset 0 of <module> and contains 2 instructions
    There are multiple starting offsets this line. Other starting offsets: 4 of <module>

    (trepan3k) info line 5
    Line 5 of "/tmp/python3-trepan/test/example/multi-line.py"
        starts at offset 16 of <module> and contains 7 instructions


.. seealso::

   :ref:`info program <info_program>`, :ref:`info frame <info_frame>` and :ref:`help syntax location <syntax_location>`.
