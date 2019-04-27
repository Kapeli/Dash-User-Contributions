uWSGI 1.9.5
===========

Changelog 20130404

Bugfixes
********

* fixed a memory leak with cachestore routing instruction (Riccardo Magliocchetti)
* fixed a memory leak in carbon plugin (Riccardo Magliocchetti)
* fixed a memory leak in the cgi plugin (Riccardo Magliocchetti)
* fixed old-style python dynamic apps
* force the emperor to honour --max-fd for vassals
* improved PSGI seek with post-buffering
* fixed kvlist escaping


New features
************

The GridFS plugin
^^^^^^^^^^^^^^^^^

A plugin exporting GridFS features is available, check official docs: :doc:`GridFS`

V8 improvements
^^^^^^^^^^^^^^^

The V8 plugin continues to improve. Preliminary JSGI 3.0 support is available as well as multithreading.

The 'require' commonjs standard has been implemented.

Writing commonjs specs will be a very long work, so maybe a partnership with projects like teajs (the old v8cgi) would be a better
path to follow.

In the mean time, we are working on docs: :doc:`V8`

The 'cgi' routing instruction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can now call CGI script directly from the :doc:`InternalRouting`

.. code-block:: ini

   [uwsgi]
   plugin = cgi
   route = ^/cgi-bin/(.+) cgi:/usr/lib/cgi-bin/$1


Availability
************

uWSGI 1.9.5 will be available since 20130404 at this url

https://projects.unbit.it/downloads/uwsgi-1.9.5.tar.gz
