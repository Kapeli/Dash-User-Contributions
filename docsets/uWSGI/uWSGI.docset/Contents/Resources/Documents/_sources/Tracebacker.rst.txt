Python Tracebacker
==================

.. versionadded:: 1.3-dev

Usually if you want to get a real-time traceback from your app you'd have to modify your code to add a hook or entry point for that as described on the :doc:`TipsAndTricks` page.

Starting from 1.3-dev, uWSGI includes a similar technique allowing you to get realtime traceback via a UNIX socket.

To enable the tracebacker, add the option ``py-tracebacker=<socket>`` where ``<socket>`` is the _basename_ for the created UNIX sockets.

If you have 4 uWSGI workers and you add ``py-tracebacker=/tmp/tbsocket``, four sockets named ``/tmp/tbsocket1`` through ``/tmp/tbsocket4`` will be created.

Connecting to one of them will return the current traceback of the threads running in the worker. To connect to those sockets you can use whatever application or method you like the best, but uWSGI includes a convenience option ``connect-and-read`` you can use::

  uwsgi --connect-and-read /tmp/tbsocket1

An example
----------

Let's write a silly test application called ``slow.py``:

.. code-block:: python

  import time  
  
  def dormi():
    time.sleep(60)
  
  def dormi2():
    dormi()
  
  def dormi3():
    dormi2()

  def dormi4():
    dormi3()
  
  def dormi5():
    dormi4()
  
  def application(e, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    dormi5()
    return "hello"

And then run it::

  uwsgi --http :8080 -w slow --master --processes 2 --threads 4 --py-tracebacker /tmp/tbsocket.

Then make a bunch of requests into it::

  curl http://localhost:8080 &
  curl http://localhost:8080 &
  curl http://localhost:8080 &
  curl http://localhost:8080 &

Now, while these requests are running (they'll take pretty much exactly a minute to complete each), you can retrieve the traceback for, let's say, the two first workers::

  ./uwsgi --connect-and-read /tmp/tbsocket.1
  ./uwsgi --connect-and-read /tmp/tbsocket.2

The tracebacker output will be something like this::

  *** uWSGI Python tracebacker output ***
  
  thread_id = uWSGIWorker1Core1 filename = ./slow.py lineno = 22 function = application line = dormi5()
  thread_id = uWSGIWorker1Core1 filename = ./slow.py lineno = 14 function = dormi5 line = def dormi5(): dormi4()
  thread_id = uWSGIWorker1Core1 filename = ./slow.py lineno = 13 function = dormi4 line = def dormi4(): dormi3()
  thread_id = uWSGIWorker1Core1 filename = ./slow.py lineno = 12 function = dormi3 line = def dormi3(): dormi2()
  thread_id = uWSGIWorker1Core1 filename = ./slow.py lineno = 11 function = dormi2 line = def dormi2(): dormi()
  thread_id = uWSGIWorker1Core1 filename = ./slow.py lineno = 9 function = dormi line = time.sleep(60)
  
  thread_id = uWSGIWorker1Core3 filename = ./slow.py lineno = 22 function = application line = dormi5()
  thread_id = uWSGIWorker1Core3 filename = ./slow.py lineno = 14 function = dormi5 line = def dormi5(): dormi4()
  thread_id = uWSGIWorker1Core3 filename = ./slow.py lineno = 13 function = dormi4 line = def dormi4(): dormi3()
  thread_id = uWSGIWorker1Core3 filename = ./slow.py lineno = 12 function = dormi3 line = def dormi3(): dormi2()
  thread_id = uWSGIWorker1Core3 filename = ./slow.py lineno = 11 function = dormi2 line = def dormi2(): dormi()
  thread_id = uWSGIWorker1Core3 filename = ./slow.py lineno = 9 function = dormi line = time.sleep(60)
  
  thread_id = MainThread filename = ./slow.py lineno = 22 function = application line = dormi5()
  thread_id = MainThread filename = ./slow.py lineno = 14 function = dormi5 line = def dormi5(): dormi4()
  thread_id = MainThread filename = ./slow.py lineno = 13 function = dormi4 line = def dormi4(): dormi3()
  thread_id = MainThread filename = ./slow.py lineno = 12 function = dormi3 line = def dormi3(): dormi2()
  thread_id = MainThread filename = ./slow.py lineno = 11 function = dormi2 line = def dormi2(): dormi()
  thread_id = MainThread filename = ./slow.py lineno = 9 function = dormi line = time.sleep(60)

Combining the tracebacker with Harakiri
---------------------------------------

If a request is killed by the :term:`harakiri<Harakiri>` feature, a traceback is automatically logged during the Harakiri phase.