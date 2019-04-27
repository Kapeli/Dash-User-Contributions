Quickstart for perl/PSGI applications
=====================================


The following instructions will guide you through installing and running a perl-based uWSGI distribution, aimed at running PSGI apps.


Installing uWSGI with Perl support
**********************************

To build uWSGI you need a c compiler (gcc and clang are supported) and the python binary (it will only run the uwsgiconfig.py script that will execute the various
compilation steps). As we are building a uWSGI binary with perl support we need perl development headers too (libperl-dev package on debian-based distros)

You can build uWSGI manually:

.. code-block:: sh

   python uwsgiconfig.py --build psgi
   
that is the same as


.. code-block:: sh

   UWSGI_PROFILE=psgi make
   
or using the network installer:

.. code-block:: sh

   curl http://uwsgi.it/install | bash -s psgi /tmp/uwsgi
   
that will create a uWSGI binary in /tmp/uwsgi (feel free to change the path to whatever you want)

Note for distro packages
************************

You distribution very probably contains a uWSGI package set. Those uWSGI packages tend to be highly modulars, so in addition to the core you need to install
the required plugins. Plugins must be loaded in your configs. In the learning phase we strongly suggest to not use distribution packages to easily follow documentation and tutorials.

Once you feel comfortable with the "uWSGI way" you can choose the best approach for your deployments.

Your first PSGI app
*******************

save it to a file named myapp.pl

.. code-block:: pl

   my $app = sub {
        my $env = shift;
        return [
                '200',
                [ 'Content-Type' => 'text/html' ],
                [ "<h1>Hello World</h1>" ],
        ];
   };

then run it via uWSGI in http mode:

.. code-block:: sh

   uwsgi --http :8080 --http-modifier1 5 --psgi myapp.pl

(remember to replace 'uwsgi' if it is not in your current $PATH)

or if you are using a modular build (like the one of your distro)

.. code-block:: sh

   uwsgi --plugins http,psgi --http :8080 --http-modifier1 5 --psgi myapp.pl
   
.. note:: Do not use --http when you have a frontend webserver, use --http-socket. Continue reading the quickstart to understand why.

What is that '--http-modifier1 5' thing ???
*******************************************

uWSGI supports various languages and platform. When the server receives a request it has to know where to 'route' it.

Each uWSGI plugin has an assigned number (the modifier), the perl/psgi one has the 5. So --http-modifier1 5 means "route to the psgi plugin"

Albeit uWSGI has a more "human-friendly" :doc:`internal routing system <InternalRouting>` using modifiers is the fastest way, so, if possible always use them


Using a full webserver: nginx
*****************************

The supplied http router, is (yes, incredible) only a router. You can use it as a load balancer or a proxy, but if you need a full webserver (for efficiently serving static files or all of those task a webserver is good at), you can get rid of the uwsgi http router (remember to change --plugins http,psgi to --plugins psgi if you are using a modular build) and put your app behind nginx.

To communicate with nginx, uWSGI can use various protocol: http, uwsgi, fastcgi, scgi...

The most efficient one is the uwsgi one. Nginx includes uwsgi protocol support out of the box.

Run your psgi application on a uwsgi socket:

.. code-block:: sh

   uwsgi --socket 127.0.0.1:3031 --psgi myapp.pl

then add a location stanza in your nginx config


.. code-block:: c

   location / {
       include uwsgi_params;
       uwsgi_pass 127.0.0.1:3031;
       uwsgi_modifier1 5;
   }

Reload your nginx server, and it should start proxying requests to your uWSGI instance

Note that you do not need to configure uWSGI to set a specific modifier, nginx will do it using the ``uwsgi_modifier1 5;`` directive

If your proxy/webserver/router speaks HTTP, you have to tell uWSGI to natively speak the http protocol (this is different from --http that will spawn a proxy by itself):

.. code-block:: sh

   uwsgi --http-socket 127.0.0.1:3031 --http-socket-modifier1 5 --psgi myapp.pl
   
as you can see we needed to specify the modifier1 to use, as the http protocol cannot carry this kind of information


Adding concurrency
******************

You can give concurrency to to your app via multiprocess,multithreading or various async modes.

To spawn additional processes use the --processes option

.. code-block:: sh

   uwsgi --socket 127.0.0.1:3031 --psgi myapp.pl --processes 4

To have additional threads use --threads

.. code-block:: sh

   uwsgi --socket 127.0.0.1:3031 --psgi myapp.pl --threads 8

Or both if you feel exotic

.. code-block:: sh

   uwsgi --socket 127.0.0.1:3031 --psgi myapp.pl --threads 8 --processes 4
   
A very common non-blocking/coroutine library in the perl world is Coro::AnyEvent. uWSGI can use it (even combined with multiprocessing) simply including the ``coroae`` plugin.

To build a uWSGI binary with ``coroae`` support just run

.. code-block:: sh

   UWSGI_PROFILE=coroae make
   
