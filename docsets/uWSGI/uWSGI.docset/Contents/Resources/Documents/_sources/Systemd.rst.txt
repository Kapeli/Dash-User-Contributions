Systemd
=======

uWSGI is a new-style daemon for `systemd <http://www.freedesktop.org/wiki/Software/systemd>`_.

It can notify status change and readyness.

When uWSGI detects it is running under systemd, the notification system is enabled.

Adding the Emperor to systemd
*****************************

One approach to integrate uWSGI apps with your init system is using the :doc:`Emperor<Emperor>`.

Your init system will talk only with the Emperor that will rule all of the apps itself.

Create a systemd service file (you can save it as /etc/systemd/system/emperor.uwsgi.service)

.. note::
   Be careful with some systemd versions (e.g. 215 in Debian Jessie), since SIGQUIT signal will trash the systemd services. Use KillSignal=SIGTERM + "die-on-term" UWSGI option there.

.. code-block:: ini

   [Unit]
   Description=uWSGI Emperor
   After=syslog.target

   [Service]
   ExecStart=/root/uwsgi/uwsgi --ini /etc/uwsgi/emperor.ini
   # Requires systemd version 211 or newer
   RuntimeDirectory=uwsgi
   Restart=always
   KillSignal=SIGQUIT
   Type=notify
   StandardError=syslog
   NotifyAccess=all

   [Install]
   WantedBy=multi-user.target

Then run it

.. code-block:: sh

   systemctl start emperor.uwsgi.service

And check its status.

.. code-block:: sh

   systemctl status emperor.uwsgi.service

You will see the Emperor reporting the number of governed vassals to systemd (and to you).

.. code-block:: sh

   emperor.uwsgi.service - uWSGI Emperor
    Loaded: loaded (/etc/systemd/system/emperor.uwsgi.service)
	  Active: active (running) since Tue, 17 May 2011 08:51:31 +0200; 5s ago
   Main PID: 30567 (uwsgi)
	  Status: "The Emperor is governing 1 vassals"
	  CGroup: name=systemd:/system/emperor.uwsgi.service
		  ├ 30567 /root/uwsgi/uwsgi --ini /etc/uwsgi/emperor.ini
		  ├ 30568 /root/uwsgi/uwsgi --ini werkzeug.ini
		  └ 30569 /root/uwsgi/uwsgi --ini werkzeug.ini


You can stop the Emperor (and all the apps it governs) with

.. code-block:: sh

   systemctl stop emperor.uwsgi.service

A simple ``emperor.ini`` could look like this (www-data is just an anonymous user)

NOTE: DO NOT daemonize the Emperor (or the master) unless you know what you are doing!!!

.. code-block:: ini

   [uwsgi]
   emperor = /etc/uwsgi/vassals
   uid = www-data
   gid = www-data

If you want to allow each vassal to run under different privileges, remove the ``uid`` and ``gid`` options from the emperor configuration (and please read the Emperor docs!)

Logging
*******

Using the previous service file all of the Emperor messages go to the syslog. You can avoid it by removing the ``StandardError=syslog`` directive.

If you do that, be sure to set a ``--logto`` option in your Emperor configuration, otherwise all of your logs will be lost!

Putting sockets in /run/
************************

On a modern system, /run/ is mounted as a tmpfs and is the right place to put sockets and pidfiles into. To have systemd automatically create a /run/uwsgi/ subdirectory with the correct user/group ownership, as well as cleaning up the directory when the daemon is stopped, add 

.. code-block:: ini

   RuntimeDirectory=uwsgi

to the [Service] section of your systemd uwsgi unit file. This ``RuntimeDirectory`` parameter requires systemd version 211 or newer. For older versions of systemd, create a systemd-tmpfiles configuration file (you can save it as /etc/tmpfiles.d/emperor.uwsgi.conf):

.. code-block:: ini

   d /run/uwsgi 0755 www-data www-data -

Socket activation
*****************

Starting from uWSGI 0.9.8.3 socket activation is available. You can setup systemd to spawn uWSGI instances only after the first socket connection.

Create the required emperor.uwsgi.socket (in ``/etc/systemd/system/emperor.uwsgi.socket``). Note that the *.socket file name must match the *.service file name.

.. code-block:: ini

   [Unit]
   Description=Socket for uWSGI Emperor

   [Socket]
   # Change this to your uwsgi application port or unix socket location
   ListenStream=/tmp/uwsgid.sock

   [Install]
   WantedBy=sockets.target

Then disable the service and enable the socket unit.

.. code-block:: sh

   # systemctl disable emperor.uwsgi.service
   # systemctl enable emperor.uwsgi.socket
   
When using Systemd socket activation, you do not need to specify any socket in your uWSGI configuration;
the instance will inherit the socket from Systemd.

To have uWSGI serve HTTP (instead of the binary uwsgi protocol) under Systemd socket activation,
set ``protocol`` to ``http``; for instance, in an INI, do this:

.. code-block:: ini
   
   [uwsgi]
   protocol = http
   wsgi = ...
   ...
   
One service per app in systemd
******************************

Another approach is to let systemd handle starting individual apps while taking
advantage of systemd template unit files, and of course socket activation. Each
app will run under its own user.

``/etc/systemd/system/uwsgi-app@.socket``:

.. code-block:: ini

  [Unit]
  Description=Socket for uWSGI app %i

  [Socket]
  ListenStream=/var/run/uwsgi/%i.socket
  SocketUser=www-%i
  SocketGroup=www-data
  SocketMode=0660

  [Install]
  WantedBy=sockets.target

``/etc/systemd/system/uwsgi-app@.service``:

.. code-block:: ini

  [Unit]
  Description=%i uWSGI app
  After=syslog.target

  [Service]
  ExecStart=/usr/bin/uwsgi \
          --ini /etc/uwsgi/apps-available/%i.ini \
          --socket /var/run/uwsgi/%i.socket
  User=www-%i
  Group=www-data
  Restart=on-failure
  KillSignal=SIGQUIT
  Type=notify
  StandardError=syslog
  NotifyAccess=all

Now, adding a new app to your system is a matter of creating the appropriate
user and enabling the socket and the service. For instance, if one were to
configure cgit:

.. code-block:: sh

  adduser www-cgit --disabled-login --disabled-password \
    --ingroup www-data --home /var/lib/www/cgit --shell /bin/false
  systemctl enable uwsgi-app@cgit.socket
  systemctl enable uwsgi-app@cgit.service
  systemctl start uwsgi-app@cgit.socket

Then configure the ini file ``/etc/uwsgi/apps-available/cgit.ini``:

.. code-block:: ini

  [uwsgi]
  master = True
  cheap = True
  idle = 600
  die-on-idle = True # If app is not used often, it will exit and be launched
                     # again by systemd requested by users.

  manage-script-name = True

  plugins = 0:cgi
  cgi = /usr/lib/cgit/cgit.cgi

And last, if applicable, configure your HTTP server the usual way.
