WebCaching framework
===========================

.. note::

    This is a port of the old caching subsystem to the new uWSGI caching API documented here :doc:`Caching`.
    Using the options here will create a new-style cache named "default".


To enable web caching, allocate slots for your items using the ``cache`` option. The following command line would create a cache that can contain at most 1000 items.

.. code-block:: sh

   ./uwsgi --socket 127.0.0.1:3031 --module mysimpleapp --master --processes 4 --cache 1000

To use the cache in your application, 

.. code-block:: python

   uwsgi.cache_set("foo_key", "foo_value") # set a key
   value = uwsgi.cache_get("foo_key") # get a key.


Persistent storage
------------------

You can store cache data in a backing store file to implement persistence. Simply add the ``cache-store <filename>`` option.
Every kernel will commit data to the disk at a different rate. You can set if/when to force this with ``cache-store-sync <n>``, where ``n`` is the number of master cycles to wait before each disk sync.

Cache sweeper
-------------

Since uWSGI 1.2, cache item expiration is managed by a thread in the :term:`master` process, to reduce the risk of deadlock. This thread can be disabled (making item expiry a no-op) with the ``cache-no-expire`` option.

The frequency of the cache sweeper thread can be set with ``cache-expire-freq <seconds>``. You can make the sweeper log the number of freed items with ``cache-report-freed-items``.

Directly accessing the cache from your web server
-------------------------------------------------

.. code-block:: nginx

   location / {
    uwsgi_pass 127.0.0.1:3031;
    uwsgi_modifier1 111;
    uwsgi_modifier2 3;
    uwsgi_param key $request_uri;
   }

That's it! Nginx would now get HTTP responses from a remote uwsgi protocol compliant server. Although honestly this is not very useful, as if you get a cache miss, you will see a blank page.

A better system, that will fallback to a real uwsgi request would be

.. code-block:: nginx

   location / {
     uwsgi_pass 192.168.173.3:3032;
     uwsgi_modifier1 111;
     uwsgi_modifier2 3;
     uwsgi_param key $request_uri;
     uwsgi_pass_request_headers off;
     error_page 502 504 = @real;
   }

   location @real {
     uwsgi_pass 192.168.173.3:3032;
     uwsgi_modifier1 0;
     uwsgi_modifier2 0;
     include uwsgi_params;
   }
   
Django cache backend
--------------------

If you are running Django, there's a ready-to-use application called ``django-uwsgi-cache``. It is maintained by Ionel Cristian Mărieș at https://github.com/ionelmc/django-uwsgi-cache and available on pypi.


.. _caching configuration: https://docs.djangoproject.com/en/dev/topics/cache/?from=olddocs#the-per-site-cache
