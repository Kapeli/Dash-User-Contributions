The Emperor protocol
====================

As of 1.3 you can spawn custom applications via the :doc:`Emperor<Emperor>`.

Non-uWSGI Vassals should never daemonize, to maintain a link with the Emperor.
If you want/need better integration with the Emperor, implement the Emperor
protocol.

The protocol
------------

An environment variable ``UWSGI_EMPEROR_FD`` is passed to every vassal,
containing a file descriptor number.

.. code-block:: python

  import os
  has_emperor = os.environ.get('UWSGI_EMPEROR_FD')
  if has_emperor:
     print "I'm a vassal snake!"

Or in Perl,

.. code-block:: python

  my $has_emperor = $ENV{'UWSGI_EMPEROR_FD'}
  if ($has_emperor) {
    print "I am a vassal.\n"
  }

Or in C,

.. code-block:: c

  int emperor_fd = -1;
  char *has_emperor = getenv("UWSGI_EMPEROR_FD");
  if (has_emperor) {
      emperor_fd = atoi(has_emperor);
      fprintf(stderr, "I am a vassal.\n");
  }

From now you can receive (and send) messages from (and to) the Emperor over this file descriptor.

Messages are byte sized (0-255), and each number (byte) has a meaning.

== ==
0  Sent by the Emperor to stop a vassal
1  Sent by the Emperor to reload a vassal / sent by a vassal when it has been spawned
2  Sent by a vassal to ask the Emperor for configuration chunk
5  Sent by a vassal when it is ready to accept requests
17 Sent by a vassal after the first request to announce loyalty
22 Sent by a vassal to notify the Emperor of voluntary shutdown
26 Heartbeat sent by the vassal. After the first received heartbeat, the Emperor will expect more of them from the vassal.
30 Sent by the vassal to ask for :doc:`Broodlord` mode.
== ==
