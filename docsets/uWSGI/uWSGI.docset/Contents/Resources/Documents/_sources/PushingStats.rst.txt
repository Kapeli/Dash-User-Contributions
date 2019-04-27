Pushing statistics (from 1.4)
=============================

IMPORTANT: the Metrics subsystem offers a better introduction to the following concepts. See :doc:`Metrics`

Starting from uWSGI 1.4 you can push statistics (the same JSON blob you get with the :doc:`StatsServer`)
via various systems (called stats pushers).

Statistics are pushed at regular intervals (default 3 seconds).

The 'file' stats pusher
***********************

By default the 'file' stats pusher is available up to 1.9.18. Starting from 1.9.19 is available as a plugin (stats_pusher_file).

It allows you to save json chunks to a file (open in appended mode)

.. code-block:: ini

   [uwsgi]
   socket = :3031
   module = foobar
   master = true
   stats-push = file:path=/tmp/foobar,freq=10

this config will append JSON to the /tmp/foobar file every 10 seconds


The 'mongodb' stats pusher
**************************

This is the first developed stats pusher plugin, allowing you to store JSON
data directly on a mongodb collection

.. code-block:: ini

   [uwsgi]
   plugins = stats_pusher_mongodb
   socket = :3031
   module = foobar
   master = true
   stats-push = mongodb:addr=127.0.0.1:5151,collection=uwsgi.mystats,freq=4

This config will insert JSON data to the collection uwsgi.mystats on the mongodb server 127.0.0.1:5151
every 4 seconds.

To build the plugin you need mongodb development headers (mongodb-dev on Debian/Ubuntu)

.. code-block:: sh

   python uwsgiconfig.py --plugin plugins/stats_pusher_mongodb

will do the trick


Notes
*****

You can configure all of the stats pusher you need, just specify multiple stats-push options

.. code-block:: ini

   [uwsgi]
   plugins = stats_pusher_mongodb
   socket = :3031
   module = foobar
   master = true
   stats-push = mongodb:addr=127.0.0.1:5151,collection=uwsgi.mystats,freq=4
   stats-push = mongodb:addr=127.0.0.1:5152,collection=uwsgi.mystats,freq=4
   stats-push = mongodb:addr=127.0.0.1:5153,collection=uwsgi.mystats,freq=4
   stats-push = mongodb:addr=127.0.0.1:5154,collection=uwsgi.mystats,freq=4

