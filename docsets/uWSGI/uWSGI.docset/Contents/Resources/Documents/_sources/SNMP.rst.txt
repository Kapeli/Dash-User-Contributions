The embedded SNMP server
========================

The uWSGI server embeds a tiny SNMP server that you can use to integrate your web apps with your monitoring infrastructure.

To enable SNMP support, you must run the uWSGI UDP server and choose a SNMP community string (which is the rudimentary authentication system used by SNMP).

.. code-block:: sh

  ./uwsgi -s :3031 -w staticfilesnmp --udp 192.168.0.1:2222 --snmp --snmp-community foo
  # or the following. Using the SNMP option to pass the UDP address is a lot more elegant. ;)
  ./uwsgi -s :3031 -w myapp --master --processes 4 --snmp=192.168.0.1:2222 --snmp-community foo

This will run the uWSGI server on TCP port 3031 and UDP port 2222 with SNMP enabled with "foo" as the community string.

Please note that the SNMP server is started in the master process after dropping the privileges. If you want it to listen on a privileged port, you can either use :doc:`Capabilities<Capabilities>` on Linux, or use the ``master-as-root`` option to run the master process as root. The :file:`staticfilesnmp.py` file is included in the distribution and is a simple app that exports a counter via SNMP.

The uWSGI SNMP server exports 2 group of information:

* General information is managed by the uWSGI server itself. The base OID to access uWSGI SNMP information is ``1.3.6.1.4.1.35156.17`` (``iso.org.dod.internet.private.enterprise.unbit.uwsgi``). General options are mapped to ``1.3.6.1.4.1.35156.17.1.x``.
* Custom information is managed by the apps and accessed via ``1.3.6.1.4.1.35156.17.2.x``

So, to get the number of requests managed by the uWSGI server, you could do

.. code-block:: sh

  snmpget -v2c -c foo 192.168.0.1:2222 1.3.6.1.4.1.35156.17.1.1 # 1.1 corresponds to ``general.requests``

Exporting custom values
-----------------------

To manage custom values from your app you have these Python functions,

* :py:func:`uwsgi.snmp_set_counter32`
* :py:func:`uwsgi.snmp_set_counter64`
* :py:func:`uwsgi.snmp_set_gauge`
* :py:func:`uwsgi.snmp_incr_counter32`
* :py:func:`uwsgi.snmp_incr_counter64`
* :py:func:`uwsgi.snmp_incr_gauge`
* :py:func:`uwsgi.snmp_decr_counter32`
* :py:func:`uwsgi.snmp_decr_counter64`
* :py:func:`uwsgi.snmp_decr_gauge`

So if you wanted to export the number of users currently logged in (this is a gauge as it can lower) as custom OID 40, you'd call

.. code-block:: python

  users_logged_in = random.randint(0, 1024) # a more predictable source of information would be better.
  uwsgi.snmp_set_gauge(40, users_logged_in)

and to look it up,

.. code-block:: sh

  snmpget -v2c -c foo 192.168.0.1:2222 1.3.6.1.4.1.35156.17.2.40

The system snmp daemon (net-snmp) can be configured to proxy SNMP requests to uwsgi. This allows you to run the system daemon and uwsgi at the same time, and runs all SNMP requests through the system daemon first. To configure the system snmp daemon (net-snmp) to proxy connections to uwsgi, add these lines to the bottom of /etc/snmp/snmpd.conf and restart the daemon:

.. code-block:: sh

   proxy -v 2c -c foo 127.0.0.1:2222 .1.3.6.1.4.1.35156.17
   view    systemview    included   .1.3.6.1.4.1.35156.17

Replace 'foo' and '2222' with the community and port configured in uwsgi. 