or

.. code-block:: sh

   curl http://uwsgi.it/install | bash -s coroae /tmp/uwsgi
   
you will end with a uWSGI binary including both the ``psgi`` and ``coroae`` plugins.

Now run your application in Coro::AnyEvent mode:


.. code-block:: sh

   uwsgi --socket 127.0.0.1:3031 --psgi myapp.pl --coroae 1000 --processes 4
   
it will run 4 processes each able to manage up to 1000 coroutines (or Coro microthreads).


Adding robustness: the Master process
*************************************

It is highly recommended to have the master process always running on productions apps.

It will constantly monitor your processes/threads and will add funny features like the :doc:`StatsServer`

To enable the master simply add --master

.. code-block:: sh

   uwsgi --socket 127.0.0.1:3031 --psgi myapp.pl --processes 4 --master
   
Using config files
******************

uWSGI has literally hundreds of options. Dealing with them via command line is basically silly, so try to always use config files.
uWSGI supports various standards (xml, .ini, json, yaml...). Moving from one to another is pretty simple. The same options you can use via command line can be used
on config files simply removing the ``--`` prefix:

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   psgi = myapp.pl
   processes = 4
   master = true
   
or xml:

.. code-block:: xml

   <uwsgi>
     <socket>127.0.0.1:3031</socket>
     <psgi>myapp.pl</psgi>
     <processes>4</processes>
     <master/>
   </uwsgi>
   
To run uWSGI using a config file, just specify it as argument:

.. code-block:: sh

   uwsgi yourconfig.ini
   
if for some reason your config cannot end with the expected extension (.ini, .xml, .yml, .js) you can force the binary to
use a specific parser in this way:

.. code-block:: sh

   uwsgi --ini yourconfig.foo
   
.. code-block:: sh

   uwsgi --xml yourconfig.foo

.. code-block:: sh

   uwsgi --yaml yourconfig.foo

and so on

You can even pipe configs (using the dash to force reading from stdin):

.. code-block:: sh

   perl myjsonconfig_generator.pl | uwsgi --json -

Accessing uWSGI options within application code
***********************************************

uWSGI options can be accessed within application code via ``uwsgi::opt``.

.. code-block:: pl

   my $uwsgi_opt = uwsgi::opt;
   print $uwsgi_opt->{'http'};

Automatically starting uWSGI on boot
************************************

If you are thinking about writing some init.d script for spawning uWSGI, just sit (and calm) down and check if your system does not offer you a better (more modern) approach.

Each distribution has chosen a startup system (:doc:`Upstart<Upstart>`, :doc:`Systemd`...) and there are tons of process managers available (supervisord, god...).

uWSGI will integrate very well with all of them (we hope), but if you plan to deploy a big number of apps check the uWSGI :doc:`Emperor<Emperor>`
it is the dream of every devops.

Security and availability
*************************

ALWAYS avoid running your uWSGI instances as root. You can drop privileges using the uid and gid options

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   uid = foo
   gid = bar
   chdir = path_toyour_app
   psgi = myapp.pl
   master = true
   processes = 8


A common problem with webapp deployment is "stuck requests". All of your threads/workers are stuck blocked on a request and your app cannot accept more of them.

To avoid that problem you can set an ``harakiri`` timer. It is a monitor (managed by the master process) that will destroy processes stuck for more than the specified number of seconds

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   uid = foo
   gid = bar
   chdir = path_toyour_app
   psgi = myapp.pl
   master = true
   processes = 8
   harakiri = 30

will destroy workers blocked for more than 30 seconds. Choose carefully the harakiri value !!!

In addition to this, since uWSGI 1.9, the stats server exports the whole set of request variables, so you can see (in realtime) what your instance is doing (for each worker, thread or async core)

Enabling the stats server is easy:

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   uid = foo
   gid = bar
   chdir = path_toyour_app
   psgi = myapp.pl
   master = true
   processes = 8
   harakiri = 30
   stats = 127.0.0.1:5000
   
just bind it to an address (UNIX or TCP) and just connect (you can use telnet too) to it to receive a JSON representation of your instance.

The ``uwsgitop`` application (you can find it in the official github repository) is an example of using the stats server to have a top-like realtime monitoring tool (with colors !!!)


Offloading
**********

:doc:`OffloadSubsystem` allows you to free your workers as soon as possible when some specific pattern matches and can be delegated
to a pure-c thread. Examples are sending static file from the filesystem, transferring data from the network to the client and so on.

Offloading is very complex, but its use is transparent to the end user. If you want to try just add --offload-threads <n> where <n> is the number of threads to spawn (one for cpu is a good value).

When offload threads are enabled, all of the parts that can be optimized will be automatically detected.


And now
*******

You should already be able to go in production with such few concepts, but uWSGI is an enormous project with hundreds of features
and configurations. If you want to be a better sysadmin, continue reading the full docs.
