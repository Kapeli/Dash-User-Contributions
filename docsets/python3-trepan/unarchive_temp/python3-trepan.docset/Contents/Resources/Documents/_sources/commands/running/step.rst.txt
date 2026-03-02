.. index:: step
.. _step:

Step (step into)
----------------

**step** [ **+** | **-** | **<** | **>** | **!** ] [*event*...] [*count*]

Execute the current line, stopping at the next event.

With an integer argument, step that many times.

*event* is list of an event name which is one of: ``call``,
``return``, ``line``, ``exception``, ``c-call``, ``c-return``, or ``c-exception``.


If specified, only those stepping events will be considered. If no
list of event names is given, then any event triggers a stop when the
count is zero.

There is however another way to specify an event: you can suffix one
of the symbols ``<``, ``>``, or ``!`` after the command or on an alias
of that.  A suffix of ``+`` on a command or an alias forces a move to
another line, while a suffix of ``-`` disables this requirement.  A
suffix of ``>`` will continue until the next call. ``finish`` will run
run until the return for that call, in contrast to ``step<`` continues to the
return of *any* call which might occur inside a nested call.

If no suffix is given, the debugger setting ``different-line``
determines this behavior.

An example. Use ``step>`` to skip over a number of statements to get a call that is coming up:

::

     (trepan3k) list
     29    	    # Make: a <= b
     30    	    if a > b:
     31    	       (a, b) = (b, a)
     32    	       pass
     33
     34 -->	    if a <= 0:
     35    	        return None
     36    	    if a == 1 or b-a == 0:
     37    	        return a
     38    	    return gcd(b-a, a)

If we know that ``a >=1 and b != 0``, then by running ``step>`` we will
skip over all of the testing and proceed into the ``gcd()`` call:

::

    (trepan3k) step>
    (/tmp/python3-trepan/test/example/gcd.py:26): gcd
    -> 26 def gcd(a,b):
    a = 3
    b = 3
    (trepan3k)

Now if we want to continue execution to the return, run ``step<``:

::

   (trepan3k) step<
   step<
   (/tmp/python3-trepan/test/example/gcd.py:37 @62): gcd
   <- 37         return a
   R=> 3

Note that ``finish`` does the same thing as ``step<`` and might even be more reliable here.

For ``step>``, ``break`` is sometimes better.

Step Examples:
++++++++++++++

::

    step        # step 1 event, *any* event
    step 1      # same as above
    step 5/5+0  # same as above
    step line   # step only line events
    step call   # step only call events
    step>       # same as above
    step call line # Step line *and* call events

.. seealso::

   :ref:`next <next>` command. :ref:`skip <skip>`, :ref:`jump <jump>` (there's no `hop` yet), :ref:`continue <continue>`, and :ref:`finish <finish>` provide other ways to progress execution.
