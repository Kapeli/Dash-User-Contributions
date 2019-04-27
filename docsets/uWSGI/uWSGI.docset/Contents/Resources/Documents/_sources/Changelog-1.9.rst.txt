uWSGI 1.9
=========


This is the version that will lead to the LTS 2.0. It includes a lot of internal changes and removal of a lot of basically unused, broken, or too ugly functionality.

Options deprecated in 1.0.x have been definitely removed.

Non-blocking for all
********************

From now on, all of the request plugins, need to be non-blocking. A new set of
C/C++/Obj-C api have been added to help the user/developer writing non-blocking
code in a safe way.  Plugins like the RPC one have been rewritten using that
new api, allowing you to use it with engines like Gevent or Coro::Anyevent The
async mode has been rewritten to better cooperate with this new rule. More info
can be found on :doc:`Async` The new async mode requires some form of
coroutine/greenthread/suspend engine to correctly work. Again, check
:doc:`Async`

Coro::AnyEvent
**************

The Perl/PSGI plugin is one of the most ancient in the uWSGI project, but used to not support the async mode in advanced ways.

Thanks to the new :doc:`Async` mode, a Coro::Anyevent (coroae) loop engine has been added.

To build it you need the Coro::Anyevent package (you can use cpanm to get it), then just add --coroae <n> to your options
where <n> is the number of async cores to spawn.


The JVM plugin
**************

We finally have a truly working JVM infrastructure in uWSGI 1.9.  Check the new
docs at :doc:`JVM` Improved :doc:`JWSGI` support is available as well as the
new Clojure :doc:`Ring` plugin

The Mono ASP.NET plugin
***********************

The first Mono plugin attempt (in 2010) was a total failure. Now we have a new shining implementation.

Check docs here :doc:`Mono`

Language independent HTTP body management
*****************************************

One of the most annoying task in writing uWSGI request plugins, was re-implementing the management of HTTP body reader every time.

The new non-blocking api added 3 simple generic C/C++/Obj-C functions to deal with it in a language independent way:

.. code-block:: c

   char *uwsgi_request_body_read(struct wsgi_request *wsgi_req, ssize_t hint, ssize_t *rlen);
   char *uwsgi_request_body_readline(struct wsgi_request *wsgi_req, ssize_t hint, ssize_t *rlen);
   void uwsgi_request_body_seek(struct wsgi_request *wsgi_req, off_t pos); 


they automatically manage post-buffering, non-blocking and upload progress.

All of the request plugins have been updated to the new api



Faster uwsgi/HTTP/FastCGI/SCGI native sockets
*********************************************

All of the --socket protocol parsers have been rewritten to be faster (less
syscall usage) and to use less memory.  They are now more complex, but you
should note (on loaded site) a reduced amount of syscalls per-request.

The SCGI protocol support has been added, while a NPH fastcgi mode (where the output is HTTP instead of cgi) has been implemented.

The FastCGI protocol now supports true sendfile() usage

The old behaviour of storing the request body for HTTP and FastCGI on a temp
file, has been removed (unless you use post-buffering).  This means you can now
have upload progress with protocols other than uwsgi.

Request logging VS err logging
******************************

One of the most annoying problem with older uWSGI releases was the lack of
ability to easily split request logs from error logs.  You can now create a
logger and map it only to request logging:

.. code-block:: ini

   [uwsgi]
   req-logger = syslog
   ...

As an example you may want to send request logging to syslog and redis, and error log to mongodb (on the foo.bar collection):

.. code-block:: ini

   [uwsgi]
   req-logger = syslog
   req-logger = redislog:127.0.0.1:6269
   logger = mongodblog:127.0.0.1:9090,foo.bar
   ...

Or just use (boring) files

.. code-block:: ini

   [uwsgi]
   req-logger = file:/tmp/reqlog
   logger = file:/tmp/errlog
   ...

Chain reloading
***************

When in lazy/lazy_apps mode, you can simply destroy a worker to force it to
reload the application code.

A new reloading system named "chain reload", allows you to reload one worker at
time (opposed to the standard way where all of the workers are destroyed in
bulk)

Chain reloading can only be triggered via "touch": --touch-chain-reload <file>

Offloading improvements
***********************

Offloading appeared in uWSGI 1.4 and is one of the most loved features.  In 1.9
we added a new engine: "write", that allows you to offload the write of files
on disk.  A general function api uwsgi.offload() is on work, to allow
applications to access the offload engine.  All of the uWSGI parts sending
static files (including the language-specific implementations, like WSGI
wsgi.file_wrapper) have been extended to automatically use offloading if
available.  This means you can use your Framework's way for serving static
files, without losing too much performance and (more important) without
blocking your workers.


