Reliably use FUSE filesystems for uWSGI vassals (with Linux)
============================================================

Requirements: uWSGI 1.9.18, Linux kernel with FUSE and namespaces support.

FUSE is a technology allowing the implementation of filesystems in user space (hence the name: **F**\ ilesystem in **Use**\ rspace).
There are hundreds of high-quality FUSE filesystems, so having your application relying on them is a common situation.

FUSE filesystems are normal system processes, so as any process in the system, they can crash (or you may involuntarily kill them).
In addition to this, if you host multiple applications, each one requiring a FUSE mount point, you may want to avoid polluting the main mount points namespace and, more important,
avoid having unused mount points in your system (i.e. an instance is completely removed and you do not want its FUSE mount point to be still available in the system).

The purpose of this tutorial is to configure an Emperor and a series of vassals, each one mounting a FUSE filesystem.

A Zip filesystem
^^^^^^^^^^^^^^^^

`fuse-zip <https://code.google.com/p/fuse-zip/>`_ is a FUSE process exposing a zip file as a filesystem.

Our objective is to store whole app in a zip archive and instruct uWSGI to mount it as a filesystem (via FUSE) under ``/app``.

The Emperor 
***********

.. code-block:: ini

   [uwsgi]
   emperor = /etc/uwsgi/vassals
   emperor-use-clone = fs,pid
   
The trick here is to use Linux namespaces to create vassals in a new pid and filesystem namespace.

The first one (``fs``) allows mount point created by the vassal to be available only to the vassal (without messing with the main system), while the ``pid``
allows the uWSGI master to be the "init" process (pid 1) of the vassal. Being "pid 1" means that when you die all your children die too. In our scenario (where our vassal launches a FUSE process on startup) it means that when
the vassal is destroyed, the FUSE process is destroyed too, as well as its mount point.

A Vassal
********

.. code-block:: ini

   [uwsgi]
   uid = user001
   gid = user001
   
   ; mount FUSE filesystem under /app (but only if it is not a reload)
   if-not-reload =
     exec-as-user = fuse-zip -r /var/www/app001.zip /app
   endif =
   
   http-socket = :9090
   psgi = /app/myapp.pl
   
Here we use the ``-r`` option of the ``fuse-zip`` command for a read-only mount.

Monitoring mount points
***********************

The problem with the current setup is that if the ``fuse-zip`` process dies, the instance will no more be able to access ``/app`` until it is respawned.

uWSGI 1.9.18 added the ``--mountpoint-check`` option. It forces the master to constantly verify the specified filesystem. If it fails, the whole instance will be brutally destroyed.
As we are under The Emperor, soon after the vassal is destroyed it will be restarted in a clean state (allowing the FUSE mount point to be started again).

.. code-block:: ini

   [uwsgi]
   uid = user001
   gid = user001
   
   ; mount FUSE filesystem under /app (but only if it is not a reload)
   if-not-reload =
     exec-as-user = fuse-zip -r /var/www/app001.zip /app
   endif =
   
   http-socket = :9090
   psgi = /app/myapp.pl
   
   mountpoint-check = /app
   
Going Heavy Metal: A CoW rootfs (unionfs-fuse)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`unionfs-fuse <http://podgorny.cz/moin/UnionFsFuse>`_ is a user-space implementation of a union filesystem.
A union filesystem is a stack of multiple filesystems, so directories with same name are merged into a single view.

Union filesystems are more than this and one of the most useful features is copy-on-write (COW or CoW).
Enabling CoWs means you will have an immutable/read-only mount point base and all of the modifications to it will go to another mount point.

Our objective is to have a read-only rootfs shared by all of our customers, and a writable mount point (configured as CoW) for each customer, in which every modification will be stored.

The Emperor
***********

Previous Emperor configuration can be used, but we need to prepare our
filesystems.

The layout will be:

.. code-block:: c

   /ufs (where we initially mount our unionfs for each vassal)
   /ns
     /ns/precise (the shared rootfs, based on Ubuntu Precise Pangolin)
     /ns/lucid (an alternative rootfs for old-fashioned customers, based on Ubuntu Lucid Lynx)
     /ns/saucy (another shared rootfs, based on Ubuntu Saucy Salamander)
     
     /ns/cow (the customers' writable areas)
       /ns/cow/user001
       /ns/cow/user002
       /ns/cow/userXXX
       ...
       
We create our rootfs:

.. code-block:: sh

   debootstrap precise /ns/precise
   debootstrap lucid /ns/lucid
   debootstrap saucy /ns/saucy
   
And we create the ``.old_root`` directory in each one (it is required for ``pivot_root``, see below):

.. code-block:: sh

   mkdir /ns/precise/.old_root
   mkdir /ns/lucid/.old_root
   mkdir /ns/saucy/.old_root
   
Be sure to install the required libraries into each of them (especially the libraries required for your language).

The ``uwsgi`` binary must be executable in this rootfs, so you have to invest a bit of time in it (a good approach is having a language plugin
compiled for each distribution and placed into a common directory, for example, each rootfs could have an ``/opt/uwsgi/plugins/psgi_plugin.so`` file and so on).

A Vassal
********

Here things get a bit more complicated. We need to launch the unionfs process (as root, as it must be our new rootfs) and then call ``pivot_root`` (a more advanced ``chroot`` available on Linux).

:doc:`../Hooks` are the best way to run custom commands (or functions) at various uWSGI startup phases.

In our example we will run FUSE processes at the "pre-jail" phase, and deal with mount points at the "as-root" phase (that happens after ``pivot_root``).

.. code-block:: ini

   [uwsgi]
   ; choose the approach that suits you best (plugins loading)
   ; this will be used for the first run ...
   plugins-dir = /ns/precise/opt/uwsgi/plugins
   ; and this after a reload (where our rootfs is already /ns/precise)
   plugins-dir = /opt/uwsgi/plugins
   plugin = psgi
   
   ; drop privileges
   uid = user001
   gid = user001
   
   ; chdir to / to avoid problems after pivot_root
   hook-pre-jail = callret:chdir /
   ; run unionfs-fuse using chroot (it is required to avoid deadlocks) and cow (we mount it under /ufs)
   hook-pre-jail = exec:unionfs-fuse -ocow,chroot=/ns,default_permissions,allow_other /precise=RO:/cow/%(uid)=RW /ufs

   ; change the rootfs to the unionfs one
   ; the .old_root directory is where the old rootfs is still available
   pivot_root = /ufs /ufs/.old_root
   
   ; now we are in the new rootfs and in 'as-root' phase
   ; remount the /proc filesystem
   hook-as-root = mount:proc none /proc
   ; bind mount the original /dev in the new rootfs (simplifies things a lot)
   hook-as-root = mount:none /.old_root/dev /dev bind
   ; recursively un-mount the old rootfs
   hook-as-root = umount:/.old_root rec,detach
   
   ; common bind
   http-socket = :9090
   
   ; load the app (fix it according to your requirements)
   psgi = /var/www/myapp.pl
   
   ; constantly check for the rootfs (seems odd but is is very useful)
   mountpoint-check = /
   
If your app will try to write to its filesystem, you will see that all
of the created/updated files are available in its ``/cow`` directory.

Notes
^^^^^

Some FUSE filesystems do not commit writes until they are unmounted.
In such a case unmounting on vassal shutdown is a good trick:

.. code-block:: ini

   [uwsgi]
   ; vassal options ...
   ...
   ; umount on exit
   exec-as-user-atexit = fusermount -u /app
