uWSGI Go support (1.4 only)
===========================

.. warning:: Starting from 1.9.20, the Go plugin has been superseded by the :doc:`GCCGO` plugin.

Starting from uWSGI 1.4-dev you can host Go web applications in your uWSGI
stack.  You can download Go from http://golang.org/ .  Currently Linux
i386/x86_64, FreeBSD i386/x86_64 and OSX are supported.  For OSX support, you
need Go 1.0.3+ or you will need to apply the patch available at
http://code.google.com/p/go/source/detail?r=62b7ebe62958 Goroutines are
currently supported only on Linux i386/x86_64.

Building uWSGI with Go support
******************************

Go support can be built as an embedded component or plugin.  The main
difference with the setup of other languages is this time we will build a uwsgi
library and not a uwsgi binary. This library will be used by a Go package named
uwsgi.go you can link with your apps.  Do not be afraid as in the uWSGI
distribution there is already a build profile to make a completely (monolithic)
distribution with Go support embedded.  At the end of the build procedure you
will have a libuwsgi.so shared library and a uwsgi.a Go package.

To build uWSGI+go just run (from uWSGI sources directory)

.. code-block:: sh

   UWSGI_PROFILE=go make

or if Python is not in your system path, or you need to use a specific python
version:

.. code-block:: sh

   /usr/local/bin/python uwsgiconfig.py --build go

(or wherever your custom Python is)

At the end of the build procedure you will have a libuwsgi.so file (copy or
link it to a library directory like /usr/local/lib or /usr/lib and eventually
run ldconfig if needed) and a uwsgi.a file in a subdirectory (based on your
arch/os) in plugins/go/pkg.

.. important::

   The last message from the build procedure reports the ``GOPATH`` you should
   use when building uWSGI Go apps (copy/remember/annotate that value
   somewhere).

   If you already know how the Go import system works, feel free to copy
   uwsgi.a in your system-wide GOPATH.

Writing the first Go application
********************************

By default the uWSGI Go plugin supports the ``http.DefaultServeMux`` handler,
so if your app is already based on it, running it in uWSGI should be extremely
simple.

.. code-block:: go

   package main

   import (
           "uwsgi"
           "net/http"
           "fmt"
   )

   func oneHandler(w http.ResponseWriter, r *http.Request) {
           fmt.Fprintf(w, "<h1>One</h1>")
   }


   func twoHandler(w http.ResponseWriter, r *http.Request) {
           fmt.Fprintf(w, "<h2>Two</h2>")
   }

   func main() {
           http.HandleFunc("/one/", oneHandler)
           http.HandleFunc("/two/", twoHandler)
           uwsgi.Run()
   }

As you can see, the only differences from a standard ``net/http``-based
application are the need to ``import "uwsgi"`` need and calling ``uwsgi.Run()``
function, which will run the whole uWSGI server.  If you want to use your
personal request handler instead of ``http.DefaultServeMux``, use
``uwsgi.Handler(http.Handler)`` or
``uwsgi.RequestHandler(func(http.ResponseWriter, *http.Request))`` to set it.

.. code-block:: go

   func myHandler(w http.ResponseWriter, r *http.Request) {
           fmt.Fprintf(w, "<h2>Two</h2>")
   }

   func main() {
           uwsgi.RequestHandler(myHandler)
           uwsgi.Run()
   }

Building your first app
***********************

Assuming you saved your app as helloworld.go, just run the following.

.. code-block:: sh

   GOPATH=/home/foobar/uwsgi/plugins/go go build helloworld.go

change GOPATH to the value you got from the build procedure, or to the dir you
have installed/copied uwsgi.a If all goes well you will end with a 'helloworld'
executable.  That executable is a full uWSGI server (yes, really).

.. code-block:: sh

   ./helloworld --http :8080 --http-modifier1 11

Just point your browser to the port 8080 and check /one/ and /two/ You can
start adding processes and a master:

.. code-block:: sh

   ./helloworld --http :8080 --http-modifier1 11 --master --processes 8

Note: modifier1 11 is officially assigned to Go.

Going in production
*******************

In a production environment you will probably put a webserver/proxy in front of
your app. Thus your nginx config will look like this::

   location / {
       include uwsgi_params;
       uwsgi_pass 127.0.0.1:3031;
       uwsgi_modifier1 11;
   }

while your uWSGI config will be something like this...

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   master = true
   processes = 4

Finally simply run your app:

.. code-block:: sh

   ./helloworld config.ini

Goroutines (currently Linux/FreeBSD-only)
*****************************************

Goroutines are very probably the most interesting feature of the Go platform.
A uWSGI loop engine for goroutines is automatically embedded in the uWSGI
library when you build it with the go plugin.  To spawn goroutines in each
uWSGI process just add the ``goroutines = N`` option, where N is the number of
goroutines to spawn.

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   master = true
   processes = 4
   goroutines = 100

With this config you will spawn 100 goroutines for each uWSGI process, yielding
a grand total of 400 goroutines (!) As far as uWSGI is concerned, goroutines
map to pthreads, but you will be able to spawn coroutine-based tasks from your
application as well.

uWSGI api
*********

It is fairly simple to access the uWSGI API from your Go app. To do so invoke
the functions exported by the uwsgi package:

.. code-block:: go

   package main

   import (
      "fmt"
      "uwsgi"
   )

   func hello2(signum int) {
           fmt.Println("I am an rb_timer running on mule", uwsgi.MuleId())
   }

   func hello(signum int) {
           fmt.Println("Ciao, 3 seconds elapsed")
   }

   func postinit() {
           uwsgi.RegisterSignal(17, "", hello)
           uwsgi.AddTimer(17, 3)

           uwsgi.RegisterSignal(30, "mule1", hello2)
           uwsgi.AddRbTimer(30, 5)
   }

   func foofork() {
      fmt.Println("fork() has been called")
   }

   func main() {
           uwsgi.PostInit(postinit)
           uwsgi.PostFork(foofork)
           uwsgi.Run()
   }


The PostInit() function set the 'hook' to be called after the Go initialization
is complete.  The PostFork() function set the 'hook' to be called after each
fork() In postinit hook we register two uwsgi signals, with the second one
being run in a mule (the mule1) To run the code just build your new app as
above and execute it

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   master = true
   processes = 2
   goroutines = 20
   mules = 2
   memory-report = true

This time we have added memory-report, try it to see how memory-cheap Go apps
can be.

Running from the Emperor
************************

If you are running in Emperor mode, you can run uWSGI-Go apps by using the
``privileged-binary-patch`` option.  Your vassal configuration should be
something like this.

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   master = true
   processes = 2
   goroutines = 20
   mules = 2
   memory-report = true
   uid = foobar
   gid = foobar
   privileged-binary-patch = /tmp/bin/helloworld

(Obviously change ``/tmp/bin/helloworld`` to wherever your app lives...)

Notes
*****

* A series of interesting go examples can be found in the ``t/go`` directory of
  the uWSGI source distribution.
* Changing process names is currently not possible without modifying the go core
* You cannot use uWSGI native threads with Go (just use --goroutines)
* Only a little part of the uWSGI API has been exposed so far. If you want to
  hack on it or need more, just edit the uwsgi.go file in the
  plugins/go/src/uwsgi directory
* Goroutines require the async mode (if you are customizing your uWSGI library
  remember to always include it)
* It looks like it is possible to load the Python, Lua and PSGI plugins without
  problems even in goroutines mode (more tests needed)
