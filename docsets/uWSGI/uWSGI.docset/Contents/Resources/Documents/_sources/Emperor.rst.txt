The uWSGI Emperor -- multi-app deployment
=========================================

If you need to deploy a big number of apps on a single server, or a group of
servers, the Emperor mode is just the ticket.  It is a special uWSGI instance
that will monitor specific events and will spawn/stop/reload instances (known
as :term:`vassals<vassal>`, when managed by an Emperor) on demand.

By default the Emperor will scan specific directories for supported (.ini,
.xml, .yml, .json, etc.) uWSGI configuration files, but it is extensible using
:term:`imperial monitor` plugins.  The ``dir://`` and ``glob://`` plugins are
embedded in the core, so they need not be loaded, and are automatically
detected. The ``dir://`` plugin is the default.

* Whenever an imperial monitor detects a new configuration file, a new uWSGI instance will be spawned with that configuration.
* Whenever a configuration file is modified (its modification time changed, so ``touch --no-dereference`` may be your friend), the corresponding app will be reloaded.
* Whenever a config file is removed, the corresponding app will be stopped.
* If the emperor dies, all the vassals die.
* If a vassal dies for any reason, the emperor will respawn it.

Multiple sources of configuration may be monitored by specifying ``--emperor`` multiple times.

.. seealso::

  See :doc:`ImperialMonitors` for a list of the Imperial Monitor plugins
  shipped with uWSGI and how to use them.

.. toctree::

  ImperialMonitors
  EmperorProtocol
  OnDemandVassals

Special configuration variables
-------------------------------

Using :ref:`Placeholders` and :ref:`MagicVars` in conjunction with the Emperor
will probably save you a lot of time and make your configuration more DRY.
Suppose that in /opt/apps there are only Django_ apps.  /opt/apps/app.skel (the
.skel extension is not a known configuration file type to uWSGI and will be
skipped)

.. code-block:: ini

  [uwsgi]
  chdir = /opt/apps/%n
  threads = 20
  socket = /tmp/sockets/%n.sock
  env = DJANGO_SETTINGS_MODULE=%n.settings
  module = django.core.handlers.wsgi:WSGIHandler()

And then for each app create a symlink::

  ln -s /opt/apps/app.skel /opt/apps/app1.ini
  ln -s /opt/apps/app.skel /opt/apps/app2.ini

Finally, start the Emperor with the ``--emperor-nofollow`` option. Now you can reload each vassal separately with the command::

  touch --no-dereference $INI_FILE

.. _Django: http://djangoproject.com

Passing configuration parameters to all vassals
-----------------------------------------------

Starting from 1.9.19 you can pass options using the ``--vassal-set`` facility

.. code-block:: ini

   [uwsgi]
   emperor = /etc/uwsgi/vassals
   vassal-set = processes=8
   vassal-set = enable-metrics=1

this will add ``--set processes=8`` and ``--set enable-metrics=1`` to each vassal

You can force the Emperor to pass options to uWSGI instances using environment
variables too.  Every environment variable of the form ``UWSGI_VASSAL_xxx`` will be
rewritten in the new instance as ``UWSGI_xxx``, with the usual
:ref:`configuration implications<ConfigEnv>`.

For example::

  UWSGI_VASSAL_SOCKET=/tmp/%n.sock uwsgi --emperor /opt/apps

will let you avoid specifying the socket option in configuration files.

Alternatively, you can use the ``--vassals-include`` option let each
vassal automatically include a complete config file::

  uwsgi --emperor /opt/apps --vassals-include /etc/uwsgi/vassals-default.ini

Note that if you do this, ``%n`` (and other magic variables) in the
included file will resolve to the name of the included file, not the
original vassal configuration file. If you want to set options in the
included file using the vassal name, you'll have to use placeholders.
For example, in the vassal config, you write::

  [uwsgi]
  vassal_name = %n
  ... more options

In the ``vassal-defaults.ini``, you write::

  [uwsgi]
  socket = /tmp/sockets/%(vassal_name).sock

.. _Tyrant:

Tyrant mode (secure multi-user hosting)
---------------------------------------

