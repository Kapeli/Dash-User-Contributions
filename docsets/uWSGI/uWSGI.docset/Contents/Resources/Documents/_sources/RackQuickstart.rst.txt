Quickstart for ruby/Rack applications
=====================================

The following instructions will guide you through installing and running a Ruby-based uWSGI distribution aimed at running Rack apps.

Installing uWSGI with Ruby support
**********************************

To build uWSGI you need a C compiler (gcc and clang are supported) and the Python binary (to run the uwsgiconfig.py script that will execute the various compilation steps).

As we are building an uWSGI binary with Ruby support we need the Ruby development headers too (the ``ruby-dev`` package on Debian-based distributions).

You can build uWSGI manually -- all of these are equivalent:

.. code-block:: sh

   make rack
   UWSGI_PROFILE=rack make
   make PROFILE=rack
   python uwsgiconfig.py --build rack
   
But if you are lazy, you can download, build and install an uWSGI + Ruby binary in a single shot:

.. code-block:: sh

   curl http://uwsgi.it/install | bash -s rack /tmp/uwsgi
   
Or in a more "Ruby-friendly" way:

.. code-block:: sh

   gem install uwsgi
   
All of these methods build a "monolithic" uWSGI binary.
The uWSGI project is composed by dozens of plugins. You can choose to build the server core and having a plugin for every feature (that you will load when needed),
or you can build a single binary with all the features you need. This latter kind of build is called 'monolithic'.

This quickstart assumes a monolithic binary (so you do not need to load plugins).
If you prefer to use your package distributions (instead of building uWSGI from official sources), see below.

Note for distro packages
************************

Your distribution very probably contains an uWSGI package set. Those uWSGI packages tend to be highly modular (and occasionally highly outdated),
so in addition to the core you need to install the required plugins. Plugins must be loaded in your uWSGI configuration.
In the learning phase we strongly suggest to not use distribution packages to easily follow documentation and tutorials.

Once you feel comfortable with the "uWSGI way" you can choose the best approach for your deployments.

As an example, the tutorial makes use of the "http" and "rack" plugins. If you are using a modular build be sure to load them with the ``--plugins http,rack`` option.

Your first Rack app
*******************

Rack is the standard way for writing Ruby web apps.

This is a standard Rack Hello world script (call it app.ru):

.. code-block:: rb

   class App

     def call(environ)
       [200, {'Content-Type' => 'text/html'}, ['Hello']]
     end
     
   end
   
   run App.new
   
The ``.ru`` extension stands for "rackup", which is the deployment tool included in the Rack distribution.
Rackup uses a little DSL, so to use it into uWSGI you need to install the rack gem:

.. code-block:: sh

   gem install rack
   
Now we are ready to deploy with uWSGI:

.. code-block:: sh

   uwsgi --http :8080 --http-modifier1 7 --rack app.ru

(remember to replace ‘uwsgi’ if it is not in your current $PATH)

or if you are using a modular build (like the one of your distribution)

.. code-block:: sh

   uwsgi --plugins http,rack --http :8080 --http-modifier1 7 --rack app.ru
   
With this command line we've spawned an HTTP proxy routing each request to a process (named the 'worker') that manages it and send back the response to the HTTP router (that sends back to the client).

If you are asking yourself why spawning two processes, it is because this is the normal architecture you will use in production (a frontline web server with a backend application server).

If you do not want to spawn the HTTP proxy and directly force the worker to answer HTTP requests just change the command line to

.. code-block:: sh

   uwsgi --http-socket :8080 --http-socket-modifier1 7 --rack app.ru
   
now you have a single process managing requests (but remember that directly exposing the application server to the public is generally dangerous and less versatile).

What is that '--http-modifier1 7' thing?
****************************************

uWSGI supports various languages and platforms. When the server receives a request it has to know where to 'route' it.

Each uWSGI plugin has an assigned number (the modifier), the ruby/rack one has the 7. So ``--http-modifier1 7`` means "route to the rack plugin".

