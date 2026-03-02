.. index:: eval
.. _eval:

Eval (evaluate Python code)
---------------------------

**eval** *python-statement*

Run *python-statement* in the context of the current frame.

If no string is given, we run the string from the current source code
about to be run. If the command ends `?` (via an alias) and no string is
given, the following translations occur:

::

   assert <expr>         => <expr>
   {if|elif} <expr> :    => <expr>
   while <expr> :        => <expr>
   return <expr>         => <expr>
   for <var> in <expr> : => <expr>
   <var> = <expr>        => <expr>

The above is done via regular expression matching. No fancy parsing is
done, say, to look to see if *expr* is split across a line or whether
var an assignment might have multiple variables on the left-hand side.

Eval Examples
+++++++++++++

::

    eval 1+2  # 3
    eval      # Run current source-code line
    eval?     # but strips off leading 'if', 'while', ..
              # from command

.. seealso::

   :ref:`python <python>`,
   :ref:`set autoeval <set_autoeval>`, :ref:`pr <pr>`,
   :ref:`pp <pp>` and :ref:`examine <examine>`.
