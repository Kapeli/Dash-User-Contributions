.. index:: bpython
.. _bpython:

BPython (go into a bpython shell)
---------------------------------

**bpython** [*-d* ]

.. note::

   this command is available only if bpython is installed

Run Python as a command subshell. The *sys.ps1* prompt will be set to
``trepan2 >>>``.

If *-d* is passed, you can access debugger state via local variable
*debugger*.

To issue a debugger command use function *dbgr()*. For example:

::

      dbgr('info program')

.. seealso::

   :ref:`python <python>`, and :ref:`ipython <ipython>`.
