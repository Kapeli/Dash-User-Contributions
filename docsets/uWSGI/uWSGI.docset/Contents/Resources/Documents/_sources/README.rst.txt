The uWSGI project
=================

The uWSGI project aims at developing a full stack for building hosting services.

Application servers (for various programming languages and protocols), proxies, process managers and monitors are all implemented
using a common api and a common configuration style.

Thanks to its pluggable architecture it can be extended to support more platforms and languages.

Currently, you can write plugins in C, C++ and Objective-C.

The "WSGI" part in the name is a tribute to the namesake Python standard, as it has been the first developed plugin for the project.

Versatility, performance, low-resource usage and reliability are the strengths of the project (and the only rules followed).

Included components (updated to latest stable release)
======================================================

The Core (implements configuration, processes management, sockets creation, monitoring, logging, shared memory areas, ipc, cluster membership and the :doc:`SubscriptionServer`)

Request plugins (implement application server interfaces for various languages and platforms: WSGI, PSGI, Rack, Lua WSAPI, CGI, PHP, Go ...)

Gateways (implement load balancers, proxies and routers)

The :doc:`Emperor <Emperor>` (implements massive instances management and monitoring)

Loop engines (implement events and concurrency, components can be run in preforking, threaded, asynchronous/evented and green thread/coroutine modes. Various technologies are supported, including uGreen, Greenlet, Stackless, :doc:`Gevent <Gevent>`, Coro::AnyEvent, :doc:`Tornado <Tornado>`, Goroutines and Fibers)

.. note::

  uWSGI is a very active project with a fast release cycle. For this reason the code and the documentation may not always be in sync.
  We try our best to have good documentation, but it is a hard work. Sorry for that.
  If you are in trouble, the mailing list is the best source for help regarding uWSGI.
  Contributors for documentation (in addition to code) are always welcome.


Quickstarts
===========

.. toctree::
   :maxdepth: 1

   WSGIquickstart
   PSGIquickstart
   RackQuickstart
   Snippets


Table of Contents
=================

.. toctree::
   :maxdepth: 1

   Download
   Install
   BuildSystem
   Management
   LanguagesAndPlatforms
   SupportedPlatforms
   WebServers
   FAQ
   ThingsToKnow
   Configuration
   FallbackConfig
   ConfigLogic
   Options
   CustomOptions
   ParsingOrder
   Vars
   Protocol
   AttachingDaemons
   MasterFIFO
   Inetd
   Upstart
   Systemd
   Circus
   Embed
   Logging
   LogFormat
   LogEncoders
   Hooks
   WorkerOverride
   Glossary
   ThirdPartyPlugins

Tutorials
=========

.. toctree::
   :maxdepth: 1

   tutorials/CachingCookbook
   tutorials/Django_and_nginx
   tutorials/dreamhost
   tutorials/heroku_python
   tutorials/heroku_ruby
   tutorials/ReliableFuse
   tutorials/DynamicProxying
   tutorials/GraphiteAndMetrics


Articles
========

.. toctree::
   :maxdepth: 1

   articles/SerializingAccept
   #articles/MassiveHostingWithEmperorAndNamespaces
   articles/TheArtOfGracefulReloading
   articles/FunWithPerlEyetoyRaspberrypi
   articles/OffloadingWebsocketsAndSSE
   articles/WSGIEnvBehaviour



uWSGI Subsystems
================

.. toctree::
   :maxdepth: 1

   AlarmSubsystem
   Caching
   WebCaching
   Cron
   Fastrouter
   InternalRouting
   Legion
   Locks
   Mules
   OffloadSubsystem
   Queue
   RPC
   SharedArea
   Signals
   Spooler
   SubscriptionServer
   StaticFiles
   SNI
   GeoIP
   Transformations
   WebSockets
   Metrics
   Chunked

Scaling with uWSGI
==================

