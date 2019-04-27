uWSGI 1.9.14
============

Changelog [20130721]


Bugfixes
********

- fixed python modifier1 management (was hardcoded to 0)
- fixed url decoding in http and http-socket (it now supports lowercase hex, spotted by Miles Shang)
- more user-friendly error message for undeletable unix sockets
- fixed --http-auto-chunked in http 1.1 keepalive mode (André Cruz)
- fixed python wheel support (Fraser Nevett)
- fixed --safe-fd (was not correctly honoured by the Emperor)
- fixed ruby 2.x reloading
- improved support for OSX Tiger (yes, OSX 10.4)
- better computation of listen queue load
- fixed v8 build on OSX
- fixed pypy rpc
- improved chunked api performance
- fixed latin1 encoding with python3
- fixed --spooler-ordered (Roberto Leandrini)
- fixed php status line reported in request logs


New features
************

Ruby 1.9.x/2.x native threads support
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ruby 1.9 (mri) introduced native threads support (very similar to the CPython ones, governed by a global lock named GVL).

For various reasons (check the comments on top of the source plugin) the ruby threads support in uWSGI has been implemented as a "loop engine plugin".

You need to build the "rbthreads" plugin (it is automatic when using the 'ruby2' build profile) and enable it with '--rbthreads'

The gem script has been extended, automatically selecting the 'ruby2' build profile when a ruby >= 1.9 is detected (this should make the life easier for Heroku users)

Rails4 is the first Ruby on Rails version supporting and blessing threads (in 3.x you need to explicitly enable support). You can use
multiple threads in Rails4 only when in "production" mode, otherwise your app will deadlock after the first request.

An example config:

.. code-block:: ini

   [uwsgi]
   plugins = rack,rbthreads
   master = true
   ; spawn 2 processes
   processes = 2
   ; spawn 8 threads
   threads = 8
   ; enable ruby threads
   rbthreads = true
   ; load the Rack app
   rack = config.ru
   ; bind to an http port
   http-socket = :9090
   http-socket-modifier1 = 7
   
it will generate a total of 16 threads

Filesystem monitoring interface (fsmon)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Currently uWSGI is able to monitor filesystem changes using the "simple" --touch-* facility or the signal framework (using various
operating system api like inotify or kqueue).

A new interface for plugin writers named "fsmon" has been added, allowing easy implementation of realtime filesystem monitors.

Three new options have been added:

   `--fs-reload <path>`
   
   
   `--fs-brutal-reload <path>`
   
   
   `--fs-signal <path> <signal>`
   
Contrary to the --touch-* options they are realtime (the master is woke up as soon as the item changes) and. uses kernel facilities
(currently only inotify() and kqueue() are supported). Thanks to this choice you can now monitor a whole directory for changes (without the need of external
processes/wrapper like inotifywatch)

uClibc support
^^^^^^^^^^^^^^

Author: Natanael Copa

uWSGI can now be built on uclibc-based systems (generally, embedded systems)

Alpine Linux is the operating system on which the support has been tested

Lua 5.2 support
^^^^^^^^^^^^^^^

Author: Natanael Copa

the lua plugins now supports Lua 5.2

setscheme, setdocroot
^^^^^^^^^^^^^^^^^^^^^

This two new routing actions allow you to dynamically override DOCUMENT_ROOT and UWSGI_SCHEME

sendfile, fastfile
^^^^^^^^^^^^^^^^^^

This two actions (added to the router_static plugin) allows you to return static files to the client bypassing the DOCUMENT_ROOT check.

The first one forces the use of the sendfile() syscall (where available), while the second automatically tries to choose the best serving strategy (like offloading)

--reload-on-fd and --brutal-reload-on-fd
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Two new options allowing you to reload an instance when a file descriptor is ready.

Currently the best usage scenario is for the oom_control cgroup interface (via eventfd).

Supposing you have a process wrapper allocating an eventfd() reporting OOM events (and exposed as the 'OOM' environment var) you can force a uWSGI reload
when out of memory with:

.. code-block:: ini

   [uwsgi]
   ...
   reload-on-fd = $(OOM):8 OUT OF MEMORY !!!
   

it means:

monitor the $(OOM) file descriptor and read 8 bytes from it when ready (it is an eventfd() requirement), then print "OUT OF MEMORY !!!" in the logs and gracefully reload the instance.

Obviously this is only a way to use it. The UNIX world is file-descriptor based so you have plenty of funny ways to use it.


Spooler improvements
^^^^^^^^^^^^^^^^^^^^

Author: Roberto Leandrini


Effectively all of the work has been done in uwsgidecorators.py

You can now pass to all of the available spooler-related decorators the "pass_arguments=True" option, to automatically
serialize the spooler function parameters. This is an abstraction avoiding you the need to serialize/deserialize arguments.

In addition to this the decorators have been extended to implement __call__ in this way you can directly call spooler decorated functions
as normal functions.

--emperor-nofollow
^^^^^^^^^^^^^^^^^^

Enabling this option will allows the Emperor to watch for symbolic links mtime update instead of the mtime of the real file.

Alberto Scotto is working on an updated version supporting both (should be ready for the next release)

daemontools envdir support
^^^^^^^^^^^^^^^^^^^^^^^^^^

Albeit daemontools look old-fashioned, things like envdirs (http://cr.yp.to/daemontools/envdir.html) are heavily used in various context.

uWSGI got two new options (--envdir <path> and --early-envdir <path>) allowing you to support this special (archaic ?) configuration way.

xmldir improvements
^^^^^^^^^^^^^^^^^^^

Author: Guido Berhoerster

The xmldir plugins has been improved supporting iconv-based utf8 encoding. Various minor fixes have been committed.

The examples directory contains two new files showing an xmldir+xslt usage


Breaking News !!!
*****************

Servlet 2.5 support development has just started. The plugin is present in the tree but it is unusable (it is a hardcoded
jsp engine). We expect a beta version after the summer. Obviously we shameless consider :doc:`JWSGI` a better approach than servlet for non-Enterprise people ;)

Availability
************

Download uWSGI 1.9.14 from

https://projects.unbit.it/downloads/uwsgi-1.9.14.tar.gz
