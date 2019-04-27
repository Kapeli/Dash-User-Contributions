uWSGI 2.0
=========

Changelog [20131230]

Important changes
*****************

Dynamic options have been definitely removed as well as the broken_plugins directory

Bugfixes and improvements
*************************

- improved log rotation
- do not rely on unix signals to print request status during harakiri
- added magic vars for uid and gid
- various Lua fixes
- a tons of coverity-governed bugfixes made by Riccardo Magliocchetti

New features
************

--attach-daemon2
^^^^^^^^^^^^^^^^

this is a keyval based option for configuring external daemons.

Updated docs are: :doc:`AttachingDaemons`

Linux setns() support
^^^^^^^^^^^^^^^^^^^^^

One of the biggest improvements in uWSGI 1.9-2.0 has been the total support for Linux namespaces.

This last patch adds support for the setns() syscall.

This syscall allows a process to "attach" to a running namespace.

uWSGI instances can exposes their namespaces file descriptors (basically they are the files in /proc/self/ns) via a unix socket.

External instances connects to that unix socket and automatically enters the mapped namespace.

to spawn an instance in "namespace server mode", you use the ``--setns-socket <addr>`` option

.. code-block:: sh

   uwsgi --setns-socket /var/run/ns.socket --unshare net,ipc,uts ...
   
   
to attach you simply use ``--setns <addr>``


.. code-block:: sh

   uwsgi --setns /var/run/ns.socket ...
   
Updated docs: :doc:`Namespaces`

"private" hooks
^^^^^^^^^^^^^^^

When uWSGI runs your hooks, it verbosely print the whole hook action line. This could be a security problem
in some scenario (for example when you run initial phases as root user but allows unprivileged access to logs).

Prefixing your action with a '!' will suppress full logging:

.. code-block:: ini

   [uwsgi]
   hook-asap = !exec:my_secret_command

Support for yajl library (JSON parser)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Til now uWSGI only supported jansson as the json parser required for managing .js config files.

You can now use the yajl library (available in centos) as alternative JSON parser (will be automatically detected)

Perl spooler support
^^^^^^^^^^^^^^^^^^^^

The perl/PSGI plugin can now be used as a spooler server:

.. code-block:: pl

   uwsgi::spooler(sub {
        my $args = shift;
        print Dumper($args);
        return -2;
   });


The client part is still missing as we need to fix some internal api problem.

Expect it in 2.0.1 ;)

Gateways can drop privileges
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Gateways (like http router, sslrouter, rawrouter, forkptyrouter ...) can now drop privileges independently by the master.

Currently only the http/https/spdy router exposes the new option (``--http-uid/--http-gid``)

Subscriptions-governed SNI contexts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The subscription subsystem now supports 3 additional keys (you can set them with the --subscribe2 option):

``sni_key``

``sni_cert``

``sni_ca``

all of the takes a path to the relevant ssl files.

Check: :doc:`SNI`


Availability
************

uWSGI 2.0 has been released on 20131230 and can be downloaded from:

https://projects.unbit.it/downloads/uwsgi-2.0.tar.gz
