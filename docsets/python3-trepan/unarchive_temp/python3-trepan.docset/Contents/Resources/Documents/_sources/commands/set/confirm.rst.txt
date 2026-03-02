.. index:: set; confirm
.. _set_confirm:

Set Confirm
------------

**set confirm** [ **on** | **off** ]

Set confirmation of potentially dangerous operations.

Some operations are a bit disruptive like terminating the program.
To guard against running this accidentally, by default we ask for
confirmation. Commands can also be exempted from confirmation by suffixing
them with an exclamation mark (!).

.. seealso::

   :ref:`show confirm <show_confirm>`
