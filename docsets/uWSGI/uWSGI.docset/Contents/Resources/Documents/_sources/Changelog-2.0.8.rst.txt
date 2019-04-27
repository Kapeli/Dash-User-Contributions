uWSGI 2.0.8
===========

Note: this is the first version with disabled-by-default SSL3, if you need it, you can re-enable with ``--ssl-enable3`` option

Bugfixes
--------

* fixed PHP `SCRIPT_NAME` usage when ``--php-app`` is in place
* allow "appendn" hook without second argument
* fix heap corruption in the Carbon plugin (credits: Nigel Heron)
* fix `getifaddrs()` memory management
* fixed `tcsetattr()` usage
* fixed kevent usage of return value (credits: Adriano Di Luzio)
* ensure PSGI response headers are in the right format
* fixed reloading of attached daemons
* fixed SSL/TLS shutdown
* fixed mountpoint logic for paths not ending with / (credits: Adriano Di Luzio)
* fixed Python3 support in spooler decorators (credits: Adriano Di Luzio)

New Features
------------

RTSP and chunked input backports from 2.1 for the HTTP router
*************************************************************

The ``--http-manage-rtsp`` and ``--http-chunked-input` have been backported from 2.1 allowing the HTTP router
to detect RTSP and chunked requests automatically. This is useful for the upcoming https://github.com/unbit/uwsgi-realtime plugin.

--hook-post-fork
****************

This custom hook allows you to call actions after each `fork()`.

fallback to trollius for asyncio plugin
***************************************

If you build the asyncio plugin for python2, a fallback to the `trollius <https://trollius.readthedocs.io/>`_ module will be tried.

This feature has gotten basically zero test coverage, so every report (bug or success alike) is welcome.

added sweep_on_full, clear_on_full and no_expire to ``--cache2``
****************************************************************

Three new options for ``--cache2`` have been added for improving the caching expire strategies:

* ``sweep_on_full`` will call a sweep (delete all of the expired items) as soon as the cache became full
* ``clear_on_full`` will completely clear the cache as soon as it is full
* ``no_expire`` forces the cache to not generate a cache sweeper thread, delegating items removal to the two previous options

backported wait-for-fs/mountpoints from 2.1
*******************************************

* ``--wait-for-fs <path>`` suspend the uWSGI startup until a file/directory is available
* ``--wait-for-file <path>`` suspend the uWSGI startup until a file is available
* ``--wait-for-dir <path>`` suspend the uWSGI startup until a directory is available
* ``--wait-for-mountpoint <path>`` suspend the uWSGI startup until a mountpoint is available

improved the offload api (backport from 2.1)
********************************************

uWSGI 2.0.8 is compatible with the upcoming https://github.com/unbit/uwsgi-realtime plugin that allows the use of realtime features
(like websockets or audio/video streaming) using the uWSGI offload engine + Redis publish/subscribe.

Allows building plugins from remote sources as embedded
*******************************************************

The UWSGI_EMBED_PLUGINS environment variable has been extended to support remote plugins. As an example you can build a monolithic
uwsgi binary with the Avahi and realtime plugins as:

.. code-block:: sh

   UWSGI_EMBED_PLUGINS="avahi=https://github.com/20tab/uwsgi-avahi,realtime=https://github.com/unbit/uwsgi-realtime" make

Automatically manage HTTP_X_FORWARDED_PROTO
*******************************************

Albeit a new standard is avavailble in the HTTP world for forwarded sessions (http://tools.ietf.org/html/rfc7239) this release
adds support for the X-Forwarded-Proto header, automatically setting the request scheme accordingly.

Availability
------------

uWSGI 2.0.8 has been released on 20141026. Download it from:

https://projects.unbit.it/downloads/uwsgi-2.0.8.tar.gz
