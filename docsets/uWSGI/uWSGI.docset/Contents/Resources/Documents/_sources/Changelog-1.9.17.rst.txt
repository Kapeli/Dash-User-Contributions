uWSGI 1.9.17
============

Changelog [20130917]


Bugfixes
********

- the 'pty' client is now blocking (safer approach)
- removed strtok() usage (substituted by a new uwsgi api function on top of strtok_r() )
- fixed --pty-exec (Credits: C Anthony Risinger)
- listen_queue/somaxconn linux check is now done even for UNIX sockets



New features
************

The Master FIFO
^^^^^^^^^^^^^^^

This is a new management way in addition to UNIX signals. As we have no more free signals to use (and generally dealing with signals and pidfiles is not very funny), all of the new management features of uWSGI will be based on the master fifo.

Docs are already available: :doc:`MasterFIFO`


The asap hook
^^^^^^^^^^^^^

Credits: Matthijs Kooijman

a new hook, named 'asap' has been added. It will be run soon after the options are parsed.

Check: :doc:`Hooks`

The TCC (libtcc) plugin
^^^^^^^^^^^^^^^^^^^^^^^

TCC is an embeddable c compilers. It includes a shared library (libtcc) you can use to compile strings of c code on the fly.

The libtcc uWSGI plugins allows compiling strings of c to process symbols. CUrrently the "tcc" hook engine has been implemented:

.. code-block:: ini

   [uwsgi]
   hook-asap = tcc:mkdir("/var/run/sockets");printf("directory created\n");
   hook-as-user = tcc:printf("i am process with pid %d\n", getpid());
   hook-post-app = tcc:if (getenv("DESTROY_THE_WORLD")) exit(1);
   http-socket = /var/run/sockets/foobar.sock



The forkptyrouter gateway
^^^^^^^^^^^^^^^^^^^^^^^^^

While work on Linux containers/namespaces continues to improve we have added this special router/gateway allowing dynamic allocation of pseodoterminals
in uWSGI instances. To access the sockets created by the forkptyrouter you can use the --pty-connect option exposed by the 'pty' plugin.

Documention is being worked on.

added a new magic var for ANSI escaping
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The %[ magic var has been added, it allows you to define ANSI sequences in your logs.

If you like coloured logs:

.. code-block:: ini

   log-encoder = format %[[33m${msgnl}%[[0m
   
Routable log encoders
^^^^^^^^^^^^^^^^^^^^^

You can now attach log encoders to specific log routes:

.. code-block:: ini

   [uwsgi]
   logger = stderr file:/dev/tty
   log-route = stderr ubuntu
   log-route = stderr clock
   print = %[[34mHELLO%[[0m
   ; add an encoder to the 'stderr' logger
   log-encoder = format:stderr %[[33m${msgnl}%[[0m
   http-socket = :9090

--vassals-include
^^^^^^^^^^^^^^^^^

Credits: Matthijs Kooijman

This is like --vassal-inherit but the parsing will be "immediate" (so you can use placeholders)

The Emperor heartbeat system is now mercyless...
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The old approach for the heartbeat Emperor subsystem was asking for "gentle" reload to bad vassals.

Now vassals not sending heartbeat (after being registered with the heartbeat subsystem) are killed with -9

The result of this patch will be more robust bad vassals management

logpipe
^^^^^^^

Author: INADA Naoki

You can now send loglines to the stdin of an external command:

.. code-block:: ini

   req-logger = pipe:/usr/local/bin/mylogger

added "fd" logger to "logfile" plugin
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

you can directly send logs to a file descriptors:

.. code-block:: ini

   req-logger = fd:17


Availability
************

uWSGI 1.9.17 has been released on Semptember 22th 2013

You can download it from:

https://projects.unbit.it/downloads/uwsgi-1.9.17.tar.gz
