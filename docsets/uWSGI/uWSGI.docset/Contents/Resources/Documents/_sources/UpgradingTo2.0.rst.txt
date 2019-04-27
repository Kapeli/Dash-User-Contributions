Upgrading your 1.x uWSGI instances to 2.0 (work in progress)
============================================================

The following notes are for users moving from 1.0, 1.2 and 1.4 to uWSGI 2.0.

Users of the 1.9 tree can skip this document as 2.0 is a "stabilized/freezed" 1.9.

What's new
----------

License change
**************

uWSGI is now GPL2 + linking exception instead of plain GPL2.

This should address some legal issues with users compiling uWSGI as a library (libuwsgi.so) and loading non-GPL compatible plugins/libraries.

Non-blocking by default
***********************

All of the I/O of the uWSGI stack (from the core to the plugins) is now fully non-blocking.

No area in the whole stack is allowed to block (except your app obviously), and plugins must use uWSGI's I/O API.

When you load loop engines like gevent or Coro::AnyEvent, the uWSGI internals are patched to support their specific non-blocking hooks.

What does this mean for app developers?

Well, the most important aspect is that network congestions or kernel problems do not block your instances and badly behaving peers
are closed if they do not unblock in the socket-timeout interval (default 4 seconds).

Newer, faster and better parsers
********************************

uWSGI 2.0 has support for pluggable protocols. The following protocols are supported and all of them have been updated
for better performance:

* ``uwsgi`` -- the classic uwsgi parser, improved for reduced syscall usage
* ``http`` -- the classic HTTP parser, improved for reduced syscall usage (supports the PROXY1 protocol)
* ``https`` -- (new) support for native HTTPS
* ``fastcgi`` -- classic FastCGI parser, improved for reduced syscall usage
* ``scgi`` -- (new) support for SCGI
* ``suwsgi`` -- (new) secured uwsgi, uwsgi over SSL (supported by Nginx 1.5)
* ``puwsgi`` -- (new) persistent uwsgi, uwsgi with persistent connections, supported only internally
* ``mongrel2`` -- classic zeromq/mongrel2 support, now it is exposed as a plugin
* ``raw`` -- (new) fake parser, allows you to write applications directly working on file descriptors

New reloading ways
******************

uWSGI 2.0 introduces a blast of new ways for reloading instances.

.. seealso::

   :doc:`TheArtOfGracefulReloading`

Other new features
******************

* :doc:`MasterFIFO` -- A signal-free new approach for managing your instances.
* :doc:`Caching` & :doc:`tutorials/CachingCookbook` -- The new generation caching subsystem.
* :doc:`SharedArea` -- The new sharedarea.
* :doc:`SNI`
* :doc:`Legion`
* :doc:`WebSockets`
* :doc:`Hooks`
* :doc:`Transformations`
* :doc:`Namespaces`
* :doc:`FreeBSDJails`
* :doc:`Metrics`
* :doc:`tutorials/GraphiteAndMetrics`
* :doc:`RPC` -- now supports 64-bit length responses

New plugin build system
***********************

It is pretty fun (and easy) to write uWSGI plugins, but (funnily enough) the worst aspect was building them, as dealing with build profiles, cflags, ldflags and friends tend to lead to all sorts of bugs and crashes.

A simplified (and saner) build system for external plugins has been added. Now you only need to call the uwsgi binary you want to build the plugin for:

.. code-block:: sh

   uwsgi --build-plugin <plugin>
   
where <plugin> is the directory where the plugin sources (and the uwsgiplugin.py file) are stored.

.. seealso::

   :doc:`ThirdPartyPlugins`

Strict mode
***********

while having the freedom of defining custom options in uWSGI config files is a handy features, sometimes typos will
bring you lot of headaches.

Adding --strict to your instance options will instruct uWSGI config parser to raise an error when not-available options have been specified.

If you are in trouble and want to be sure you did not have written wrong options, add --strict and retry

Cygwin support
**************

Yes, you can now build and run uWSGI on Windows systems :(

kFreeBSD support
****************

PyPy support
************

JVM support
***********

Mono support
************

V8 support
**********

Upgrading Notes
---------------

* Snapshotting mode is no longer available. Check the new graceful reloading ways for better approaches.
* Mongrel2 support is no longer a built-in. you have to build the 'mongrel2' plugin to pair uWSGI with Mongrel2.
* LDAP and Sqlite support has been moved to two plugins, you need to load them for using their features.
* Dynamic options are no more.
* The 'admin' plugin is gone.
* Probes have been removed, the alarm framework presents better ways to monitor services.
* The shared area API changed dramatically, check the new sharedarea docs.
