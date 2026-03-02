.. index:: set; events
.. _set_events:

Set Events
----------
**set events** [*event* ...]

Sets the events that the debugger will stop on. Event names are:

.. hlist::
   :columns: 3

   * ``c_call``
   * ``c_exception``
   * ``c_return``
   * `call``
   * ``exception``
   * ``line``
   * ``return``

`all` can be used as an abbreviation for listing all event names.

Changing trace event filters works independently of turning on or off
tracing-event printing.

Set Events Examples:
++++++++++++++++++++

::

  set events line        # Set trace filter for line events only.
  set events call return # Trace calls and returns only
  set events all         # Set trace filter to all events.

.. seealso::

   :ref:`set trace <set_trace>`, :ref:`show trace <show_trace>`, and
   :ref:`show events <show_events>`
