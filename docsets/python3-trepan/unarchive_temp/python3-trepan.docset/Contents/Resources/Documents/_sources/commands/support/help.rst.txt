.. index:: help
.. _help:

Help (Won't you please help me if you can)
------------------------------------------

**help** [*command* [*subcommand*]|*expression*]

Without argument, print the list of available debugger commands.

When an argument is given, it is first checked to see if it is command
name.

If the argument is an expression or object name, you get the same
help that you would get inside a Python shell running the built-in
*help()* command.

If the environment variable *$PAGER* is defined, the file is
piped through that command.  You'll notice this only for long help
output.

Some commands like `info`, `set`, and `show` can accept an
additional subcommand to give help just about that particular
subcommand. For example `help info line` give help about the
info line command.

.. seealso::

   :ref:`examine <examine>` and :ref:`whatis <whatis>`.
