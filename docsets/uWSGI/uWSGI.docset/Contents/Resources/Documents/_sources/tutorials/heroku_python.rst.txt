Running python webapps on Heroku with uWSGI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Prerequisites: a Heroku account (on the cedar platform), git (on the local system) and the heroku toolbelt.

Note: you need a uWSGI version >= 1.4.6 to correctly run python apps. Older versions may work, but are not supported.

Preparing the environment
*************************

On your local system prepare a directory for your project:

.. code-block:: sh

   mkdir uwsgi-heroku
   cd uwsgi-heroku
   git init .
   heroku create

the last command will create a new heroku application (you can check it on the web dashboard).

For our example we will run the Werkzeug WSGI testapp, so we need to install the werkzeug package in addition to uWSGI.

First step is creating a requirements.txt file and tracking it with git.

The content of the file will be simply

.. code-block:: sh

   uwsgi
   werkzeug

Let's track it with git

.. code-block:: sh

   git add requirements.txt

Creating the uWSGI config file
******************************

Now we can create our uWSGI configuration file. Basically all of the features can be used on heroku

.. code-block:: ini

   [uwsgi]
   http-socket = :$(PORT)
   master = true
   processes = 4
   die-on-term = true
   module = werkzeug.testapp:test_app
   memory-report = true

as you can see this is a pretty standard configuration. The only heroku-required options are --http-socket and --die-on-term.

The first is required to bind the uWSGI socket to the port requested by the Heroku system (exported via the environment variable PORT we can access with $(PORT))

The second one (--die-on-term) is required to change the default behaviour of uWSGI when it receive a SIGTERM (brutal reload, while Heroku expect a shutdown)

The memory-report option (as we are in a memory constrained environment) is a good thing.

Remember to track the file

.. code-block:: sh

   git add uwsgi.ini

Preparing for the first commit/push
***********************************

We now need the last step: creating the Procfile.

The Procfile is a file describing which commands to start. Generally (with other deployment systems) you will use it for every
additional process required by your app (like memcached, redis, celery...), but under uWSGI you can continue using its advanced facilities to manage them.

So, the Procfile, only need to start your uWSGI instance:

.. code-block:: sh

   web: uwsgi uwsgi.ini

Track it

.. code-block:: sh

   git add Procfile

And finally let's commit all:

.. code-block:: sh

   git commit -a -m "first commit"

and push it (read: deploy) to Heroku:

.. code-block:: sh

    git push heroku master

The first time it will requires a couple of minutes as it need to prepare your virtualenv and compile uWSGI.

Following push will be much faster.

Checking your app
*****************

Running ``heroku logs`` you will be able to access uWSGI logs. You should get all of your familiar information, and eventually
some hint in case of problems.

Using another version of python
*******************************

Heroku supports different python versions. By default (currently, february 2013), Python 2.7.3 is enabled.

If you need another version just create a runtime.txt in your repository with a string like that:

.. code-block:: sh

   python-2.7.2

to use python 2.7.2

Remember to add/commit that in the repository.

Every time you change the python version, a new uWSGI binary is built.

Multiprocess or Multithread ?
*****************************

It obviosuly depend on your app. But as we are on a memory-limited environment you can expect better memory usage with threads.

In addition to this, if you plan to put production-apps on Heroku be sure to understand how Dynos and their proxy works
(it is very important. really)

Async/Greethreads/Coroutine ?
*****************************

As always, do not trust people suggesting you to ALWAYS use some kind of async mode (like gevent). If your app
is async-friendly you can obviously use gevent (it is built by default in recent uWSGI releases), but if you do not know that, remain
with multiprocess (or multithread).

Harakiri
********

As said previously, if you plan to put production-apps on heroku, be sure to understand how dynos and their proxy works. Based on that,
try to always set the harakiri parameters to a good value for your app. (do not ask for a default value, IT IS APP-DEPENDENT)

Static files
************

Generally, serving static files on Heroku is not a good idea (mainly from a design point of view). You could obviously have that need.
In such a case remember to use uWSGI facilities for that, in particular offloading is the best way to leave your workers free while you serve big files (in addition to this remember that your static files must be tracked with git)

Adaptive process spawning
*************************

None of the supported algorithm are good for the Heroku approach and, very probably, it makes little sense to use a dynamic process
number on such a platform.

Logging
*******

If you plan to use heroku on production, remember to send your logs (via udp for example) on an external server (with persistent storage).

Check the uWSGI available loggers. Surely one will fit your need. (pay attention to security, as logs will fly in clear).

UPDATE: a udp logger with crypto features is on work.

Alarms
******

All of the alarms plugin should work without problems

The Spooler
***********

As your app runs on a non-persistent filesystem, using the Spooler is a bad idea (you will easily lose tasks).

Mules
*****

They can be used without problems

Signals (timers, filemonitors, crons...)
****************************************

They all works, but do not rely on cron facilities, as heroku can kill/destroy/restarts your instances in every moment.

External daemons
****************

The --attach-daemon option and its --smart variants work without problems. Just remember you are on a volatile filesystem and you are not
free to bind on port/addresses as you may wish

Monitoring your app (advanced/hacky)
*************************************

Albeit Heroku works really well with newrelic services, you always need to monitor the internals of your uWSGI instance.

Generally you enable the stats subsystem with a tool like uwsgitop as the client.

You can simply add uwsgitop to you requirements.txt

.. code-block:: sh

   uwsgi
   uwsgitop
   werkzeug

and enable the stats server on a TCP port (unix sockets will not work as the instance running uwsgitop is not on the same server !!!):

.. code-block:: ini

   [uwsgi]
   http-socket = :$(PORT)
   master = true
   processes = 4
   die-on-term = true
   module = werkzeug.testapp:test_app
   memory-report = true
   stats = :22222

Now we have a problem: how to reach our instance ?

We need to know the LAN address of the machine where our instance is phisically running. To accomplish that, a raw trick is running
ifconfig on uWSGI startup:

.. code-block:: ini

   [uwsgi]
   http-socket = :$(PORT)
   master = true
   processes = 4
   die-on-term = true
   module = werkzeug.testapp:test_app
   memory-report = true
   stats = :22222
   exec-pre-app = /sbin/ifconfig eth0

Now thanks to the ``heroku logs`` command you can know where your stats server is

.. code-block:: sh

   heroku run uwsgitop 10.x.x.x:22222

change x.x.x with the discovered address and remember that you could not be able to bind on port 22222, so change it accordingly.

Is it worthy to make such a mess to get monitoring ? If you are testing your app before going to production, it could be a good idea,
but if you plan to buy more dynos, all became so complex that you'd better to use some heroku-blessed technique (if any)