.. toctree::
   :maxdepth: 1

   Cheaper
   Emperor
   Broodlord
   Zerg
   DynamicApps
   SSLScaling

Securing uWSGI
==============

.. toctree::
   :maxdepth: 1

   Capabilities
   Cgroups
   KSM
   Namespaces
   FreeBSDJails
   ForkptyRouter
   TunTapRouter


Keeping an eye on your apps
===========================

.. toctree::
   :maxdepth: 1

   Nagios
   SNMP
   PushingStats
   Carbon
   StatsServer
   Metrics


Async and loop engines
======================

.. toctree::
   :maxdepth: 1

   Async
   Gevent
   Tornado
   uGreen
   asyncio



Web Server support
==================

.. toctree::
   :maxdepth: 1

   Apache
   Cherokee
   HTTP
   HTTPS
   SPDY
   Lighttpd
   Mongrel2
   Nginx
   OpenBSDhttpd


Language support
==================

.. toctree::
   :maxdepth: 2

   Python
   PyPy
   PHP
   Perl
   Ruby
   Lua
   JVM
   Mono
   CGI
   GCCGO
   Symcall
   XSLT
   SSI
   V8
   GridFS
   GlusterFS
   Rados

Other plugins
=============

.. toctree::
   :maxdepth: 1

   Pty
   SPNEGO
   LDAP


Broken/deprecated features
==========================

.. toctree::
   :maxdepth: 1

   Erlang
   ManagementFlag
   Go


Release Notes
=============

Stable releases
---------------

.. toctree::
   :maxdepth: 1

   Changelog-2.0.18
   Changelog-2.0.17.1
   Changelog-2.0.17
   Changelog-2.0.16
   Changelog-2.0.15
   Changelog-2.0.14 
   Changelog-2.0.13.1
   Changelog-2.0.13
   Changelog-2.0.12
   Changelog-2.0.11.2
   Changelog-2.0.11.1
   Changelog-2.0.11
   Changelog-2.0.10
   Changelog-2.0.9
   Changelog-2.0.8
   Changelog-2.0.7
   Changelog-2.0.6
   Changelog-2.0.5
   Changelog-2.0.4
   Changelog-2.0.3
   Changelog-2.0.2
   Changelog-2.0.1
   Changelog-2.0
   Changelog-1.9.21
   Changelog-1.9.20
   Changelog-1.9.19
   Changelog-1.9.18
   Changelog-1.9.17
   Changelog-1.9.16
   Changelog-1.9.15
   Changelog-1.9.14
   Changelog-1.9.13
   Changelog-1.9.12
   Changelog-1.9.11
   Changelog-1.9.10
   Changelog-1.9.9
   Changelog-1.9.8
   Changelog-1.9.7
   Changelog-1.9.6
   Changelog-1.9.5
   Changelog-1.9.4
   Changelog-1.9.3
   Changelog-1.9.2
   Changelog-1.9.1
   Changelog-1.9



Contact
=======

================== =
Mailing list       http://lists.unbit.it/cgi-bin/mailman/listinfo/uwsgi
Gmane mirror       http://dir.gmane.org/gmane.comp.python.wsgi.uwsgi.general
IRC                #uwsgi @ irc.freenode.org. The owner of the channel is `unbit`.
Twitter            https://twitter.com/unbit
Commercial support http://unbit.com/
================== =

.

Commercial support
==================

You can buy commercial support from http://unbit.com

Donate
======

uWSGI development is maintained by `Unbit <http://unbit.it/>`_ . You can buy commercial support and licensing. If you are not an Unbit customer, or you cannot/do not want to buy a commercial uWSGI license, consider making a donation. Obviously please feel free to ask for new features in your donation.

We will give credit to everyone who wants to sponsor new features.

Check http://unbit.it/uwsgi_donate for the donation link.

Sponsors
========

https://www.pythonanywhere.com/

https://lincolnloop.com/

https://yourlabs.io/oss

https://fili.com

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
