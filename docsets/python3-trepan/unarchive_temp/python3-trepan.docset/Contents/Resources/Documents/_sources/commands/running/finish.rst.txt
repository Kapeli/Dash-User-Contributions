.. index:: finish
.. _finish:

Finish (step out)
-----------------

**finish** [*level*]

Continue execution until leaving the current function. When *level* is
specified, that many frame levels need to be popped. Note that *yield*
and exceptions raised my reduce the number of stack frames. Also, if a
thread is switched, we stop ignoring levels.

See the :ref:`break <break>` command if you want to stop at a
particular point in a program.

.. seealso::

   :ref:`step <step>` :ref:`skip <skip>`, :ref:`jump <jump>`, :ref:`continue <continue>`, and :ref:`finish <finish>` provide other ways to progress
