uWSGI 2.0.11
============

[20150701]

Bugfixes
********

- [pypy] fixed misuse of ffi.string
- fixed detection for gcc 5 (jimfunk)
- fixed shared sockets for gateways
- [psgi] Changed abs to labs because offset is declared as a long (Peter H. Ezetta)
- add null terminator to uwsgi_get_dot_h() and uwsgi_config_py() (Jay Oster)
- fixed thread waiting during stop/restart (Kaiwen Xu)
- fixed chain reloading verbosity
- [python] fixed spooler job reference counting (Curtis Maloney)
- various static analysis improvements (Riccardo Magliocchetti)
- fixed sharedarea support for very big ranges
- fixed gzip transformation for zero-sized responses (Curtis Maloney)
- fixed management of https client certificate authentication (Vladimir Didenko)
- fixed OpenBSD build
- fixed TMPFILE permissions


New Features
************

The mem_collector thread
^^^^^^^^^^^^^^^^^^^^^^^^

Evil memory monitors (like --evil-reload-on-rss) are now asynchronously managed by a dedicated thread.

This solves the issue of runaway processes not catched by the master.

fixpathinfo routing action
^^^^^^^^^^^^^^^^^^^^^^^^^^

This is another step in removing the need of the infamous uwsgi_modifier1 30 relic.

This routing action assumes the PATH_INFO cgi var has the SCRIPT_NAME part included.

This action allows you to set SCRIPT_NAME in nginx without bothering to rewrite the PATH_INFO (something nginx cannot afford)

.. code-block:: ini

   [uwsgi]
   ; blindly assumes PATH_INFO is clobbered with SCRIPT_NAME
   route-run = fixpathinfo:

uwsgi[sor] and time[micros] routing vars
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This two new vars exposes the start of the current request (in micros) and the current time (again in micros)

.. code-block:: ini

   [uwsgi]
   route-run = log:request started at ${uwsgi[sor]}
   route-run = log:current micros time is ${time[micros]}

wait-for-socket
^^^^^^^^^^^^^^^

This works like wait-for-fs/iface/file/dir

The spawn of the instance is suspended until the specified tcp/unix socket is ready.

You can use it to synchronize vassals spawn (like stopping a vassal until a postgresql server has been spawned)

wait_for hooks
^^^^^^^^^^^^^^

All of the wait-for-* functions can now be used as a hook:

.. code-block:: ini

   [uwsgi]
   ; wait for postgres soon after privileges drop
   hook-as-user = wait_for_socket:127.0.0.1:5432

Availability
************

You can download uWSGI 2.0.11 from

https://projects.unbit.it/downloads/uwsgi-2.0.11.tar.gz
