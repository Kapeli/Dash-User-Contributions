The Master FIFO
===============

Available from uWSGI 1.9.17.

Generally you use UNIX signals to manage the master, but we are running out of signal numbers and (more importantly) not needing to mess with PIDs
greatly simplifies the implementation of external management scripts.

So, instead of signals, you can tell the master to create a UNIX named pipe (FIFO) that you may use to issue commands to the master.

To create a FIFO just add ``--master-fifo <filename>`` then start issuing commands to it.

.. code-block:: sh

   echo r > /tmp/yourfifo
   
You can send multiple commands in one shot.

.. code-block:: sh

   # add 3 workers and print stats
   echo +++s > /tmp/yourfifo

Available commands
******************

* '0' to '9' - set the fifo slot (see below)
* '+' - increase the number of workers when in cheaper mode (add ``--cheaper-algo manual`` for full control)
* '-' - decrease the number of workers when in cheaper mode (add ``--cheaper-algo manual`` for full control)
* 'B' - ask Emperor for reinforcement (broodlord mode, requires uWSGI >= 2.0.7)
* 'C' - set cheap mode
* 'c' - trigger chain reload
* 'E' - trigger an Emperor rescan
* 'f' - re-fork the master (dangerous, but very powerful)
* 'l' - reopen log file (need --log-master and --logto/--logto2)
* 'L' - trigger log rotation (need --log-master and --logto/--logto2)
* 'p' - pause/resume the instance
* 'P' - update pidfiles (can be useful after master re-fork)
* 'Q' - brutally shutdown the instance
* 'q' - gracefully shutdown the instance
* 'R' - send brutal reload
* 'r' - send graceful reload
* 'S' - block/unblock subscriptions
* 's' - print stats in the logs
* 'W' - brutally reload workers
* 'w' - gracefully reload workers

FIFO slots
**********

uWSGI supports up to 10 different FIFO files. By default the first specified is bound (mapped as '0').

During the instance's lifetime you can change from one FIFO to another by simply sending the number of the FIFO slot to use.

.. code-block:: ini

   [uwsgi]
   master-fifo = /tmp/fifo0
   master-fifo = /tmp/fifo1
   master-fifo = /var/run/foofifo
   processes = 2
   ...

By default ``/tmp/fifo0`` will be allocated, but after sending:

.. code-block:: sh

   echo 1 > /tmp/fifo0
   
the ``/tmp/fifo1`` file will be bound.

This is very useful to map FIFO files to specific instance when you (ab)use the 'fork the master' command (the 'f' one).

.. code-block:: sh

   echo 1fp > /tmp/fifo0
   
After sending this command, a new uWSGI instance (inheriting all of the bound sockets) will be spawned, the old one will be put in "paused" mode (the 'p' command).

As we have sent the '1' command before 'f' and 'p' the old instance will now accept commands on /tmp/fifo1 (the slot 1), and the new one will use the default one ('0').

There are lot of tricks you can accomplish, and lots of ways to abuse the forking of the master.

Just take into account that corner-case problems can occur all over the place, especially if you use the most complex features of uWSGI.

Notes
*****

* The FIFO is created in non-blocking modes and recreated by the master every time a client disconnects.
* You can override (or add) commands using the global array ``uwsgi_fifo_table`` via plugins or C hooks.
* Only the uid running the master has write access to the fifo.
