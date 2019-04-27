Jailing your apps using Linux Namespaces
========================================

If you have a recent Linux kernel (>2.6.26) and you are not on the Itanium architecture you can use the namespaces support.

What are namespaces?
--------------------

They are an elegant (more elegant than most of the jailing systems you might find in other operating systems) way to "detach" your processes from a specific layer of the kernel and assign them to a new one.

The 'chroot' system available on UNIX/Posix systems is a primal form of namespaces: a process sees a completely new file system root and has no access to the original one.

Linux extends this concept to the other OS layers (PIDs, users, IPC, networking etc.), so a specific process can live in a "virtual OS" with a new group of pids, a new set of users, a completely unshared IPC system (semaphores, shared memory etc.), a dedicated network interface and its own hostname.

uWSGI got full namespaces support in 1.9/2.0 development cycle.

clone() vs unshare()
--------------------

To place the current process in a new namespace you have two syscalls: the venerable ``clone()``, that will create a new process in the specified namespace
and the new kid on the block, ``unshare()``, that changes namespaces for the current running process.

``clone()`` can be used by the Emperor to directly spawn vassals in new namespaces:

.. code-block:: ini

   [uwsgi]
   emperor = /etc/uwsgi/vassals
   emperor-use-clone = fs,net,ipc,uts,pid
   
will run each vassal with a dedicated filesystem, networking, SysV IPC and UTS view.

.. code-block:: ini

   [uwsgi]
   unshare = ipc,uts
   ...
   
will run the current instance in the specified namespaces.

Some namespace subsystems require additional steps for sane usage (see below).

Supported namespaces
--------------------

* ``fs`` -> CLONE_NEWNS, filesystems
* ``ipc`` -> CLONE_NEWIPC, sysv ipc
* ``pid`` -> CLONE_NEWPID, when used with unshare() requires an additional ``fork()``. Use one of the --refork-* options.
* ``uts`` -> CLONE_NEWUTS, hostname
* ``net`` -> CLONE_NEWNET, new networking, UNIX sockets from different namespaces are still usable, they are a good way for inter-namespaces communications
* ``user`` -> CLONE_NEWUSER, still complex to manage (and has differences in behaviours between kernel versions) use with caution

setns()
-------

In addition to creating new namespaces for a process you can attach to already running ones using the ``setns()`` call.

Each process exposes its namespaces via the ``/proc/self/ns`` directory. The setns() syscall uses the file descriptors obtained from the files in that directory
to attach to namespaces.

As we have already seen, UNIX sockets are a good way to communicate between namespaces, the uWSGI ``setns()`` feature works by creating an UNIX socket that receives requests
from processes wanting to join its namespace. As UNIX sockets allow file descriptors passing, the "client" only need to call setns() on them.

* ``setns-socket <addr>`` exposes /proc/self/ns on the specified unix socket address
* ``setns <addr>`` connect to the specified unix socket address, get the filedescriptors and use setns() on them
* ``setns-preopen`` if enabled the /proc/self/ns files are opened on startup (before privileges drop) and cached. This is useful for avoiding running the main instance as root.
* ``setns-socket-skip <name>`` some file in /proc/self/ns can create problems (mostly the 'user' one). You can skip them specifying the name. (you can specify this option multiple times)

pivot_root
----------

This option allows you to change the rootfs of your currently running instance.

It is better than chroot as it allows you to access the old file system tree before (manually) unmounting it.

It is a bit complex to master correctly as it requires a couple of assumptions:

``pivot_root <new> <old>``

<new> is the directory to mount as the new rootfs and <old> is where to access the old tree.

<new> must be a mounted file system, and <old> must be under this file system.

A common pattern is:

.. code-block:: ini

   [uwsgi]
   unshare = fs
   hook-post-jail = mount:none /distros/precise /ns bind
   pivot_root = /ns /ns/.old_root
   ...
   
(Remember to create ``/ns`` and ``/distro/precise/.old_root``.)

When you have created the new file system layout you can umount /.old_root recursively:

.. code-block:: ini

   [uwsgi]
   unshare = fs
   hook-post-jail = mount:none /distros/precise /ns bind
   pivot_root = /ns /ns/.old_root
   ; bind mount some useful fs like /dev and /proc
   hook-as-root = mount:proc none /proc nodev hidepid=2
   hook-as-root = mount:none /.old_root/dev /dev bind
   hook-as-root = mount:none /.old_root/dev/pts /dev/pts bind
   ; umount the old tree
   hook-as-root = umount:/.old_root rec,detach


