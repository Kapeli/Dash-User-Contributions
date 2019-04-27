The RADOS plugin
====================

Available from uWSGI 1.9.16, stable from uWSGI 2.0.6

official modifier1: 28

Authors: Javier Guerra, Marcin Deranek, Roberto De Ioris, Sokolov Yura aka funny_falcon

The 'rados' plugin allows you to serve objects stored in a Ceph cluster directly using the librados API.

Note that it's not the CephFS filesystem, nor the 'radosgw' S3/Swift-compatible layer; RADOS is the bare object-storage layer.


Step1: Ceph cluster and content
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to try a minimal Ceph instalation, you can follow this guide: http://ceph.com/docs/master/start/. note that
you only need the OSD and MON daemons, the MDS are needed only for CephFS filesystems.

Once you get it running, you should have a configuration file (by default on /etc/ceph/ceph.con), and should be able to use the `rados` utility.

.. code-block:: sh

   rados lspools

by default, you should have at least the 'data', 'metadata' and 'rbd' pools.  Now add some content to the 'data' pool.
For example, if you have a 'list.html' file and images 'first.jpeg', 'second.jpeg' on a subdirectory 'imgs/':

.. code-block:: sh

   rados -p data put list.html list.html
   rados -p data put imgs/first.jpeg imgs/first.jpeg
   rados -p data put imgs/second.jpeg imgs/second.jpeg
   rados -p data ls -

note that RADOS doesn't have a concept of directories, but the object names can contain slashes.


Step2: uWSGI
^^^^^^^^^^^^

A build profile, named 'rados' is already available, so you can simply do:

.. code-block:: sh

   make PROFILE=rados
   
or

.. code-block:: sh

   python uwsgiconfig.py --build rados
   
or use the installer

.. code-block:: sh

   # this will create a binary called /tmp/radosuwsgi that you will use instead of 'uwsgi'
   curl http://uwsgi.it/install | bash -s rados /tmp/radosuwsgi

Obviously you can build rados support as plugin

.. code-block:: sh

   uwsgi --build-plugin plugins/rados/

or the old style:

.. code-block:: sh

   python uwsgiconfig.py --plugin plugins/rados/

You can now start an HTTP server to serve RADOS objects:

.. code-block:: ini

   [uwsgi]
   ; bind on port 9090
   http-socket = :9090
   ; set the default modifier1 to the rados one
   http-socket-modifier1 = 28
   ; mount our rados pool
   rados-mount = mountpoint=/rad/,pool=data,config=/etc/ceph/ceph.conf
   ; spawn 30 threads
   threads = 30

the 'rados-mount' parameter takes various subparameters:

 - mountpoint: required, the URL prefix on which the RADOS objects will appear.
 - pool: required, the RADOS pool to serve.
 - config: optional, the path to the ceph config file.
 - timeout: optional, set the timeout for operations, in seconds
 - allow_put: allow calling the ``PUT`` HTTP method to store new objects
 - allow_delete: allow calling the ``DELETE`` HTTP method to remove objects
 - allow_mkcol: allow calling ``MKCOL`` HTTP method to create new pools
 - allow_propfind: (requires uWSGI 2.1) allow calling the WebDAV ``PROPFIND`` method
 - buffer_size: maximum buffer size for ``GET`` requests in bytes (min 8192, max 16777216, default to 131072)
 - put_buffer_size: maximum buffer size for ``PUT`` requests (default to buffer_size)

In this example, your content will be served at http://localhost:9090/rad/list.html, http://localhost:9090/rad/imgs/first.jpeg
and http://localhost:9090/rad/imgs/second.jpeg.


High availability
^^^^^^^^^^^^^^^^^

The RADOS storage system is fully distributed, just starting several uWSGI workers on several machines with the same
'ceph.conf', all will see the same pools.  If they all serve on the same mountpoint, you get a failure-resistant
RADOS-HTTP gateway.


Multiple mountpoints
^^^^^^^^^^^^^^^^^^^^

You can issue several 'rados-mount' entries, each one will define a new mountpoint.  This way you can expose different
RADOS pools at different URLs.

HTTP methods
^^^^^^^^^^^^

The following methods are supported:

