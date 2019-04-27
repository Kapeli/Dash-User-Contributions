uWSGI 2.0.12
============

[20151230]

Bugfixes
--------

- 'rpcvar' routing action correctly returns NEXT on empty response
- uwsgiconfig: fix handling of empty keys in python3 (Simone Basso)
- plugins/alarm_speech: fix AppKit spelling to support case-sensitive filesystems (Andrew Janke)
- Fix inheriting INET address 0.0.0.0 (INADA Naoki)
- core/xmlconf: correctly initialize libxml2 (Riccardo Magliocchetti)
- Pass LIBDIR to linker in python plugin (Borys Pierov)
- Platforms-related build fixes for pty, forkptyrouter and mono plugins (Jonas Smedegaard and Riccardo Magliocchetti)

New Features and Backports
--------------------------

The custom worker api
*********************

Finally you are able to override the uWSGI processing model to completely get control of it. This is very similar to what
you can do in projects like gunicorn (and its integration with tornado or gevent). Obviously native plugins are still the best approach (they allow integration with uWSGI api and states), but in some case you may want to use uWSGI process management facilities and let your app do the rest of the work.

Currently only the python plugin supports "overriding" of workers, an aiohttp (asyncio) example module is available:

https://github.com/unbit/uwsgi-docs/blob/master/WorkerOverride.rst


--wsgi-disable-file-wrapper
***************************

This option disables the wsgi.file_wrapper optimization of the WSGI standard. In some corner case this is the only trick to avoid errors.

Official PHP 7 support
**********************

PHP 7 is now officially supported in the php plugin.


uwsgi.spooler_get_task api (Credits: Alexandre Bonnetain)
*********************************************************

This patch allows you to easily parse spooler files.

Check the example/test here:

https://github.com/unbit/uwsgi/blob/master/t/spooler/read.py

--if-hostname-match (Credits: Alexandre Bonnetain)
**************************************************

This options for config logic allows you to define options only when a regexp over the hostname matches:

.. code-block:: ini

   [uwsgi]
   if-hostname-match = ^prod
     threads = 20
   endif =
   


Availability
------------

You can download uWSGI 2.0.12 from https://projects.unbit.it/downloads/uwsgi-2.0.12.tar.gz
