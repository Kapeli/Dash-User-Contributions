uWSGI 2.0.7
===========

Changelog [20140905]

Bugfixes
********

- fixed counters in Statsd plugin (Joshua C. Forest)
- fixed caching in PHP plugin (Andrew Bevitt)
- fixed management of system users starting with a number
- fixed request body readline using `memmove` instead of `memcpy` (Andrew Wason)
- ignore "user" namespace in `setns` (still a source of problems)
- fixed Python3 RPC bytes/string mess (result: we support both)
- do not destroy the Emperor on failed mount hooks
- fixed symbol lookup error in the Mono plugin on OS X (Ventero)
- fixed FastCGI and SCGI protocols error when out of buffer happens
- fixed Solaris/SmartOS I/O management
- fixed two memory leaks in the RPC subsystem (Riccardo Magliocchetti)
- fixed the Rados plugin's PUT method (Martin Mlynář)
- fixed multiple Python mountpoints with multiple threads in cow mode
- stats UNIX socket is now deleted by `vacuum`
- fixed off-by-one corruption in cache LRU mode
- force single-CPU build in Cygwin (Guido Notari)

New Features and improvements
*****************************

Allow calling the spooler from every CPython context
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

At Europython 2014, Ultrabug (an uWSGI contributor and packager) asked for the possibility to spool tasks directly from a greenlet.

Done.

store_delete cache2 option
^^^^^^^^^^^^^^^^^^^^^^^^^^

Author: goir

The `store_delete` flag of the `--cache2` option allows you to force the cache engine to automatically remove invalid
backing store files instead of steadfastly refusing to launch.

file logger rotation
^^^^^^^^^^^^^^^^^^^^

Author: Riccardo Magliocchetti

The `file` logger has been extended to allow the use of rotation (the same system used by the non-pluggable `--logto`).

https://github.com/unbit/uwsgi/commit/0324e5965c360dccfb873ffe351dec88ddab59c5

Vassal plugin hooks
^^^^^^^^^^^^^^^^^^^

The plugin hook API has been extended with two new hooks: `vassal` and `vassal_before_exec`.

They allow customizing a vassal soon after its process has been created.

The first third-party plugin using it is 'apparmor': https://github.com/unbit/uwsgi-apparmor

This allows you to apply an Apparmor profile to a vassal.


Broodlord improvements
^^^^^^^^^^^^^^^^^^^^^^

The Broodlord subsystem has been improved with a new option: `--vassal-sos` that automatically ask for reinforcement when all of the workers of an instance are busy.

In addition to this a sysadmin can now manually ask for reinforcement sending the 'B' command to the master FIFO of an instance.

Availability
************

uWSGI 2.0.7 has been released on 20140905, and you can download it from

https://projects.unbit.it/downloads/uwsgi-2.0.7.tar.gz
