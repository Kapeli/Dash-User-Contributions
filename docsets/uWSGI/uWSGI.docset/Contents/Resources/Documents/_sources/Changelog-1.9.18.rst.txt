uWSGI 1.9.18
============

Changelog [20131011]

License change
**************

This version of uWSGI is the first of the 1.9 tree using GPL2 + linking exception instead of plain GPL2.

This new license should avoid any problems when using uWSGI as a shared library (or when linking it with non-GPL2 compatible libraries)

Remember: if you need to make closed-source modifications to uWSGI you can buy a commercial license.

Bugfixes
********

- fixed uwsgi native protocol support on big endian machines
- fixed jvm build system for arm (Jorge Gallegos)
- fixed a memleak spotted by cppcheck in zlib management
- chdir() at every emperor glob iteration
- correctly honour --force-cwd
- fixed ia64/Linux compilation (Jonas Smedegaard/Riccardo Magliocchetti)
- fixed ruby rvm paths parsing order
- added waitpid() after daemon's SIGTERM (Łukasz Mierzwa)
- fixed pid numbering after --idle (Łukasz Mierzwa)
- fixed/improved cheaper memory limits (Łukasz Mierzwa)
- correctly close inherited sockets in gateways
- fix checks for MAP_FAILED in mmap() (instead of NULL)
- fixed FastCGI non-blocking body read() (patch by Arkaitz Jimenez)
- fixed attach.py script
- avoid crashing on non-conformant PSGI response headers
- run the python autoreloader even in non-apps mode when non-lazy

New Features
************

Minimal build profiles
^^^^^^^^^^^^^^^^^^^^^^

Albeit the memory usage of the uWSGI core is generally between 1.8 and 2.5 megs, there are use cases in which you want an even minimal
core and set of embedded plugins.

Examples are users not making use of uWSGI specific features, or cases in which the libraries used by uWSGI nameclash with others (like openssl or zeromq).

A bunch of 'minimal' build profiles have been added:

 * pyonly (build a minimal CPython WSGI server)
 * pypyonly (build a minimal PyPy WSGI server)
 * plonly (build a minimal PSGI server)
 * rbonly (build a minimal Rack server)
 
the only supported configuration format is .ini and internal routing and legion subsystem are not builtin.

For example if you want to install a minimal uWSGI binary via pip:

.. code-block:: sh

   UWSGI_PROFILE=pyonly pip install uwsgi
   
IMPORTANT: minimal build profiles do not improve performance, for the way uWSGI is designed, unused features do not waste CPU. Minimal build profiles impact on final binary size only
   
Auto-fix modifier1
^^^^^^^^^^^^^^^^^^

Setting the modifier1 for non-python plugin is pretty annoying (read: you always forget about it).

Now if the modifier1 of the request is zero, but the python plugin is not loaded (or there are no python apps loaded) the first configured app
will be set instead (unless you disable with feature with --no-default-app).

This means you can now run:

.. code-block:: sh

   uwsgi --http-socket :9090 --psgi myapp.pl
   
instead of

.. code-block:: sh

   uwsgi --http-socket :9090 --http-socket-modifier1 5 --psgi myapp.pl

obviously try to always set the modifier1, this is only a handy hack

Perl auto reloader
^^^^^^^^^^^^^^^^^^

The --perl-auto-reload option allows the psgi plugin to check for changed modules after every request. It takes the frequency (in seconds) of the scan.

The scan happens after a request has been served. It is suboptimal, but it is the safest choice too.

The "raw" mode (preview technology, only for CPython)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

While working on a new server-side project in Unbit we had the need to expose our web application using a very specific protocol (none of the ones supported by uWSGI).

Our first way was adding the new protocol as a plugin, but soon we realize that is was too-specific. So we decided to introduce the RAW mode.

Raw mode allows you to directly parse the request in your application callable. Instead of getting a list of CGI vars/headers in your callable
you only get the file descriptor soon after accept().

You can then read()/write() to that file descriptor in full freedom.

.. code-block:: python

   import os
   def application(fd):
      os.write(fd, "Hello World")
      
.. code-block:: sh

   uwsgi --raw-socket :7070 --python-raw yourapp.py

Raw mode disables request logging. We currently support it only for CPython, if we get reports (or interest) about it for the other languages we will add
support for sure.

IMPORTANT: raw mode is not a standard, so do not expect any middleware or common usage patterns will apply. Use it as a low-level socket wrapper. 



Optional NON-standard support for CPython buffer protocol for WSGI responses
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Authors: yihuang with help of INADA Naoki (methane)

The WSGI (PEP333/3333) is pretty clear about the type of valid objects for responses: str for python2, bytes for python3

