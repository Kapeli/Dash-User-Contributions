Offloading Websockets and Server-Sent Events AKA "Combine them with Django safely"
==================================================================================

Author: Roberto De Ioris

Date: 20140315

Disclaimer
----------

This article shows a pretty advanced way for combining websockets (or sse) apps with Django in a "safe way". It will not show you
how cool websockets and sse are, or how to write better apps with them, it is an attempt to try to avoid bad practices with them.

In my opinion the Python web-oriented world is facing a communication/marketing problem: There is a huge number of people
running heavily blocking apps (like Django) on non-blocking technologies (like gevent) only because someone told them it is cool and will solve all of their scaling issues.

This is completely WRONG, DANGEROUS and EVIL, you cannot mix blocking apps with non-blocking engines, even a single, ultra-tiny blocking part
can potentially destroy your whole stack. As I have already said dozens of time, if your app is 99.9999999% non-blocking, it is still blocking.

And no, monkey-patching on your Django app is not magic. Unless you are using pretty-customized database adapters, tuned for working in a non-blocking way, you are doing it wrong.

At the cost of looking a huber-asshole, I strongly suggest you completely ignore people suggesting you move your Django app to gevent, eventlet, tornado or whatever, without warning you about
the hundreds of problems you may encounter.

Having said that, I love gevent, it is probably the best (with perl's Coro::AnyEvent) supported loop engine in the uWSGI project. So in this article I will use gevent for managing websocket/sse traffic and plain multiprocessing for the Django part.

If this last sentence looks like nonsense to you, you probably do not know what uWSGI offloading is...


uWSGI offloading
----------------

The concept is not a new thing, or a uWSGI specific one. Projects like nodejs or twisted have used it for ages.

.. note:: an example of a webapp serving a static file is not very interesting, nor the best thing to show, but will be useful later, when presenting a real-world scenario with X-Sendfile

Immagine this simple WSGI app:

.. code-block:: python

   def application(env, start_response):
       start_response('200 OK',[('Content-Type','text/plain')])
       f = open('/etc/services')
       # do not do it, if the file is 4GB it will allocate 4GB of memory !!!
       yield f.read()

This will simply return the content of /etc/services. It is a pretty tiny file, so in few milliseconds your process will be ready to process another request.

What if /etc/services is 4 gigabytes? Your process (or thread) will be blocked for several seconds (even minutes), and will not be able to manage another request
until the file is completely transferred.

Wouldn't it be cool if you could tell another thread to send the file for you, so you will be able to manage another request?

Offloading is exactly this: it will give you one ore more threads for doing simple and slow task for you. Which kind of tasks? All of those that can be managed
in a non-blocking way, so a single thread can manage thousand of transfers for you.

You can see it as the DMA engine in your computer, your CPU will program the DMA to transfer memory from a controller to the RAM, and then will be freed to accomplish another task while the DMA works in background.

To enable offloading in uWSGI you only need to add the ``--offload-threads <n>`` option, where <n> is the number of threads per-process to spawn. (generally a single thread will be more than enough, but if you want to use/abuse your multiple cpu cores feel free to increase it)

Once offloading is enabled, uWSGI will automatically use it whenever it detects that an operation can be offloaded safely.

In the python/WSGI case any use of wsgi.file_wrapper will be offloaded automatically, as well as when you use the uWSGI proxy features for passing requests to other server speaking the uwsgi or HTTP protocol.

A cool example (showed even in the Snippets page of uWSGI docs) is implementing an offload-powered X-Sendfile feature:

.. code-block:: ini

   [uwsgi]
   ; load router_static plugin (compiled in by default in monolithic profiles)
   plugins = router_static
   
   ; spawn 2 offload threads
   offload-threads = 2
   
   ; files under /etc can be safely served (DANGEROUS !!!)
   static-safe = /etc
   
   ; collect the X-Sendfile response header as X_SENDFILE var
   collect-header = X-Sendfile X_SENDFILE
   
   ; if X_SENDFILE is not empty, pass its value to the "static" routing action (it will automatically use offloading if available)
   response-route-if-not = empty:${X_SENDFILE} static:${X_SENDFILE}

   ; now the classic options
   plugins = python
   ; bind to HTTP port 8080
   http-socket = :8080
   ; load a simple wsgi-app
   wsgi-file = myapp.py
  
  
Now in our app we can X-Sendfile to send static files without blocking:

.. code-block:: python

   def application(env, start_response):
       start_response('200 OK',[('X-Sendfile','/etc/services')])
       return []


A very similar concept will be used in this article: We will use a normal Django to setup our session, to authorize the user and whatever (that is fast) you want, then we will return a special header that will instruct uWSGI to offload the connection to another uWSGI instance (listening on a private socket) that will manage the websocket/sse transaction using gevent in a non-blocking way.

Our SSE app
-----------

The SSE part will be very simple, a gevent-based WSGI app will send the current time every second:

.. code-block:: python

   from sse import Sse
   import time

   def application(e, start_response):
       print e
       # create the SSE session
       session = Sse()
       # prepare HTTP headers
       headers = []
       headers.append(('Content-Type','text/event-stream'))
       headers.append(('Cache-Control','no-cache'))
       start_response('200 OK', headers)
       # enter the loop
       while True:
           # monkey patching will prevent sleep() blocking
           time.sleep(1)
           # add the message
           session.add_message('message', str(time.time()))
           # send to the client
           yield str(session)
           
Let's run it on /tmp/foo UNIX socket (save the app as sseapp.py)

.. code-block:: sh

   uwsgi --wsgi-file sseapp.py --socket /tmp/foo --gevent 1000 --gevent-monkey-patch
   
(monkey patching is required for time.sleep(), feel free to use gevent primitives for sleeping if you want/prefer)

The (boring) HTML/Javascript
----------------------------

.. code-block:: html

   <html>
       <head>
       </head>
       <body>
         <h1>Server sent events</h1>
         <div id="event"></div>
         <script type="text/javascript">

         var eventOutputContainer = document.getElementById("event");
         var evtSrc = new EventSource("/subscribe");

         evtSrc.onmessage = function(e) {
             console.log(e.data);
             eventOutputContainer.innerHTML = e.data;
         };

         </script>
       </body>
     </html>

It is very simple, it will connect to /subscribe and will start waiting for events.

The Django view
---------------

Our django view, will be very simple, it will simply generate a special response header (we will call it X-Offload-to-SSE) with the username of the logged user as its value:

.. code-block:: python

   def subscribe(request):
       response = HttpResponse()
       response['X-Offload-to-SSE'] = request.user
       return response
       
Now we are ready for the "advanced" part.


Let's offload the SSE transaction
---------------------------------

The configuration could look a bit complex but it is the same concept of the X-Sendfile seen before:

.. code-block:: ini

   [uwsgi]
   ; the boring part
   http-socket = :9090
   offload-threads = 2
   wsgi-file = sseproject/wsgi.py
   
   ; collect X-Offload-to-SSE header and store in var X_OFFLOAD
   collect-header = X-Offload-to-SSE X_OFFLOAD
   ; if X_OFFLOAD is defined, do not send the headers generated by Django
   response-route-if-not = empty:${X_OFFLOAD} disableheaders:
   ; if X_OFFLOAD is defined, offload the request to the app running on /tmp/foo
   response-route-if-not = empty:${X_OFFLOAD} uwsgi:/tmp/foo,0,0
   
The only "new' part is the use of ``disableheaders`` routing action. It is required otherwise the headers generated by Django
will be sent along the ones generated by the gevent-based app.

You could avoid it (remember that ``disableheaders`` has been added only in 2.0.3) removing the call to start_response() in the gevent app (at the risk of being cursed by some WSGI-god) and changing the Django view
to set the right headers:

.. code-block:: python

   def subscribe(request):
       response = HttpResponse()
       response['Content-Type'] = 'text/event-stream'
       response['X-Offload-to-SSE'] = request.user
       return response
       
Eventually you may want to be more "streamlined" and simply detect for 'text/event-stream' content_type presence:

.. code-block:: ini

   [uwsgi]
   ; the boring part
   http-socket = :9090
   offload-threads = 2
   wsgi-file = sseproject/wsgi.py
   
   ; collect Content-Type header and store in var CONTENT_TYPE
   collect-header = Content-Type CONTENT_TYPE
   ; if CONTENT_TYPE is 'text/event-stream', forward the request
   response-route-if = equal:${CONTENT_TYPE};text/event-stream uwsgi:/tmp/foo,0,0
   
   
Now, how to access the username of the Django-logged user in the gevent app?

You should have noted that the gevent-app prints the content of the WSGI environ on each request. That environment is the same
of the Django app + the collected headers. So accessing environ['X_OFFLOAD'] will return the logged username. (obviously in the second example, where the content type is used, the variable with the username is no longer collected, so you should fix it)

You can pass all of the information you need using the same approach, you can collect all of the vars you need and so on.

You can even add variables at runtime:


.. code-block:: ini

   [uwsgi]
   ; the boring part
   http-socket = :9090
   offload-threads = 2
   wsgi-file = sseproject/wsgi.py
   
   ; collect Content-Type header and store in var CONTENT_TYPE
   collect-header = Content-Type CONTENT_TYPE
   
   response-route-if = equal:${CONTENT_TYPE};text/event-stream addvar:FOO=BAR
   response-route-if = equal:${CONTENT_TYPE};text/event-stream addvar:TEST1=TEST2
   
   ; if CONTENT_TYPE is 'text/event-stream', forward the request
   response-route-if = equal:${CONTENT_TYPE};text/event-stream uwsgi:/tmp/foo,0,0
   
Or (using goto for better readability):

.. code-block:: ini

   [uwsgi]
   ; the boring part
   http-socket = :9090
   offload-threads = 2
   wsgi-file = sseproject/wsgi.py
   
   ; collect Content-Type header and store in var CONTENT_TYPE
   collect-header = Content-Type CONTENT_TYPE
   
   response-route-if = equal:${CONTENT_TYPE};text/event-stream goto:offload
   response-route-run = last:
   
   response-route-label = offload
   response-route-run = addvar:FOO=BAR
   response-route-run = addvar:TEST1=TEST2
   response-route-run = uwsgi:/tmp/foo,0,0


Simplifying things using the uwsgi api (>= uWSGI 2.0.3)
-------------------------------------------------------

While dealing with headers is pretty HTTP friendly, uWSGI 2.0.3 added the possibility to define per-request variables
directly in your code.

This allows a more "elegant" approach (even if highly non-portable):

.. code-block:: python

   import uwsgi
   
   def subscribe(request):
       uwsgi.add_var("LOGGED_IN_USER", request.user)
       uwsgi.add_var("USER_IS_UGLY", "probably")
       uwsgi.add_var("OFFLOAD_TO_SSE", "y")
       uwsgi.add_var("OFFLOAD_SERVER", "/tmp/foo")
       return HttpResponse()
       
Now the config can change to something more gentle:

.. code-block:: ini

   ; the boring part
   http-socket = :9090
   offload-threads = 2
   wsgi-file = sseproject/wsgi.py
   
   ; if OFFLOAD_TO_SSE is 'y', do not send the headers generated by Django
   response-route-if = equal:${OFFLOAD_TO_SSE};y disableheaders:
   ; if OFFLOAD_TO_SSE is 'y', offload the request to the app running on 'OFFLOAD_SERVER'
   response-route-if = equal:${OFFLOAD_TO_SSE};y uwsgi:${OFFLOAD_SERVER},0,0
   
Have you noted how we allowed the Django app to set the backend server to use using a request variable?

Now we can go even further. We will not use the routing framework (except for disabling headers generation):

.. code-block:: python

   import uwsgi
   
   def subscribe(request):
       uwsgi.add_var("LOGGED_IN_USER", request.user)
       uwsgi.add_var("USER_IS_UGLY", "probably")
       uwsgi.route("uwsgi", "/tmp/foo,0,0")
       return HttpResponse()
       
and a simple:

.. code-block:: ini

   ; the boring part
   http-socket = :9090
   offload-threads = 2
   wsgi-file = sseproject/wsgi.py
   
   response-route = ^/subscribe disableheaders:


What about Websockets ?
-----------------------

We have seen how to offload SSE (that are mono-directional). We can offload websockets too (that are bidirectional).

The concept is the same, you only need to ensure (as before) that no headers are sent by django, (otherwise the websocket handshake will fail) and then you
can change your gevent app:

.. code-block:: python

   import time
   import uwsgi

   def application(e, start_response):
       print e
       uwsgi.websocket_handshake()
       # enter the loop
       while True:
           # monkey patching will prevent sleep() to block
           time.sleep(1)
           # send to the client
           uwsgi.websocket_send(str(time.time()))
           
Using redis or uWSGI caching framework
--------------------------------------

Request vars are handy (and funny), but they are limited (see below). If you need to pass a big amount of data between Django and the sse/websocket app, Redis
is a great way (and works perfectly with gevent). Basically you store infos from django to redis and than you pass only the hash key (via request vars) to the sse/websocket app.

The same can be accomplished with the uWSGI caching framework, but take into account redis has a lot of data primitives, while uWSGI only supports key->value items.

Common pitfalls
---------------

* The amount of variables you can add per-request is limited by the uwsgi packet buffer (default 4k). You can increase it up to 64k with the --buffer-size option.

* This is the whole point of this article: do not use the Django ORM in your gevent apps unless you know what you are doing!!! (read: you have a django database adapter that supports gevent and does not suck compared to the standard ones...)

* Forget about finding a way to disable headers generation in django. This is a "limit/feature" of its WSGI adapter, use the uWSGI facilities (if available) or do not generate headers in your gevent app. Eventually you can modify wsgi.py in this way:

.. code-block:: python

   """
   WSGI config for sseproject project.

   It exposes the WSGI callable as a module-level variable named ``application``.

   For more information on this file, see
   https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
   """

   import os
   os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sseproject.settings")

   from django.core.wsgi import get_wsgi_application
   django_application = get_wsgi_application()
   
   def fake_start_response(status, headers, exc_info=None):
       pass
   
   def application(environ, start_response):
       if environ['PATH_INFO'] == '/subscribe':
           return django_application(environ, fake_start_response)
       return django_application(environ, start_response)
