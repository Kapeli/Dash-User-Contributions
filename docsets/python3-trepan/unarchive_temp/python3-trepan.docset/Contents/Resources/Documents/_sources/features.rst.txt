.. contents:: :local:

Features
========

Since this debugger is similar to other_ trepanning_ debuggers_ and *gdb* in general, knowledge gained by learning this is transferable to those
debuggers and vice versa.

There's a lot of cool stuff here that's not in the stock
Python debugger *pdb*, or in any other Python debugger that I know about.


More Exact location information
-------------------------------

Python reports line information on the granularity of a line. To get more precise information, we can (de)parse into Python the bytecode
around a bytecode offset, such as the place you are stopped at.

So far as I know, there is no other debugger that decompiles code at runtime.

See the `deparse <deparse>`_ command for details.

We use information in the line number table in bytes to understand
which lines are breakpointable, and in which module or function the
line appears. Use `info line <_info_line>`_ to see this information.

In the future, we may allow specifying an offset to indicate which
offset to stop at when there are several choices for a given line
number.


Debugging Python bytecode (no source available)
-----------------------------------------------

You can pass the debugger the name of Python bytecode, and many times, the debugger will merrily proceed.  This debugger tries very hard to find the source code. Either by using the current executable search path
(e.g. ``PATH``) or for some by looking inside the bytecode for a
filename in the main code object (``co_filename``) and applying that
with a search path that takes into account the directory where the
bytecode lives.

Failing to find source code this way, and in other situations where
source code can't be found, the debugger will decompile the bytecode
and use that for showing source test. *This allows us to debug `eval`'d
or `exec''d code.*

But if you happen to know where the source code is located, you can
associate a file source code with the current name listed in the
bytecode. See the :ref:`set substitute <set_substitute>` for
details here.


Source-code Syntax Colorization
-------------------------------

Terminal source code is colorized via pygments_ . And with that you
can set the pygments color style, e.g., "colorful", "paraiso-dark". See
:ref:`set style <set_style>`. Furthermore, we make use of terminal bold
and emphasized text in debugger output and help text. Of course, you
can also turn this off. Starting with release 0.6.0, you can use your
own pygments_style_, provided you have a terminal that supports 256
colors. If your terminal supports the basic ANSI color sequences only,
we support that too in both dark and light themes.


Command Completion
------------------

GNU readline command completion is available. Command completion is
not just a simple static list, but varies depending on the
context. For example, for frame-changing commands which take optional
numbers, on the list of *valid numbers* is considered.

Terminal Handling
-----------------

We can adjust debugger output depending on the line width of your
terminal. If it changes, or you want to adjust it, see :ref:`set width <set_width>` .

Smart Eval
----------

If you want to evaluate the current source line before it is run in
the code, use ``eval``. To evaluate the text of a common fragment of a line,
such as the expression part of an *if* statement, you can do that with
``eval?``. See :ref:`eval` for more information.

More Stepping Control
---------------------

Sometimes you want small steps, and sometimes large steps.

This fundamental issue is handled in a couple of ways:

Step Granularity
................

There are now ``step`` *event* and ``next`` *event* commands with
aliases to ``s+``, ``s>`` and so on. The plus-suffixed commands force
a different line on a subsequent stop, the dash-suffixed commands
don't.  Suffixes ``>``, ``<``, and ``!`` specify ``call``, ``return``
and ``exception`` events respectively. And without a suffix you get
the default; this is set by the ``set different`` command.

Event Filtering and Tracing
...........................

By default the debugger stops at every event: ``call``, ``return``,
``line``, ``exception``, ``c-call``, ``c-exception``. If you just want
to stop at ``line`` events (which is largely what you happens in
*pdb*) you can. If however you just want to stop at calls and returns,
that's possible too. Or pick some combination.

In conjunction with handling *all* events by default, the event status is shown when stopped. The reason for stopping is also available via ``info program``.

Event Tracing of Calls and Returns
----------------------------------

I'm not sure why this was not done before. Probably because of the
lack of the ability to set and move by different granularities,
tracing calls and returns lead to too many uninteresting stops (such
as at the same place you just were at). Also, stopping on function
definitions probably also added to this tedium.

Because we're really handling return events, we can show you the return value. (*pdb* has an "undocumented" *retval* command that doesn't seem to work.)

Debugger Macros via Python Lambda Expressions
---------------------------------------------

There are debugger macros.  In *gdb*, there is a *macro* debugger command to extend debugger commands.

However, Python has its own rich programming language, so it seems silly
to recreate the macro language that is in *gdb*. Simpler and more
powerful is just to use Python here. A debugger macro here is just a
lambda expression that returns a string or a list of strings. Each
string returned should be a debugger command.

We also have *aliases* for the extremely simple situation where you
want to give an alias to an existing debugger command. But beware:
some commands, like step_ inspect command suffixes and change their
behavior accordingly.

We also envision a number of other ways to allow the extension of this
debugger either through additional modules or through user-supplied debugger command directories.

Byte-code Instruction Introspection
------------------------------------

We do more in the way of looking at the byte codes to give better information. Through this, we can provide:

* A *skip* command. It is like the *jump* command, but you don't have
  to deal with line numbers.
* Disassembly of code fragments. You can now disassemble relative to
  the stack frames you are currently stopped at.
* Better interpretation of where you are when inside *execfile* or
  *exec*. (But really, though this is probably a Python compiler
  misfeature.)
* Check that breakpoints are set only where they make sense.
* A more accurate determination of whether you are at a function-defining
  *def* or *class* statements (because the caller instruction contains
  ``MAKE_FUNCTION`` or ``BUILD_CLASS``.)

Even without "deparsing" mentioned above, the ability to disassemble
where the PC is currently located (see `info pc <info_pc>`_), by line number range or byte-offset range lets you tell exactly where you are and the code is getting run.

Some Debugger Command Arguments can be Variables and Expressions
----------------------------------------------------------------

Commands that take integer arguments like *up*, *list*, or *disassemble* allow you to use a Python expression which may include
local or global variables that evaluate to an integer. This
eliminates the need in *gdb* for special "dollar" debugger
variables. (Note, however, because of *shlex* parsing, expressions can't have embedded blanks.)

Out-of-Process Debugging
------------------------

You can now debug your program in a different process or even on a different computer on a different network!

Egg, Wheel, and Tarballs
------------------------

Can be installed via the usual *pip* or *easy_install*. There is a
source tarball. `How To Install
<https://python2-trepan.readthedocs.io/en/latest/install.html>`_ has
full instructions and installing from git and by other means.

