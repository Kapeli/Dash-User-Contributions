Setting up Graphite on Ubuntu using the Metrics subsystem
=========================================================

This tutorial will guide you in installing a multi-app server, with each application sending metrics to a central graphite/carbon server.

Graphite is available here: http://graphite.wikidot.com/

The uWSGI Metrics subsystem is documented here :doc:`../Metrics`

The tutorial assumes an Ubuntu Saucy (13.10) release on amd64

While for Graphite we will use Ubuntu official packages, uWSGI core and plugins will be downloaded and installed from official sources

Installing Graphite and the others needed packages
**************************************************

.. code-block:: sh

   sudo apt-get install python-dev ruby-dev bundler build-essential libpcre3-dev graphite-carbon graphite-web
   
python-dev and ruby-dev are required as we want to support both WSGI and Rack apps.

pcre development headers allow you to build uWSGI with internal routing support (something you always want)

Initializing Graphite
*********************

The first step will be enabling th Carbon server.

The Graphite project is composed by three subsystems: whisper, carbon and the web frontend

Whisper is a data storage format (similar to rrdtool)

Carbon is the server gathering metrics and storing them in whisper files (well it does more, but this is its main purpose)

The web frontend visualize the charts/graphs built from the data gathered by the carbon server.

To enable the carbon server edit ``/etc/default/graphite-carbon`` and set CARBON_CACHE_ENABLED to true

Before starting the carbon server we need to build its search index.

Just run:

.. code-block:: sh

   sudo /usr/bin/graphite-build-search-index

Then start the carbon server (at the next reboot it will be automatically started)

.. code-block:: sh

   sudo /etc/init.d/carbon-cache start

Building and Installing uWSGI
*****************************

Download latest stable uWSGI tarball

.. code-block:: sh

   wget https://projects.unbit.it/downloads/uwsgi-latest.tar.gz
   
explode it, and from the created directory run:

.. code-block:: sh

   python uwsgiconfig.py --build core
   
this will build the uWSGI "core" binary.

We now want to build the python, rack and carbon plugins:

.. code-block:: sh

   python uwsgiconfig.py --plugin plugins/python core
   python uwsgiconfig.py --plugin plugins/rack core
   python uwsgiconfig.py --plugin plugins/carbon core
   
   
now we have ``uwsgi``, ``python_plugin.so``, ``rack_plugin.so`` and ``carbon_plugin.so``

let's copy it to system directories:

.. code-block:: sh

   sudo mkdir /etc/uwsgi
   sudo mkdir /usr/lib/uwsgi
   sudo cp uwsgi /usr/bin/uwsgi
   sudo cp python_plugin.so /usr/lib/uwsgi
   sudo cp rack_plugin.so /usr/lib/uwsgi
   sudo cp carbon_plugin.so /usr/lib/uwsgi

Setting up the uWSGI Emperor
****************************

Create an upstart config file for starting :doc:`../Emperor`

.. code-block:: sh

   # Emperor uWSGI script

   description "uWSGI Emperor"
   start on runlevel [2345]
   stop on runlevel [06]

   exec /usr/bin/uwsgi --emperor /etc/uwsgi
   
save it as ``/etc/init/emperor.conf`` and start the Emperor:

.. code-block:: sh

   start emperor
   
   
From now on, to start uWSGI instances just drop their config files into /etc/uwsgi

Spawning the Graphite web interface
***********************************

Before starting the graphite web interface (that is a Django app) we need to initialize its database.

Just run:

.. code-block:: sh

   sudo graphite-manage syncdb
   
this is the standard django syncdb command for manage.py. Just answer the questions to create an admin user.

Now we are ready to create a uWSGI vassal:

.. code-block:: ini

   [uwsgi]
   plugins-dir = /usr/lib/uwsgi
   plugins = python
   uid = _graphite
   gid = _graphite
   wsgi-file = /usr/share/graphite-web/graphite.wsgi
   http-socket = :8080
   
Save it as ``/etc/uwsgi/graphite.ini``
   
the _graphite user (and group) is created by the graphite ubuntu package. Our uWSGI vassal will run under this privileges.

The web interface will be available on the port 8080 of your server natively speaking HTTP. If you prefer to proxy it,
just change ``http-socket`` to ``http`` or place it behind a full webserver like nginx (this step is not covered in this tutorial)


Spawning vassals sending metrics to Graphite
********************************************

We are now ready to send applications metrics to the carbon/graphite server.

For every vassal file in /etc/uwsgi just be sure to add the following options:

.. code-block:: ini

   [uwsgi]
   ...
   plugins = carbon
   enable-metrics = true
   carbon-use-metrics = true
   carbon-id = %n
   carbon = 127.0.0.1:2003
   ...

The ``carbon-id`` set a meaningful prefix to each metric (%n automatically translates to the name without extension of the vassal file).

The ``carbon`` option set the address of the carbon server to send metrics to (by default the carbon server binds on port 2003, but you can change it editing
``/etc/carbon/carbon.conf`` and restarting the carbon server)

Using Graphiti (Ruby/Sinatra based) as alternative frontend
***********************************************************

Graphiti is an alternative dashboard/frontend from Graphite writte in Sinatra (a Ruby/Rack framework).

Graphiti requires redis, so be sure a redis server is running in your system.

Running:

.. code-block:: sh

   sudo apt-get install redis-server
   
will be enough

First step is cloning the graphiti app (place it where you want/need):

.. code-block:: sh

   git clone https://github.com/paperlesspost/graphiti.git
   
then run the bundler tool (if you are not confident with the ruby world it is a tool for managing dependencies)

.. code-block:: sh

   bundle install

.. note:: if the eventmachine gem installation fails, add "gem 'eventmachine'" in the Gemfile as the first gem and run bundle update. This will ensure latest eventmachine version will be installed

After bundle has installed all of the gems, you have to copy the graphiti example configuration:

.. code-block:: sh

   cp config/settings.yml.example config/settings.yml
   
edit it and set graphite_base_url to the url where the graphite web interface (the django one) is running.

Now we can deploy it on uWSGI

.. code-block:: ini

   [uwsgi]
   plugins-dir = /usr/lib/uwsgi
   plugins = rack
   chdir = <path_to_graphiti>
   rack = config.ru
   rbrequire = bundler/setup
   http-socket = :9191
   uid = _graphite
   gid = _graphite
   
save it as ``/etc/uwsgi/graphiti.ini`` to let the Emperor deploy it

You can now connect to port 9191 to manage your gathered metrics.

As always you are free to place the instance under a proxy.

Notes
*****

By default the carbon server listens on a public address. Unless you know what you are doing you should point it to a local one (like 127.0.0.1)

uWSGI exports a gazillion of metrics (and more are planned), do not be afraid to use them

There is no security between apps and the carbon server, any apps can write metrics to it. If you are hosting untrusted apps you'd better to use other approcahes (like giving a graphite instance to every user in the system)

The same is true for redis, if you run untrusted apps a shared redis instance is absolutely not a good choice from a secuity point of view