Though uWSGI also has a more "human-friendly" :doc:`internal routing system <InternalRouting>` using modifiers is the fastest way, so if at all possible always use them.

Using a full webserver: nginx
*****************************

The supplied HTTP router, is (yes, astoundingly enough) only a router.
You can use it as a load balancer or a proxy, but if you need a full web server (for efficiently serving static files or all of those task a webserver is good at),
you can get rid of the uwsgi HTTP router (remember to change --plugins http,rack to --plugins rack if you are using a modular build) and put your app behind Nginx.

To communicate with Nginx, uWSGI can use various protocol: HTTP, uwsgi, FastCGI, SCGI, etc.

The most efficient one is the uwsgi one. Nginx includes uwsgi protocol support out of the box.

Run your rack application on an uwsgi socket:

.. code-block:: sh

   uwsgi --socket 127.0.0.1:3031 --rack app.ru

then add a location stanza in your nginx config

.. code-block:: c

   location / {
       include uwsgi_params;
       uwsgi_pass 127.0.0.1:3031;
       uwsgi_modifier1 7;
   }

Reload your nginx server, and it should start proxying requests to your uWSGI instance.

Note that you do not need to configure uWSGI to set a specific modifier, nginx will do it using the ``uwsgi_modifier1 5;`` directive.

Adding concurrency
******************

With the previous example you deployed a stack being able to serve a single request at time.

To increase concurrency you need to add more processes.
If you are hoping there is a magic math formula to find the right number of processes to spawn, well... we're sorry.
You need to experiment and monitor your app to find the right value.
Take in account every single process is a complete copy of your app, so memory usage should be taken in account.

To add more processes just use the `--processes <n>` option:

.. code-block:: sh

   uwsgi --socket 127.0.0.1:3031 --rack app.ru --processes 8
   
will spawn 8 processes.

Ruby 1.9/2.0 introduced an improved threads support and uWSGI supports it via the 'rbthreads' plugin. This plugin is automatically
built when you compile the uWSGI+ruby (>=1.9) monolithic binary.

To add more threads:

.. code-block:: sh

   uwsgi --socket 127.0.0.1:3031 --rack app.ru --rbthreads 4
   
or threads + processes

.. code-block:: sh

   uwsgi --socket 127.0.0.1:3031 --rack app.ru --processes --rbthreads 4
   
There are other (generally more advanced/complex) ways to increase concurrency (for example 'fibers'), but most of the time
you will end up with a plain old multi-process or multi-thread models. If you are interested, check the complete documentation over at :doc:`Rack`.

Adding robustness: the Master process
*************************************

It is highly recommended to have the uWSGI master process always running on productions apps.

It will constantly monitor your processes/threads and will add fun features like the :doc:`StatsServer`.

To enable the master simply add ``--master``

.. code-block:: sh

   uwsgi --socket 127.0.0.1:3031 --rack app.ru --processes 4 --master
   
Using config files
******************

uWSGI has literally hundreds of options (but generally you will not use more than a dozens of them). Dealing with them via command line is basically silly, so try to always use config files.

uWSGI supports various standards (XML, INI, JSON, YAML, etc). Moving from one to another is pretty simple.
The same options you can use via command line can be used with config files by simply removing the ``--`` prefix:

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   rack = app.ru
   processes = 4
   master = true
   
or xml:

.. code-block:: xml

   <uwsgi>
     <socket>127.0.0.1:3031</socket>
     <rack>app.ru</rack>
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

and so on.

You can even pipe configs (using the dash to force reading from stdin):

.. code-block:: sh

   ruby myjsonconfig_generator.rb | uwsgi --json -
   
The fork() problem when you spawn multiple processes
****************************************************

uWSGI is "Perlish" in a way, there is nothing we can do to hide that. Most of its choices (starting from "There's more than one way to do it") came from the Perl world (and more generally from classical UNIX sysadmin approaches).

Sometimes this approach could lead to unexpected behaviors when applied to other languages/platforms.

One of the "problems" you can face when starting to learn uWSGI is its ``fork()`` usage.

By default uWSGI loads your application in the first spawned process and then ``fork()`` itself multiple times.

