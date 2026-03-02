Breakpoints
===========

A *breakpoint* can make your program stop at that point. You can set
breakpoints with the break command and its variants. You can specify
the place where your program should stop by file and line number or by
function name.

The debugger assigns a number to each breakpoint when you create it;
these numbers are successive integers starting with 1. In many of the
commands for controlling various features of breakpoints you use this
number. Each breakpoint may be enabled or disabled; if disabled, it
has no effect on your program until you enable it again.

The debugger allows you to set any number of breakpoints at the same
place in your program. There is nothing unusual about this because
different breakpoints can have different conditions associated with
them.

The simplest sort of breakpoint breaks every time your program reaches
a specified place. You can also specify a condition for a
breakpoint. A condition is just a Boolean expression in your
programming language. A breakpoint with a condition evaluates the
expression each time your program reaches it, and your program stops
only if the condition is true.

This is the converse of using assertions for program validation; in
that situation, you want to stop when the assertion is violated-that
is, when the condition is false.

Break conditions can have side effects, and may even call functions in
your program. This can be useful, for example, to activate functions
that log program progress, or to use your own print functions to
format special data structures. The effects are completely predictable
unless there is another enabled breakpoint at the same address. (In
that case, pydb might see the other breakpoint first and stop your
program without checking the condition of this one.) Note that
breakpoint commands are usually more convenient and flexible than
break conditions for the purpose of performing side effects when a
breakpoint is reached.

Break conditions can be specified when a breakpoint is set, by adding
a comma in the arguments to the break command. They can also be
changed at any time with the :ref:`condition <condition>` command.

In certain cases using a breakpoint may cause ``next``, ``finish`` and
``continue`` instructions to slow down the execution of your
program. See :ref:`running <running>` for more information.

.. toctree::
   :maxdepth: 1

   breakpoints/break
   breakpoints/clear
   breakpoints/condition
   breakpoints/delete
   breakpoints/disable
   breakpoints/enable
   breakpoints/tbreak
