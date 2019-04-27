uWSGI asynchronous/non-blocking modes (updated to uWSGI 1.9)
============================================================

.. warning::

  Beware! Async modes will not speed up your app, they are aimed at improving concurrency.
  Do not expect that enabling some of the modes will work flawlessly, asynchronous/evented/non-blocking
  systems require app cooperation, so if your app is developed without taking specific async engine rules
  into consideration, you are doing it wrong. Do not trust people suggesting you to blindly use
  async/evented/non-blocking systems!
 
Glossary
--------

uWSGI, following its modular approach, splits async engines into two families.

Suspend/Resume engines
**********************

They simply implement coroutine/green threads techniques. They have no event engine, so you have to use
the one supplied by uWSGI. An Event engine is generally a library exporting primitives for platform-independent
non-blocking I/O (libevent, libev, libuv, etc.). The uWSGI event engine is enabled using the ``--async <n>`` option.

Currently the uWSGI distribution includes the following suspend/resume engines:

* ``uGreen`` - Unbit's green thread implementation (based on ``swapcontext()``)
* ``Greenlet`` - Python greenlet module
* ``Stackless`` - Stackless Python
* ``Fiber`` - Ruby 1.9 fibers

Running the uWSGI async mode without a proper suspend/resume engine will raise a warning, so for a minimal non-blocking app
you will need something like that:

.. code-block:: sh

  uwsgi --async 100 --ugreen --socket :3031

An important aspect of suspend/resume engines is that they can easily destroy your process if it is not aware of them.
Some of the language plugins (most notably Python) have hooks to cooperate flawlessly with coroutines/green threads. Other languages
may fail miserably. Always check the uWSGI mailing list or IRC channel for updated information.

Older uWSGI releases supported an additional system: callbacks.
Callbacks is the approach used by popular systems like node.js. This approach requires **heavy** app cooperation, and for complex projects
like uWSGI dealing with this is extremely complex. For that reason, callback approach **is not supported** (even if technically
possible)
Software based on callbacks (like :doc:`Tornado`) can be used to combine them with some form of suspend engine.

I/O engines (or event systems)
******************************

uWSGI includes an highly optimized evented technology, but can use alternative approaches too.

I/O engines always require some suspend/resume engine, otherwise ugly things happen (the whole uWSGI codebase is coroutine-friendly, so you can
play with stacks pretty easily).

Currently supported I/O engines are:

* :doc:`Tornado`
* :doc:`libuv` (work in progress)
* :doc:`libev` (work in progress)

Loop engines
************

Loop engines are packages/libraries exporting both suspend/resume techniques and an event system. When loaded, they override
the way uWSGI manages connections and signal handlers (uWSGI signals, *not* POSIX signals).

Currently uWSGI supports the following loop engines:

* ``Gevent`` (Python, libev, greenlet)
* ``Coro::AnyEvent`` (Perl, coro, anyevent)

Although they are generally used by a specific language, pure-C uWSGI plugins (like the CGI one) can use them
to increase concurrency without problems.

Async switches
--------------

To enable async mode, you use the ``--async`` option (or some shortcut for it, exported by loop engine plugins).

The argument of the ``--async`` option is the number of "cores" to initialize. Each core can manage a single request, so the more core you
spawn, more requests you will be able to manage (*and more memory you will use*). The job of the suspend/resume engines
is to stop the current request management, move to another core, and eventually come back to the old one (and so on).

Technically, cores are simple memory structures holding request's data, but to give the user the illusion of a multithreaded system
we use that term.

The switch between cores needs app cooperation. There are various ways to accomplish that, and generally, if you are using
a loop engine, all is automagic (or requires very little effort).

.. warning:: 

  If you are in doubt, **do not use async mode**.

Running uWSGI in Async mode
---------------------------

To start uWSGI in async mode, pass the ``--async`` option with the number of "async cores" you want.

.. code-block:: sh

  ./uwsgi --socket :3031 -w tests.cpubound_async --async 10

This will start uWSGI with 10 async cores. Each async core can manage a request, so with this setup you can accept 10 concurrent requests with only one process. You can also start more processes (with the ``--processes`` option), each will have its own pool of async cores.

When using :term:`harakiri` mode, every time an async core accepts a request, the harakiri timer is reset. So even if a request blocks the async system, harakiri will save you.

The ``tests.cpubound_async`` app is included in the source distribution. It's very simple:

.. code-block:: python

  def application(env, start_response):
      start_response('200 OK', [('Content-Type', 'text/html')])
      for i in range(1, 10000):
          yield "<h1>%s</h1>" % i

Every time the application does ``yield`` from the response function, the execution of the app is stopped, and a new request or a previously suspended request on another async core will take over. This means the number of async cores is the number of requests that can be queued.

If you run the ``tests.cpubound_async`` app on a non-async server, it will block all processing: will not accept other requests until the heavy cycle of 10000 ``<h1>``\ s is done.

Waiting for I/O
---------------

If you are not under a loop engine, you can use the uWSGI API to wait for I/O events.

Currently only 2 functions are exported:

* :py:func:`uwsgi.wait_fd_read`
* :py:func:`uwsgi.wait_fd_write`

These functions may be called in succession to wait for multiple file descriptors:

.. code-block:: python

  uwsgi.wait_fd_read(fd0)
  uwsgi.wait_fd_read(fd1)
  uwsgi.wait_fd_read(fd2)
  yield ""  # yield the app, let uWSGI do its magic

Sleeping
--------

On occasion you might want to sleep in your app, for example to throttle bandwidth.

Instead of using the blocking ``time.sleep(N)`` function, use ``uwsgi.async_sleep(N)`` to yield control for N seconds.

.. seealso:: See :file:`tests/sleeping_async.py` for an example.

Suspend/Resume
--------------

Yielding from the main application routine is not very practical, as most of the time your app is more advanced than a simple callable and is formed of tons of functions and various levels of call depth.

Worry not! You can force a suspend (using coroutine/green thread) by simply calling ``uwsgi.suspend()``:

.. code-block:: python

  uwsgi.wait_fd_read(fd0)
  uwsgi.suspend()

``uwsgi.suspend()`` will automatically call the chosen suspend engine (uGreen, greenlet, etc.).

Static files
------------

:doc:`Static file server<StaticFiles>` will automatically use the loaded async engine.
