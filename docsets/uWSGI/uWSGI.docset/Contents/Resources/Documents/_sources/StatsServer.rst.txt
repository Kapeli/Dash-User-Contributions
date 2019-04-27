The uWSGI Stats Server
======================

In addition to :doc:`SNMP<SNMP>`, uWSGI also supports a Stats Server mechanism which exports the uWSGI state as a JSON object to a socket.

Simply use the ``stats`` option followed by a valid socket address. If you want the stats served over HTTP you will need to also add the ``stats-http`` option.

.. code-block:: sh

    --stats 127.0.0.1:1717
    --stats /tmp/statsock
    --stats :5050
    --stats @foobar
    # Any of the above socket types can also return stats using HTTP
    --stats 127.0.0.1:1717 --stats-http

If a client connects to the specified socket it will get a JSON object containing uWSGI internal statistics before the connection ends.

.. code-block:: sh

    uwsgi --socket :3031 --stats :1717 --module welcome --master --processes 8

then

.. code-block:: sh

    nc 127.0.0.1 1717
    # or for convenience...
    uwsgi --connect-and-read 127.0.0.1:1717

will return something like this:

.. code-block:: js

    {
      "workers": [{
        "id": 1,
        "pid": 31759,
        "requests": 0,
        "exceptions": 0,
        "status": "idle",
        "rss": 0,
        "vsz": 0,
        "running_time": 0,
        "last_spawn": 1317235041,
        "respawn_count": 1,
        "tx": 0,
        "avg_rt": 0,
        "apps": [{
          "id": 0,
          "modifier1": 0,
          "mountpoint": "",
          "requests": 0,
          "exceptions": 0,
          "chdir": ""
        }]
      }, {
        "id": 2,
        "pid": 31760,
        "requests": 0,
        "exceptions": 0,
        "status": "idle",
        "rss": 0,
        "vsz": 0,
        "running_time": 0,
        "last_spawn": 1317235041,
        "respawn_count": 1,
        "tx": 0,
        "avg_rt": 0,
        "apps": [{
          "id": 0,
          "modifier1": 0,
          "mountpoint": "",
          "requests": 0,
          "exceptions": 0,
          "chdir": ""
        }]
      }, {
        "id": 3,
        "pid": 31761,
        "requests": 0,
        "exceptions": 0,
        "status": "idle",
        "rss": 0,
        "vsz": 0,
        "running_time": 0,
        "last_spawn": 1317235041,
        "respawn_count": 1,
        "tx": 0,
        "avg_rt": 0,
        "apps": [{
          "id": 0,
          "modifier1": 0,
          "mountpoint": "",
          "requests": 0,
          "exceptions": 0,
          "chdir": ""
        }]
      }, {
        "id": 4,
        "pid": 31762,
        "requests": 0,
        "exceptions": 0,
        "status": "idle",
        "rss": 0,
        "vsz": 0,
        "running_time": 0,
        "last_spawn": 1317235041,
        "respawn_count": 1,
        "tx": 0,
        "avg_rt": 0,
        "apps": [{
          "id": 0,
          "modifier1": 0,
          "mountpoint": "",
          "requests": 0,
          "exceptions": 0,
          "chdir": ""
        }]
      }, {
        "id": 5,
        "pid": 31763,
        "requests": 0,
        "exceptions": 0,
        "status": "idle",
        "rss": 0,
        "vsz": 0,
        "running_time": 0,
        "last_spawn": 1317235041,
        "respawn_count": 1,
        "tx": 0,
        "avg_rt": 0,
        "apps": [{
          "id": 0,
          "modifier1": 0,
          "mountpoint": "",
          "requests": 0,
          "exceptions": 0,
          "chdir": ""
        }]
      }, {
        "id": 6,
        "pid": 31764,
        "requests": 0,
        "exceptions": 0,
        "status": "idle",
        "rss": 0,
        "vsz": 0,
        "running_time": 0,
        "last_spawn": 1317235041,
        "respawn_count": 1,
        "tx": 0,
        "avg_rt": 0,
        "apps": [{
          "id": 0,
          "modifier1": 0,
          "mountpoint": "",
          "requests": 0,
          "exceptions": 0,
          "chdir": ""
        }]
      }, {
        "id": 7,
        "pid": 31765,
        "requests": 0,
        "exceptions": 0,
        "status": "idle",
        "rss": 0,
        "vsz": 0,
        "running_time": 0,
        "last_spawn": 1317235041,
        "respawn_count": 1,
        "tx": 0,
        "avg_rt": 0,
        "apps": [{
          "id": 0,
          "modifier1": 0,
          "mountpoint": "",
          "requests": 0,
          "exceptions": 0,
          "chdir": ""
        }]
      }, {
        "id": 8,
        "pid": 31766,
        "requests": 0,
        "exceptions": 0,
        "status": "idle",
        "rss": 0,
        "vsz": 0,
        "running_time": 0,
        "last_spawn": 1317235041,
        "respawn_count": 1,
        "tx": 0,
        "avg_rt": 0,
        "apps": [{
          "id": 0,
          "modifier1": 0,
          "mountpoint": "",
          "requests": 0,
          "exceptions": 0,
          "chdir": ""
        }]
      }]
    }
        

uwsgitop
--------

``uwsgitop`` is a top-like command that uses the stats server. It is available on PyPI, so use ``easy_install`` or ``pip`` to install it (package name ``uwsgitop``, naturally).

The sources are available on Github. https://github.com/unbit/uwsgitop

