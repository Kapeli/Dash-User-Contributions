Running uWSGI instances with Circus
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Circus (https://circus.readthedocs.io/en/0.7/) is a process manager written in
Python. It is very similar to projects like Supervisor, but with several
additional features.  Although most, if not all, of it's functionalities have a
counterpart in uWSGI, Circus can be used as a library allowing you to build
dynamic configurations (and extend uWSGI patterns). This aspect is very
important and may be the real selling point of Circus.

Socket activation
*****************

Based on the venerable inetd pattern, Circus can bind to sockets and pass them to children.

Start with a simple Circus config (call it circus.ini):

.. code-block:: ini

   [circus]
   endpoint = tcp://127.0.0.1:5555
   pubsub_endpoint = tcp://127.0.0.1:5556
   stats_endpoint = tcp://127.0.0.1:5557

   [watcher:dummy]
   cmd = uwsgi --http-socket fd://$(circus.sockets.foo) --wsgi-file yourapp.wsgi
   use_sockets = True
   send_hup = True
   stop_signal = QUIT

   [socket:foo]
   host = 0.0.0.0
   port = 8888

run it with

.. code-block:: sh

    circusd circus.ini

(Better) Socket activation
**************************

If you want to spawn instances on demand, you will likely want to shut them
down when they are no longer used.  To accomplish that use the --idle uWSGI
option.

.. code-block:: ini

   [circus]
   check_delay = 5
   endpoint = tcp://127.0.0.1:5555
   pubsub_endpoint = tcp://127.0.0.1:5556
   stats_endpoint = tcp://127.0.0.1:5557

   [watcher:dummy]
   cmd = uwsgi --master --idle 60 --http-socket fd://$(circus.sockets.foo) --wsgi-file yourapp.wsgi
   use_sockets = True
   warmup_delay = 0
   send_hup = True
   stop_signal = QUIT

   [socket:foo]
   host = 0.0.0.0
   port = 8888

This time we have enabled the master process. It will manage the --idle option, shutting down the instance if it is
inactive for more than 60 seconds.