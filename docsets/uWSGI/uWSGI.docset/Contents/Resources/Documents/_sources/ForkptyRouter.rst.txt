The Forkpty Router
==================

Dealing with containers is now a common deployment pattern. One of the most annoying tasks when dealing with jails/namespaces
is 'attaching' to already running instances.

The forkpty router aims at simplifyng the process giving a pseudoterminal server to your uWSGI instances.

A client connect to the socket exposed by the forkpty router and get a new pseudoterminal connected to a process (generally a shell, but can be whatever you want)

uwsgi mode VS raw mode
**********************

Clients connecting to the forkpty router can use two protocols for data exchange: uwsgi and raw mode.

The raw mode simply maps the socket to the pty, for such a reason you will not be able to resize your terminal or send specific signals.
The advantage of this mode is in performance: no overhead for each char.

The uwsgi mode encapsulates every instruction (stdin, signals, window changes) in a uwsgi packet. This is very similar to how ssh works, so if you
plan to use the forkpty router for shell sessions the uwsgi mode is the best choice (in terms of user experience).

The overhead of the uwsgi protocol (worst case) is 5 bytes for each stdin event (single char)

Running the forkpty router
**************************

The plugin is not builtin by default, so you have to compile it:

.. code-block:: sh

	uwsgi --build-plugin plugins/forkptyrouter

or, using the old plugin build system:

.. code-block:: sh

	python uwsgiconfig.py --plugin plugins/forkptyrouter

generally compiling the pty plugin is required too (for client access)

.. code-block:: sh

   uwsgi --build-plugin plugins/pty

or again, using the old build system:

.. code-block:: sh

	python uwsgiconfig.py --plugin plugins/pty

Alternatively, you can build all in one shot with:

.. code-block:: sh

   UWSGI_EMBED_PLUGINS=pty,forkptyrouter make

Now you can run the forkptyrouter as a standard gateway (we use UNIX socket as we want a communication channel with jails, and we unshare the uts namespace to give a new hostname)

.. code-block:: ini

   [uwsgi]
   master = true
   unshare = uts
   exec-as-root = hostname iaminajail
   uid = kratos
   gid = kratos
   forkpty-router = /tmp/fpty.socket

and connect with the pty client:

.. code-block:: sh

   uwsgi --pty-connect /tmp/fpty.socket
   

now you have a shell (/bin/sh by default) in the uWSGI instance. Running ``hostname`` will give you 'iaminajail'

Eventually you can avoid using uWSGI to attacj to the pty and instead you can rely on this simple python script:

.. code-block:: py

   import socket
   import sys
   import os
   import select
   import copy
   from termios import *
   import atexit
   
   s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
   s.connect(sys.argv[1])
   
   tcattr = tcgetattr(0)
   orig_tcattr = copy.copy(tcattr)
   atexit.register(tcsetattr, 0, TCSANOW, orig_tcattr)
   
   tcattr[0] |= IGNPAR
   tcattr[0] &= ~(ISTRIP | IMAXBEL | BRKINT | INLCR | IGNCR | ICRNL | IXON | IXANY | IXOFF);
   tcattr[0] &= ~IUCLC;
   tcattr[3] &= ~(ICANON | ECHO | ECHOE | ECHOK | ECHONL);
   tcattr[3] &= ~IEXTEN;
   tcattr[1] &= ~OPOST;
   tcattr[6][VMIN] = 1;
   tcattr[6][VTIME] = 0;
   
   tcsetattr(0, TCSANOW, tcattr);
   
   while True:
       (rl, wl, xl) = select.select([0, s], [], [])
       if s in rl:
           buf = s.recv(4096)
           if not buf: break
           os.write(1, buf)
       if 0 in rl:
           buf = os.read(0, 4096)
           if not buf: break
           s.send(buf)
           



The previous example uses raw mode, if you resize the client terminal you will se no updates.

To use the 'uwsgi' mode add a 'u':

.. code-block:: ini

   [uwsgi]
   master = true
   unshare = uts
   exec-as-root = hostname iaminajail
   uid = kratos
   gid = kratos
   forkpty-urouter = /tmp/fpty.socket


.. code-block:: sh

   uwsgi --pty-uconnect /tmp/fpty.socket

a single instance can expose both protocols on different sockets

.. code-block:: ini

   [uwsgi]
   master = true
   unshare = uts
   exec-as-root = hostname iaminajail
   uid = kratos
   gid = kratos
   forkpty-router = /tmp/raw.socket
   forkpty-urouter = /tmp/uwsgi.socket

Changing the default command
****************************

By default the forkpty router run /bin/sh on new connections.

You can change the command using the --forkptyrouter-command

.. code-block:: ini

   [uwsgi]
   master = true
   unshare = uts
   exec-as-root = hostname iaminajail
   uid = kratos
   gid = kratos
   forkpty-router = /tmp/raw.socket
   forkpty-urouter = /tmp/uwsgi.socket
   forkptyrouter-command= /bin/zsh
