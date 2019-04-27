The uWSGI Signal Framework
==========================

.. warning:: Raw usage of uwsgi signals is for advanced users only. You should see :doc:`PythonDecorators` for a more elegant abstraction.

.. note:: uWSGI Signals have _nothing_ in common with UNIX/Posix signals (if you are looking for those, :doc:`Management` is your page).

Over time, your uWSGI stack is growing, you add spoolers, more processes, more plugins, whatever. The more features you add the more you need all of these components to speak to each other.

Another important task for today's rich/advanced web apps is to respond to different events. An event could be a file modification, a new cluster node popping up, another one (sadly) dying, a timer having elapsed... whatever you can imagine.

Communication and event management are all managed by the same subsystem -- the uWSGI signal framework.

uWSGI signals are managed with sockets, so they are *fully reliable*. When you send an uWSGI signal, you can be sure that it will be delivered.

The Signals table
-----------------

Signals are simple *1 byte* messages that are routed by the master process to workers and spoolers.

When a worker receives a signal it searches the signals table for the corresponding handler to execute.

The signal table is shared by all workers (and protected against race conditions by a shared lock).

Every uWSGI process (mainly the master though) can write into it to set signal handlers and recipient processes.

.. warning::
  
  Always pay attention to who will run the signal handler. It must have access to the handler itself.
  This means that if you define a new function in ``worker1`` and register it as a signal handler, only ``worker1`` can run it.
  The best way to register signals is defining them in the master, so (thanks to ``fork()``) all workers see them.

Defining signal handlers
------------------------

To manage the signals table the uWSGI API exposes one simple function, :py:meth:`uwsgi.register_signal`.

These are two simple examples of defining signal table items, in Python and Lua.

.. code-block:: py

    import uwsgi
    
    def hello_signal(num):
        print "i am the signal %d" % num
    
    def hello_signal2(num):
        print "Hi, i am the signal %d" % num
    
    # define 2 signal table items (30 and 22)
    uwsgi.register_signal(30, "worker", hello_signal)
    uwsgi.register_signal(22, "workers", hello_signal2)

.. code-block:: lua

    function hello_signal(sig)
        print("i am Lua, received signal " .. sig ..)
    end
    
    # define a single signal table item (signal 1)
    uwsgi.register_signal(1, "worker", hello_signal)
    

Signals targets
---------------

The third argument of uwsgi.register_signal is the 'signal target'.

It instructs the system about 'who' must run the handler. By default the target is 'worker' that means 'the first available worker'. The following targets are available:

- workerN (run the signal handler only on worker N)
- worker/worker0 (the default one, run the signal handler on the first available worker)
- workers (run the signal handler on all the workers)
- active-workers (run the signal handlers on all the active [non-cheaped] workers)
- spooler (run the signal on the first available spooler)
- mules (run the signal handler on all of the mules)
- muleN (run the signal handler on mule N)
- mule/mule0 (run the signal handler on the first available mule)
- farmN/farm_XXX (run the signal handler in the mule farm N or named XXX)

Raising signals
---------------

Signals may be raised using :py:meth:`uwsgi.signal`. When you send a signal, it is copied into the master's queue. The master will then check the signal table and dispatch the messages.

External events
---------------

The most useful feature of uWSGI signals is that they can be used to announce external events.

At the time of writing the available external events are

* filesystem modifications
* timers/rb_timers
* cron

Other events are exposed via plugins, like https://github.com/unbit/uwsgi-pgnotify raising signal whenever a postgres notification channel is ready.

Filesystem modifications
^^^^^^^^^^^^^^^^^^^^^^^^

To map a specific file/directory modification event to a signal you can use :py:meth:`uwsgi.add_file_monitor`.

An example:

.. code-block:: py

    import uwsgi
    
    def hello_file(num):
            print "/tmp has been modified !!!"
    
    uwsgi.register_signal(17, "worker", hello_file)
    uwsgi.add_file_monitor(17, "/tmp")

From now on, every time ``/tmp`` is modified, signal 17 will be raised and ``hello_file`` will be run by the first available worker.

Timers
^^^^^^ 

Timers are another useful feature in web programming -- for instance to clear sessions and shopping carts and what-have-you.

Timers are implemented using kernel facilities (most notably kqueue on BSD systems and timerfd() on modern Linux kernels). uWSGI also contains support for rb_timers, timers implemented in user space using red-black trees.

To register a timer, use :meth:`uwsgi.add_timer`. To register an rb_timer, use :meth:`uwsgi.add_rb_timer`.

.. code-block:: py

    import uwsgi
    
    def hello_timer(num):
            print "2 seconds elapsed, signal %d raised" % num
    
    def oneshot_timer(num):
            print "40 seconds elapsed, signal %d raised. You will never see me again." % num
    
    
    uwsgi.register_signal(26, "worker", hello_timer)
    uwsgi.register_signal(30, "", oneshot_timer)
    
    uwsgi.add_timer(26, 2) # never-ending timer every 2 seconds
    uwsgi.add_rb_timer(30, 40, 1) # one shot rb timer after 40 seconds
    
Signal 26 will be raised every 2 seconds and handled by the first available worker.
Signal 30 will be raised after 40 seconds and executed only once.

signal_wait and signal_received
-------------------------------

Unregistered signals (those without an handler associated) will be routed to the first available worker to use the :meth:`uwsgi.signal_wait` function.

.. code-block:: xxx

    uwsgi.signal_wait()
    signum = uwsgi.signal_received()

You can combine external events (file monitors, timers...) with this technique to implement event-based apps. A good example is a chat server where every core waits for text sent by users.

You can also wait for specific (even registered) signals by passing a signal number to ``signal_wait``.

Todo/Known Issues
-----------------

* Signal table entry cannot be removed (this will be fixed soon)
* Iterations work only with rb_timers
* uwsgi.signal_wait() does not work in async mode (will be fixed)
* Add iterations to file monitoring (to allow one-shot event as timers)
