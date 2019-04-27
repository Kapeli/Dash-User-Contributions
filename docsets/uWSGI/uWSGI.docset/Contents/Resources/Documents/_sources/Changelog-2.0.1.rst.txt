uWSGI 2.0.1
===========

Changelog [20140209]

Bugfixes and improvements
*************************

- due to a wrong prototype declaration, building uWSGI without SSL resulted in a compilation bug. The issue has been fixed.
- a race condition preventing usage of a massive number of threads in the PyPy plugin has been fixed
- check for heartbeat status only if heartbeat subsystem has been enabled
- improved heartbeat code to support various corner cases
- improved psgi.input to support offset in read()
- fixed (and simplified) perl stacktrace usage
- fixed sni secured subscription
- CGI plugin does not require anymore that Status header is the first one (Andjelko Horvat)
- fixed CPython mule_msg_get timeout parsing
- allows embedding of config files via absolute paths
- fixed symcall rpc
- fixed a memory leak in CPython spooler api (xiaost)
- The --no-orphans hardening has been brought back (currently Linux-only)
- improved dotsplit router mode to reduce DOS risk
- sub-Emperor are now loyal by default
- fixed non-shared ruby 1.8.7 support
- fixed harakiri CPython tracebacker
- request vars are now correctly exposed by the stats server
- support log-master for logfile-chown
- improved legion reload
- fixed tuntap netmask
- fixed busyness plugin without metrics subsystem

New features
************

uWSGI 2.0 is a LTS branch, so do not expect too much new features. 2.0.1 is the first maintainance release, so you still get a bunch of them
(mainly features not complete in 2.0)


Perl native Spooler support
---------------------------

Perl finally got full support for the Spooler subsystem. In 2.0 we added server support, in 2.0.1 we completed client support too.

.. code-block:: pl

   use Data::Dumper;

   uwsgi::spooler(sub {
        my $env = shift;
        print Dumper($env);
        return uwsgi::SPOOL_OK;
   });

   uwsgi::spool({'foo' => 'bar', 'arg2' => 'test2'})


--alarm-backlog
---------------

Raise the specified alarm when the listen queue is full

.. code-block:: ini

   [uwsgi]
   alarm = myalarm cmd:mail -s 'ALARM ON QUEUE' admin@example.com
   alarm-backlog = myalarm

--close-on-exec2
----------------

Credits: Kaarle Ritvanen

this flag applies CLOSE_ON_EXEC socket flag on all of the server socket. Use it if you do not want you request-generated processes to inherit the server file descriptor.

Note: --close-on-exec applies the flag on all of the sockets (client and server)

simple notifications subsystem
------------------------------

An annoying problem with subscriptions is that the client does not know if it has been correctly subscribed to the server.

The notification subsystem allows you to add to the subscription packet a datagram address (udp or unix) on which the server will send back
messages (like successful subscription)

.. code-block:: ini

   [uwsgi]
   ; enable the notification socket
   notify-socket = /tmp/notify.socket
   ; pass it in subscriptions
   subscription-notify-socket = /tmp/notify.socket
   ...
   
the notification subsystem is really generic. Expect more subsystem to use it in the future.

pid namespace for daemons (Linux only)
--------------------------------------

This is a Linux-only, epxerimental feature allowing you to spawn a daemon in a new pid namespace. This feature requires the master running as root.

Check: :doc:`AttachingDaemons`

Resubscriptions
---------------

The fastrouter and the http/https/spdy router now support "resubscription".

You can specify a dgram address (udp or unix) on which all of the subscriptions request will be forwarded to (obviously changing the node address to the router one)

The system could be useful to build 'federated' setup:

.. code-block:: ini

   [uwsgi]
   fastrouter = 192.168.0.1:3031
   fastrouter-subscription-server = 127.0.0.1:5000
   fastrouter-resubscribe = 192.168.0.2:5000
   
with this setup the fastrouter on 192.168.0.2 will have all of the records of 192.168.0.1 with the destination set to 192.168.0.1:3031.

filesystem monitor api
----------------------

The real-time filesystem notification api has been standardized and it is now usable by plugins. The prototype to register a monitor is:

.. code-block:: c

   struct uwsgi_fsmon *uwsgi_register_fsmon(char *path, void (*func) (struct uwsgi_fsmon *), void *data) {
   
it will register a monitor on "path" triggering the function "func" passing "data" as argument.

Remember, this is different from the "touch" api, that is poll-based and can only monitor files. (while fsmon can monitor directories too)

support for yajl 1.0
--------------------

2.0 added support yajl JSON parser (version 2). 2.0.1 added support for 1.0 too

for-readline
------------

a config-logic iterator that yield file lines:

.. code-block:: ini

   [uwsgi]
   for-readline = /etc/myenvs
     env = %(_)
   end-for =

%i and %j magic vars
--------------------

%i -> returns the inode of the currently parsed file

%j -> returns hex representation of 32bit djb33x hashing of the currently parsed absolute filename

--inject-before and --inject-after
----------------------------------

This two new options should make the config templating system complete for everyone.

They basically prepend and append 'blobs' to a config file.

Yeah, it sound a bit nonsense.

Check the following example:

header.xml:

.. code-block:: xml

   <uwsgi>
       <socket>:3031</socket>
       
footer.xml:

.. code-block:: xml

   <master/>
       </uwsgi>
       
and body.xml:

.. code-block:: xml

   <processes>8</processes>
   
you can build a single config tree with:

.. code-block:: sh

   uwsgi --show-config --inject-before header.xml --inject-after footer.xml --xml body.xml
   
this approach, albeit raw, allows you to use magic-vars in more advanced ways (as you have control on the context of the file using them)

Note: ordering is important, --inject-before and --inject-after must be specified before the relevant config option.

--http-server-name-as-http-host
-------------------------------

Some Ruby/Rack middleware make a questionable check on SERVER_NAME/HTTP_HOST matching.

This flag allow the http router to map SERVER_NAME to HTTP_HOST automatically instead of instructing your uWSGI instances to do it.

better Emperor's Ragnarok (shutdown procedure)
----------------------------------------------

The 'Ragnarok' is the Emperor phase executed when you ask him to shutdown.

Before 2.0.1, this procedure simply send KILL to vassals to brutally destroy them.

The new Ragnarok is way more benevolent, asking vassals to gracefully shutdown.

The Emperor tolerance for vassals not shutting down can be tuned with --reload-mercy (default 30 seconds)

PyPy paste support
------------------

Two new options for PyPy plugin have been added for paste support:

--pypy-paste <config>

--pypy-ini-paste <ini>

they both maps 1:1 to the CPython variants, but contrary to it they automatically fix logging

Availability
************

You can download uWSGI 2.0.1 from: https://projects.unbit.it/downloads/uwsgi-2.0.1.tar.gz
