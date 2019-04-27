uWSGI 1.9.9
===========

Changelog [20130508]

Special Warning !!!
*******************

The router_basicauth plugin has changed its default behaviour to return "break" if authorization fails.

The "basicauth-next" action, uses the old behaviour (returning "next")

This new approach should reduce security problems caused by wrong configurations

Bugfixes
********

* do not increment "tx" statistics counter for "unaccountable" plugins
* fixed --backtrace-depth
* fixed cache-sync parsing
* fixed mule farms initialization
* fixed multithreading bug when regexp conditional route is used
* fixed default-app usage in the psgi plugin
* fixed python dynamic mode + threads
* fixed error reporting in corerouter when retry is in place
* correctly report harakiri condition for gateways

New Features
************

The WebDav plugin
^^^^^^^^^^^^^^^^^

WebDav is one of the much requested features for the project. We now have a beta-quality plugin, already supporting
additional standards like the carddav:

https://github.com/unbit/uwsgi/blob/master/t/webdav/carddav.ini

The official modifier is 35, and to mount a simple directory as a webdav shares (for use with windows, gnome...) you only need to
specify the --webdav-mount option:

.. code-block:: ini

   [uwsgi]
   plugin = webdav
   http-socket = :9090
   http-socket-modifier1 = 35
   webdav-mount = /home/foobar

remember to protect shares:

.. code-block:: ini

   [uwsgi]
   plugin = webdav,router_basicauth
   http-socket = :9090
   http-socket-modifier1 = 35
   route-run = basicauth:CardDav uWSGI server,unbit:unbit
   webdav-mount = /home/foobar

WebDav attributes are stored as filesystem xattr, so be sure to use a filesystem supporting them (ext4, xfs, hfs+...)

LOCK/UNLOCK support is still incomplete

Official docs will be available soon.

Support for Go 1.1 (more or less, sad news for go users...)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Albeit you can successfully embed go 1.1 apps in uWSGI, go 1.1 will be completely fork() unsafe.

That means you are not able to use multiprocessing, the master, mules and so on.

Basically half of the uWSGI features will be no more usable in go apps.

Things could change in the future, but currently our objective is better integration with the gccgo project.

Go 1.0.x will continue to be supported (unless gccgo shows itself as a better alternative)

More to come soon.

Improved async modes
^^^^^^^^^^^^^^^^^^^^

Stackless, Greenlet and Fiber support have been updated to support new async features

The radius plugin
^^^^^^^^^^^^^^^^^

You can now authenticate over radius servers using the router_radius plugin:

.. code-block:: ini

   [uwsgi]
   plugin = webdav,router_radius
   http-socket = :9090
   http-socket-modifier1 = 35
   route-run = radius:realm=CardDav uWSGI server,server=127.0.0.1:1812
   webdav-mount = /home/foobar

The SPNEGO plugin
^^^^^^^^^^^^^^^^^

Another authentication backend, using SPNEGO (kerberos)

.. code-block:: ini

   [uwsgi]
   plugin = webdav,router_spnego
   http-socket = :9090
   http-socket-modifier1 = 35
   route-run = spnego:HTTP@localhost
   webdav-mount = /home/foobar

The plugin is beta quality as it leaks memory (it looks like a bug in MIT-kerberos) and Heimdal implementation does not work.

More reports are wellcomed

The ldap authenticator
^^^^^^^^^^^^^^^^^^^^^^

(Author: Łukasz Mierzwa)

Currently it lacks SASL support. Will be improved soon.

.. code-block:: ini

   [uwsgi]
   ...
   plugins = router_ldapauth
   route = ^/a ldapauth:LDAP realm,url=ldap://ldap.domain,com;basedn=ou=users,dc=domain.com;binddn=uid=proxy,dc=domain,dc=com;bindpw=password



New internal routing features
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We removed the GOON action, as it was messy and basically useless with the new authentication approach

The "setscriptname" action has been added to override the internally computed SCRIPT_NAME (not only the var)

