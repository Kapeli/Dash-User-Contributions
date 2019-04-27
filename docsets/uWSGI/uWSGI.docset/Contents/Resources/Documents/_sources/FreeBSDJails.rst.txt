FreeBSD Jails
=============

uWSGI 1.9.16 introduced native FreeBSD jails support.

FreeBSD jails can be seen as new-generation chroot() with fine-grained tuning of what this "jail" can see.

They are very similar to Linux namespaces even if a bit higher-level (from the API point of view).

Jails are available since FreeBSD 4


Why managing jails with uWSGI ?
*******************************

Generally jails are managed using the system tool "jail" and its utilities.

Til now running uWSGI in FreeBSD jails was pretty common, but for really massive setups (read: hosting business)
where an Emperor (for example) manages hundreds of unrelated uWSGI instances, the setup could be really overkill.

Managing jails directly in uWSGI config files highly reduce sysadmin costs and helps having a better organization of the whole infrastructure.

Old-style jails (FreeBSD < 8)
*****************************

FreeBSD exposes two main api for managing jails. The old (and easier) one is based on the jail() function.

It is available since FreeBSD 4 and allows you to set the rootfs, the hostname and one ore more ipv4/ipv6 addresses

Two options are needed for running a uWSGI instance in a jail: --jail and --jail-ip4/--jail-ip6 (effectively they are 3 if you use IPv6)

``--jail <rootfs> [hostname] [jailname]``

``--jail-ip4 <address>`` (can be specified multiple times)

``--jail-ip6 <address>`` (can be specified multiple times)

Showing how to create the rootfs for your jail is not the objective of this document, but personally i hate rebuilding from sources, so generally
i simply explode the base.tgz file from an official repository and chroot() to it to make the fine tuning.

An important thing you have to remember is that the ip addresses you attach to a jail must be available in the system (as aliases). As always we tend to abuse uWSGI facilities.
In our case the --exec-pre-jail hook will do the trick


.. code-block:: ini

   [uwsgi]
   ; create the jail with /jails/001 as rootfs and 'foobar' as hostname
   jail = /jails/001 foobar
   ; create the alias on 'em0'
   exec-pre-jail = ifconfig em0 192.168.0.40 alias
   ; attach the alias to the jail
   jail-ip4 = 192.168.0.40
   
   ; bind the http-socket (we are now in the jail)
   http-socket = 192.168.0.40:8080
   
   ; load the application (remember we are in the jail)
   wsgi-file = myapp.wsgi
   
   ; drop privileges
   uid = kratos
   gid = kratos
   
   ; common options
   master = true
   processes = 2

New style jails (FreeBSD >= 8)
******************************

FreeBSD 8 introdiced a new advanced api for managing jails. Based on the jail_set() syscall, libjail exposes dozens of features
and allows fine-tuning of your jails. To use the new api you need the --jail2 option (aliased as --libjail)

``--jail2 <key>[=value]``

Each --jail2 option maps 1:1 with a jail attribute so you can basically tune everything !

.. code-block:: ini

   [uwsgi]
   ; create the jail with /jails/001 as rootfs
   jail2 = path=/jails/001
   ; set hostname to 'foobar'
   jail2 = host.hostname=foobar
   ; create the alias on 'em0'
   exec-pre-jail = ifconfig em0 192.168.0.40 alias
   ; attach the alias to the jail
   jail2 = ip4.addr=192.168.0.40
   
   ; bind the http-socket (we are now in the jail)
   http-socket = 192.168.0.40:8080
   
   ; load the application (remember we are in the jail)
   wsgi-file = myapp.wsgi
   
   ; drop privileges
   uid = kratos
   gid = kratos
   
   ; common options
   master = true
   processes = 2
   

Note for FreeBSD >= 8.4 but < 9.0
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

uWSGI uses ipc semaphores on FreeBSD < 9 (newer FreeBSD releases have POSIX semaphores support).

Since FreeBSD 8.4 you need to explicitely allows sysvipc in jails. So be sure to have

.. code-block:: ini

   [uwsgi]
   ...
   jail2 = allow.sysvipc=1
   ...
   
   
DevFS
*****

