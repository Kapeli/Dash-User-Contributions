uWSGI 1.9.4
===========

Changelog 20130330

Bugfixes
********

fixed cache statistics exported by the stats subsystem (Łukasz Mierzwa)

fixed CoroEV bug in after_request (Tom Molesworth and John Berthels)

update cache items after a restore from persistent storage (Łukasz Mierzwa)

fixed signal handling in non-worker processes

fixed thundering herd in multiple mules setup

ported the cplusplus skeletal plugin to the new api

fixed uWSGI reloading when build as a shared library

New features
************

SmartOS official support
^^^^^^^^^^^^^^^^^^^^^^^^

From now on, SmartOS is included in the officially supported operating systems

V8 initial support
^^^^^^^^^^^^^^^^^^

The Lua previous suggestion for writing uWSGI routing rules and configurations, woke up lot of javascript users stating that javascript
itself could be a valid alternative. A V8 plugin is now available, supporting RPC, signal handlers and configurations. You need libv8 headers to build it:

.. code-block:: sh

   python uwsgiconfig.py --plugin plugins/v8

.. code-block:: js

   var config = {};
   config['socket'] = [':3031', ':3032', ':3033'];
   config['master'] = true;
   config['processes'] = 3+1;
   config['module'] = 'werkzeug.testapp:test_app';

   config;

.. code-block:: sh

   uwsgi --plugin v8 --config foo.js

The previous example will allows you to write dynamic configs in javascript, while you can export javascript functions via the RPC subsystem:

.. code-block:: js

   function part1(request_uri, remote_addr) {
        return '<h1>i am part1 for ' + request_uri + ' ' + remote_addr + "</h1>" ;
   }

   function part2(request_uri, remote_addr) {
        return '<h2>i am part2 for ' + request_uri + ' ' + remote_addr + "</h2>" ;
   }

   function part3(request_uri, remote_addr) {
        return '<h3>i am part3 for ' + request_uri + ' ' + remote_addr + "</h3>" ;
   }

   uwsgi_register_rpc('part1', part1);
   uwsgi_register_rpc('part2', part2);
   uwsgi_register_rpc('part3', part3);

.. code-block:: ini

   [uwsgi]
   plugin = v8
   v8-load = func.js
   cache2 = name=foobar,items=10

   http-socket = :9090

   route-run = addheader:Content-Type: text/html
   route-run = cache:key=pippo,name=foobar
   route-run = cachestore:key=pippo,name=foobar
   route-run = rpcnext:part1 ${REQUEST_URI} ${REMOTE_ADDR}
   route-run = rpcnext:part2 ${REQUEST_URI} ${REMOTE_ADDR}
   route-run = rpcnext:part3 ${REQUEST_URI} ${REMOTE_ADDR}
   route-run = break:

The previous example generates an HTTP response from 3 javascript functions and store it in the uWSGI cache.

Curious about rpcnext ?

The rpcnext routing action
^^^^^^^^^^^^^^^^^^^^^^^^^^

We can already call rpc functions from the routing subsystem to generate response. With the rpcnext action (aliased as rpcblob too)
you can call multiple rpc functions and assemble the return values in a single response.

Legion improvements
^^^^^^^^^^^^^^^^^^^

We are hardly working in stabilizing :doc:`Legion` The objective is have a rock-solid clustering implementation for uWSGI 2.0
that you can use even from your applications.

The code in 1.9.4 has been refactored a bit by Łukasz Mierzwa to allow easier integration with external plugins.

A new "join" hook has been added, it is called as soon as a node becomes active part of a legion (read, it is part of a quorum).

Availability
************

uWSGI 1.9.4 will be available since 20130330 at this url

https://projects.unbit.it/downloads/uwsgi-1.9.4.tar.gz
