Running
=======

Running, restarting, or stopping the program.

When a program is stopped, there are several possibilities for further
program execution. You can:

* terminate the program inside the debugger
* restart the program
* continue its execution until it would normally terminate or until a
  breakpoint is hit
* step execution, which runs for a limited amount of code before stopping

About Debugging Overhead
------------------------

Explanation of Problem
~~~~~~~~~~~~~~~~~~~~~~

When you enable the debugger, there are callbacks made in the running
of the program when certain events happen. Events are things that occur in
running the program, like when the code reaches a new line in the
program, when a call or return occurs, or when an exception is raised.

The overhead in running these callbacks slows down your
program. Currently, the overhead can be greater than the overhead in
``pdb``. This is because the debugger tries to be more precise and
careful it tracing, and the features it provides are more powerful. In
most cases, we can do this without a significant slow down in the
debugged program.

But in certain situations, the overhead in running debugged code can
be large. This happens when we want to "step over" a function that is
large and complex, like an ``import`` of a large module.

For example, if you turn on the debugger and run the ``import pandas`` instruction, it can increase your CPU usage for a while.  ::

   $ cat slow.py
   #!/usr/bin/env python3
   import pandas as pd
   print(pd)

   $ trepan3k slow.py
   (/tmp/slow.py:1): <module>
   -> 1 import pandas as pd
   (trepan3k) next
    -- 1 import pandas as pd
   (trepan3k) next # this may be slow and increase your CPU a bit
   (/tmp/slow.py:2 @10): <module>
   -- 2 print(pd)

The debugger overhead only concerns the instructions of the program to
be debugged, the instructions of the trepan3k interpreter are not
analyzed.

Given this, here is how to speed up the above ::

   $ trepan3k slow.py
   (/tmp/slow.py:1): <module>
   -> 1 import pandas as pd
   (trepan3k) next
   (trepan3k) import pandas as pd
    -- 1 import pandas as pd
   (trepan3k) next # this will run fast
   (/tmp/slow.py:2 @10): <module>
   -- 2 print(pd)

Alternatively, modifying the program with a call to ``debug`` will also run fast::

   $ cat fast.py
   #!/usr/bin/env python3
   import pandas as pd
   from trepan.api import debug; debug()
   print(pd)

   $ python fast.py
   (/tmp/fast.py:3 @36): <module>
   -- 3 print(pd)
   (trepan3k)

Techniques to Reduce Debugger Overhead
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Activate the debugger only when you need it

   Look at
   https://python3-trepan.readthedocs.io/en/latest/entry-exit.html#calling-the-debugger-from-your-program.
   By doing there is no slowdown whatsoever until the first breakpoint
   is hit.

#. Remove keep breakpoints when you no longer need them

When there are *any* breakpoints in the program, the debugger has to check every event to see if the event is the target of a breakpoint.

In particular, the ``continue``, ``finish``, and ``next`` (step over) commands are much slower.

Therefore, remove *all* breakpoints when they are no longer
needed. Consider using temporary or one-time breakpoints when you need to stop only once.


#. Use debugging commands with less overhead

``continue`` when there are no breakpoints pending probably gives the
fastest execution. ``info break`` will show you if there are any
breakpoints. Recall that one-time breakpoints are removed after they
are encountered.

When no breakpoints are used, the ``continue`` command will cause the debugger to remove its trace hook, and execution should continue at normal speed.

The ``step`` is usually fast, because there is generally very little
debugger overhead between stopping points.

The ``next`` (step over) debugger command is faster without a breakpoint than when there are breakpoint because without breakpoints, there is
less debugger overhead in checking for the stopping condition.

The ``finish`` command when there are no breakpoints is faster than when there are breakpoints.
Without breakpoints debugger will remove tracing calls.

When there must breakpoint in use, setting a breakpoint and running
``continue`` is faster than the ``next`` command. Because ``next`` has
to check stack depth, that can considerably slow things down.

Debugging commands
------------------

.. toctree::
   :maxdepth: 1

   running/continue
   running/exit
   running/finish
   running/jump
   running/kill
   running/next
   running/quit
   running/run
   running/restart
   running/skip
   running/step
   running/stepi
