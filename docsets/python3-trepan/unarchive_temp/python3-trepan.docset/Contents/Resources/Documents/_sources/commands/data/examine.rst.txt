.. index:: examine
.. _examine:

Examine
-------

**examine** *expr1* [*expr2* ...]

Examine value, type and object attributes of an expression.

In contrast to normal Python expressions, expressions should not have
blanks which would cause shlex to see them as different tokens.

Examine Examples
++++++++++++++++

::

    examine x+1   # ok
    examine x + 1 # not ok

.. seealso::

   :ref:`pr <pr>`, :ref:`pp <pp>`, and :ref:`whatis <whatis>`.