The emperor is normally run as root, setting the UID and GID in each
instance's config. The vassal instance then drops privileges before serving
requests. In this mode, if your users have access to their own uWSGI
configuration files, you can't trust them to set the correct ``uid`` and
``gid``. You could run the emperor as unprivileged user (with ``uid`` and
``gid``) but all of the vassals would then run under the same user, as
unprivileged users are not able to promote themselves to other users.  For this
case the Tyrant mode is available -- just add the ``emperor-tyrant`` option.

In Tyrant mode the Emperor will run the vassal using the UID/GID of the vassal
configuration file (or for other Imperial Monitors, by some other method of
configuration).  If Tyrant mode is used, the vassal configuration files must
have UID/GID > 0. An error will occur if the UID or GID is zero, or if the UID
or GID of the configuration of an already running vassal changes.


Tyrant mode for paranoid sysadmins (Linux only)
***********************************************

If you have built a uWSGI version with :doc:`Capabilities` options enabled, you
can run the Emperor as unprivileged user but maintaining the minimal amount of
root-capabilities needed to apply the tyrant mode

.. code-block:: ini

   [uwsgi]
   uid = 10000
   gid = 10000
   emperor = /tmp
   emperor-tyrant = true
   cap = setgid,setuid


Loyalty
-------

As soon as a vassal manages a request it will became "loyal". This status is
used by the Emperor to identify bad-behaving vassals and punish them.

Throttling
----------

Whenever two or more vassals are spawned in the same second, the Emperor will
start a throttling subsystem to avoid `fork bombing`_.  The system adds a
throttle delta (specified in milliseconds via the :ref:`OptionEmperorThrottle`
option) whenever it happens, and waits for that duration before spawning a new
vassal.  Every time a new vassal spawns without triggering throttling, the
current throttling duration is halved.

.. _fork bombing: http://en.wikipedia.org/wiki/Fork_bomb

Blacklist system
----------------

Whenever a non-loyal vassal dies, it is put in a shameful blacklist.  When in a
blacklist, that vassal will be throttled up to a maximum value (tunable via
:ref:`OptionEmperorMaxThrottle`), starting from the default throttle delta of
3.  Whenever a blacklisted vassal dies, its throttling value is increased by
the delta (:ref:`OptionEmperorThrottle`).

You can also empty the blacklist by sending the signal SIGURG to the emperor
process. This will reset the throttle value.

Heartbeat system
----------------

Vassals can voluntarily ask the Emperor to monitor their status.  Workers of
heartbeat-enabled vassals will send "heartbeat" messages to the Emperor. If the
Emperor does not receive heartbeats from an instance for more than N (default
30, :ref:`OptionEmperorRequiredHeartbeat`) seconds, that instance will be
considered hung and thus reloaded.  To enable sending of heartbeat packet in a
vassal, add the :ref:`OptionHeartbeat` option.

.. important::

  If all of your workers are stuck handling perfectly legal requests such as
  slow, large file uploads, the Emperor will trigger a reload as if the workers
  are hung.  The reload triggered is a graceful one, so you will be able to tune
  your config/timeout/mercy for sane behaviour.

.. TODO: Clarify the above admonition

Using Linux namespaces for vassals
----------------------------------

On Linux you can tell the Emperor to run vassals in "unshared" contexts. That means you can run each vassal with a dedicated view of the filesystems, ipc, uts, networking, pids and uids.

Things you generally do with tools like ``lxc`` or its abstractions like ``docker`` are native in uWSGI.

For example if you want to run each vassals in a new namespace:

.. code-block:: ini

   [uwsgi]
   emperor = /etc/uwsgi/vassals
   emperor-use-clone = fs,net,ipc,pid,uts

now each vassal will be able to modify the filesystem layout, networking, hostname and so on without damaging the main system.

A couple of helper daemons are included in the uWSGI distribution to simplify management of jailed vassals. Most notably :doc:`TunTapRouter` allows full user-space networking in jails, while
the ``forkpty router`` allows allocation of pseudoterminals in jails

It is not needed to unshare all of the subsystem in your vassals, sometimes you only want to give dedicated ipc and hostname to a vassal and hide from the processes list:

.. code-block:: ini

   [uwsgi]
   emperor = /etc/uwsgi/vassals
   emperor-use-clone = fs,ipc,pid,uts

