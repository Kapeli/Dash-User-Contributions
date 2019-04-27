Quickstart for Python/WSGI applications
=======================================

This quickstart will show you how to deploy simple WSGI applications and common web frameworks.

Python here is meant as CPython, for PyPy you need to use the specific plugin: :doc:`PyPy`, Jython support is under construction.

.. note::

    You need at least uWSGI 1.4 to follow the quickstart. Anything older is no longer maintained and is highly buggy!

Installing uWSGI with Python support
************************************

.. tip::

    When you start learning uWSGI, try to build from official sources: using distribution-supplied packages may bring you
    plenty of headaches. When things are clear, you can use modular builds (like the ones available in your distribution).

uWSGI is a (big) C application, so you need a C compiler (like gcc or clang) and the Python development headers.

On a Debian-based distro an

.. code-block:: sh

   apt-get install build-essential python-dev

will be enough.

You have various ways to install uWSGI for Python:

* via pip

  .. code-block:: sh

      pip install uwsgi

* using the network installer

  .. code-block:: sh

      curl http://uwsgi.it/install | bash -s default /tmp/uwsgi

  (this will install the uWSGI binary into ``/tmp/uwsgi``, feel free to change it).

* via downloading a source tarball and "making" it

  .. code-block:: sh

      wget https://projects.unbit.it/downloads/uwsgi-latest.tar.gz
      tar zxvf uwsgi-latest.tar.gz
      cd <dir>
      make

  (after the build you will have a ``uwsgi`` binary in the current directory).

Installing via your package distribution is not covered (would be impossible to make everyone happy), but all of the general rules apply.

