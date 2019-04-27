uWSGI 1.9.2
===========

Changelog 20130326

Bugfixes
********

Fixed python3 response headers managament (wrong refcnt)

Fixed readline() on request body when postbuffering is in place

Fixed ruby fiber plugin

New features
************

route-run and the cachestore routing action
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can now store responses automatically in the uWSGI cache:

.. code-block:: ini

   [uwsgi]
   http-socket = :9090
   ; ensure the sweeper thread will run
   master = true
   cache2 = name=pippo2,items=10
   module = werkzeug.testapp:test_app
   route-run = cache:key=${REQUEST_URI},name=pippo2
   route-run = cachestore:key=${REQUEST_URI},expires=30,name=pippo2

this example check every request for its availability in the cache 'pippo2'. If not available the request plugin (werkzeug test app)
will run normally and its output will be stored in the cache (only if it returns a HTTP 200 status)

``--route-run`` is a new option allowing you to directly call routing action without checking for a specific condition (yes, it is an optimization)

routing access to cookie and query string
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Check updated docs :doc:`InternalRouting`

empty internal routing condition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Check updated docs :doc:`InternalRouting`

The Geoip plugin
^^^^^^^^^^^^^^^^

Check official docs :doc:`GeoIP`

The SSI plugin (beta)
^^^^^^^^^^^^^^^^^^^^^

Check official docs :doc:`SSI`

Availability
************

uWSGI 1.9.2 has been released on 20130326 and can be downloaded from:

https://projects.unbit.it/downloads/uwsgi-1.9.2.tar.gz