* GET -> retrieve a resource
* HEAD -> like GET but without body
* OPTIONS -> (requires uWSGI 2.1) returns the list of allowed HTTP methods and WebDAV support
* PUT -> requires allow_put in mountpoint options, store a resource in ceph: curl -T /etc/services http://localhost:8080/services
* MKCOL -> requires allow_mkcol in mountpoint options, creates a new pool: curl -X MKCOL http://localhost:8080/anewpool (the pool 'anewpool' will be created)
* DELETE -> requires allow_delete in mountpoint options, removes an object
* PROPFIND -> requires allow_propfind in mountpoint options (uWSGI 2.1+), implements WebDAV PROPFIND method

Features
^^^^^^^^

* multiprocessing is supported
* async support is fully functional, the ugreen suspend engine is the only supported one:


.. code-block:: ini

   [uwsgi]
   ; bind on port 9090
   http-socket = :9090
   ; set the default modifier1 to the rados one
   http-socket-modifier1 = 28
   ; mount our rados pool
   rados-mount = mountpoint=/rad/,pool=data,config=/etc/ceph/ceph.conf
   ; spawn 1000 async cores
   async = 1000
   ; required !!!
   ugreen = true

Caching example
^^^^^^^^^^^^^^^

Caching is highly recommended to improve performance and reduce the load on the Ceph cluster. This is a good example:

.. code-block:: ini

   [uwsgi]
   ; create a bitmap cache with max 1000 items storable in 10000 4k blocks
   cache2 = name=radoscache,items=1000,blocks=10000,blocksize=4096,bitmap=1
   
   ; check every object ending with .html in the 'radoscache' cache
   route = \.html$ cache:key=${PATH_INFO},name=radoscache,content_type=text/html
   ; if not found, store it at the end of the request for 3600 seconds (this will automatically enable Expires header)
   route = \.html$ cachestore:key=${PATH_INFO},name=radoscache,expires=3600
   
   ; general options
   
   ; master is always a good idea
   master = true
   ; bind on http port 9090 (better to use a uwsgi socket behind a proxy like nginx)
   http-socket = :9090
   ; set the default modifier1 to the rados one
   http-socket-modifier1 = 28
   ; mount our rados 'htmlpages' pool
   rados-mount = mountpoint=/,pool=htmlpages
   
   ; spawn multiple processes and threads
   processes = 4
   threads = 8

To test the caching behaviour, a tool like uwsgicachetop (https://pypi.python.org/pypi/uwsgicachetop) will be very useful. 

More information about caching here: :doc:`CachingCookbook`

Security note
^^^^^^^^^^^^^

Enabling MKCOL, PUT and DELETE may be high security risks.

Combine them with the internal routing framework for adding authentication/authorization policies:

.. code-block:: ini

   [uwsgi]
   master = true
   ; bind on http port 9090 (better to use a uwsgi socket behind a proxy like nginx)
   http-socket = :9090
   ; set the default modifier1 to the rados one
   http-socket-modifier1 = 28
   ; mount our rados 'htmlpages' pool
   rados-mount = mountpoint=/,pool=htmlpages,allow_put=1,allow_mkcol=1
   
   ; spawn multiple processes and threads
   processes = 4
   threads = 8
   
   ; permit PUT only to authenticated 'foo' user
   route-if = equal:${REQUEST_METHOD};PUT basicauth:my secret area,foo:bar
   
   ; allow MKCOL only from 127.0.0.1
   route-if = equal:${REQUEST_METHOD};MKCOL goto:check_localhost
   ; end of the chain
   route-run = last:
   
   route-label = check_localhost
   ; if REMOTE_ADDR = 127.0.0.1 -> continue to rados plugin
   route-remote-addr = ^127\.0\.0\.1$ continue:
   ; otherwise break with 403
   route-run = break:403 Forbidden
   


Notes
^^^^^

* The plugin automatically enables the MIME type engine.
* There is no directory index support. It makes no sense in rados/ceph context.
* You should drop privileges in your uWSGI instances, so be sure you give the right permissions to the ceph keyring.
* If you use it for getting/storing large objects, consider increasing ``buffer_size``. 4194304 is very performant value, 1048576 is also good, if you wish to conserve memory.
* PUT into Erasure coded pools is supported. ``put_buffer_size`` is automatically adjusted to satisfy pool alignment requirements.
