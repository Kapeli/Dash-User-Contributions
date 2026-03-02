.. index:: python
.. _python:

Python (go into a Python shell)
-------------------------------

**python** [*-d* ]

Run Python as a command subshell. The *sys.ps1* prompt will be set to
``trepan3k >>>``.

If *-d* is passed, you can access debugger state via local variable
*debugger*.

To issue a debugger command use function *dbgr()*. For example:

::

      dbgr('info program')

.. seealso::

   :ref:`eval <eval>`,
   :ref:`set autoeval <set_autoeval>`,
   :ref:`ipython <ipython>`, and :ref:`bpython <bpython>`.
