uWSGI 2.0.5
===========

Changelog [20140601]

Bugfixes
--------

- fixed support for repeated headers in the Lua plugin (Credits: tizoc)
- fixed support for embedding configuration in OpenBSD and NetBSD
- various fixes in the cURL-based plugins (Credits: Yu Zhao)
- fixed milliseconds-based waits
- fixed sharedarea's poller
- fixed the JSON encoder in the stats server
- fixed FastCGI parser and implemented EOF management (Credits:  Jeff Trawick)
- improved fast on-demand mode
- avg_rt computation is excluded for static files
- fixed variable support in uwsgi internal router
- fixed websockets + keepalive ordering
- disable SIGPIPE management in coroutine-based loop engines
- fixed 64-bit sharedarea management in 32-bit systems
- honor chmod/chown-socket in fd0 mode
- hack to avoid Safari on iOS making a mess with keepalive
- fixed log setup when both --logto and --log2 are used (Credits: Łukasz Mierzwa)
- fixed mule_get_msg EAGAIN
- signal_pidfile returns the right error code
- fixed asyncio on OSX

New features
------------

graceful reload of mule processes (Credits: Paul Egan)
******************************************************

`SIGHUP` is now sent to mules instead of directly killing them.
You are free to trap/catch the signal in your code.
If a mule does not die in the allowed "mercy time" (`--mule-reload-mercy`, default 60 seconds), SIGKILL will be sent.

`return` routing action (Credits: Yu Zhao)
******************************************

This new action will allow users to write simplified "break" clauses.

For example, "return:403" is equivalent to "break:403 Forbidden", with response body "Forbidden".

The response body is quite useful for telling end users what's going wrong.

--emperor-no-blacklist
**********************

This new option completely disables the Emperor's blacklisting subsystem.

Icecast2 protocol helpers
*************************

One of the upcoming unbit.com projects is a uWSGI based audio/video streaming server.

The plugin (should be released during Europython 2014) already supports the Icecast2 protocol.

A bunch of patches have been added to the HTTP router to support the Icecast2 protocol.

For example the ``--http-manage-source`` option allows the HTTP router to honor `SOURCE` method requests, automatically placing them in raw mode.

--metrics-no-cores, --stats-no-cores, --stats-no-metrics
********************************************************

When you have hundreds (or thousands) of async cores, exposing metrics for them may get really slow.

Three new options have been added allowing you to disable the generation of core-related metrics and consequently their usage in the stats server.

sharedarea improvements
***********************

The sharedarea API continues to improve. Latest patches include support for memory-mapping files (or devices) (`mmap`) directly from the command line.

An interesting way to test this is mapping the BCM2835 memory of the Raspberry PI. This little example allows you to read the RPi system timer.

.. code-block:: sh

   uwsgi --sharedarea file=/dev/mem,offset=0x20003000,size=4096 ...
   
Now you can read a 64-bit value from the first (zero-based) sharedarea:

.. code-block:: python

   # read 64bit from 0x20003004
   timer = uwsgi.sharedarea_read64(0, 0x04)
   
(Obviously, when reading and writing the Raspberry Pi memory, be careful. An error could crash the whole system!)

UWSGI_GO_CHEAP_CODE
*******************

This exit code (15) can be raised by a worker to tell the master to not respawn it.

PROXY1 support for the http router (Credits: bgglenn)
*****************************************************

The option ``--http-enable-proxy-protocol`` allows the HTTP router to understand PROXY1 protocol requests, such as those made by Haproxy or Amazon Elastic Load Balancer (ELB).

reset_after_push for metrics (Credits: Babacar Tall)
****************************************************

This metric attribute ensures that the metric value is reset to 0 (or its hardcoded `initial_value`) after the metric is pushed to external systems (such as Carbon or StatsD).

setremoteaddr
*************

This new routing action allows you to completely override the `REMOTE_ADDR` detected by protocol handlers:

.. code-block:: ini

   [uwsgi]
   ; treat all requests as local
   route-run = setremoteaddr:127.0.0.1

the `resolve` option
********************

There are uWSGI options (or plugins) that do not automatically resolve DNS names to IP addresses. This option allows you to map
a placeholder to the DNS resolution result of a string:

.. code-block:: ini

   [uwsgi]
   ; place the dns resolution of 'example.com' in the 'myserver' placeholder
   resolve = myserver=example.com
   ; %(myserver) would now be 93.184.216.119
   subscribe2 = server=%(myserver),key=foobar

Availability
-------------

uWSGI 2.0.5 has been released on [20140601] and can be downloaded from:

https://projects.unbit.it/downloads/uwsgi-2.0.5.tar.gz
