The GeoIP plugin
================

The ``geoip`` plugin adds new routing vars to your internal routing subsystem.
GeoIP's vars are prefixed with the "geoip" tag.  To build the geoip plugin you
need the official GeoIP C library and its headers.  The supported databases are
the country and city one, and they are completely loaded on memory at startup.

The country database give access to the following variables:

* ``${geoip[country_code]}``
* ``${geoip[country_code3]}``
* ``${geoip[country_name]}``

while the city one offers a lot more at the cost of increased memory usage for
storing the database

* ``${geoip[continent]}``
* ``${geoip[country_code]}``
* ``${geoip[country_code3]}``
* ``${geoip[country_name]}``
* ``${geoip[region]}``
* ``${geoip[region_name]}``
* ``${geoip[city]}``
* ``${geoip[postal_code]}``
* ``${geoip[latitude]}`` (``${geoip[lat]}``)
* ``${geoip[longitude]}`` (``${geoip[lon]}``)
* ``${geoip[dma]}``
* ``${geoip[area]}``

Enabling geoip lookup
*********************

To enable the GeoIP lookup system you need to load at least one database. After
having loaded the geoip plugin you will get 2 new options:

* ``--geoip-country`` specifies a country database
* ``--geoip-city`` specifies a city database

If you do not specify at least one of them, the system will always return empty strings.

An example
**********

.. code-block:: ini

   [uwsgi]
   plugin = geoip
   http-socket = :9090
   ; load the geoip city database
   geoip-city = GeoLiteCity.dat
   module = werkzeug.testapp:test_app
   ; first some debug info (addvar will ad WSGI variables you will see in the werkzeug testapp)
   route-run = log:${geoip[country_name]}/${geoip[country_code3]}
   route-run = addvar:COUNTRY=${geoip[country_name]}
   route-run = log:${geoip[city]}/${geoip[region]}/${geoip[continent]}
   route-run = addvar:COORDS=${geoip[lon]}/${geoip[lat]}
   route-run = log:${geoip[region_name]}
   route-run = log:${geoip[dma]}/${geoip[area]}

   ; then something more useful
   ; block access to all of the italians (hey i am italian do not start blasting me...)
   route-if = equal:${geoip[country_name]};Italy break:403 Italians cannot see this site :P
   ; try to serve a specific page translation
   route = ^/foo/bar/test.html static:/var/www/${geoip[country_code]}/test.html

Memory usage
************

The country database is tiny so you will generally have no problem in using it.
Instead, the city database can be huge (from 20MB to more than 40MB).  If you
have lot of instances using the GeoIP city database and you are on a recent
Linux system, consider using :doc:`KSM` to reduce memory usage. All of the
memory used by the GeoIP database can be shared by all instances with it.
