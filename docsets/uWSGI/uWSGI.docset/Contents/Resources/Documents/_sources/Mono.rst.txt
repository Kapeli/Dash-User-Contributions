The Mono ASP.NET plugin
=======================

uWSGI 1.9 added support for the Mono platform, especially for the ASP.NET infrastructure.

The most common way to deploy Mono ASP.NET applications is with the XSP project, a simple web server gateway
implementing HTTP and FastCGI protocols.

With the Mono plugin you will be able to host ASP.net applications directly in uWSGI, gaining all of its features in your application for free.

As all of the other uWSGI plugin you can call functions exported from the other languages using the :doc:`RPC` subsystem.

Building uWSGI + Mono
*********************

You can build Mono support as a plugin or in a monolithic build.

A build profile named "mono" is available, making the task pretty simple.

Be sure to have mono installed in your system. You need the Mono headers, the ``mcs`` compiler and the System.Web assembly. They are available in standard mono distributions.

On recent Debian/Ubuntu systems you can use

.. code-block:: sh

    apt-get install build-essential python mono-xsp4 asp.net-examples

``mono-xsp4`` is a trick to install all we need in a single shot, as ASP.net examples will be used for testing our setup.

We can build a monolithic uWSGI distribution with Mono embedded:

.. code-block:: sh

   UWSGI_PROFILE=mono make

At the end of the procedure (if all goes well) you will get the path to the ``uwsgi.dll`` assembly.

You may want to install it in your GAC (with gacutil -i <path>) to avoid specifying its path every time. This library allows access to the uWSGI api from Mono applications.

Starting the server
*******************

The Mono plugin has an official ``modifier1``, 15.

.. code-block:: ini

   [uwsgi]
   http = :9090
   http-modifier1 = 15
   mono-app = /usr/share/asp.net-demos
   mono-index = index.asp

The previous setup assumes uwsgi.dll has been installed in the GAC, if it is not your case you can force its path with:

.. code-block:: ini

   [uwsgi]
   http = :9090
   http-modifier1 = 15
   mono-app = /usr/share/asp.net-demos
   mono-index = index.asp
   mono-assembly = /usr/lib/uwsgi/uwsgi.dll

``/usr/share/asp.net-demos`` is the directory containing Mono's example ASP.net applications.

If starting uWSGI you get an error about not being able to find uwsgi.dll, you can enforce a specific search path with

.. code-block:: ini

   [uwsgi]
   http = :9090
   http-modifier1 = 15
   mono-app = /usr/share/asp.net-demos
   mono-index = index.asp
   mono-assembly = /usr/lib/uwsgi/uwsgi.dll
   env = MONO_PATH=/usr/lib/uwsgi/

Or you can simply copy uwsgi.dll into the ``/bin`` directory of your site directory (``/usr/share/asp.net-demos`` in this case).

The ``mono-index`` option is used to set the file to search when a directory is requested. You can specify it multiple times.

Under the hood: the mono key
****************************

The previous example should have worked flawlessly, but internally lot of assumptions have been made.

The whole mono plugin relies on the "key" concept. A key is a unique identifier for a .net application. In the example case the key for the application
is "/usr/share/asp.net-demos". This is a case where the key maps 1:1 with the virtualhost map. To map a virtualhost path to a specific key you can use the form

.. code-block:: ini

   [uwsgi]
   http = :9090
   http-modifier1 = 15
   mono-app = /foobar=/usr/share/asp.net-demos

now the /foobar key maps to the /usr/share/asp.net-demos .net app.

By default the requested key is mapped to the DOCUMENT_ROOT variable. So in this new case /foobar should be the DOCUMENT_ROOT value.

But the uWSGI http router has no concept of DOCUMENT_ROOT so how the previous example could work ? This is because the first loaded app is generally the default one, so the mono plugin, being not able to
find an app returned the default one.

Using DOCUMENT_ROOT as the key could be quite limiting. So the --mono-key option is available. Let's build a massive virtualhosting stack using uWSGI internal routing

.. code-block:: ini

   [uwsgi]
   http = :9090
   http-modifier1 = 15
   mono-key = MONO_APP
   route-run = addvar:MONO_APP=/var/www/asp/${HTTP_HOST}
   
MONO_APP is not the variable the mono plugin will search for applications (instead of DOCUMENT_ROOT).

Thanks to internal routing we set it (dynamically) to the path of host-specific application root, so a request to example.com
will map to /var/www/asp/example.com


Concurrency and fork() unfriendliness
**************************************

As the Mono VM is not ``fork()`` friendly, a new VM is spawned for each worker. This ensures you can run your application in multiprocessing mode.

Mono has really solid multithreading support and it works great with uWSGI's thread support.

.. code-block:: ini

   [uwsgi]
   http = :9090
   http-modifier1 = 15
   mono-app = /usr/share/asp.net-demos
   mono-index = index.asp
   mono-assembly = /usr/lib/uwsgi/uwsgi.dll
   env = MONO_PATH=/usr/lib/uwsgi/
  
   master = true
   processes = 4
   threads = 20

With this setup you will spawn 4 processes each with 20 threads. Try to not rely on a single process. Albeit it is a common setup in the so-called "Enterprise environments", having multiple processes ensures you greater availability (thanks to the master work).
This rule (as an example) applies even to the :doc:`JVM` plugin.

API access
**********

This is a work in progress. Currently only a couple of functions are exported. High precedence will be given to the :doc:`RPC` and Signal subsystem and to the :doc:`Caching` framework.

Tricks
******

As always uWSGI tries to optimize (where possible) the "common" operations of your applications. Serving static files is automatically accelerated (or offloaded if offloading is enabled) and all of the path resolutions are cached.