Better static files management/serving
**************************************

uWSGI 1.9 received many improvements in static file serving.

You may want to check: :doc:`StaticFiles`

For syadmins one of the most interesting new features is the ability to use the
uWSGI new generation cacheing (see below) to store request -> absolute_path
mappings

The New Generation Cache subsystem (cache2)
*******************************************

The uWSGI caching subsystem has been completely rewritten to be a more general
purpose in-memory key/value store.  The old caching subsystem has been re-built
on top of it, and is now more of a general "web caching" system.  The new
cache subsystem allows you to control all of the aspects of your memory store,
from the hashing algorithm to the amount of blocks.

You can now have multiple caches per-instance (identified by name)

To create a cache just use the new --cache2 option

.. code-block:: ini

   [uwsgi]
   cache2 = name=mycache,items=100
   cache2 = name=faster,items=200,hash=murmur2,keysize=100,blocksize=4096
   cache2 = name=fslike,items=1000,keysize=256,bitmap=1,blocks=2000,blocksize=8192
   ...


In this example we created 3 caches: mycache, faster and fslike.

The first one is a standard old-style, cache able to store 100 items of a
maximum size of 64k with keys limited to 2048 bytes using djb33x hashing
algorithm The second one use the murmur2 hashing algorithm, each key can be at
most 1000 bytes, can store 200 items of max 4k The last one works like a
filesystem, where each item can span over multiple blocks. That means, fslike
cache can save lot of memory for boject of different size (but it will be
slower than non-bitmap based caches)

The options you can specify in cache2 are the following:

``name`` the name of the cache (must be unique) REQUIRED

``items/max_items/maxitems`` set the max number of items the cache can store REQUIRED

``blocksize`` set the size of a single block

``blocks`` set the number of blocks (used only in bitmap mode)

``hash`` set the hashing algorithm, currently supported: djbx33 and murmur2

``hashsize/hash_size`` set the size of the hash table (default to 65536 items)

``keysize/key_size`` set the max size of a key

``store`` set the filename in which to persistent store the cache

``store_sync/storesync`` set the frequency (in seconds) at which msync() is called to flush cache on disk (when in persistent mode)

``node/nodes`` the new cache subsystem can send cache updates via udp packet. With this option you set one or more (separated with `;`) udp addresses on which to send updates

``sync`` set it to the address of a cache server. Its whole content will be copied in the new cache (use it for initial sync)

``udp/udp_servers/udp_server/udpservers/udpserver`` bind to the specified udp addresses (separated with `;`) listening for cache updates

``bitmap`` enable botmap mode (set it to 1)

If you are asking yourself why such low-level tunings exists, you have to take in account that the new caching subsystem is used in lot of areas, so for different
needs you may want different tuning. Just check :doc:`SSLScaling` for an example

The old --cache-server option has been removed. The threaded cache server added in 0.9.8 has been completed superseeded
by the new non blocking infrastructure. If you load the "cache" plugin (enabled by default in monolithic build) a cache server
will be available and managed by the workers.


Update docs are available here :doc:`Caching`

The Legion subsystem
********************

The Legion subsystem is a new whole addition to the uWSGI project.  It has
superseeded the old Clustering subsystem (which has been removed in 1.9).  It
implements a quorum system to manage shared resources in clustered
environments.  Docs are already available: :doc:`Legion`

Cygwin (windows) support
************************

uWSGI can be compiled on windows machines using the cygwin POSIX emulation
system.  The event subsystem uses simple poll() (mapped to select() on cygwin),
while the lock engine uses windows mutexes.  Albeit from our tests it looks
pretty solid, we consider the porting still "experimental"


Advanced Exceptions subsystem
*****************************

As well as the request body language-independent management, an exception
management system has been added.  Currently supported only in the Python and
Ruby plugins, allows language-independent handling of exceptions cases (like
reloading on a specific exception).  The --catch-exception option has been
improved to show lot of useful information. Just try it (in development !!!)
Future development will allow automatic sending of exception to system like
Sentry or Airbrake.

SPDY, SSL and SNI
*****************

Exciting new features have been added to the SSL system and the HTTP router

SPDY support (currently only version 3) will get lot of users attention, but SNI subsystem is what sysadmins will love

Preliminary docs are available

:doc:`SPDY`

