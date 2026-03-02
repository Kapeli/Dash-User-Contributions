.. _syntax_command:

Debugger Command Syntax
=======================

Command names and arguments are separated with spaces like POSIX shell
syntax. Parenthesis around the arguments and commas between them are
not used. If the first non-blank character of a line starts with `#`,
the command is ignored.

Commands are split at wherever ``;;`` appears. This process disregards
any quotes or other symbols that have meaning in Python. The strings
after the leading command string are put back on a command queue, and
there should be white space around ``;;``.

Within a single command, tokens are then white-space split. Again, this process disregards quotes or symbols that have meaning in Python.
Some commands like :ref:`eval <eval>`, :ref:`macro <macro>`, and
:ref:`break <break>` have access to the untokenized string entered and make use of that rather than the tokenized list.

Resolving a command name involves possibly 4 steps. Some steps may be
omitted depending on early success or some debugger settings:

1. The leading token is first looked up in the macro table. If it is in the table, the expansion replaces the current command and
possibly other commands pushed onto a command queue. See `help macros` for
help on how to define macros, and `info macro` for current macro
definitions.

2. The leading token is next looked up in the debugger alias table, and the name may be substituted there. See "help alias" for how to define
aliases, and "show alias" for the current list of aliases.

3. After the above, the leading token is looked up in a table of debugger
commands. If an exact match is found, the command name and arguments
are dispatched to that command.

4. If, after all of the above, we still don't find a command, the line
may be evaluated as a Python statement in the current context of the
program at the point it is stopped. However, this is done only if
"auto evaluation" is on.  It is on by default.

If :ref:`auto eval <set_autoeval>` is not set on, or if running the Python statement produces an error, we display an error message that the entered string is "undefined".

If you want python-, ipython-, or bpython-like shell
command-processing, it's possible to go into a ``python`` shell with the
corresponding command. It is also possible to arrange to go into a ``python`` shell every time you enter the debugger.

.. seealso::

  :ref:`help syntax suffixes <syntax_suffixes>`
