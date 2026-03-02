Entering the Debugger
**********************

.. toctree::
.. contents::


Invoking the Debugger Initially
===============================

The simplest way to debug your program is to run ``trepan3k``. Give the name of your program and its options, and any debugger options:

.. code:: console

        $ cat test.py
        print('Hello, World!')

        $ trepan3k test.py

For help on trepan3k's options, use the ``--help`` option.

.. code:: console

        $ trepan3k --help
        Usage: trepan3k [debugger-options] [python-script [script-options...]]
        ...

To separate options to the program you want to debug from trepan3k's
options put `--` after the debugger's options:

.. code:: console

      $ trepan3k --trace -- test.py --test-option1 b c

If you have previously set up remote debugging using
``trepan3k --server``, you'll want to run the client version of *trepan3k*
which is a separate program ``trepan3kc``.

Calling the debugger from IPython
=================================

Installing the IPython extension
--------------------------------

Use the `trepan IPython extension <https://github.com/rocky/ipython-trepan>`_.

To install, execute the following code snippet in an IPython shell or IPython notebook cell:

.. code:: python

    %load https://raw.github.com/rocky/ipython-trepan/master/trepanmagic.py


Trepan IPython Magic Functions
------------------------------

After installing the trepan extension, the following IPython magic functions are added:

* `%trepan_eval`  evaluate a Python statement under the debugger
* `%trepan` run the debugger on a Python program
* `%trepan_pm`  do post-mortem debugging

Example
+++++++

.. code::

	  $ ipython
	  Python 3.6.8 (default, Aug 20 2019, 17:12:48)
	  Type 'copyright', 'credits' or 'license' for more information
	  ...

	  In [1]: %load https://raw.github.com/rocky/ipython-trepan/master/trepanmagic.py
	  trepanmagic.py loaded
	  In [2]: import os.path
	  In [3]: %trepan_eval os.path.join('foo', 'bar')
	  (/tmp/eval_stringS9ST2e.py:1 remapped <string>): <module>
	  -> 1 (os.path.join('foo', 'bar'))
	  (trepan3k) s
	  (/usr/lib/python3.6/posixpath.py:75): join
	  (trepan3k) n
	  (/usr/lib/python3.6/posixpath.py:80): join
	  -- 80     a = os.fspath(a)
	  (trepan3k) c
	  Out[3]: 'foo/bar'
	  In [4]:

See also the `examples <https://github.com/rocky/ipython-trepan/tree/master/examples>`_ directory.


Calling the debugger from an Interactive Python Shell
=====================================================

*Note: By "interactive Python shell," I mean running "python" or "python -i" and this is distinct from going into IPython, which was covered in the last section.*

Put these lines in a file::

	  import inspect
	  from trepan.api import run_eval
	  def debug(str):
	    frame = inspect.currentframe()
	    return run_eval(str, globals_=frame.f_globals, locals_=frame.f_locals)
	  print(".pythonrc.py loaded") # customize or remove this

A copy of the above can be found `here <https://github.com/rocky/python2-trepan/blob/master/PYTHONSTARTUP/pythonrc>`_. I usually put these lines in `$HOME/.pythonrc.py`. Set the environment variable *PYTHONSTARTUP* to `$HOME/.pythonrc.py`.

After doing this, when you run `python -i` you should see on entry the *print* message from the file. For example:

.. code:: console

   	  $ python -i
	  Python ...
	  Type "help", "copyright", "credits" or "license" for more information.
	  .pythonrc.py loaded
	  >>>

If you see the above `.pythonrc.py` message, great! If not, it might be that *PYTHONSTARTUP* is not defined. Here run:

.. code:: console

	  >>> path=".pythonrc.py" # customize to location of file
          >>> exec(open(path).read())
	  pythonrc loaded
	  >>>

and you should see the ".pythonrc.py" message as shown above.

Once that code is loaded, the *debug()* function is defined. To debug
some Python code, you can call that function. Here is an example:

.. code:: console

    >>> import os.path
    >>> debug('os.path.join("a", "b")')
    (/tmp/eval_stringBMzXCQ.py:1 remapped <string>): <module>
    -> 1 os.path.join("a", "b")
    (trepan3k) step
    (/usr/lib/python3.6/posixpath.py:75): join
    -> 68 def join(a, *p):
    (trepan3k) continue
    'a/b'
    >>>

Note in the above, we pass to the *debug()* function a *string*.
That is, we pass `'os.path.join("a", "b")'`, not
`os.path.join("a", "b")` which would have the effect of running the code to be evaluated first *before* calling *debug()*. This is not an error, but debugging evaluating a string, is probably not what you want to do.

*To do: add and document run_call()*

Calling the debugger from your program
======================================

Sometimes it is not feasible to invoke the program from the debugger.
Although the debugger tries to set things up to make it look like your
program is called, sometimes the differences matter. Also, the debugger
adds overhead and slows down your program.

Another possibility, then, is to add statements into your program to call the debugger at the spot in the program you want.

Python 3.7 and later
--------------------

In Python 3.7 and later, a ``breakpoint()`` builtin was added. Add a ``breakpoint()`` function call to your Python code, then set the environment variable ``PYTHONBREAKPOINT`` to ``trepan.api.debug`` before running the program.

For example, here is some Python code:

.. code:: python

        # Code run here; pdb or trepan3k is not loaded yet at all!
        # work, work, work...
        breakpoint() # Get thee to thyne debugger!


Now run Python with ``PYTHONBREAKPOINT`` set to ``trepan.api.debug``:

.. code:: shell

	  PYTHONBREAKPOINT=trepan.api.debug python test/example/gcd-breakpoint.py 3 5

Or, if you don't want to set the variable each time you run some Python code:

.. code:: shell

	  $ export PYTHONBREAKPOINT=trepan.api.debug
	  $ python test/example/gcd-breakpoint.py 3 5


If you want to set up to debug remotely, set ``PYTHONBREAKPOINT`` to ``trepan.api.debug_for_remote_access``:


.. code:: shell

	  export PYTHONBREAKPOINT=trepan.api.debug_for_remote_access

Before Python 3.7
-----------------

Before Python 3.7, you still add statements into your program to call
the debugger at the spot in the program you want. To do this,
``import trepan.api`` and make a call to ``trepan.api.debug()``. For
example:

.. code:: python

        # Code run here trepan3k/trepan3k doesn't even see at all.
        # ...
        from trepan.api import debug
        # trepan is accessible but inactive.
        # work, work, work...
        debug() # Get thee to thyne debugger!

Since *debug()* is a function, a call to it can be nested inside some sort of
conditional statement, allowing one to be very precise about the
conditions you want to debug under. And until first call to *debug()*,
there is no debugger overhead.

*debug()* causes the statement after the call to be stopped at.
Sometimes though, there is no after statement. In this case, adding the named parameter ``step_ignore=0`` will cause the debugger to be entered
inside the *debug()* call:

.. code:: python

          # ...
          def foo():
             # some code
             debug(step_ignore=0) # Stop before even returning from the debug() call
          foo()  # Note there's no statement following foo()

If you want a startup profile to get run, you can pass a list of file names in the option ``start_opts``. For example, let's say I want to set the
formatting style and automatic source code listing in my debugger
session, I would put the trepan debugger commands in a file, say
``/home/rocky/trepan-startup`` and then list that file like this:

.. code:: python

          debug(start_opts={'startup-profile': ["/home/rocky/trepan-startup"]})

Calling the debugger from pytest
================================

The only thing needed here is to ensure you add the ``-s`` option and add an explicit
a ``debug()`` function call; (or a ``breakpoint`` function call after setting environment variable ``PYTHONBREAKPOINT`` to ``trepan.api.debug``).

For example::

    import pytest
    from trepan.api import debug
    def test_function():
        ...
        debug()    # get thee to thyne debugger!
        x = 1
        ...


