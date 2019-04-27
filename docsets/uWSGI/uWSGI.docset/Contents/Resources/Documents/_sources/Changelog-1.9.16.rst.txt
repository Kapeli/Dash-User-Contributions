uWSGI 1.9.16
============

Changelog [20130914]


Important change in the gevent plugin shutdown/reload procedure !!!
*******************************************************************

The shutdown/reload phase when in gevent mode has been changed to better integrate
with multithreaded (and multigreenlet) environments (most notably the newrelic agent).

Instead of "joining" the gevent hub, a new "dummy" greenlet is spawned and "joined".

During shutdown only the greenlets spawned by uWSGI are taken in account, and after all of them are destroyed
the process will exit. This is different from the old approach where the process wait for ALL the currently available greenlets
(and monkeypatched threads).

If you prefer the old behaviout just specify the option --gevent-wait-for-hub 


Bugfixes/Improvements
*********************

- fixed CPython reference counting bug in rpc and signal handlers
- improved smart-attach-daemon for slow processes
- follow Rack specifications for QUERY_STRING,SCRIPT_NAME,SERVER_NAME and SERVER_PORT
- report missing internal routing support (it is only a warning when libpcre is missing)
- better ipcsem support during shutdown and zerg mode (added --persistent-ipcsem as special case)
- fixed fastcgi bug exposed by apache mod_fastcgi
- do not call pre-jail hook on reload
- force linking with -lrt on solaris
- report thunder lock status
- allow custom priority in rsyslog plugin

New features
************

FreeBSD jails native support
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

uWSGI got nativr FreeBSD jails support. Official documentation is here :doc:`FreeBSDJails`

The Rados plugin
^^^^^^^^^^^^^^^^

Author: Javier Guerra

Based on the :doc:`GlusterFS` plugin, a new one allowing access to Rados object storage is available:

 :doc:`Rados`

The TunTap router
^^^^^^^^^^^^^^^^^

This new gateway is the result of tons of headaches while trying to build better (read: solid) infrastructures with Linux namespaces.

While dealing with uts, ipc, pid and filesystem namespaces is pretty handy, managing networking is a real pain.

We introduced lot of workaroud in uWSGI 1.9.15 (especially to simplify the veth management) but finally we realized
that those systems do not scale in terms of management.

The TunTap router tries to solve the issue moving the networking part of jailed vassals in user space.

Basically each vassal create one or more tuntap devices. This devices are connected (via a unix socket) to the "tuntap router"
allowing access from the vassal to the external network.

That means a single network interface in the main namespace and one for each vassal.

The performance are already quite good (we are only losing about 10% in respect of kernel-level routing) but can be optimized.

In addition to this the tuntap router has a simple userspace firewall you can use to manage complex routing rules.

Documentation is still in progress, but you can configure a tuntap router following the big comment on top of this file:

https://github.com/unbit/uwsgi/blob/master/plugins/tuntap/tuntap.c

while you can connect to it with ``--tuntap-device <dev> <socket>`` where <dev> is the tuntap device to create in the vassal/client and <socket> is the unix address
of the tuntap router

An Example Emperor

.. code-block:: ini

   [uwsgi]
   tuntap-router = emperor0 /tmp/tuntap.socket
   exec-as-root = ifconfig emperor0 192.168.0.1 netmask 255.255.255.0 up
   exec-as-root = iptables -t nat -F
   exec-as-root = iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
   exec-as-root = echo 1 >/proc/sys/net/ipv4/ip_forward
   emperor-use-clone = ipc,uts,fs,pid,net
   emperor = /etc/vassals

and one of its vassals:

.. code-block:: ini

   [uwsgi]
   tuntap-device = uwsgi0 /tmp/tuntap.socket
   exec-as-root = ifconfig lo up
   exec-as-root = ifconfig uwsgi0 192.168.0.2 netmask 255.255.255.0 up
   exec-as-root = route add default gw 192.168.0.1
   exec-as-root = hostname foobar
   socket = /var/www/foobar.socket
   psgi-file = foobar.pl

Linux O_TMPFILE
^^^^^^^^^^^^^^^

Latest Linux kernel support a new operational mode for opening files: O_TMPFILE

this flag open a temporary file (read: unlinked) without any kind of race conditions.

This mode is automatically used if available (no options needed)

Linux pivot-root
^^^^^^^^^^^^^^^^

When dealing with Linux namespaces, changing the root filesystem is one of the main task.

chroot() is generally too simple, while pivot-root allows you more advanced setup

The syntax is ``--pivot-root <new_root> <old_root>``

Cheaper memlimit
^^^^^^^^^^^^^^^^

Author: Łukasz Mierzwa

This new check allows control of dynamic process spawning based on the RSS usage:

https://uwsgi-docs.readthedocs.io/en/latest/Cheaper.html#setting-memory-limits

Log encoders
^^^^^^^^^^^^

There are dozens of log engines and storage system nowadays. The original uWSGI approach was developing a plugin for every engine.

While working with logstash and fluentd we realized that most of the logging pluging are reimplementations of the same concept over and over again.

We followed an even more modular approach introducing log encoders:

:doc:`LogEncoders`

They are basically patterns you can apply to each logline

New "advanced" Hooks
^^^^^^^^^^^^^^^^^^^^

A new series of hooks for developers needing little modifications to the uWSGI cores are available.

Documention about the whole hooks subsystem is now available (it is a work in progress):

:doc:`Hooks`

New mount/umount hooks
^^^^^^^^^^^^^^^^^^^^^^

When dealing with namespaces and jails, mounting and unmounting filesystems is one of the most common tasks.

As the mount and umount commands could not be available during the setup phase, these 2 hooks have been added directly calling the
syscalls.

Check :doc:`Hooks`


Availability
************

uWSGI 1.9.16 has been released on September 14th 2013. You can download it from:

https://projects.unbit.it/downloads/uwsgi-1.9.16.tar.gz
