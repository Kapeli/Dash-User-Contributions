.. index:: info; frame
.. _info_frame:

**info frame** [-v] [ *frame-number* | *frame-object* ]


Info Frame
----------

Show the detailed information for *frame-number* or the current frame if
*frame-number* is not specified. You can also give a frame object instead of
a frame number

Specific information includes:

* the frame number (if not an object)
* the source-code line number that this frame is stopped in
* the last instruction executed; -1 if the program are before the first instruction
* a function that tracing this frame or `None`
* Whether the frame is in restricted execution
* Exception type and value if there is one

If `-v` is given we show builtin and global names the frame sees.

.. seealso::

   :ref:`info locals <info_locals>`, :ref:`info globals <info_globals>`,
   :ref:`info args <info_args>`
