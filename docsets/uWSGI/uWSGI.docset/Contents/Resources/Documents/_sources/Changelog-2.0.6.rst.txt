uWSGI 2.0.6
===========

Changelog [20140701]


Bugfixes
^^^^^^^^

* fixed a memory leak in the subscription system
* fixed shortcut for ssl-socket
* fixed Apache2 mod_proxy_uwsgi. It is now considered stable with all Apache MPM engines.
* fixed SCRIPT_NAME and PATH_TRANSLATED generation in the PHP plugin (thanks Matthijs Kooijman)
* remove the old FIFO socket from the event queue when recreating it (thanks Marko Tiikkaja)


New features
^^^^^^^^^^^^

The new Rados plugins
*********************

Credits: Marcin Deranek

The Rados plugin has been improved and stabilized, and now it is considered stable and usable in production.

Async modes and multithreading correctly work.

Support for uploading objects (via PUT) and creating new pools (MKCOL) has been added.

Expect WebDAV support in uWSGI 2.1.

Docs have been updated: https://uwsgi-docs.readthedocs.io/en/latest/Rados.html

--if-hostname
*************

This is configuration logic for including options only when the system's hostname matches a given value.

.. code-block:: ini

   [uwsgi]
   if-hostname = node1.local
     socket = /tmp/socket1.socket
   endif =
   
   if-hostname = node2.local
     socket = /var/run/foo.socket
   endif = 
   
Apache2 `mod_proxy_uwsgi` stabilization
***************************************

After literally years of bug reports and corrupted data and other general badness, `mod_proxy_uwsgi` is finally stable.

On modern Apache2 releases it supports UNIX sockets too.

Updated docs: https://uwsgi-docs.readthedocs.io/en/latest/Apache.html#mod-proxy-uwsgi

uwsgi[rsize] routing var
************************

The new `uwsgi[rsize]` routing variable (meaningful only in the 'final' chain) exposes the response size of the request.

the `callint` scheme
********************

This scheme allows you to generate blobs from functions exposed by your uWSGI instance:

.. code-block:: ini

   [uwsgi]
   uid = @(callint://get_my_uid)
   gid = @(callint://get_my_gid)
   
--fastrouter-fallback-on-no-key
*******************************

The corerouter's fallback procedure requires that a valid key (domain name) has been requested.

This option forces the various routers to trigger the fallback procedure even if a key has not been found.

PHP 5.5 opcode caching via --php-sapi-name
******************************************

For mysterious reasons the PHP 5.5+'s opcode caching is not enabled in the "embed" SAPI. This option allows you to fake the SAPI name -- `apache` is a good option -- to force the opcode caching engine to turn on.

Improved chain-reloading
************************

Thanks to Marko Tiikkaja, the chain reloading procedure correctly works in cheaper modes and is more verbose.

added 'chdir' keyval to --attach-daemon2
****************************************

You can now set where attached daemons need to chdir().

Availability
^^^^^^^^^^^^

uWSGI 2.0.6 has been released on 20140701

You can download it from

https://projects.unbit.it/downloads/uwsgi-2.0.6.tar.gz