a vassal could be:

.. code-block:: ini

   [uwsgi]
   ; set the hostname
   exec-as-root = hostname foobar
   ; umount /proc and remount to hide processes
   ; as we are in the 'fs' namespace umounting /proc does not interfere with the main one
   exec-as-root = umount /proc
   exec-as-root = mount -t proc none /proc
   ; drop privileges
   uid = foobar
   gid = foobar
   ; bind to the socket
   socket = /tmp/myapp.socket
   psgi = myapp.pl


The Imperial Bureau of Statistics
---------------------------------

You can enable a statistics/status service for the Emperor by adding the
:ref:`OptionEmperorStats` option with a TCP address. By connecting to that
address, you'll get a JSON-format blob of statistics.

.. _BinaryPatch:

Running non-uWSGI apps or using alternative uWSGIs as vassals
-------------------------------------------------------------

You can ``exec()`` a different binary as your vassal using the
``privileged-binary-patch``/``unprivileged-binary-patch`` options.  The first
one patches the binary after socket inheritance and shared socket
initialization (so you will be able to use uWSGI-defined sockets).  The second
one patches the binary after privileges drop. In this way you will be able to
use uWSGI's UID/GID/chroot/namespace/jailing options.  The binary is called
with the same arguments that were passed to the vassal by the Emperor.

.. code-block:: ini

  ; i am a special vassal calling a different binary in a new linux network namespace
  [uwsgi]
  uid = 1000
  gid = 1000
  unshare = net
  unprivileged-binary-patch = /usr/bin/myfunnyserver

.. important::

  *DO NOT DAEMONIZE* your apps. If you do so, the Emperor will lose its connection with them.

The uWSGI arguments are passed to the new binary. If you do not like that
behaviour (or need to pass custom arguments) add ``-arg`` to the binary patch
option, yielding:

.. code-block:: ini

  ; i am a special vassal calling a different binary in a new linux network namespace
  ; with custom options
  [uwsgi]
  uid = 1000
  gid = 1000
  unshare = net
  unprivileged-binary-patch-arg = ps aux

or:

.. code-block:: ini

  ;nginx example
  [uwsgi]
  privileged-binary-patch-arg = nginx -g "daemon off;"

.. seealso::

  Your custom vassal apps can also speak with the emperor using the :doc:`emperor protocol <EmperorProtocol>`.

Integrating the Emperor with the FastRouter
-------------------------------------------

The FastRouter is a proxy/load-balancer/router speaking :doc:`Protocol`.  Yann
Malet from `Lincoln Loop`_ has released `a draft about massive Emperor +
Fastrouter deployment`_ (PDF) using :doc:`Caching` as a hostname to socket
mapping storage.

.. _Lincoln Loop: http://lincolnloop.com/

.. _`a draft about massive Emperor + Fastrouter deployment`: https://projects.unbit.it/uwsgi/raw-attachment/wiki/Emperor/lincolnloop.pdf

Notes
-----

* At startup, the emperor ``chdir()`` to the vassal dir. All vassal instances will start from here.
* If the uwsgi binary is not in your system path you can force its path with ``binary-path``::

    ./uwsgi --emperor /opt/apps --binary-path /opt/uwsgi/uwsgi

* Sending ``SIGUSR1`` to the emperor will print vassal status in its log.
* Stopping (``SIGINT``/``SIGTERM``/``SIGQUIT``) the Emperor will invoke
  Ragnarok and kill all the vassals.
* Sending ``SIGHUP`` to the Emperor will reload all vassals.
* Sending ``SIGURG`` to the Emperor will remove all vassals from the blacklist
* The emperor should generally not be run with ``--master``, unless master
  features like advanced logging are specifically needed.
* The emperor should generally be started at server boot time and left alone,
  not reloaded/restarted except for uWSGI upgrades; emperor reloads are a bit
  drastic, reloading all vassals at once. Instead vassals should be reloaded
  individually when needed, in the manner of the imperial monitor in use.

Todo
----

* Docs-TODO: Clarify what the "chdir-on-startup" behavior does with
  non-filesystem monitors.
* Export more magic vars
* Add support for multiple sections in xml/ini/yaml files (this will allow to
  have a single config file for multiple instances)