One thing you may want to take into account when testing this quickstart with distro-supplied packages, is that very probably your distribution
has built uWSGI in modular way (every feature is a different plugin that must be loaded). To complete this quickstart,
you have to prepend ``--plugin python,http`` to the first series of examples, and ``--plugin python`` when the HTTP router is removed (if this
doesn't make sense to you, just continue reading).

The first WSGI application
**************************

Let's start with a simple "Hello World" example:

.. code-block:: python

   def application(env, start_response):
       start_response('200 OK', [('Content-Type','text/html')])
       return [b"Hello World"]

(save it as ``foobar.py``).

As you can see, it is composed of a single Python function. It is called "application" as this is the default function
that the uWSGI Python loader will search for (but you can obviously customize it).

Deploy it on HTTP port 9090
***************************

Now start uWSGI to run an HTTP server/router passing requests to your WSGI application:

.. code-block:: sh

   uwsgi --http :9090 --wsgi-file foobar.py

That's all.

.. note:: Do not use ``--http`` when you have a frontend webserver or you are doing some form of benchmark, use ``--http-socket``. Continue reading the quickstart to understand why.


Adding concurrency and monitoring
*********************************

The first tuning you would like to make is adding concurrency (by default uWSGI starts with a single process and a single thread).

You can add more processes with the ``--processes`` option or more threads with the ``--threads`` option (or you can have both).

.. code-block:: sh

   uwsgi --http :9090 --wsgi-file foobar.py --master --processes 4 --threads 2

This will spawn 4 processes (each with 2 threads), a master process (will respawn your processes when they die) and the HTTP router (seen before).

One important task is monitoring. Understanding what is going on is vital in production deployment. The stats subsystem allows
you to export uWSGI's internal statistics as JSON:

.. code-block:: sh

   uwsgi --http :9090 --wsgi-file foobar.py --master --processes 4 --threads 2 --stats 127.0.0.1:9191

Make some request to your app and then telnet to the port 9191, you'll get lots of fun information. You may want to use
"uwsgitop" (just ``pip install`` it), which is a top-like tool for monitoring instances.

.. attention::

    Bind the stats socket to a private address (unless you know what you are doing), otherwise everyone could access it!

Putting behind a full webserver
*******************************

Even though uWSGI HTTP router is solid and high-performance, you may want to put your application behind a fully-capable webserver.

uWSGI natively speaks HTTP, FastCGI, SCGI and its specific protocol named "uwsgi" (yes, wrong naming choice).
The best performing protocol is obviously uwsgi, already supported by nginx and Cherokee (while various Apache modules are available).

A common nginx config is the following:

.. code-block:: c

   location / {
       include uwsgi_params;
       uwsgi_pass 127.0.0.1:3031;
   }

This means "pass every request to the server bound to port 3031 speaking the uwsgi protocol".

Now we can spawn uWSGI to natively speak the uwsgi protocol:

.. code-block:: sh

   uwsgi --socket 127.0.0.1:3031 --wsgi-file foobar.py --master --processes 4 --threads 2 --stats 127.0.0.1:9191

If you'll run ``ps aux``, you will see one process less. The HTTP router has been removed as our "workers" (the processes assigned to uWSGI)
natively speak the uwsgi protocol.

If your proxy/webserver/router speaks HTTP, you have to tell uWSGI to natively speak the http protocol (this is different from --http that will spawn a proxy by itself):

.. code-block:: sh

   uwsgi --http-socket 127.0.0.1:3031 --wsgi-file foobar.py --master --processes 4 --threads 2 --stats 127.0.0.1:9191

Automatically starting uWSGI on boot
************************************

If you are thinking about firing up vi and writing an init.d script for spawning uWSGI, just sit (and calm) down and make sure your system doesn't offer a better (more modern) approach first.

Each distribution has chosen a startup system (:doc:`Upstart<Upstart>`, :doc:`Systemd`...) and there are tons of process managers available (supervisord, god, monit, circus...).

uWSGI will integrate very well with all of them (we hope), but if you plan to deploy a big number of apps check the uWSGI :doc:`Emperor<Emperor>` - it is more or less the dream of every devops engineer.

Deploying Django
****************

Django is very probably the most used Python web framework around. Deploying it is pretty easy (we continue our configuration with 4 processes with 2 threads each).

We suppose the Django project is in ``/home/foobar/myproject``:

.. code-block:: sh

   uwsgi --socket 127.0.0.1:3031 --chdir /home/foobar/myproject/ --wsgi-file myproject/wsgi.py --master --processes 4 --threads 2 --stats 127.0.0.1:9191

(with ``--chdir`` we move to a specific directory). In Django this is required to correctly load modules.

Argh! What the hell is this?! Yes, you're right, you're right... dealing with such long command lines is unpractical, foolish and error-prone.
Never fear! uWSGI supports various configuration styles. In this quickstart we will use .ini files.

.. code-block:: ini

    [uwsgi]
    socket = 127.0.0.1:3031
    chdir = /home/foobar/myproject/
    wsgi-file = myproject/wsgi.py
    processes = 4
    threads = 2
    stats = 127.0.0.1:9191

A lot better!

Just run it:

.. code-block:: sh

   uwsgi yourfile.ini

If the file ``/home/foobar/myproject/myproject/wsgi.py`` (or whatever you have called your project) does not exist, you are very probably
using an old (< 1.4) version of Django. In such a case you need a little bit more configuration:

.. code-block:: sh

   uwsgi --socket 127.0.0.1:3031 --chdir /home/foobar/myproject/ --pythonpath .. --env DJANGO_SETTINGS_MODULE=myproject.settings --module "django.core.handlers.wsgi:WSGIHandler()" --processes 4 --threads 2 --stats 127.0.0.1:9191

Or, using the .ini file:

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   chdir = /home/foobar/myproject/
   pythonpath = ..
   env = DJANGO_SETTINGS_MODULE=myproject.settings
   module = django.core.handlers.wsgi:WSGIHandler()
   processes = 4
   threads = 2
   stats = 127.0.0.1:9191

Older (< 1.4) Django releases need to set ``env``, ``module`` and the ``pythonpath`` (``..`` allow us to reach
the ``myproject.settings`` module).


Deploying Flask
***************

Flask is a popular Python web microframework.

Save the following example as ``myflaskapp.py``:

.. code-block:: python

   from flask import Flask

   app = Flask(__name__)

   @app.route('/')
   def index():
       return "<span style='color:red'>I am app 1</span>"

Flask exports its WSGI function (the one we called "application" at the beginning of this quickstart) as "app", so we need to instruct uWSGI to use it.
We still continue to use the 4 processes/2 threads and the uwsgi socket as the base:

.. code-block:: sh

   uwsgi --socket 127.0.0.1:3031 --wsgi-file myflaskapp.py --callable app --processes 4 --threads 2 --stats 127.0.0.1:9191

(the only addition is the ``--callable`` option).

Deploying web2py
****************

Again a popular choice. Unzip the web2py source distribution on a directory of choice and write a uWSGI config file:

.. code-block:: ini

   [uwsgi]
   http = :9090
   chdir = path_to_web2py
   module = wsgihandler
   master = true
   processes = 8

.. note::

    On recent web2py releases you may need to copy the ``wsgihandler.py`` script out of the ``handlers`` directory.

We used the HTTP router again. Just go to port 9090 with your browser and you will see the web2py welcome page.

Click on the administrative interface and... oops, it does not work as it requires HTTPS. Do not worry, the uWSGI router
is HTTPS-capable (be sure you have OpenSSL development headers: install them and rebuild uWSGI, the build system
will automatically detect it).

First of all generate your key and certificate:

.. code-block:: sh

   openssl genrsa -out foobar.key 2048
   openssl req -new -key foobar.key -out foobar.csr
   openssl x509 -req -days 365 -in foobar.csr -signkey foobar.key -out foobar.crt

Now you have 2 files (well 3, counting the ``foobar.csr``), ``foobar.key`` and ``foobar.crt``. Change the uWSGI config:

.. code-block:: ini

   [uwsgi]
   https = :9090,foobar.crt,foobar.key
   chdir = path_to_web2py
   module = wsgihandler
   master = true
   processes = 8

Re-run uWSGI and connect to port 9090 using ``https://`` with your browser.

A note on Python threads
************************

If you start uWSGI without threads, the Python GIL will not be enabled, so threads generated by your application
will never run. You may not like that choice, but remember that uWSGI is a language-independent server, so most of its choices
are for maintaining it "agnostic".

But do not worry, there are basically no choices made by the uWSGI developers that cannot be changed with an option.

If you want to maintain Python threads support without starting multiple threads for your application, just add
the ``--enable-threads`` option (or ``enable-threads = true`` in ini style).

Virtualenvs
***********

uWSGI can be configured to search for Python modules in a specific virtualenv.

Just add ``virtualenv = <path>`` to your options.

Security and availability
*************************

**Always** avoid running your uWSGI instances as root. You can drop privileges using the ``uid`` and ``gid`` options:

.. code-block:: ini

   [uwsgi]
   https = :9090,foobar.crt,foobar.key
   uid = foo
   gid = bar
   chdir = path_to_web2py
   module = wsgihandler
   master = true
   processes = 8

If you need to bind to privileged ports (like 443 for HTTPS), use shared sockets. They are created before dropping
privileges and can be referenced with the ``=N`` syntax, where ``N`` is the socket number (starting from 0):

.. code-block:: ini

   [uwsgi]
   shared-socket = :443
   https = =0,foobar.crt,foobar.key
   uid = foo
   gid = bar
   chdir = path_to_web2py
   module = wsgihandler
   master = true
   processes = 8

A common problem with webapp deployment is "stuck requests". All of your threads/workers are stuck (blocked on request) and your app cannot accept more requests.
To avoid that problem you can set a ``harakiri`` timer. It is a monitor (managed by the master process) that will destroy processes stuck for more than the specified number of seconds (choose ``harakiri`` value carefully). For example, you may want to destroy workers blocked for more than 30 seconds:

.. code-block:: ini

   [uwsgi]
   shared-socket = :443
   https = =0,foobar.crt,foobar.key
   uid = foo
   gid = bar
   chdir = path_to_web2py
   module = wsgihandler
   master = true
   processes = 8
   harakiri = 30

In addition to this, since uWSGI 1.9, the stats server exports the whole set of request variables, so you can see (in realtime) what your instance is doing (for each worker, thread or async core).


Offloading
**********

:doc:`OffloadSubsystem` allows you to free your workers as soon as possible when some specific pattern matches and can be delegated
to a pure-c thread. Examples are sending static file from the file system, transferring data from the network to the client and so on.

Offloading is very complex, but its use is transparent to the end user. If you want to try just add ``--offload-threads <n>`` where <n> is the number of threads to spawn (1 per CPU is a good value to start with).

When offload threads are enabled, all of the parts that can be optimized will be automatically detected.

Bonus: multiple Python versions for the same uWSGI binary
*********************************************************

As we have seen, uWSGI is composed of a small core and various plugins. Plugins can be embedded in the binary or loaded dynamically. When you build uWSGI for Python, a series of plugins plus the Python one are embedded in the final binary.

This could be a problem if you want to support multiple Python versions without building a binary for each one.

The best approach would be having a little binary with the language-independent features built in, and one plugin for each Python version that will be loaded on-demand.

In the uWSGI source directory:

.. code-block:: sh

   make PROFILE=nolang
   
This will build a uwsgi binary with all the default plugins built-in except the Python one.

Now, from the same directory, we start building Python plugins:

.. code-block:: sh

   PYTHON=python3.4 ./uwsgi --build-plugin "plugins/python python34"
   PYTHON=python2.7 ./uwsgi --build-plugin "plugins/python python27"
   PYTHON=python2.6 ./uwsgi --build-plugin "plugins/python python26"

You will end up with three files: ``python34_plugin.so``, ``python27_plugin.so``, ``python26_plugin.so``. Copy these into your desired directory. (By default, uWSGI searches for plugins in the current working directory.)

Now in your configurations files you can simply add (at the very top) the `plugins-dir` and `plugin` directives.

.. code-block:: ini

   [uwsgi]
   plugins-dir = <path_to_your_plugin_directory>
   plugin = python26
   
This will load the ``python26_plugin.so`` plugin library from the directory into which you copied the plugins.

And now...
**********

You should already be able to go into production with such few concepts, but uWSGI is an enormous project with hundreds of features
and configurations. If you want to be a better sysadmin, continue reading the full docs.
