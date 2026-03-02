.. index:: jump

Jump
----

**jump** *lineno*

Set the next line that will be executed.

There are a number of limitations on what line can be set.

You can't jump:

* into the body of a for loop
* into an ``except`` block from outside
* outside or inside of a code block you are stopped

Jumping to a previous line is one way to reexecuting code.
Jumping to a return statement may get you back to the caller
function without running more code in the current frame.

.. seealso::

   :ref:`skip <skip>`,
   :ref:`next <next>`, :ref:`step <step>`, :ref:`continue <continue>`, and
   :ref:`finish <finish>` provide other ways to progress.

   :ref:`eval <eval>` can be used to run Python code without changing the execution line.
