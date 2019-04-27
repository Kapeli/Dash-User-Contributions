The GlusterFS plugin
====================

Available from uWSGI 1.9.15

official modifier1: 27

The 'glusterfs' plugin allows you to serve files stored in glusterfs filesystems directly using the glusterfs api
available starting from GlusterFS 3.4

This approach (compared to serving via fuse or nfs) has various advantages in terms of performances and ease of deployment.


Step1: glusterfs installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

we build glusterfs from official sources, installing it in /opt/glusterfs on 3 nodes (192.168.173.1, 192.168.173.2, 192.168.173.3).

.. code-block:: sh

   ./configure --prefix=/opt/glusterfs
   make
   make install
   
now start the configuration/control daemon with:

.. code-block:: sh

   /opt/glusterfs/sbin/glusterd
   
from now on we can start configuring our cluster

Step2: the first cluster
^^^^^^^^^^^^^^^^^^^^^^^^

run the control client to access the glusterfs shell:

.. code-block:: sh

   /opt/glusterfs/sbin/gluster
   
the first step is "discovering" the other nodes:

.. code-block:: sh

   # do not run on node1 !!!
   peer probe 192.168.173.1
   # do not run on node2 !!!
   peer probe 192.168.173.2
   # do not run on node3 !!!
   peer probe 192.168.173.3

remember, you do not need to run "peer probe" for the same address of the machine on which you are running
the glusterfs console. You have to repeat the procedure on each node of the cluser.

Now we can create a replica volume (/exports/brick001 dir has to exist in every node):

.. code-block:: sh

   volume create unbit001 replica 3 192.168.173.1:/exports/brick001 192.168.173.2:/exports/brick001 192.168.173.3:/exports/brick001
   
and start it:

.. code-block:: sh

   volume start unbit001
   
Now you should be able to mount your glusterfs filesystem and start writing files in it (you can use nfs or fuse)

Step3: uWSGI
^^^^^^^^^^^^

a build profile, named 'glusterfs' is already available, so you can simply do:

.. code-block:: sh

   PKG_CONFIG_PATH=/opt/glusterfs/lib/pkgconfig/ UWSGI_PROFILE=glusterfs make
   
The profile currently disable 'matheval' support as the glusterfs libraries use bison/yacc with the same function prefixes (causing nameclash).


You can now start your HTTP serving fastly serving glusterfs files (remember no nfs or fuse are involved):

.. code-block:: ini

   [uwsgi]
   ; bind on port 9090
   http-socket = :9090
   ; set the default modifier1 to the glusterfs one
   http-socket-modifier1 = 27
   ; mount our glusterfs filesystem
   glusterfs-mount = mountpoint=/,volume=unbit001,server=192.168.173.1:0
   ; spawn 30 threads
   threads = 30
   

High availability
^^^^^^^^^^^^^^^^^

The main GlusterFS selling point is high availability. With the prevopus setup we introduced a SPOF with the control daemon.

The 'server' option allows you to specify multiple control daemons (they are tried until one responds)

.. code-block:: ini

   [uwsgi]
   ; bind on port 9090
   http-socket = :9090
   ; set the default modifier1 to the glusterfs one
   http-socket-modifier1 = 27
   ; mount our glusterfs filesystem
   glusterfs-mount = mountpoint=/,volume=unbit001,server=192.168.173.1:0;192.168.173.2:0;192.168.173.3:0
   ; spawn 30 threads
   threads = 30
   
The '0' port is a glusterfs convention, it means 'the default port' (generally 24007). You can specify whatever port you need/want

Multiple mountpoints
^^^^^^^^^^^^^^^^^^^^

If your webserver (like nginx or the uWSGI http router) is capable of setting protocol vars (like SCRIPT_NAME or UWSGI_APPID) you can mount multiple
glusterfs filesystems in the same instance:

.. code-block:: ini

   [uwsgi]
   ; bind on port 9090
   http-socket = :9090
   ; set the default modifier1 to the glusterfs one
   http-socket-modifier1 = 27
   ; mount our glusterfs filesystem
   glusterfs-mount = mountpoint=/,volume=unbit001,server=192.168.173.1:0;192.168.173.2:0;192.168.173.3:0
   glusterfs-mount = mountpoint=/foo,volume=unbit002,server=192.168.173.1:0;192.168.173.2:0;192.168.173.3:0
   glusterfs-mount = mountpoint=/bar,volume=unbit003,server=192.168.173.1:0;192.168.173.2:0;192.168.173.3:0
   ; spawn 30 threads
   threads = 30
   
Multiprocess VS multithread
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Currently a mix of the both will offers you best performance and availability.

Async support is on work

Internal routing
^^^^^^^^^^^^^^^^

The :doc:`InternalRouting` allows you to rewrite requests to change the requested files. Currently the glusterfs plugin only uses the PATH_INFO, so you can change it
via the 'setpathinfo' directive

Caching is supported too. Check the tutorial (linked in the homepage) for some cool idea


Using capabilities (on Linux)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your cluster requires clients to bind on privileged ports (<1024) and you do not want to change that thing (and obviously you do not want to run uWSGI as root)
you may want to give your uWSGI instance the NET_BIND_SERVICE capability. Just ensure you have a capabilities-enabled uWSGI and add

.. code-block:: sh

   ... --cap net_bind_service ...
   
to all of the instances you want to connect to glusterfs

Notes:
^^^^^^

The plugin automatically enables the mime type engine.

There is no directory index support
