.. index:: disassemble
.. _disassemble:

Disassemble (CPython disassembly)
---------------------------------

**disassemble** [*thing*]

**disassemble** [*address-range*]

Disassembles bytecode. See `help syntax arange` for what can go in an
assembly-list range.

Without arguments, print lines starting from where the last list left off
since the last entry to the debugger. We start off at the location indicated
by the current stack.

in addition you can also use:

  - a '.' for the location of the current frame
  - a '-' for the lines before the last list
  - a '+' for the lines after the last list

With a class, method, function, pyc-file, code or string argument
disassemble that.

Assembly output format is be controlled by the setting of ``set
asmfmt``. Output formats are those described the ``xdis`` ``pydisasm``
disassembler.

Disassmble Examples
++++++++++++++++++++

::

       disassemble    # Possibly lots of stuff disassembled
       disassemble .  # Disassemble lines starting at current stopping point.
       disassemble +                  # Same as above
       disassemble +0                 # Same as above
       disassemble os.path            # Disassemble all of os.path
       disassemble os.path.normcase   # Disaassemble just method os.path.normcase
       disassemble -3  # Disassemble subtracting 3 from the current line number
       disassemble +3  # Disassemble adding 3 from the current line number
       disassemble 3                  # Disassemble starting from line 3
       disassemble 3 10               # Disassemble lines 3 to 10
       disassemble myprog.pyc         # Disassemble file myprog.pyc

.. seealso::

 :ref:`help syntax arange <syntax_arange>` for the specification of an address range :ref:`deparse <deparse>`, :ref:`list <list>`, :ref:`info pc <info_pc>`, and :ref:`set asmfmt <set_disasmflavor>`.
