uGreen -- uWSGI Green Threads
=============================

uGreen is an implementation of `green threads`_ on top of the :doc:`uWSGI async platform<Async>`.

It is very similar to Python's greenlet but built on top of the POSIX ``swapcontext()`` function. To take advantage of uGreen you have to set the number of async cores that will be mapped to green threads.

For example if you want to spawn 30 green threads:

.. code-block:: sh

  ./uwsgi -w tests.cpubound_green -s :3031 --async 30 --ugreen

The ``ugreen`` option will enable uGreen on top of async mode.

Now when you call :py:func:`uwsgi.suspend` in your app, you'll be switched off to another green thread.

.. _green threads: http://en.wikipedia.org/wiki/Green_threads

Security and performance
------------------------

To ensure (relative) isolation of green threads, every stack area is protected by so called "guard pages".

An attempt to write out of the stack area of a green thread will result in a segmentation fault/bus error (and the process manager, if enabled, will respawn the worker without too much damage).

The context switch is very fast, we can see it as:

* On switch
  
  1. Save the Python Frame pointer
  2. Save the recursion depth of the Python environment (it is simply an int)
  3. Switch to the main stack

* On return

  1. Re-set the uGreen stack
  2. Re-set the recursion depth
  3. Re-set the frame pointer

The stack/registers switch is done by the POSIX ``swapcontext()`` call and we don't have to worry about it.


Async I/O
---------

For managing async I/O you can use the Async mode FD wait functions :py:func:`uwsgi.wait_fd_read` and :py:func:`uwsgi.wait_fd_write`.

Stack size
----------

You can choose the uGreen stack size using the ``ugreen-stacksize <pages>`` option. The argument is in pages, not bytes.

Is this better than Greenlet or Stackless Python?
-------------------------------------------------

Weeeeelll... it depends. uGreen is faster (the stack is preallocated) but requires more memory (to allocate a stack area for every core). Stackless and Greenlet probably require less memory... but Stackless requires a heavily patched version of Python. 

If you're heavily invested in making your app as async-snappy as possible, it's always best to do some tests to choose the best one for you. As far as uWSGI is concerned, you can move from async engine to another without changing your code.

What about ``python-coev``?
---------------------------

Lots of uGreen has been inspired by it. The author's way to map Python threads to their implementation allows ``python-coev`` to be a little more "trustworthy" than Stackless Python. However, like Stackless, it requires a patched version of Python... :(

Can I use uGreen to write Comet apps?
-------------------------------------

Yeah! Sure! Go ahead. In the distribution you will find the ``ugreenchat.py`` script. It is a simple/dumb multiuser Comet chat. If you want to test it (for example 30 users) run it with

.. code-block:: sh

  ./uwsgi -s :3031 -w ugreenchat --async 30 --ugreen

The code has comments for every ugreen-related line. You'll need `Bottle`_, an amazing Python web micro framework to use it.

.. _Bottle: http://bottlepy.org/docs/dev/

Psycopg2 improvements
---------------------

uGreen can benefit from the new psycopg2 async extensions and the psycogreen project. See the :file:`tests/psycopg2_green.py` and :file:`tests/psycogreen_green.py` files for examples.