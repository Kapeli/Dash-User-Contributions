.. index:: macro
.. _macro:

Macro (add a debugger macro)
----------------------------

**macro** *macro-name* *lambda-object*

Define *macro-name* as a debugger macro. Debugger macros get a list of
arguments which you supply without parenthesis or commas. See below for
an example.

The macro (really a Python lambda) should return either a String or an
List of Strings. The string in both cases is a debugger command. Each
string gets tokenized by a simple split() . Note that macro processing
is done right after splitting on ``;;``. As a result, if the macro
returns a string containing ``;;`` this will not be interpreted as
separating debugger commands.

If a list of strings is returned, then the first string is shifted from
the list and executed. The remaining strings are pushed onto the command
queue. In contrast to the first string, subsequent strings can contain
other macros. ``;;`` in those strings will be split into separate
commands.

Here is an trivial example. The below creates a macro called ``l=``
which is the same thing as ``list .``:

::

        macro l= lambda: 'list .'

A simple text to text substitution of one command was all that was
needed here. But usually you will want to run several commands. So those
have to be wrapped up into a list.

The below creates a macro called ``fin+`` which issues two commands
``finish`` followed by ``step``:

::

        macro fin+ lambda: ['finish','step']

If you wanted to parameterize the argument of the ``finish`` command you
could do that this way:

::

        macro fin+ lambda levels: ['finish %s' % levels ,'step']

Invoking with:

::

         fin+ 3

would expand to: ``['finish 3', 'step']``

If you were to add another parameter for ``step``, the note that the
invocation might be:

::

         fin+ 3 2

rather than ``fin+(3,2)`` or ``fin+ 3, 2``.

.. seealso::

   :ref:`alias <alias>`, and :ref:`info macro <info_macro>`.