:doc:`SNI`

HTTP router keepalive, auto-chunking, auto-gzip and transparent websockets
***************************************************************************

Many users have started using the HTTP/HTTPS/SPDY router in production,
so we started adding features to it. Remember this is ONLY a router/proxy, NO
I/O is allowed, so you may not be able to throw away your
old-good webserver.

The new options:

``--http-keepalive`` enable HTTP/1.1 keepalive connections

``--http-auto-chunked`` for backend response without content-length (or chunked encoding already enabled), transform the output in chunked mode to maintain keepalive connections

``--http-auto-gzip`` automatically gzip content if uWSGI-Encoding header is set to gzip, but content size (Content-Length/Transfer-Encoding) and Content-Encoding are not specified

``--http-websockets`` automatically detect websockets connections to put the request handler in raw mode

The SSL router (sslrouter)
**************************

A new corerouter has been added, it works in the same way as the rawrouter one,
but will terminate ssl connections.  The sslrouter can use sni for implementing
virtualhosting (using the --sslrouter-sni option)

Websockets api
**************

20Tab S.r.l. (a company working on HTML5 browsers game) sponsored the
development of a fast language-independent websockets api for uWSGI. The api is
currently in very good shape (and maybe faster than any other implementation).
Docs still need to be completed but you may want to check the following
examples (a simple echo):

https://github.com/unbit/uwsgi/blob/master/tests/websockets_echo.pl (perl)

https://github.com/unbit/uwsgi/blob/master/tests/websockets_echo.py (python)

https://github.com/unbit/uwsgi/blob/master/tests/websockets_echo.ru (ruby)

New Internal Routing (turing complete ?)
****************************************

The internal routing subsystem has been rewritten to be 'programmable'. You can
see it as an apache mod_rewrite with steroids (and goto ;) Docs still need to
be ported, but the new system allows you to modify/filter CGI vars and HTTP
headers on the fly, as well as managing HTTP authentication and caching.

Updated docs here (still work in progress) :doc:`InternalRouting`

Emperor ZMQ plugin
******************

A new imperial monitor has been added allowing vassals to be governed over zeromq messages:

https://uwsgi-docs.readthedocs.io/en/latest/ImperialMonitors.html#zmq-zeromq

Total introspection via the stats server
****************************************

The stats server now exports all of the request variables of the currently
running requests for each core, so it works in multithread mode too. This is a
great way to inspect what your instance is doing and how it does it In the
future, uwsgitop could be extended to show the currently running request in
realtime.

Nagios plugin
*************

Ping requests sent using nagios plugin will no longer be counted in apps
request stats.  This means that if application had --idle option enabled nagios
pings will no longer prevent app from going to idle state, so starting with 1.9
--idle should be disabled when nagios plugin is used. Otherwise app may be put
in idle state just before nagios ping request, when ping arrives it needs to
wake from idle and this might take longer than ping timeout, causing nagios
alerts.

Removed and deprecated features
*******************************

- The --app option has been removed. To load applications on specific mountpoints use the --mount option

- The --static-offload-to-thread option has been removed. Use the more versatile --offload-threads

- The grunt mode has been removed. To accomplish the same behaviour just use threads or directly call fork() and uwsgi.disconnect()

- The send_message/recv_message api has been removed (use language-supplied functions)

Working On, Issues and regressions
***********************************

We missed the timeline for a bunch of expected features:

- SPNEGO support, this is an internal routing instruction to implement SPNEGO authentication support

- Ruby 1.9 fibers support has been rewritten, but need tests

- Erlang support did not got required attention, very probably will be post-poned to 2.0

- Async sleep api is incomplete

- SPDY push is still not implemented

- RADIUS and LDAP internal routing instructions are unimplemented

- The channel subsystem (required for easy websockets communications) is still unimplemented

In addition to this we have issues that will be resolved in upcoming minor releases:

- the --lazy mode lost usefulness, now it is like --lazy-apps but with workers-reload only policy on SIGHUP

- it looks like the JVM does not cooperate well with coroutine engines, maybe we should add a check for it

- Solaris and Solaris-like systems did not get heavy testing

Special thanks
**************

A number of users/developers helped during the 1.9 development cycle. We would like to make special thanks to:

Łukasz Mierzwa (fastrouters scalability tests)

Guido Berhoerster (making the internal routing the new skynet)

Riccardo Magliocchetti (static analysis)

André Cruz (HTTPS and gevent battle tests)

Mingli Yuan (Clojure/Ring support and test suite)