Modularity
----------

The Debugger plays nicely with other trace hooks. You can have several debugger objects.

Many of the things listed below doesn't directly effect end-users, but
it does eventually by way of more robust and featureful code. And
keeping developers happy is a good thing.(TM)

* Commands and subcommands are individual classes now, not methods in a class. This means they now have properties like the context in which they can be run, a minimum abbreviation name, or alias names. To add a new command, you basically add a file in a directory.
* I/O is its own layer. This simplifies interactive readline behavior from reading commands over a TCP socket.
* An interface is its own layer. Local debugging, remote debugging, and running debugger commands from a file (``source``) are different interfaces. This means, for example, that we are able to give better error reporting if a debugger command file has an error.
* There is an experimental Python-friendly interface for front-ends
* more testable. Much more unit and functional tests. More of *pydb*'s integration tests will eventually be added.

Documentation
-------------

Documentation: http://python3-trepan.readthedocs.org

See Also
--------


* trepan2_ : trepan debugger for Python 2
* trepanxpy_ : trepan debugger for `x-python <https://pypi.python.org/pypi/x-python>`_, the bytecode interpreter written in Python
* pydbgr_  : previous incarnation of the Python 2 debugger
* Tutorial_: for ways to get into the debugger
* https://pypi.python.org/pypi/uncompyle6 : Python decompiler

.. _pygments:  http://pygments.org
.. _pygments_style:  http://pygments.org/docs/styles/
.. _pydb:  http://bashdb.sf.net/pydb
.. _pydbgr: https://pypi.python.org/pypi/pydbgr
.. _other: https://www.npmjs.com/package/trepanjs
.. _trepanning: https://rubygems.org/gems/trepanning
.. _trepan2:  https://pypi.org/project/trepan2/
.. _trepanxpy:  http://github.com/rocky/trepan-xpy
.. _Tutorial:  https://python3-trepan.readthedocs.io/en/latest/entry-exit.html
.. _debuggers: https://metacpan.org/pod/Devel::Trepan
.. _this: http://bashdb.sourceforge.net/pydb/features.html
.. _install: http://python3-trepan.readthedocs.org/en/latest/install.html
.. _step: https://python2-trepan.readthedocs.org/en/latest/commands/running/step.html
