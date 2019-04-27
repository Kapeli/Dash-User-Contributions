On demand vassals (socket activation)
=====================================

Inspired by the venerable xinetd/inetd approach, you can spawn your vassals
only after the first connection to a specific socket. This feature is available
as of 1.9.1. Combined with –idle/–die-on-idle options, you can have truly
on-demand applications.

When on demand is active for particular vassal, emperor won't spawn it on start
(or when it's config changes), but it will rather create socket for that
vassal and monitor if anything connects to it.

At the first connection, the vassal is spawned and the socket passed as the file
descriptor 0. File descriptor 0 is always checked by uWSGI so you do not need to
specify a --socket option in the vassal file. This works automagically for uwsgi
sockets, if you use other protocols (like http or fastcgi) you have to
specify it with the --protocol option

.. important::

  If you will define in your vassal config same socket as used by emperor for
  on demand action, vassal will override that socket file. That could lead to
  unexpected behaviour, for example on demand activation of that vassal will
  work only once.

On demand vassals with filesystem-based imperial monitors
---------------------------------------------------------

For filesystem-based imperial monitors, such as ``dir://`` or ``glob://``,
defining on demand vassals involves defining one of three additional settings
for your emperor:

--emperor-on-demand-extension <ext>
***********************************

this will instruct the Emperor to check for a file named <vassal>+<ext>, if the
file is available it will be read and its content used as the socket to wait
for:

.. code-block:: sh

   uwsgi --emperor /etc/uwsgi/vassals --emperor-on-demand-extension .socket

supposing a myapp.ini file in /etc/uwsgi/vassals, a /etc/uwsgi/vassals/myapp.ini.socket
will be searched for (and its content used as the socket name). Note that
myapp.ini.socket isn't a socket! This file only contains path for actual socket
(tcp or unix).

--emperor-on-demand-directory <dir>
***********************************

This is a less-versatile approach supporting only UNIX sockets. Basically the
name (without extension and path) of the vassal is appended to the specified
directory + the .socket extension and used as the on-demand socket:

.. code-block:: sh

   uwsgi --emperor /etc/uwsgi/vassals --emperor-on-demand-directory /var/tmp

using the previous example, the socket /var/tmp/myapp.socket will be
automatically bound.

--emperor-on-demand-exec <cmd>
******************************

This is most flexible solution for defining socket for on demand action and
(very probably) you will use it in very big deployments. Every time a new vassal
is added the supplied command is run passing full path to vassal config file as
the first argument. The STDOUT of the command is used as the socket name.

Using on demand vassals with other imperial monitors
----------------------------------------------------

For some imperial monitors, such as ``pg://``, ``mongodb://``, ``zmq://`` socket
for on demand activation is returned by imperial monitor by itself. For example
for ``pg://`` if executed on database query returns more than 5 fields, 6th
field will be used as socket for on demand activation. Check
:doc:`ImperialMonitors` for more information.

For some imperial monitors, such as ``amqp://``, socket activation is not
possible yet.

Combining on demand vassals with ``--idle`` and ``--die-on-idle``
-----------------------------------------------------------------

For truly on demand applications, you can add to each vassal ``--idle`` and
``--die-on-idle`` options. This will allow suspend or completely turn off
applications that are no longer requested. ``--idle`` without
``--die-on-idle`` will work pretty much like without emperor, but adding
``--die-on-idle`` will give you superpower for completely shutting down
applications and returning back to on-demand mode.

Emperor will simply put vassal back to on-demand mode when it dies gracefully
and turn it back on when there are any requests waiting or socket.

.. important::

  As mentioned before, you should **never** put in your vassal config file
  socket that was passed to emperor for on-demand mode. For unix sockets,
  file path that socket lives on will be rewritten with new socket, but old
  socket will be still connected to your emperor. Emperor will listen for
  connections on that old socket, but all requests will arrive to new one.
  That means, if your vassal will be shut down because of idle state, it will
  be **never** put back on (emperor won't receive any connections for
  on-demand socket).

  For tcp socket, that can cause each request to be handled **twice**.
