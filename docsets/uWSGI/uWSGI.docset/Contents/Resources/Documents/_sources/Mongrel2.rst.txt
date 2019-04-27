Attaching uWSGI to Mongrel2
===========================

Mongrel2_ is a next-next-generation webserver that focuses on modern webapps.

Just like uWSGI, it is fully language agnostic, cluster-friendly and delightfully controversial :)

It uses the amazing ZeroMQ_ library for communication, allowing reliable, easy message queueing and configuration-free scalability.

Starting from version 0.9.8-dev, uWSGI can be used as a Mongrel2 handler.

.. _Mongrel2: http://mongrel2.org/
.. _ZeroMQ: http://www.zeromq.org/

Requirements
------------

To enable ZeroMQ/Mongrel2 support in uWSGI you need the zeromq library (2.1+) and the uuid library.

Mongrel2 can use JSON or tnetstring to pass data (such as headers and various other information) to handlers. uWSGI supports tnetstring out of the box but requires the `Jansson <http://www.digip.org/jansson/>`_ library to parse JSON data.
If you don't install jansson or do not want to use JSON, make sure you specify ``protocol='tnetstring'`` in the Handler in the Mongrel2 configuration, as the default is to use JSON. This would result in a rather obscure "JSON support not enabled. Skip request" message in the uWSGI log.

Configuring Mongrel2
--------------------

You can find ``mongrel2-uwsgi.conf`` shipped with the uWSGI source. You can use this file as a base to configure Mongrel2.


.. code-block:: python

  main = Server(
      uuid="f400bf85-4538-4f7a-8908-67e313d515c2",
      access_log="/logs/access.log",
      error_log="/logs/error.log",
      chroot="./",
      default_host="192.168.173.11",
      name="test",
      pid_file="/run/mongrel2.pid",
      port=6767,
      hosts = [
          Host(name="192.168.173.11", routes={
              '/': Handler(send_spec='tcp://192.168.173.11:9999',
                      send_ident='54c6755b-9628-40a4-9a2d-cc82a816345e', 
                      recv_spec='tcp://192.168.173.11:9998', recv_ident='',
                      protocol='tnetstring')
          })
      ]
  )

  settings = {'upload.temp_store':'tmp/mongrel2.upload.XXXXXX'}
  servers = [main]

It is a pretty standard Mongrel2 configuration with upload streaming enabled.

Configuring uWSGI for Mongrel2
------------------------------

To attach uWSGI to Mongrel2, simply use the :ref:`OptionZeromq` option:

.. code-block:: sh

  uwsgi --zeromq tcp://192.168.173.11:9999,tcp://192.168.173.11:9998

You can spawn multiple processes (each one will subscribe to Mongrel2 with a different uuid)

.. code-block:: sh
 
  uwsgi --zeromq tcp://192.168.173.11:9999,tcp://192.168.173.11:9998 -p 4

You can use threads too. Each thread will subscribe to the Mongrel2 queue but the responder socket will be shared by all the threads and protected by a mutex.

.. code-block:: sh

  uwsgi --zeromq tcp://192.168.173.11:9999,tcp://192.168.173.11:9998 -p 4 --threads 8
  # This will spawn 4 processes with 8 threads each, totaling 32 threads.

Test them all
-------------

Add an application to uWSGI (we will use the werkzeug.testapp as always)

.. code-block:: sh

  uwsgi --zeromq tcp://192.168.173.11:9999,tcp://192.168.173.11:9998 -p 4 --threads 8 --module werkzeug.testapp:test_app

Now launch the command on all the servers you want, Mongrel2 will distribute requests to them automagically.

Async mode
----------

.. warning::

  Async support for ZeroMQ is still under development, as ZeroMQ uses edge triggered events that complicate things in the uWSGI async architecture.

Chroot
------

By default Mongrel2 will ``chroot()``. This is a good thing for security, but can cause headaches regarding file upload streaming. Remember that Mongrel2 will save the uploaded file
in its own chroot jail, so if your uWSGI instance does not live in the same chroot jail, you'll have to choose the paths carefully. In the example Mongrel2 configuration file we have used a relative path to easily allow uWSGI to reach the file.

Performance
-----------

Mongrel2 is extremely fast and reliable even under huge loads. tnetstring and JSON are text-based (so they are a little less effective than the binary :doc:`uwsgi protocol <Protocol>`. However, as Mongrel2 does not require the expensive one-connection-for-request method, you should get pretty much the same (if not higher) results compared to a (for example) :doc:`Nginx<Nginx>` + uWSGI approach.

uWSGI clustering + ZeroMQ
-------------------------

You can easily mix uWSGI :doc:`clustering<Clustering>` with ZeroMQ.

Choose the main node and run

.. code-block:: sh

  uwsgi --zeromq tcp://192.168.173.11:9999,tcp://192.168.173.11:9998 -p 4 --threads 8 --module werkzeug.testapp:test_app --cluster 225.1.1.1:1717

And on all the other nodes simply run


.. code-block:: sh
  
  uwsgi --cluster 225.1.1.1:1717

Mixing standard sockets with ZeroMQ
-----------------------------------

You can add uwsgi/:doc:`HTTP<HTTP>`/FastCGI/... sockets to your uWSGI server in addition to ZeroMQ, but if you do, remember to disable threads! This limitation will probably be fixed in the future.

Logging via ZeroMQ
------------------

.. seealso:: :doc:`ZeroMQLogging`