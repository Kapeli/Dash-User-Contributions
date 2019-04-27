The Tornado loop engine
=======================

Available from: ```uWSGI 1.9.19-dev```

Supported suspend engines: ```greenlet```

Supported CPython versions: ```all of tornado supported versions```


The tornado loop engine allows you to integrate your uWSGI stack with the Tornado IOLoop class.

Basically every I/O operation of the server is mapped to a tornado IOLoop callback. Making RPC, remote caching, or simply writing responses
is managed by the Tornado engine.

As uWSGI is not written with a callback-based programming approach, integrating with those kind of libraries requires some form of "suspend" engine (green threads/coroutines)

Currently the only supported suspend engine is the "greenlet" one. Stackless python could work too (needs testing).

PyPy is currently not supported (albeit technically possible thanks to continulets). Drop a mail to Unbit staff if you are interested.

Why ?
*****
The Tornado project includes a simple WSGI server by itself. In the same spirit of the Gevent plugin, the purpose of Loop engines is allowing external prejects
to use (and abuse) the uWSGI api, for better performance, versatility and (maybe the most important thing) resource usage.

All of the uWSGI subsystems are available (from caching, to websockets, to metrics) in your tornado apps, and the WSGI engine is the battle-tested uWSGI one.


Installation
************

The tornado plugin is currently not built-in by default. To have both tornado and greenlet in a single binary you can do

.. code-block:: sh

   UWSGI_EMBED_PLUGINS=tornado,greenlet pip install tornado greenlet uwsgi
   
or (from uWSGI sources, if you already have tornado and greenlet installed)

.. code-block:: sh

   UWSGI_EMBED_PLUGINS=tornado,greenlet make

Running it
**********

The ``--tornado`` option is exposed by the tornado plugin, allowing you to set optimal parameters:

.. code-block:: sh

   uwsgi --http-socket :9090 --wsgi-file myapp.py --tornado 100 --greenlet
   
this will run a uWSGI instance on http port 9090 using tornado as I/O (and time) management and greenlet as suspend engine

100 async cores are allocated, allowing you to manage up to 100 concurrent requests

Integrating WSGI with the tornado api
*************************************

For the way WSGI works, dealing with callback based programming is pretty hard (if not impossible).

Thanks to greenlet we can suspend the execution of our WSGI callable until a tornado IOLoop event is available:

.. code-block:: py

   from tornado.httpclient import AsyncHTTPClient
   import greenlet
   import functools
   
   # this gives us access to the main IOLoop (the same used by uWSGI)
   from tornado.ioloop import IOLoop
   io_loop = IOLoop.instance()
   
   # this is called at the end of the external HTTP request
   def handle_request(me, response):
       if response.error:
           print("Error:", response.error)
       else:
           me.result = response.body
       # back to the WSGI callable
       me.switch()
           
    def application(e, sr):
        me = greenlet.getcurrent()
        http_client = AsyncHTTPClient()
        http_client.fetch("http://localhost:9191/services", functools.partial(handle_request, me))
        # suspend the execution until an IOLoop event is available
        me.parent.switch()
        sr('200 OK', [('Content-Type','text/plain')])
        return me.result

Welcome to Callback-Hell
************************

As always, it is not the job of uWSGI to judge programming approaches. It is a tool for sysadmins, and sysadmins should be tolerant with developers choices.

One of the things you will pretty soon experiment with this approach to programming is the callback-hell.

Let's extend the previous example to wait 10 seconds before sending back the response to the client

.. code-block:: py

   from tornado.httpclient import AsyncHTTPClient
   import greenlet
   import functools
   
   # this gives us access to the main IOLoop (the same used by uWSGI)
   from tornado.ioloop import IOLoop
   io_loop = IOLoop.instance()
   
   def sleeper(me):
       #TIMED OUT
       # finally come back to WSGI callable
       me.switch()
   
   # this is called at the end of the external HTTP request
   def handle_request(me, response):
       if response.error:
           print("Error:", response.error)
       else:
           me.result = response.body
       # add another callback in the chain
       me.timeout = io_loop.add_timeout(time.time() + 10, functools.partial(sleeper, me))
           
    def application(e, sr):
        me = greenlet.getcurrent()
        http_client = AsyncHTTPClient()
        http_client.fetch("http://localhost:9191/services", functools.partial(handle_request, me))
        # suspend the execution until an IOLoop event is available
        me.parent.switch()
        # unregister the timer
        io_loop.remove_timeout(me.timeout)
        sr('200 OK', [('Content-Type','text/plain')])
        return me.result


here we have chained two callbacks, with the last one being responsable for giving back control to the WSGI callable

The code could looks ugly or overcomplex (compared to other approaches like gevent) but this is basically the most efficient way to
increase concurrency (both in terms of memory usage and performance). Technologies like node.js are becoming popular thanks to the results they allow
to accomplish.


WSGI generators (aka yield all over the place)
**********************************************

Take the following WSGI app:

.. code-block:: py

   def application(e, sr):
       sr('200 OK', [('Content-Type','text/html')])
       yield "one"
       yield "two"
       yield "three"

if you have already played with uWSGI async mode, you knows that every yield internally calls the used suspend engine (greenlet.switch() in our case).

That means we will enter the tornado IOLoop engine soon after having called "application()". How we can give the control back to our callable if we are not waiting for events ?

The uWSGI async api has been extended to support the "schedule_fix" hook. It allows you to call a hook soon after the suspend engine has been called.

In the tornado's case this hook is mapped to something like:

.. code-block:: py

   io_loop.add_callback(me.switch)
   
in this way after every yield a me.switch() function is called allowing the resume of the callable.

Thanks to this hook you can transparently host standard WSGI applications without changing them.


Binding and listening with Tornado
**********************************

The Tornado IOLoop is executed after fork() in every worker. If you want to bind to network addresses with Tornado, remember
to use different ports for each workers:

.. code-block:: py

   from uwsgidecorators import *
   import tornado.web

   # this is our Tornado-managed app
   class MainHandler(tornado.web.RequestHandler):
       def get(self):
           self.write("Hello, world")

   t_application = tornado.web.Application([
       (r"/", MainHandler),
   ])
   
   # here happens the magic, we bind after every fork()
   @postfork
   def start_the_tornado_servers():
       application.listen(8000 + uwsgi.worker_id())
       
   # this is our WSGI callable managed by uWSGI
   def application(e, sr):
       ...
   
   
Remember: do no start the IOLoop class. uWSGI will do it by itself as soon as the setup is complete