Set up an exception handler to enter the debugger on a signal
=============================================================

This is really just a variation of one of the other methods. To install
and call the debugger on signal *USR1*:

.. code:: python

          import signal
          def signal_handler(num, f):
	    from trepan.api import debug; debug()
	    return
          signal.signal(signal.SIGUSR1, signal_handler)
          # Go about your business...

However, if you have entered the debugger either by running initially or
previously via a debug() call, trepan has already set up such default
handlers for many of the popular signals, like *SIGINT*. To see what
*trepan3k* has installed use the ``info signals`` command:

::

        (trepan3k) info signals INT
         Signal        Stop   Print   Stack   Pass    Description
         SIGINT        Yes    Yes     No      No      Interrupt
        (trepan3k) info signals
        Signal        Stop    Print   Stack   Pass    Description

        SIGHUP        Yes     Yes     No      No      Hangup
        SIGSYS        Yes     Yes     No      No      Bad system call
        ...

Commonly occurring signals like *CHILD* and unmaskable signals like
*KILL* are not intercepted.

Set up an exception handler allow remote connections
====================================================

The extends the example before to set to allow remote debugging when
the process gets a `USR1` signal

.. code:: python

    import signal

    def signal_handler(num, f):
        from trepan.interfaces import server as Mserver
        from trepan.api import debug
        connection_opts={'IO': 'TCP', 'PORT': 1955}
        intf = Mserver.ServerInterface(connection_opts=connection_opts)
        dbg_opts = {'interface': intf}
        print('Starting TCP server listening on port 1955.')
        debug(dbg_opts=dbg_opts)
        return

    signal.signal(signal.SIGUSR1, signal_handler)
    # Go about your business...

    import time
    import os
    print(os.getpid())
    for i in range(10000):
        time.sleep(0.2)

Now run that:

::

    $ python /tmp/foo.py
    8530

From the above output, we helpfully listed the pid of the Python process we want to debug.

Now in a shell, we send the signal to go into the debugger listening for commands on port 1955. You will have to adjust the
process id.

.. code:: console

    $ kill -USR1 8530   # Adjust the pid to what you see above

And in the shell where we ran `/tmp/foo.py`, you should now see the new output:

.. code:: console

   $ python /tmp/foo.py
   8530
   Starting TCP server listening on port 1955. # This is new

Back to the shell where we issued the `kill -USR1` we can now
attach to the debugger on port 1955:

.. code:: console

   $ trepan3k --client --port 1955
   Connected.
   (/tmp/foo.py:11 @101): signal_handler
   -- 11     return
   (trepan3k*) backtrace
     6    	    connection_opts={'IO': 'TCP', 'PORT': 1955}
     7    	    intf = Mserver.ServerInterface(connection_opts=connection_opts)
     8    	    dbg_opts = {'interface': intf}
     9    	    print('Starting TCP server listening on port 1955.')
    10    	    debug(dbg_opts=dbg_opts)
    11  ->	    return
    12
    13    	signal.signal(signal.SIGUSR1, signal_handler)
    14    	# Go about your business...
   (trepan3k*) list
    ->   0 signal_handler(num=10, f=<frame object at 0x7f9036796050>)
         called from file '/tmp/foo.py' at line 11
    ##   1 <module> file '/tmp/foo.py' at line 20


Startup Profile
===============

A startup profile is a text file that contains debugger commands. For example, it might look like this:

.. code:: console

      $ cat ~/.config/trepanpy/profile/alternate-profile.py
      set autolist
      set different on
      set autoeval on
      set style colorful
      # Note that the below is a debugger command, not an (invalid) Python command
      print "My trepan startup file loaded"
      $


By default, the file ``$HOME/.config/trepan3k/profile/profile.py`` is
loaded, and if a file exists ``trepan3k`` starts up. To change this
default behavior and *not* have the default profile loaded, use the
option ``-n``, or ``--nx`` in the ``trepan3k`` invocation.
