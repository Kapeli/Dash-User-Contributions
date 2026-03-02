.. index:: ipython
.. _ipython:

IPython (go into an IPython shell)
----------------------------------

**ipython** [*-d* ]

.. note::

   this command is available only if ipython is installed

Run Python as a command subshell. The *sys.ps1* prompt will be set to
``trepan3k >>>``.

If *-d* is passed, you can access debugger state via local variable
*debugger*.

To issue a debugger command use function *dbgr()*. For example:

::

      dbgr('info program')

.. seealso::

   :ref:`python <python>`, and :ref:`bpython <bpython>`.
