.. index:: set; skip
.. _set_skip:

Set Skip
--------
Set stopping before *def* or *class* (function or class) statements.

Classes may have many methods and stand-alone programs may have many
functions. Often there isn't much value to stopping before defining a
new function or class into Python's symbol table. (More to the point,
it can be an annoyance.) However if you do want this, for example
perhaps you want to debug methods is over-writing one another, then
set this off.

.. seealso::

   :ref:`show skip <show_skip>`