It means your app is loaded a single time and then copied.

While this approach speedups the start of the server, some application could have problems with this technique (especially those initializing db connections
on startup, as the file descriptor of the connection will be inherited in the subprocesses).

If you are unsure about the brutal preforking used by uWSGI, just disable it with the ``--lazy-apps`` option. It will force uWSGI to completely load
your app one time per each worker.

Deploying Sinatra
*****************

Let's forget about fork(), and back to fun things. This time we're deploying a Sinatra application:

.. code-block:: rb

   require 'sinatra'

   get '/hi' do
     "Hello World"
   end

   run Sinatra::Application
   
save it as ``config.ru`` and run as seen before:

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   rack = config.ru
   master = true
   processes = 4
   lazy-apps = true
   
.. code-block:: sh

   uwsgi yourconf.ini
   
Well, maybe you already noted that basically nothing changed from the previous app.ru examples.

That is because basically every modern Rack app exposes itself as a .ru file (generally called config.ru), so there is no need
for multiple options for loading applications (like for example in the Python/WSGI world).

Deploying RubyOnRails >= 3
**************************

Starting from 3.0, Rails is fully Rack compliant, and exposes a config.ru file you can directly load (like we did with Sinatra).

The only difference from Sinatra is that your project has a specific layout/convention expecting your current working directory is the one containing the project, so let's add a chdir option:

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   rack = config.ru
   master = true
   processes = 4
   lazy-apps = true
   chdir = <path_to_your_rails_app>
   env = RAILS_ENV=production
   
.. code-block:: sh

   uwsgi yourconf.ini
   
In addition to chdir we have added the 'env' option that set the ``RAILS_ENV`` environment variable.

Starting from 4.0, Rails support multiple threads (only for ruby 2.0):

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   rack = config.ru
   master = true
   processes = 4
   rbthreads = 2
   lazy-apps = true
   chdir = <path_to_your_rails_app>
   env = RAILS_ENV=production

Deploying older RubyOnRails
***************************

Older Rails versions are not fully Rack-compliant. For such a reason a specific option is available in uWSGI to load older Rails apps (you will need the 'thin' gem too).

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   master = true
   processes = 4
   lazy-apps = true
   rails = <path_to_your_rails_app>
   env = RAILS_ENV=production
   
So, in short, specify the ``rails`` option, passing the rails app directory as the argument, instead of a Rackup file.

Bundler and RVM
***************

Bundler is the standard de-facto Ruby tool for managing dependencies. Basically you specify the gems needed by your app in the Gemfile text file and then you launch bundler to install them.

To allow uWSGI to honor bundler installations you only need to add:

.. code-block:: ini

   rbrequire = rubygems
   rbrequire = bundler/setup
   env = BUNDLE_GEMFILE=<path_to_your_Gemfile>

(The first require stanza is not required for ruby 1.9/2.x.)

Basically those lines force uWSGI to load the bundler engine and to use the Gemfile specified in the ``BUNDLE_GEMFILE`` environment variable.

When using Bundler (like modern frameworks do) your common deployment configuration will be:

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   rack = config.ru
   master = true
   processes = 4
   lazy-apps = true
   rbrequire = rubygems
   rbrequire = bundler/setup
   env = BUNDLE_GEMFILE=<path_to_your_Gemfile>
   
In addition to Bundler, RVM is another common tool.

It allows you to have multiple (independent) Ruby installations (with their gemsets) on a single system.

To instruct uWSGI to use the gemset of a specific RVM version just use the `--gemset` option:

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   rack = config.ru
   master = true
   processes = 4
   lazy-apps = true
   rbrequire = rubygems
   rbrequire = bundler/setup
   env = BUNDLE_GEMFILE=<path_to_your_Gemfile>
   gemset = ruby-2.0@foobar
   
