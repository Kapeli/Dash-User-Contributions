Stack
=====

Examining the call stack.

The call stack is made up of stack frames.  The debugger assigns
numbers to stack frames counting from zero for the innermost
(currently executing) frame.

At any time the debugger identifies one frame as the "selected" frame.
Variable lookups are done with respect to the selected frame.  When
the program being debugged stops, the debugger selects the innermost
frame.  The commands below can be used to select other frames by
number or address.


.. toctree::
   :maxdepth: 1

   stack/backtrace
   stack/frame
   stack/up
   stack/down