The DevFS virtual filesystem manages the /dev directory on FreeBSD.

The /dev filesystem is not mounted in the jail, but you can need it for literally hundreds of reasons.

Two main approaches are available: mounting it in the /dev/ directory of the roots before creating the jail, or allowing the jail to mount it


.. code-block:: ini

   [uwsgi]
   ; avoid re-mounting the file system every time
   if-not-exists = /jails/001/dev/zero
     exec-pre-jail = mount -t devfs devfs /jails/001/dev
   endif =
   ; create the jail with /jails/001 as rootfs
   jail2 = path=/jails/001
   ; set hostname to 'foobar'
   jail2 = host.hostname=foobar
   ; create the alias on 'em0'
   exec-pre-jail = ifconfig em0 192.168.0.40 alias
   ; attach the alias to the jail
   jail2 = ip4.addr=192.168.0.40
   
   ; bind the http-socket (we are now in the jail)
   http-socket = 192.168.0.40:8080
   
   ; load the application (remember we are in the jail)
   wsgi-file = myapp.wsgi
   
   ; drop privileges
   uid = kratos
   gid = kratos
   
   ; common options
   master = true
   processes = 2


or (allow the jail itself to mount it)

.. code-block:: ini

   [uwsgi]
   ; create the jail with /jails/001 as rootfs
   jail2 = path=/jails/001
   ; set hostname to 'foobar'
   jail2 = host.hostname=foobar
   ; create the alias on 'em0'
   exec-pre-jail = ifconfig em0 192.168.0.40 alias
   ; attach the alias to the jail
   jail2 = ip4.addr=192.168.0.40
   
   ; allows mount of devfs in the jail
   jail2 = enforce_statfs=1
   jail2 = allow.mount
   jail2 = allow.mount.devfs
   ; ... and mount it
   if-not-exists = /dev/zero
     exec-post-jail = mount -t devfs devfs /dev
   endif =
   
   ; bind the http-socket (we are now in the jail)
   http-socket = 192.168.0.40:8080
   
   ; load the application (remember we are in the jail)
   wsgi-file = myapp.wsgi
   
   ; drop privileges
   uid = kratos
   gid = kratos
   
   ; common options
   master = true
   processes = 2


Reloading
*********

Reloading (or binary patching) is a bit annoying to manage as uWSGI need to re-exec itself, so you need a copy of the binary, plugins and the config file
in your jail (unless you can sacrifice graceful reload and simply delegate the Emperor to respawn the instance)

Another approach is (like with devfs) mounting the directory with the uwsgi binary (and the eventual plugins) in the jail itself and instruct
uWSGI to use this new path with --binary-path


The jidfile
***********

Each jail can be referenced by a unique name (optional) or its "jid". This is similar to a "pid", as you can use it
to send commands (and updates) to an already running jail. The --jidfile <file> option allows you to store the jid in a file
for use with external applications.

Attaching to a jail
*******************

You can attach uWSGI instances to already running jails (they can be standard persistent jail too) using --jail-attach <id>

The id argument can be a jid or the name of the jail.

This feature requires FreeBSD 8

Debian/kFreeBSD
***************

This is an official Debian project aiming at building an os with FreeBSD kernel and common Debian userspace.

It works really well, and it has support for jails too.

Let's create a jail with debootstrap

.. code-block:: sh

   debootstrap wheezy /jails/wheezy
   
add a network alias

.. code-block:: sh

   ifconfig em0 192.168.173.105 netmask 255.255.255.0 alias
   
(change em0 with your network interface name)

and run it

.. code-block:: sh

   uwsgi --http-socket 192.168.173.105:8080 --jail /jails/wheezy -jail-ip4 192.168.173.105
   

Jails with Forkpty Router
*************************

You can easily attach to FreeBSD jails with :doc:`ForkptyRouter`

Just remember to have /dev (well, /dev/ptmx) mounted in your jail to allow the forkpty() call

Learn how to deal with devfs_ruleset to increase security of your devfs


Notes
*****

A jail is destroyed when the last process running in it dies

By default everything mounted under the rootfs (before entering the jail) will be seen by the jail it self (we have seen it before when dealing with devfs)
