Monitoring uWSGI with Nagios
============================

The official uWSGI distribution includes a plugin adding Nagios_\ -friendly output.

To monitor, and eventually get warning messages, via Nagios, launch the following command, where ``node`` is the socket (UNIX or TCP) to monitor.

.. code-block:: sh

  uwsgi --socket <node> --nagios

Setting warning messages
------------------------

You can set a warning message directly from your app with the :func:`uwsgi.set_warning_message` function. All ping responses (used by Nagios too) will report this message.

.. _Nagios: http://www.nagios.com/