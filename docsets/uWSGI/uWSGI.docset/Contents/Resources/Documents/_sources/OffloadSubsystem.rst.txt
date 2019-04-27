The uWSGI offloading subsystem
==============================

Offloading is a way to optimize tiny tasks, delegating them to one or more threads.

These threads run such tasks in a non-blocking/evented way allowing for a huge amount of concurrency.

Various components of the uWSGI stack are offload-friendly, and the long-term target is to allow
application code to abuse them.


To start the offloading subsystem just add --offload-threads <n>, where <n> is the number of threads (per-worker) to spawn.
They are native threads, they are lock-free (no shared resources), thundering-herd free (requests to the system
are made in round-robin) and they are the best way to abuse your CPU cores.

The number of offloaded requests is accounted in the "offloaded_requests" metric of the stats subsystem.


Offloading static files
***********************

The first offload-aware component is the static file serving system.

When offload threads are available, the whole transfer of the file is delegated to one of those threads, freeing your worker
suddenly (so it will be ready to accept new requests)

Example:

.. code-block:: ini

   [uwsgi]
   socket = :3031
   check-static = /var/www
   offload-threads = 4

Offloading internal routing
***************************

The router_uwsgi and router_http plugins are offload-friendly.

You can route requests to external uwsgi/HTTP servers without being worried about having a blocked worker during
the response generation.

Example:

.. code-block:: ini

   [uwsgi]
   socket = :3031
   offload-threads = 8
   route = ^/foo http:127.0.0.1:8080
   route = ^/bar http:127.0.0.1:8181
   route = ^/node http:127.0.0.1:9090

Since 1.9.11 the ``cache`` router is offload friendly too.

.. code-block:: ini

   [uwsgi]
   socket = :3031
   offload-threads = 8
   route-run = cache:key=${REQUEST_URI}

As soon as the object is retrieved from the cache, it will be transferred in one of the offload threads.

The Future
**********

The offloading subsystem has a great potential, you can think of it as a software DMA: you program it, and then it goes alone.

Currently it is pretty monolithic, but the idea is to allow more complex plugins (a redis one is in the works).

Next step is allowing the user to "program" it via the uwsgi api.