Just pay attention you need a uWSGI binary (or a plugin if you are using a modular build) for every Ruby version (that's Ruby version, not gemset!).

If you are interested, this is a list of commands to build the uWSGI core + 1 one plugin per every Ruby version installed in rvm:

.. code-block:: sh

   # build the core
   make nolang
   # build plugin for 1.8.7
   rvm use 1.8.7
   ./uwsgi --build-plugin "plugins/rack rack187"
   # build for 1.9.2
   rvm use 1.9.2
   ./uwsgi --build-plugin "plugins/rack rack192"
   # and so on...
   
Then if you want to use ruby 1.9.2 with the @oops gemset:

.. code-block:: ini

   [uwsgi]
   plugins = ruby192
   socket = 127.0.0.1:3031
   rack = config.ru
   master = true
   processes = 4
   lazy-apps = true
   rbrequire = rubygems
   rbrequire = bundler/setup
   env = BUNDLE_GEMFILE=<path_to_your_Gemfile>
   gemset = ruby-1.9.2@oops

Automatically starting uWSGI on boot
************************************

If you are thinking about firing up vi and writing an init.d script for spawning uWSGI, just sit (and calm) down and make sure your system doesn't offer a better (more modern) approach first.

Each distribution has chosen a startup system (:doc:`Upstart<Upstart>`, :doc:`Systemd`...) and there are tons of process managers available (supervisord, god, monit, circus...).

uWSGI will integrate very well with all of them (we hope), but if you plan to deploy a big number of apps check the uWSGI :doc:`Emperor<Emperor>` - it is more or less the dream of every devops engineer.

Security and availability
*************************

ALWAYS avoid running your uWSGI instances as root. You can drop privileges using the uid and gid options.

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   uid = foo
   gid = bar
   chdir = path_toyour_app
   rack = app.ru
   master = true
   processes = 8


A common problem with webapp deployment is "stuck requests". All of your threads/workers are stuck blocked on a request and your app cannot accept more of them.

To avoid that problem you can set an ``harakiri`` timer. It is a monitor (managed by the master process) that will destroy processes stuck for more than the specified number of seconds.

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   uid = foo
   gid = bar
   chdir = path_toyour_app
   rack = app.ru
   master = true
   processes = 8
   harakiri = 30

This will destroy workers blocked for more than 30 seconds. Choose the harakiri value carefully!

In addition to this, since uWSGI 1.9, the stats server exports the whole set of request variables, so you can see (in real time) what your instance is doing (for each worker, thread or async core)

Enabling the stats server is easy:

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   uid = foo
   gid = bar
   chdir = path_to_your_app
   rack = app.ru
   master = true
   processes = 8
   harakiri = 30
   stats = 127.0.0.1:5000
   
just bind it to an address (UNIX or TCP) and just connect (you can use telnet too) to it to receive a JSON representation of your instance.

The ``uwsgitop`` application (you can find it in the official github repository) is an example of using the stats server to have a top-like realtime monitoring tool (with fancy colors!)

Memory usage
************

Low memory usage is one of the selling point of the whole uWSGI project.

Unfortunately being aggressive with memory by default could (read well: could) lead to some performance problems.

By default the uWSGI Rack plugin calls the Ruby GC (garbage collector) after every request. If you want to reduce this rate just add the ``--rb-gc-freq <n>`` option, where n is the number of requests after the GC is called.

If you plan to make benchmarks of uWSGI (or compare it with other solutions) take in account its use of GC.

Ruby can be a real memory devourer, so we prefer to be aggressive with memory by default instead of making hello-world benchmarkers happy.

Offloading
**********

:doc:`OffloadSubsystem` allows you to free your workers as soon as possible when some specific pattern matches and can be delegated
to a pure-c thread. Examples are sending static file from the file system, transferring data from the network to the client and so on.

Offloading is very complex, but its use is transparent to the end user. If you want to try just add ``--offload-threads <n>`` where <n> is the number of threads to spawn (1 per CPU is a good value to start with).

When offload threads are enabled, all of the parts that can be optimized will be automatically detected.


And now
*******

You should already be able to go in production with such few concepts, but uWSGI is an enormous project with hundreds of features
and configurations. If you want to be a better sysadmin, continue reading the full docs.

Welcome!