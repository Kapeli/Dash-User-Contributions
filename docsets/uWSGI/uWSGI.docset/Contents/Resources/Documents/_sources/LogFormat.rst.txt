Formatting uWSGI requests logs 
==============================

uWSGI has a ``--logformat`` option for building custom request loglines. The
syntax is simple:

.. code-block:: ini

   [uwsgi]
   logformat = i am a logline reporting "%(method) %(uri) %(proto)" returning with status %(status)

All of the variables marked with ``%()`` are substituted using specific rules.
Three kinds of logvars are defined ("offsetof", functions, and user-defined).

offsetof
********

These are taken blindly from the internal ``wsgi_request`` structure of the current request.

* ``%(uri)`` -> REQUEST_URI
* ``%(method)`` -> REQUEST_METHOD
* ``%(user)`` -> REMOTE_USER
* ``%(addr)`` -> REMOTE_ADDR
* ``%(host)`` -> HTTP_HOST
* ``%(proto)`` -> SERVER_PROTOCOL
* ``%(uagent)`` -> HTTP_USER_AGENT (starting from 1.4.5)
* ``%(referer)`` -> HTTP_REFERER (starting from 1.4.5)

functions
*********

These are simple functions called for generating the logvar value:

* ``%(status)`` -> HTTP response status code
* ``%(micros)`` -> response time in microseconds
* ``%(msecs)`` -> response time in milliseconds
* ``%(secs)`` -> response time in seconds
* ``%(time)`` -> timestamp of the start of the request
* ``%(ctime)`` -> ctime of the start of the request
* ``%(epoch)`` -> the current time in Unix format
* ``%(size)`` -> response body size + response headers size (since 1.4.5)
* ``%(ltime) -> human-formatted (Apache style)`` request time (since 1.4.5)
* ``%(hsize)`` -> response headers size (since 1.4.5)
* ``%(rsize)`` -> response body size (since 1.4.5)
* ``%(cl)`` -> request content body size (since 1.4.5)
* ``%(pid)`` -> pid of the worker handling the request (since 1.4.6)
* ``%(wid)`` -> id of the worker handling the request (since 1.4.6)
* ``%(switches)`` -> number of async switches (since 1.4.6)
* ``%(vars)`` -> number of CGI vars in the request (since 1.4.6)
* ``%(headers)`` -> number of generated response headers (since 1.4.6)
* ``%(core)`` -> the core running the request (since 1.4.6)
* ``%(vsz)`` -> address space/virtual memory usage (in bytes) (since 1.4.6)
* ``%(rss)`` -> RSS memory usage (in bytes) (since 1.4.6)
* ``%(vszM)`` -> address space/virtual memory usage (in megabytes) (since 1.4.6)
* ``%(rssM)`` -> RSS memory usage (in megabytes) (since 1.4.6)
* ``%(pktsize)`` -> size of the internal request uwsgi packet (since 1.4.6)
* ``%(modifier1)`` -> modifier1 of the request (since 1.4.6)
* ``%(modifier2)`` -> modifier2 of the request (since 1.4.6)
* ``%(metric.XXX)`` -> access the XXX metric value (see :doc:`Metrics`)
* ``%(rerr)`` -> number of read errors for the request (since 1.9.21)
* ``%(werr)`` -> number of write errors for the request (since 1.9.21)
* ``%(ioerr)`` -> number of write and read errors for the request (since 1.9.21)
* ``%(tmsecs)`` -> timestamp of the start of the request in milliseconds since the epoch (since 1.9.21)
* ``%(tmicros)`` -> timestamp of the start of the request in microseconds since the epoch (since 1.9.21)
* ``%(var.XXX)`` -> the content of request variable XXX (like var.PATH_INFO or var.HTTP_X_MY_HEADER for headers from request, available from 1.9.21)

User-defined logvars
********************

You can define logvars within your request handler. These variables live only
per-request.

.. code-block:: python

   import uwsgi
   def application(env, start_response):
       uwsgi.set_logvar('foo', 'bar')
       # returns 'bar'
       print uwsgi.get_logvar('foo')
       uwsgi.set_logvar('worker_id', str(uwsgi.worker_id()))
       ...

With the following log format you will be able to access code-defined logvars:

.. code-block:: sh

   uwsgi --logformat 'worker id = %(worker_id) for request "%(method) %(uri) %(proto)" test = %(foo)'

uWSGI default logging
*********************

To generate uWSGI-compatible logs:

.. code-block:: ini

   [uwsgi]
   ...
   log-format = [pid: %(pid)|app: -|req: -/-] %(addr) (%(user)) {%(vars) vars in %(pktsize) bytes} [%(ctime)] %(method) %(uri) => generated %(rsize) bytes in %(msecs) msecs (%(proto) %(status)) %(headers) headers in %(hsize) bytes (%(switches) switches on core %(core))

   ...

Apache-style combined request logging
*************************************

To generate Apache-compatible logs:

.. code-block:: ini

   [uwsgi]
   ...
   log-format = %(addr) - %(user) [%(ltime)] "%(method) %(uri) %(proto)" %(status) %(size) "%(referer)" "%(uagent)"
   ...

Hacking logformat
*****************

(Updated to 1.9.21)

You can register new "logchunk" (the function to call for each logformat symbol) with

.. code-block:: c

   struct uwsgi_logchunk *uwsgi_register_logchunk(char *name, ssize_t (*func)(struct wsgi_request *, char **), int need_free);

* ``name`` -- the name of the symbol
* ``need_free`` -- if 1, means the pointer set by ``func`` must be free()d
* ``func`` -- the function to call in the log handler

.. code-block:: c

   static ssize_t uwsgi_lf_foobar(struct wsgi_request *wsgi_req, char **buf) {
           *buf = uwsgi_num2str(wsgi_req->status);
           return strlen(*buf);
   }

   static void register_logchunks() {
           uwsgi_register_logchunk("foobar", uwsgi_lf_foobar, 1);
   }
   
   struct uwsgi_plugin foobar_plugin = {
           .name = "foobar",
           .on_load = register_logchunks,
   };
   
Now if you load the foobar plugin, you will be able to use the %(foobar) request logging variable (that would report the request status).