uWSGI (heavily using mod_wsgi as a reference) always enforce such behaviour, so "exotic" patterns like returning bytearray
where not supported. Such uses are somewhat involuntary supported on pure-python application servers, just because they simply call write() over them or because they cast them to string
before returning (very inefficient)

The patch proposed by yihuang suggests the use of the low-level buffer protocol exposed by the CPython C api. Strings (in python2) and bytes (in python3) support the buffer protocol, so its use is transparent
and backward compatibility is granted too. (for the CPython C api experts: yes we support both old and new buffer protocol)

This is a NON-standard behaviour you have to voluntary enable with --wsgi-accept-buffer.

Use with care as it could mask errors and/or wrong behaviours.

Note: if you tried 1.9.18-dev you may note this option was enabled by default. It was an error. Thanks to Graham Dumpleton (mod_wsgi author) for pointing it out.

Emperor and config improvements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Credits: Matthijs Kooijman

The config system has been improved to be even more consistent in respect to strict mode (remainder: with --strict you basically check your config files for unknown options
avoiding headaches caused by typos).

New magic vars have been added exposing the name of the original config file (this simplify templating when in Emperor mode), check them at https://github.com/unbit/uwsgi-docs/blob/master/Configuration.rst#magic-variables

The Emperor got support for Linux capabilities using the --emperor-cap option. The option takes the list of capability you want to maintain
for your vassals when they start as root:

.. code-block:: ini

   [uwsgi]
   emperor = /etc/uwsgi/vassals
   emperor-cap = setuid,net_bind_service
   
with this setup your vassal will be only able to drop privileges and bind to ports < 1024

Its best friend is the CLONE_NEWUSER flag of linux namespaces that is now fully supported on uWSGI:

.. code-block:: ini

   [uwsgi]
   emperor = /etc/uwsgi/vassals
   emperor-use-clone = user
   emperor-cap = setuid,net_bind_service
   
this will create a new root user for the vassal with fewer privileges (CLONE_NEWUSER is pretty hard to understand, but the best thing
to catch it is seeing it as a new root user with dedicated capabilities)

Build system improvements
^^^^^^^^^^^^^^^^^^^^^^^^^

The build system has been improved to link custom sources on the fly. This works great for low-level hooks:

.. code-block:: c

   // embed_me.c
   #include <stdio.h>
   
   void hello_i_am_foobar() {
           printf("I Am foobar");
   }

Now we can link this file to the main uWSGI binary in one shot:


.. code-block:: sh

   UWSGI_ADDITIONAL_SOURCES=embed_me.c make

and you will automatically get access for your hooks:

.. code-block:: sh

   uwsgi --http-socket :9090 --call-asap hello_i_am_foobar
   
Finally, Riccardo Magliocchetti rewrote the build script to use optparse instead of raw/old-fashioned sys.argv parsing


Pluginized the 'schemes' management
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

schemes are the prefix part of uWSGI uri's. When you do

.. code-block:: sh

   uwsgi --ini http://foobar.local:9090/test.ini
   
the http:// is the scheme, signalling uWSGI it has to download the config file via http.

Til now those 'schemes' were hardcoded. Now they are exposed as plugins, so you can add more of them (or override the default one).

The new system has been applied to the PSGI plugin too (sorry we are sure only perl developers will understand that kind of poetry :P) so you can do things like:

.. code-block:: sh

   uwsgi --http-socket :1717 --psgi http://yourapps.local/dancer.pl
   
or

.. code-block:: sh

   ./uwsgi --binary-append-data yourapp.pl > blob001
   cat blob001 >> ./uwsgi
   ./uwsgi --http-socket :1717 --psgi data://0

mountpoints checks
^^^^^^^^^^^^^^^^^^

It could be hard to understand why an application server should check for mountpoints.

In the same way understanding how writing filesystem in userspace was silly few years ago.

So, check the article about managing Fuse filesystem with uWSGI: https://uwsgi-docs.readthedocs.io/en/latest/tutorials/ReliableFuse.html

Preliminary libffi plugin
^^^^^^^^^^^^^^^^^^^^^^^^^

As embedding c libraries for exposing hooks is becoming more common, we have started working on libffi integration, allowing
safe (and sane) argument passing to hooks. More to came soon.

Official support for kFreeBSD
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Debian/kFreeBSD is officially supported.

You can even use FreeBSD jails too !!!

:doc:`FreeBSDJails`

Availability
************

uWSGI 1.9.18 has been released on October 11th 2013 and can be downloaded from:

https://projects.unbit.it/downloads/uwsgi-1.9.18.tar.gz