Why not lxc?
------------

LXC (LinuX Containers) is a project allowing you to build full subsystems using Linux namespaces. You may ask why "reinvent the wheel" while LXC implements
a fully "virtualized" system. Apples and oranges...

LXC's objective is giving users the view of a virtual server. uWSGI namespaces support is lower level -- you can use it to detach
single components (for example you may only want to unshare IPC) to increase security and isolation.

Not all the scenario requires a full system-like view (and in lot of case is suboptimal, while in other is the best approach), try to
see namespaces as a way to increase security and isolation, when you need/can isolate a component do it with clone/unshare. When you want
to give users a full system-like access go with LXC.

The old way: the --namespace option
===================================

Before 1.9/2.0 a full featured system-like namespace support was added. It works as a chroot() on steroids.

It should be moved as an external plugin pretty soon, but will be always part of the main distribution, as it is used by lot of people
for its simplicity.

You basically need to set a root filesystem and an hostname to start your instance in a new namespace:

Let's start by creating a new root filesystem for our jail. You'll need ``debootstrap`` (or an equivalent package for your distribution).
We're placing our rootfs in ``/ns/001``, and then create a 'uwsgi' user that will run the uWSGI server.
We will use the chroot command to 'adduser' in the new rootfs, and we will install the Flask package, required by uwsgicc.

(All this needs to be executed as root)

.. code-block:: sh

    mkdir -p /ns/001
    debootstrap maverick /ns/001
    chroot /ns/001
    # in the chroot jail now
    adduser uwsgi
    apt-get install mercurial python-flask
    su - uwsgi
    # as uwsgi now
    git clone https://github.com/unbit/uwsgicc.git .
    exit # out of su - uwsgi
    exit # out of the jail
    
Now on your real system run
    
.. code-block:: sh

    uwsgi --socket 127.0.0.1:3031 --chdir /home/uwsgi/uwsgi --uid uwsgi --gid uwsgi --module uwsgicc --master --processes 4 --namespace /ns/001:mybeautifulhostname

If all goes well, uWSGI will set ``/ns/001`` as the new root filesystem, assign ``mybeautifulhostname`` as the hostname and hide the PIDs and IPC of the host system.

The first thing you should note is the uWSGI master becoming PID 1 (the "init" process) in the new namespace.
All processes generated by the uWSGI stack will be reparented to it if something goes wrong. If the master dies, all jailed processes die.

Now point your web browser to your web server and you should see the uWSGI Control Center interface.

Pay attention to the information area. The node name (used by cluster subsystem) matches the real hostname as it does not make sense to have multiple jail in the same cluster group. In the hostname field instead you will see the hostname you have set.

Another important thing is that you can see all the jail processes from your real system (they will have a different set of PIDs), so if you want to take control of the jail
you can easily do it.


.. note::

   A good way to limit hardware usage of jails is to combine them with the cgroups subsystem.

   .. seealso:: :doc:`Cgroups`

Reloading uWSGI
---------------

When running in a jail, uWSGI uses another system for reloading: it'll simply tell workers to bugger off and then exit. The parent process living outside the namespace will see this and respawn the stack in a new jail.

How secure is this sort of jailing?
-----------------------------------

Hard to say! All software tends to be secure until a hole is found.

Additional filesystems
----------------------

When app is jailed to namespace it only has access to its virtual jail root filesystem. If there is any other filesystem mounted inside the jail directory, it won't be accessible, unless you use ``namespace-keep-mount``.

.. code-block:: ini

    # app1 jail is located here
    namespace = /apps/app1
    
    # nfs share mounted on the host side
    namespace-keep-mount = /apps/app1/nfs

This will bind /apps/app1/nfs to jail, so that jailed app can access it under /nfs directory

.. code-block:: ini
    
    # app1 jail is located here
    namespace = /apps/app1
    
    # nfs share mounted on the host side
    namespace-keep-mount = /mnt/nfs1:/nfs

If the filesystem that we want to bind is mounted in path not contained inside our jail, than we can use "<source>:<dest>" syntax for --namespace-keep-mount. In this case the /mnt/nfs1 will be binded to /nfs directory inside the jail.
