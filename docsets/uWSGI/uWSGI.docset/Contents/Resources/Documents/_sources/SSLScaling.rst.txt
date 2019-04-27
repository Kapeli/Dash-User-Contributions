Scaling SSL connections (uWSGI 1.9)
===================================

Distributing SSL servers in a cluster is a hard topic. The biggest problem is sharing SSL sessions between different nodes.

The problem is amplified in non-blocking servers due to OpenSSL's limits in the way sessions are managed.

For example, you cannot share sessions in Memcached servers and access them in a non-blocking way.

A common solution (well, a compromise, maybe) until now has been to use a single SSL terminator balancing requests to multiple non-encrypted backends. This solution kinda works, but obviously it does not scale.

Starting from uWSGI 1.9-dev an implementation (based on the *stud* project) of distributed caching has been added.

Setup 1: using the uWSGI cache for storing SSL sessions
*******************************************************

You can configure the SSL subsystem of uWSGI to use the shared cache. The SSL sessions will time out according to the expiry value of the cache item. This way the cache sweeper thread (managed by the master) will destroy sessions in the cache.

.. important:: The order of the options is important. ``cache`` options must be specified BEFORE ``ssl-sessions-use-cache`` and ``https`` options.

.. code-block:: ini

   [uwsgi]
   ; spawn the master process (it will run the cache sweeper thread)
   master = true
   ; store up to 20k sessions
   cache = 20000
   ; 4k per object is enough for SSL sessions
   cache-blocksize = 4096
   ; force the SSL subsystem to use the uWSGI cache as session storage
   ssl-sessions-use-cache = true
   ; set SSL session timeout (in seconds)
   ssl-sessions-timeout = 300
   ; set the session context string (see later)
   https-session-context = foobar
   ; spawn an HTTPS router
   https = 192.168.173.1:8443,foobar.crt,foobar.key
   ; spawn 8 processes for the HTTPS router (all sharing the same session cache)
   http-processes = 8
   ; add a bunch of uwsgi nodes to relay traffic to
   http-to = 192.168.173.10:3031
   http-to = 192.168.173.11:3031
   http-to = 192.168.173.12:3031
   ; add stats
   stats = 127.0.0.1:5001

Now start blasting your HTTPS router and then telnet to port 5001. Under the "cache" object of the JSON
output you should see the values "items" and "hits" increasing. The value "miss" is increased every time a session is not found
in the cache. It is a good metric of the SSL performance users can expect.

Setup 2: synchronize caches of different HTTPS routers
******************************************************

The objective is to synchronize each new session in each distributed cache. To accomplish that you have to spawn a special thread
(``cache-udp-server``) in each instance and list all of the remote servers that should be synchronized.