The "donotlog" action forces uWSGI to not log the current request

The "regexp" routing conditions has been improved to allows grouping. Now you can easily manipulate strings and adding them as new request VARS:

.. code-block:: ini

   [uwsgi]
   ...
   route-if = regexp:${REQUEST_URI};^/(.)oo addvar:PIPPO=$1
   route-run = log:PIPPO IS ${PIPPO}

this will take the first char of foo and place in the PIPPO request var

Gevent atexit hook
^^^^^^^^^^^^^^^^^^

uwsgi.atexit hook is now honoured by the gevent plugin (Author: André Cruz)


Streaming transformations
^^^^^^^^^^^^^^^^^^^^^^^^^

Transformations can be applied on the fly (no buffering involved).

Check updated docs: :doc:`Transformations`

The xattr plugin
^^^^^^^^^^^^^^^^

The xattr plugin allows you to reference files extended attributes in the internal routing subsystem:

.. code-block:: ini

   [uwsgi]
   ...
   route-run = addvar:MYATTR=user.uwsgi.foo.bar
   route-run = log:The attribute is ${xattr[/tmp/foo:MYATTR]}


or (variant with 2 vars)

.. code-block:: ini

   [uwsgi]
   ...
   route-run = addvar:MYFILE=/tmp/foo
   route-run = addvar:MYATTR=user.uwsgi.foo.bar
   route-run = log:The attribute is ${xattr2[MYFILE:MYATTR]}


The airbrake plugin
^^^^^^^^^^^^^^^^^^^

(Author: Łukasz Mierzwa)

Currently at early stage of development allows sending uWSGI exceptions and alarms to airbrake servers.

Official docs will be available soon.

Legion Daemons
^^^^^^^^^^^^^^

(Author: Łukasz Mierzwa)

No, it is not a blackmetal band, it is a new feature of :doc:`Legion` allowing you to run external processes
only when an instance is a lord:

.. code-block:: ini

   [uwsgi]

   master = true
   http = :8081
   stats = :2101
   wsgi-file = tests/staticfile.py

   logdate = true

   legion = legion1 225.1.1.1:19678 100 bf-cbc:abc
   legion-node = legion1 225.1.1.1:19678

   legion-attach-daemon = legion1 memcached -p 10001

   legion-smart-attach-daemon = legion1 /tmp/memcached.pid memcached -p 10002 -d -P /tmp/memcached.pid


--touch-exec
^^^^^^^^^^^^

A new "touch" option (like --touch-reload) is available, triggering the execution of a command:

.. code-block:: ini

   [uwsgi]
   ...
   touch-exec = /tmp/foobar run_my_script.sh
   touch-exec = /var/test/foo.txt run_my_second_script.sh arg1 arg2


Math for cache
^^^^^^^^^^^^^^

You can now use the caching subsystem to store 64bit signed numbers and apply atomic operations on them.

The uwsgi api has been extended with 5 new functions (currently exposed only by the python plugin):

*uwsgi.cache_num(key[,cache]) -> get the 64bit number from the specified item

*uwsgi.cache_inc(key[,amount=1,expires,cache]) -> increment the specified key by the specified amount

*uwsgi.cache_dec(key[,amount=1,expires,cache]) -> deccrement the specified key by the specified amount

*uwsgi.cache_mul(key[,amount=2,expires,cache]) -> multiply the specified key by the specified amount

*uwsgi.cache_div(key[,amount=2,expires,cache]) -> divide the specified key by the specified amount

The new api has been exposed to the routing subsystem, allowing you to implement advanced patterns, like the request limiter:

https://github.com/unbit/uwsgi/blob/master/t/routing/limiter.ini

the example shows hot to limit the request of a single ip to 10 every 30 seconds

The long-term objective of this new feature is being the base for the upcoming metric subsystem

Availability
************

uWSGI 1.9.9 will be availabel since 20130508 at the following url

https://projects.unbit.it/downloads/uwsgi-1.9.9.tar.gz

