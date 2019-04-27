Zerg mode
=========

.. note::

  Yes, that's Zerg as in the "quantity-over-quality" Starcraft race. If you haven't played Starcraft, be prepared for some nonsense.

  .. note::

    Also note that this nonsense is mostly limited to the nomenclature. Zerg Mode is serious business.

When your site load is variable, it would be nice to be able to add workers dynamically.

You can obviously edit your configuration to hike up ``workers`` and reload your uWSGI instance, but for very loaded apps this is undesirable, and frankly -- who wants to do manual work like that to scale an app?

Enabling Zerg mode you can allow "uwsgi-zerg" instances to attach to your already running server and help it in the work.

Zerg mode is obviously local only. You cannot use it to add remote instances -- this is a job better done by the :doc:`Fastrouter`, the :doc:`HTTP plugin<HTTP>` or your web server's load balancer.

Enabling the zerg server
------------------------

If you want an uWSGI instance to be rushed by zerg, you have to enable the Zerg server. It will be bound to an UNIX socket and will pass uwsgi socket file descriptors to the Zerg workers connecting to it.

.. warning:: The socket must be an UNIX socket because it must be capable of passing through file descriptors. A TCP socket simply will not work.

For security reasons the UNIX socket does not inherit the ``chmod-socket`` option, but will always use the current umask.

If you have filesystem permission issues, on Linux you can use the UNIX sockets in abstract namespace, by prepending an ``@`` to the socket name.

* A normal UNIX socket:

  .. code-block:: sh

    ./uwsgi -M -p 8 --module welcome --zerg-server /var/run/mutalisk

* A socket in a Linux abstract namespace:

  .. code-block:: sh

    ./uwsgi -M -p 8 --module welcome --zerg-server @nydus


Attaching zergs to the zerg server
----------------------------------

To add a new instance to your zerg pool, simply use the --zerg option

.. code-block:: sh

  ./uwsgi --zerg /var/run/mutalisk --master --processes 4 --module welcome
  # (or --zerg @nydus, following the example above)

In this way 4 new workers will start serving requests.

When your load returns to normal values, you can simply shutdown all of the uwsgi-zerg instances without problems.

You can attach an unlimited number of uwsgi-zerg instances.

Fallback if a zerg server is not available
------------------------------------------

By default a Zerg client will not run if the Zerg server is not available. Thus, if your zerg server dies, and you reload the zerg client, it will simply shutdown.

If you want to avoid that behaviour, add a ``--socket`` directive mapping to the required socket (the one that should be managed by the zerg server) and add the ``--zerg-fallback`` option.

With this setup, if a Zerg server is not available, the Zerg client will continue binding normally to the specified socket(s).

.. TODO: This needs to be documented better. An example would rock.

Using Zerg as testers
---------------------

A good trick you can use, is suspending the main instance with the ``SIGTSTP`` signal and loading a new version of your app in a Zerg. If the code is not ok you can simply shutdown the Zerg and resume the main instance.

Zerg Pools
----------

Zergpools are special Zerg servers that only serve Zerg clients, nothing more.

You can use them to build high-availability systems that reduce downtime during tests/reloads.

You can run an unlimited number of zerg pools (on several UNIX sockets) and map an unlimited number of sockets to them.

.. code-block:: ini

  [uwsgi]
  master = true
  zergpool = /tmp/zergpool_1:127.0.0.1:3031,127.0.0.1:3032
  zergpool = /tmp/zergpool_2:192.168.173.22:3031,192.168.173.22:3032

With a config like this, you will have two zergpools, each serving two sockets.

You can now attach instances to them.

.. code-block:: sh

  uwsgi --zerg /tmp/zergpool_1 --wsgi-file myapp.wsgi --master --processes 8
  uwsgi --zerg /tmp/zergpool_2 --rails /var/www/myapp --master --processes 4

or you can attach a single instance to multiple Zerg servers.

.. code-block:: sh

  uwsgi --zerg /tmp/zergpool_1 --zerg /tmp/zergpool_2 --wsgi-file myapp.wsgi --master --processes 8