A pure-TCP load balancer (like HAProxy or uWSGI's Rawrouter) can be used to load balance between the various HTTPS routers.

Here's a possible Rawrouter config.

.. code-block:: ini

   [uwsgi]
   master = true
   rawrouter = 192.168.173.99:443
   rawrouter-to = 192.168.173.1:8443
   rawrouter-to = 192.168.173.2:8443
   rawrouter-to = 192.168.173.3:8443
   
Now you can configure the first node (the new options are at the end of the .ini config)

.. code-block:: ini

   [uwsgi]
   ; spawn the master process (it will run the cache sweeper thread)
   master = true
   ; store up to 20k sessions
   cache = 20000
   ; 4k per object is enough for SSL sessions
   cache-blocksize = 4096
   ; force the SSL subsystem to use the uWSGI cache as session storage
   ssl-sessions-use-cache = true
   ; set SSL session timeout (in seconds)
   ssl-sessions-timeout = 300
   ; set the session context string (see later)
   https-session-context = foobar
   ; spawn an HTTPS router
   https = 192.168.173.1:8443,foobar.crt,foobar.key
   ; spawn 8 processes for the HTTPS router (all sharing the same session cache)
   http-processes = 8
   ; add a bunch of uwsgi nodes to relay traffic to
   http-to = 192.168.173.10:3031
   http-to = 192.168.173.11:3031
   http-to = 192.168.173.12:3031
   ; add stats
   stats = 127.0.0.1:5001
   
   ; spawn the cache-udp-server
   cache-udp-server = 192.168.173.1:7171
   ; propagate updates to the other nodes
   cache-udp-node = 192.168.173.2:7171
   cache-udp-node = 192.168.173.3:7171

and the other two...

.. code-block:: ini

   [uwsgi]
   ; spawn the master process (it will run the cache sweeper thread)
   master = true
   ; store up to 20k sessions
   cache = 20000
   ; 4k per object is enough for SSL sessions
   cache-blocksize = 4096
   ; force the SSL subsystem to use the uWSGI cache as session storage
   ssl-sessions-use-cache = true
   ; set SSL session timeout (in seconds)
   ssl-sessions-timeout = 300
   ; set the session context string (see later)
   https-session-context = foobar
   ; spawn an HTTPS router
   https = 192.168.173.1:8443,foobar.crt,foobar.key
   ; spawn 8 processes for the HTTPS router (all sharing the same session cache)
   http-processes = 8
   ; add a bunch of uwsgi nodes to relay traffic to
   http-to = 192.168.173.10:3031
   http-to = 192.168.173.11:3031
   http-to = 192.168.173.12:3031
   ; add stats
   stats = 127.0.0.1:5001
   
   ; spawn the cache-udp-server
   cache-udp-server = 192.168.173.2:7171
   ; propagate updates to the other nodes
   cache-udp-node = 192.168.173.1:7171
   cache-udp-node = 192.168.173.3:7171

.. code-block:: ini

   [uwsgi]
   ; spawn the master process (it will run the cache sweeper thread)
   master = true
   ; store up to 20k sessions
   cache = 20000
   ; 4k per object is enough for SSL sessions
   cache-blocksize = 4096
   ; force the SSL subsystem to use the uWSGI cache as session storage
   ssl-sessions-use-cache = true
   ; set SSL session timeout (in seconds)
   ssl-sessions-timeout = 300
   ; set the session context string (see later)
   https-session-context = foobar
   ; spawn an HTTPS router
   https = 192.168.173.1:8443,foobar.crt,foobar.key
   ; spawn 8 processes for the HTTPS router (all sharing the same session cache)
   http-processes = 8
   ; add a bunch of uwsgi nodes to relay traffic to
   http-to = 192.168.173.10:3031
   http-to = 192.168.173.11:3031
   http-to = 192.168.173.12:3031
   ; add stats
   stats = 127.0.0.1:5001
   
   ; spawn the cache-udp-server
   cache-udp-server = 192.168.173.3:7171
   ; propagate updates to the other nodes
   cache-udp-node = 192.168.173.1:7171
   cache-udp-node = 192.168.173.2:7171


Start hammering the Rawrouter (remember to use a client supporting persistent SSL sessions, like your browser) and get cache statistics
from the stats server of each HTTPS terminator node. If the count of "hits" is a lot higher than the "miss" value the system is working well
and your load is distributed and in awesome hyper high performance mode.

So, what is ``https-session-context``, you ask? Basically each SSL session before being used is checked against a fixed string (the session context). If the session does not match that string, it is rejected. By default the session context is initialized to a value built from the HTTP server address. Forcing it to a shared value will avoid a session created in a node being rejected in another one.

Using named caches
******************

Starting from uWSGI 1.9 you can have multiple caches. This is a setup with 2 nodes using a new generation cache named "ssl".

The ``cache2`` option allows also to set a custom key size. Since SSL session keys are not very long, we can use it to optimize memory usage. In this example we use 128 byte key size limit, which should be enough for session IDs.

.. code-block:: ini

   [uwsgi]
   ; spawn the master process (it will run the cache sweeper thread)
   master = true
   ; store up to 20k sessions
   cache2 = name=ssl,items=20000,keysize=128,blocksize=4096,node=127.0.0.1:4242,udp=127.0.0.1:4141
   ; force the SSL subsystem to use the uWSGI cache as session storage
   ssl-sessions-use-cache = ssl
   ; set sessions timeout (in seconds)
   ssl-sessions-timeout = 300
   ; set the session context string
   https-session-context = foobar
   ; spawn an HTTPS router
   https = :8443,foobar.crt,foobar.key
   ; spawn 8 processes for the HTTPS router (all sharing the same session cache)
   http-processes = 8
   module = werkzeug.testapp:test_app
   ; add stats
   stats = :5001

and the second node...

.. code-block:: ini

   [uwsgi]
   ; spawn the master process (it will run the cache sweeper thread)
   master = true
   ; store up to 20k sessions
   cache2 = name=ssl,items=20000,blocksize=4096,node=127.0.0.1:4141,udp=127.0.0.1:4242
   ; force the SSL subsystem to use the uWSGI cache as session storage
   ssl-sessions-use-cache = ssl
   ; set session timeout
   ssl-sessions-timeout = 300
   ; set the session context string
   https-session-context = foobar
   ; spawn an HTTPS router
   https = :8444,foobar.crt,foobar.key
   ; spawn 8 processes for the HTTPS router (all sharing the same sessions cache)
   http-processes = 8
   module = werkzeug.testapp:test_app
   ; add stats
   stats = :5002

Notes
*****

If you do not want to manually configure the cache UDP nodes and your network configuration supports it, you can use UDP multicast.

.. code-block:: ini

   [uwsgi]
   ...
   cache-udp-server = 225.1.1.1:7171
   cache-udp-node = 225.1.1.1:7171

* A new gateway server is in development, named "udprepeater". It will basically forward all of UDP packets it receives to the subscribed back-end nodes. It will allow you to maintain the zero-config style of the subscription system (basically you only need to configure a single cache UDP node pointing to the repeater).
* Currently there is no security between the cache nodes. For some users this may be a huge problem, so a security mode (encrypting the packets) is in development.
