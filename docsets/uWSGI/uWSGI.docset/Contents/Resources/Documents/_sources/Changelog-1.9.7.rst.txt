uWSGI 1.9.7
===========


Bugfixes
********

- fixed teajs engine build

- fixed offloading status code (set to 202 when a request is offloaded)

- execute cron tasks within 60 second resolution, instead of 61 seconds

- fixed websocket proxy

- check for python3 unicode encoding (instead of crashing...)

- fixed ipcsem removal on reload

- fixed kqueue timer on OpenBSD, NetBSD and DragonFlyBSD

- fixed/reimplemented perl uwsgi::register_rpc

- fixed fd leak on sendfile() error

- fixed Content-Length when gzip file variant is used

- allows non-request plugins to register rpc functions

- more robust error checking for cgroups

- honour SCRIPT_NAME the in the PSGI plugin when multiple perl apps are mounted


New features
************


Legion cron
^^^^^^^^^^^

A common needs when multiple instances of an application are running, is to force only one
of them to run cron tasks. The new --legion-cron uses :doc:`Legion` to accomplish that:

.. code-block:: ini

   [uwsgi]
   ; use the new legion-mcast shortcut (with a valor 90)
   legion-mcast = mylegion 225.1.1.1:9191 90 bf-cbc:mysecret
   ; run the script only if the instance is the lord of the legion "mylegion"
   legion-cron = mylegion -1 -1 -1 -1 -1 my_script.sh


Curl cron
^^^^^^^^^

The curl_cron plugin has been added allowing the cron subsystem to call urls (via libcurl) instead of unix commands:

.. code-block:: ini

   [uwsgi]
   ; call http://uwsgi.it every minute
   curl-cron = -1 -1 -1 -1 -1 http://uwsgi.it/

The output of the request is reported in the log

The UWSGI_EMBED_PLUGINS build variable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ou can now embed plugins on the fly during the build phase. Check this example:

.. code-block:: sh

   UWSGI_EMBED_PLUGINS=gridfs,rack UWSGI_PROFILE=psgi make

this will build a monolithic binary with the default profile for psgi + the gridfs and the rack plugins (both embedded in the binary)


Gzip caching
^^^^^^^^^^^^

The cachestore routing function can now directly store items in gzip format.

Check the CachingCookbook: https://uwsgi-docs.readthedocs.io/en/latest/tutorials/CachingCookbook.html

--skip-atexit
^^^^^^^^^^^^^

A bug in the mongodb client library could cause a crash of the uWSGI server during shutdown/reload. This option
avoid calling atexit() hooks. If you are building a :doc:`GridFS` infrastructure you may want to use this option while the MongoDB guys solve the issue.

proxyhttp and proxyuwsgi
^^^^^^^^^^^^^^^^^^^^^^^^

The http and uwsgi routing instructions are now more smart. You can cache their output and get the right status code in the logs.

This requires you to NOT use offloading. If offloading is in place and do not want to use it for this two router use the proxy-prefixed variant
that will skip offloading.

You can now make cool things like:

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   ; create a cache of 100 items
   cache = 100
   ; check if a cached value is available
   route-run = cache:key=${REQUEST_URI}
   ; proxy all request to http://unbit.it
   route-run = http:81.174.68.52:80,unbit.it
   ; and cache them for 5 minutes
   route-run = cachestore:key=${REQUEST_URI},expires=300

The transformation api
^^^^^^^^^^^^^^^^^^^^^^

A generic api for manipulating the response has been added (cachestore uses it)

check :doc:`Transformations`

--alarm-fd
^^^^^^^^^^

We are improving :doc:`AlarmSubsystem` to be less-dependent on loglines. You can now trigger alarms when an fd is ready for read.

This is really useful for integration with the Linux eventfd() facility.

For example you can monitor (and throw an alarm) when your cgroup is running the OOM-Killer:

.. code-block:: ini

   [uwsgi]
   ; define an 'outofmemory' alarm that simply print the alarm in the logs
   alarm = outofmemory log:
   ; raise the alarm (with the specified message) when fd is ready (this is an eventfd se we read 8 bytes from the fd)
   alarm-fd = outofmemory $(CGROUP_OOM_FD):8 OUT OF MEMORY !!!

in this example CGROUP_OOM_FD is an environment variable mapping to the number of an eventfd() filedescriptor inherited from some kind
of startup script. Maybe (in the near future) we could be able to directly define this kind of monitor directly in uWSGI.

More information on the eventfd() + cgroup integration are here: https://www.kernel.org/doc/Documentation/cgroups/cgroups.txt

an example perl startup script:

.. code-block:: pl

   use Linux::FD;
   use POSIX;

   my $foo = Linux::FD::Event->new(0);
   open OOM,'/sys/fs/cgroup/uwsgi/memory.oom_control';
   # we dup() the file as Linux::FD::Event set the CLOSE_ON_EXEC bit (why ???)
   $ENV{'CGROUP_OOM_FD'} = dup(fileno($foo)).'';

   open CONTROL,'>/sys/fs/cgroup/uwsgi/cgroup.event_control';
   print CONTROL fileno($foo).' '.fileno(OOM)."\n";
   close CONTROL;

   exec 'uwsgi','mem.ini';

The spooler server plugin and the cheaper busyness algorithm compiled in by default
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In extremely high-loaded scenario the busyness cheaper algorithm (by Łukasz Mierzwa) has been a real
silver bullet in the past months allowing adaptive process spawning to be based on real usage time taking in account
performance and response time. For this reason the plugin is now builtin by default.

In addition to this the remote spooler plugin (allowing external process to enqueue jobs) has been added too in the default build profile.


Availability
************

uWSGI 1.9.7 will be available since 20130422 at this url:

https://projects.unbit.it/downloads/uwsgi-1.9.7.tar.gz
