uWSGI 1.9.11
============

Changelog [20130526]

Bugfixes
********

* Fixed Python 3 stdout/stderr buffering
* Fixed mule messages (``@mulefunc`` is now reliable)
* Fixed ``SCRIPT_NAME`` handling in dynamic mode
* Fixed X-Sendfile with gzip static mode
* Fixed cache item maximum size with custom block size
* Fixed cache path handling

New features
************

The new high-performance PyPy plugin
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Credits: Maciej Fijalkowski

We are pleased to announce the availability of the new PyPy plugin.

PyPy team has been great in helping us. We hope the uWSGI integration (that exposed new challenges to the PyPy project)
will help PyPy becaming better and better.

Official docs: :doc:`PyPy`

Cron improvements
^^^^^^^^^^^^^^^^^

Credits: Łukasz Mierzwa

Unique crons
------------

You can now avoid overlapping crons. The uWSGI master will track death of a single task, and until its death the same cron
will not be triggered:

.. code-block:: ini

   [uwsgi]
   unique-cron = -1 -1 -1 -1 -1 my_script.sh

cron2 syntax
------------

A key/value variant of the --cron option is now available:

.. code-block:: ini

   [uwsgi]
   cron2 = minute=39,hour=23,month=-1,week=-1,day=-1,unique=1,legion=foobar,harakiri=30

harakiri cron
-------------

When using the ``cron2`` option you are allowed to set a harakiri timeout for a cron task. Just add ``harakiri=n`` to the options.

Support for GNU Hurd
^^^^^^^^^^^^^^^^^^^^

Debian GNU/Hurd has been recently released. uWSGI 1.9.11 can be built over it, however very few tests have been made.

The memory offload engine
^^^^^^^^^^^^^^^^^^^^^^^^^

Idea: Stefano Brentegani

When serving content from the cache, a worker could get blocked during transfer from memory to the socket.

A new offload engine named "memory" allows to offload memory transfers. The cache router automatically supports it.
Support for more areas will be added soon.

To enable it just add ``--offload-threads <n>``

New Websockets chat example
^^^^^^^^^^^^^^^^^^^^^^^^^^^

An example websocket chat using Redis has been added to the repository:

https://github.com/unbit/uwsgi/blob/master/tests/websockets_chat.py

Error routes
^^^^^^^^^^^^

You can now define a routing table to be executed as soon as you set the HTTP status code in your plugin.

This allows you to completely modify the response. This is useful for custom error codes.

All of the routing standard options are available (included labels) plus an optimized ``error-route-status``
matching a specific HTTP status code:

.. code-block:: ini

   [uwsgi]
   error-route-status = 502 redirect:http://unbit.it

Support for corner case usage in wsgi.file_wrapper
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Generally the ``wsgi.file_wrapper`` callable expects a file-like object. PEP 333/3333 reports a special pattern when the object
is not a file (call ``read()`` until the object is consumed). uWSGI now supports this pattern (even if in a hacky way).

HTTP/HTTPS router keepalive improvements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Credits: André Cruz

When using ``--http-keepalive`` you can now hold the connection open even if the request has a body.


The harakiri routing action
^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can now set a harakiri timer for each request using internal routing:

.. code-block:: ini

   [uwsgi]
   ; set harakiri to 30 seconds for request starting with /slow
   route = ^/slow harakiri:30

RPC wrappers
^^^^^^^^^^^^

The RPC plugin has been extended to allows interoperation with other standards.

Currently a simple HTTP wrapper and an XML-RPC one are exposed.

The HTTP simple wrapper works by parsing ``PATH_INFO``.

A ``/foo/bar/test`` call will result in

uwsgi.rpc('foo', 'bar', 'test')

To enable this HTTP mode just set the ``modifier2`` to '2':

.. code-block:: ini

   [uwsgi]
   http-socket = :9090
   http-socket-modifier1 = 173
   http-socket-modifier2 = 2
   ; load the rpc code
   import = myrpcfuncs.py
   
or (to have more control)

.. code-block:: ini

   [uwsgi]
   http-socket = :9090
   route-run = uwsgi:,173,2
   ; load the rpc code
   import = myrpcfuncs.py


The XML-RPC wrapper works in the same way, but it uses the modifier2 value '3'. It requires a libxml2-enabled build of uWSGI.

.. code-block:: ini

   [uwsgi]
   http-socket = :9090
   route-run = uwsgi:,173,3
   ; load the rpc code
   import = myrpcfuncs.py
   
Then just call it:

.. code-block:: python

   proxy = xmlrpclib.ServerProxy("http://localhost:9090')
   proxy.hello('foo','bar','test') 
   
You can combine multiple wrappers using routing.

.. code-block:: ini

   [uwsgi]
   http-socket = :9090
   ; /xml force xmlrpc wrapper
   route = ^/xml uwsgi:,173,3
   ; fallback to HTTP simple
   route-if-not = startswith:${PATH_INFO};/xml uwsgi:,173,2
   ; load the rpc code
   import = myrpcfuncs.py


Availability
************

uWSGI 1.9.11 will be available since 20130526 at:

https://projects.unbit.it/downloads/uwsgi-1.9.11.tar.gz
