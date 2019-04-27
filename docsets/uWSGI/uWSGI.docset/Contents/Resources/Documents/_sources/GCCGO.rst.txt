The GCCGO plugin
================

uWSGI 1.9.20 officially substituted the old :doc:`Go` plugin with a new one based on GCCGO.

The usage of GCCGO allows more features and better integration with the uWSGI deployment styles.

GCC suite >= 4.8 is expected (and strongly suggested).

How it works
************

When the plugin is enabled, a new go runtime is initialized after each ``fork()``.

If a ``main`` Go function is available in the process address space it will be executed in the Go runtime, otherwise the control goes back to the uWSGI loop engine.

Why not use plain Go?
*********************

Unfortunately the standard Go runtime is currently not embeddable and does not support compiling code as shared libraries.

Both are requisite for meaningful uWSGI integration.

Starting from GCC 4.8.2, its ``libgo`` has been improved a lot and building shared libraries as well as initializing the Go runtime works like a charm (even if it required a bit of... not very elegant hacks).

Building the plugin
*******************

A build profile is available allowing you to build a uWSGI+gccgo binary ready to load Go shared libraries:

.. code-block:: sh

   make gccgo

The first app
*************

You do not need to change the way you write webapps in Go. The ``net/http`` package can be used flawlessly:

.. code-block:: go

   package main

   import "uwsgi"
   import "net/http"
   import "fmt"



   func viewHandler(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "<h1>Hello World</h1>")
   }

   func main() {
        http.HandleFunc("/view/", viewHandler)
        uwsgi.Run()
   }

The only difference is in calling ``uwsgi.Run()`` instead of initializing the Go HTTP server.

To build the code as shared library simply run:

.. code-block:: sh

   gcc -fPIC -shared -o myapp.so myapp.go
   
If you get an error about gcc not able to resolve uWSGI symbols, just add ``-I<path_to_uwsgi_binary>`` to the command line (see below):

.. code-block:: sh

   gcc -fPIC -shared -I/usr/bin -o myapp.so myapp.go
   
Now let's run it under uWSGI:

.. code-block:: sh

   uwsgi --http-socket :9090 --http-socket-modifier1 11 --go-load ./myapp.so
   
The gccgo plugin registers itself as ``modifier1`` 11, so remember to set it to run Go code.

uwsgi.gox
*********

By default when building the gccgo profile, a uwsgi.gox file is created. This can be used when building
go apps using the uWSGI API, to resolve symbols.

Remember that if you add the directory containing the uwsgi binary (as seen before) to
the includes (``-I path``) path of gcc, the binary itself will be used for resolving symbols.

Shared libraries VS monolithic binaries
***************************************

One of the main selling points for Go for many developers is the "static-all-in-one" binary approach.

A Go app basically does not have dependencies, so half of the common deployment problems just automagically disappear.

The uWSGI-friendly way for hosting Go apps is having a uWSGI binary loading a specific Go app in the form of a library.

If this is not acceptable, you can build a single binary with both uWSGI and the Go app:

.. code-block:: sh

   CFLAGS=-DUWSGI_GCCGO_MONOLITHIC UWSGI_ADDITIONAL_SOURCES=myapp.go UWSGI_PROFILE=gccgo make


Goroutines
**********

Thanks to the new GCC split stack feature, goroutines are sanely (i.e. they do not require a full pthread) implemented in gccgo.

A loop engine mapping every uWSGI core to a goroutine is available in the plugin itself.

To start uWSGI in goroutine mode just add ``--goroutines <n>`` where <n> is the maximum number of concurrent goroutines to spawn.

Like :doc:`Gevent`, uWSGI signal handlers are executed in a dedicated goroutine.

In addition to this, all blocking calls make use of the ``netpoll`` Go api. This means you can run internal routing actions, rpc included, in a goroutine.

Options
*******

* ``--go-load <path>`` load the specified go shared library in the process address space
* ``--gccgo-load <path>`` alias for go-load
* ``--go-args <arg1> <arg2> <argN>`` set arguments passed to the virtual go command line
* ``--gccgo-args <arg1> <arg2> <argN>`` alias for go-args
* ``--goroutines <n>`` enable goroutines loop engine with the specified number of async cores

uWSGI API
*********

.. note:: This section may, or may not, be out of date. Who knows!

Unfortunately only few pieces of the uWSGI API have been ported to the gccgo plugin. More features will be added in time for uWSGI 2.0.

Currently exposed API functions:

* ``uwsgi.CacheGet(key string, cache string) string``
* ``uwsgi.RegisterSignal(signum uint8, receiver string, handler func(uint8)) bool``

Notes
*****

* Please, please do not enable multithreading, it will not work and probably will never work.
* All uWSGI native features (like internal routing) work in goroutines mode. However do not expect languages like Python or Perl to work over them anytime soon.
