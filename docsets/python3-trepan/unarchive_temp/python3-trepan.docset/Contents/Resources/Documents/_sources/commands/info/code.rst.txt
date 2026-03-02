.. index:: info; code
.. _info_code:

**info code** [ *frame-number* | *code-object* ]


Info Code
----------

Specific information includes:

* the number of arguments (not including * or ** args)
* the number of local variables
* maximum stack size used by the frame
* first line associated with the code
* constants used in the bytecode
* whether code is optimized
* Should a new local namespace be created for this code? (This is True for functions and False for modules and exec code.)
* name with which this code object was defined

.. seealso::

   :ref:`info frame <info_frame>`, :ref:`info frame <info_frame>`, :ref:`info locals <info_locals>`,
