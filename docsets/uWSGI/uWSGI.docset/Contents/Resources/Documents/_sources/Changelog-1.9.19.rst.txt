uWSGI 1.9.19
============

Changelog [20131109]

This release starts the 'hardening' cycle for uWSGI 2.0 (scheduled for the end of december 2013).

The metrics subsystem was the last piece missing and this version (after 1 year of analysis) finally includes it.

During the following 2 months we will start deprecating features or plugins that got no-interest, are known to be broken or are simply superseed
by more modern/advanced ones.

Currently the following plugin and features are scheduled for removal:

- The Go plugin, superseeded by the gccgo one. (eventually the Go plugin will be brought back if something changes in the fork() support)
- Auto-snapshotting, was never documented, it has tons of corner case bugs and it is huber-complex. The features added by the :doc:`MasterFifo` allows for better implementations of snapshotting.

Waiting for decision:

- the erlang plugin is extremely old, was badly engineered and should be completely rewritten. If you are a user of it, please contact the staff. Very probably we will not be able to maintain it without sponsorship.
- the matheval support could be removed soon (unless we find some specific use that could require it), substituted by some form of simple math directly implemented in the option parser
- the admin plugin should be substituted with something more advanced. An api for defining dynamic options is on-work

Bugfixes
********

- completely skip cgroups initialization when non-root
- tons of post-static_analysis fixes by Riccardo Magliocchetti
- fixed the greenlet plugin reference counting
- avoid kevent storm for stats pusher thread
- fixed rbtimers math
- both 'cache' and 'file' routers got a 'no_content_length' key option to avoid settign the Content-Length header
- the PyPy plugin automatically enables threads/GIL
- manage dot_segments in HTTP parser
- improved srand() usage

New features
************

The Metrics subsystem
^^^^^^^^^^^^^^^^^^^^^

This was the last piece missing before uWSGI 2.0. The Metrics subsystem allows you to store "numbers" related to monitoring, graphing and quality checks and exports them in various ways.

Official docs: :doc:`Metrics`

The Tornado loop engine
^^^^^^^^^^^^^^^^^^^^^^^

While working on nodejs integration we realized that contrary to what we used to believe, Tornado (an asynchronous, callback based module for python) is usable in uWSGI.

Note: The plugin is not built-in by default

Official docs: :doc:`Tornado`

The 'puwsgi' protocol
^^^^^^^^^^^^^^^^^^^^^

A "persistent" (keep-alive) version of the 'uwsgi' parser has been added named 'puwsgi' (persistent uwsgi).

This protocol works only for request without a body and requires support from the frontend. Its use is currently for custom clients/apps, there is no webserver handler supporting it.

The ``--puwsgi-socket <addr>`` will bind a puwsgi socket to the specified address

--vassal-set
^^^^^^^^^^^^

You can tell the Emperor to pass specific options to every vassal using the --set facility:

.. code-block:: ini

   [uwsgi]
   emperor = /etc/uwsgi/vassals
   vassal-set = processes=8
   vassal-set = enable-metrics=1
   
this will add ``--set processes=8`` and ``--set enable-metrics=1`` to each vassal


The 'template' transformation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is a transformation allowing you to apply all of the internal routing patterns to your responses.

Take the following file (foo.html)

.. code-block:: html

   <html>
     <head>
       <title>Running on ${SERVER_NAME}</title>
     </head>
     <body>
       Your ip address is: ${REMOTE_ADDR}<br/>
       Served requests: ${metric[worker.0.requests]}<br/>
       Pid: ${uwsgi[pid]}<br/>
       A random UUID: ${uwsgi[uuid]}
     </body>
   </html>
   
we will apply the 'template' transformation to it:

.. code-block:: ini

   [uwsgi]
   http-socket = :9090
   ; enable the metrics subsystem
   enable-metrics = true
   ; inject the route transformation
   route-run = template:
   ; return a file (transformation will be applied to it)
   route-run = file:filename=foo.html,no_content_length=1
   
everything available in the internal routing subsystem can be used into the template transformation.

Performance are stellar, so instead of old Server Side Includes, you may want to try it.

Not enough ? combine it with caching:

.. code-block:: ini

   [uwsgi]
   http-socket = :9090
   ; enable the metrics subsystem
   enable-metrics = true
   ; load foo.html in the cache
   cache2 = name=mycache,items=10
   load-file-in-cache = foo.html
   ; inject the route transformation
   route-run = template:
   ; return the cache item (transformation will be applied to it)
   route-run = cache:key=foo.html,no_content_length=1
   
Again ?

what about chunked encoding ?

.. code-block:: ini

   [uwsgi]
   http-socket = :9090
   ; enable the metrics subsystem
   enable-metrics = true
   ; load foo.html in the cache
   cache2 = name=mycache,items=10
   load-file-in-cache = foo.html
   ; inject the route transformation
   route-run = template:
   ; inject chunked encoding
   route-run = chunked:
   ; return the cache item (transformation will be applied to it)
   route-run = cache:key=foo.html,no_content_length=1

or gzip ?

.. code-block:: ini

   [uwsgi]
   http-socket = :9090
   ; enable the metrics subsystem
   enable-metrics = true
   ; load foo.html in the cache
   cache2 = name=mycache,items=10
   load-file-in-cache = foo.html
   ; inject the route transformation
   route-run = template:
   ; inject gzip
   route-run = gzip:
   ; return the cache item (transformation will be applied to it)
   route-run = cache:key=foo.html,no_content_length=1

Availability
************

uWSGI 1.9.19 has been released on 20131109, you can download it from:

https://projects.unbit.it/downloads/uwsgi-1.9.19.tar.gz
