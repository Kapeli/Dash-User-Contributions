.. index:: stepi
.. _stepi:

Step Instruction
----------------

**stepi**  [*count*]

Execute the current line, stopping at the instruction bytecode.

With an integer argument, step bytecode instructions that many times.


Step Instruction Examples:
++++++++++++++++++++++++++

::

    stepi       # step 1 event, *any* event
    si 1        # same as above

    Related and similar is the ``step`` command.

.. seealso::

   :ref:`step <step>` command. :ref:`next <next>`, :ref:`skip <skip>`, :ref:`jump <jump>` (there's no `hop` yet), :ref:`continue <continue>`, and :ref:`finish <finish>` provide other ways to progress execution.
