.. index:: whatis
.. _whatis:

Whatis
------

**whatis** *arg*

Prints the information argument which can be a Python expression.

When possible, we give information about:

* type of argument
* doc string for the argument (if a module, class, or function)
* comments around the definition of the argument (module)
* the module it was defined in
* where the argument was defined

We get this most of this information via the *inspect* module.

.. seealso::

   the :py:mod:`inspect` module.
