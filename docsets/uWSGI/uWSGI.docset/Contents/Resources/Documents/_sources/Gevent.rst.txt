The Gevent loop engine
======================

`Gevent`_ is an amazing non-blocking Python network library built on top of
``libev`` and ``greenlet``.  Even though uWSGI supports Greenlet as
suspend-resume/greenthread/coroutine library, it requires a lot of effort and
code modifications to work with gevent.  The gevent plugin requires gevent
1.0.0 and :doc:`Async` mode.

.. _Gevent: http://www.gevent.org

Notes
-----

* The :doc:`SignalFramework` is fully working with Gevent mode. Each handler
  will be executed in a dedicated greenlet. Look at :file:`tests/ugevent.py` for
  an example.
* uWSGI multithread mode (``threads`` option) will not work with Gevent.
  Running Python threads in your apps is supported.
* Mixing uWSGI's Async API with gevent's is **EXPLICITLY FORBIDDEN**.

Building the plugin (uWSGI >= 1.4)
----------------------------------

The gevent plugin is compiled in by default when the default profile is used.
Doing the following will install the python plugin as well as the gevent one:

.. code-block:: sh

   pip install uwsgi


Building the plugin (uWSGI < 1.4)
---------------------------------

A 'gevent' build profile can be found in the :file:`buildconf` directory.

.. code-block:: sh

  python uwsgiconfig --build gevent
  # or...
  UWSGI_PROFILE=gevent make
  # or...
  UWSGI_PROFILE=gevent pip install git+git://github.com/unbit/uwsgi.git
  # or...
  python uwsgiconfig --plugin plugins/gevent # external plugin

Running uWSGI in gevent mode
----------------------------

.. code-block:: sh

   uwsgi --gevent 100 --socket :3031 --module myapp

or for a modular build:

.. code-block:: sh

   uwsgi --plugins python,gevent --gevent 100 --socket :3031 --module myapp

the argument of --gevent is the number of async cores to spawn


A crazy example
---------------

The following example shows how to sleep in a request, how to make asynchronous
network requests and how to continue doing logic after a request has been
closed.

.. code-block:: python

  import gevent
  import gevent.socket
  
  def bg_task():
      for i in range(1,10):
          print "background task", i
          gevent.sleep(2)
  
  def long_task():
      for i in range(1,10):
          print i
          gevent.sleep()
  
  def application(e, sr):
      sr('200 OK', [('Content-Type','text/html')])
      t = gevent.spawn(long_task)
      t.join()
      yield "sleeping for 3 seconds...<br/>"
      gevent.sleep(3)
      yield "done<br>"
      yield "getting some ips...<br/>"
      urls = ['www.google.com', 'www.example.com', 'www.python.org', 'projects.unbit.it']
      jobs = [gevent.spawn(gevent.socket.gethostbyname, url) for url in urls]
      gevent.joinall(jobs, timeout=2)
  
      for j in jobs:
          yield "ip = %s<br/>" % j.value
  
      gevent.spawn(bg_task) # this task will go on after request end

Monkey patching
---------------

uWSGI uses native gevent api, so it does not need monkey patching. That said,
your code may need it, so remember to call ``gevent.monkey.patch_all()`` at the
start of your app. As of uWSGI 1.9, the convenience option
``--gevent-monkey-patch`` will do that for you.
Please note that uWSGI does monkey patching before your application **starts**,
not before your application **loads**. So if you are loading other modules
while loading your application you may still need to call
``gevent.monkey.patch_all()`` yourself.

A common example is using ``psycopg2_gevent`` with django. Django will make a
connection to postgres for each thread (storing it in thread locals).

As the uWSGI gevent plugin runs on a single thread this approach will lead to a
deadlock in psycopg. Enabling monkey patch will allow you to map thread locals
to greenlets (though you could avoid full monkey patching and only call
``gevent.monkey.patch_thread()``) and solves the issue:

.. code-block:: python 

   import gevent.monkey
   gevent.monkey.patch_thread()
   import gevent_psycopg2
   gevent_psycopg2.monkey_patch()

or (to monkey patch everything)

.. code-block:: python 

   import gevent.monkey
   gevent.monkey.patch_all()
   import gevent_psycopg2
   gevent_psycopg2.monkey_patch()

Notes on clients and frontends
------------------------------

* If you're testing a WSGI application that generates a stream of data, you
  should know that ``curl`` by default buffers data until a newline. So make sure
  you either disable curl's buffering with the ``-N`` flag or have regular
  newlines in your output.
* If you are using Nginx in front of uWSGI and wish to stream data from your
  app, you'll probably want to disable Nginx's buffering.
  
.. code-block:: nginx
  
    uwsgi_buffering off;
