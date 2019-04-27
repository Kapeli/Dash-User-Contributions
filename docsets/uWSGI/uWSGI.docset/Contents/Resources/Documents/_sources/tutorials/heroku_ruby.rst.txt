Running Ruby/Rack webapps on Heroku with uWSGI
==============================================

Prerequisites: a Heroku account (on the cedar platform), git (on the local system) and the heroku toolbelt (or the old/deprecated heroku gem)

Note: you need a uWSGI version >= 1.4.8 to correctly run ruby/rack apps. Older versions may work, but are not supported.

Preparing the environment (a Sinatra application)
*************************************************

On your local system prepare the structure for your sinatra application

.. code-block:: sh

   mkdir uwsgi-heroku
   cd uwsgi-heroku
   git init .
   heroku create --stack cedar
   

the last command will create a new heroku application (you can check it on the web dashboard).

Next step is creating our Gemfile (this file contains the gem required by the application)

.. code-block:: rb

   source 'https://rubygems.org'

   gem "uwsgi"
   gem "sinatra"

we now need to run ``bundle install`` to create the Gemfile.lock file

let's track the two with git:

.. code-block:: sh

   git add Gemfile
   git add Gemfile.lock

Finally create a config.ru file containing the Sinatra sample app

.. code-block:: rb

   require 'sinatra'

   get '/hi' do
     return "ciao"
   end

   run Sinatra::Application

and track it

.. code-block:: sh

   git add config.ru

Creating the uWSGI config file
******************************

We are now ready to create the uWSGI configuration (we will use the .ini format in a file called uwsgi.ini).

The minimal setup for heroku is the following (check the comments in the file for an explanation)

.. code-block:: ini

   [uwsgi]
   ; bind to the heroku required port
   http-socket = :$(PORT)
   ; force the usage of the ruby/rack plugin for every request (7 is the official numbero for ruby/rack)
   http-socket-modifier1 = 7
   ; load the bundler subsystem
   rbrequire = bundler/setup
   ; load the application
   rack = config.ru
   ; when the app receives the TERM signal let's destroy it (instead of brutal reloading)
   die-on-term = true

but a better setup will be

.. code-block:: ini

   [uwsgi]
   ; bind to the heroku required port
   http-socket = :$(PORT)
   ; force the usage of the ruby/rack plugin for every request (7 is the official numbero for ruby/rack)
   http-socket-modifier1 = 7
   ; load the bundler subsystem
   rbrequire = bundler/setup
   ; load the application
   rack = config.ru
   ; when the app receives the TERM signal let's destroy it (instead of brutal reloading)
   die-on-term = true
   ; enable the master process
   master = true
   ; spawn 4 processes to increase concurrency
   processes = 4
   ; report memory usage after each request
   memory-report = true
   ; reload if the rss memory is higher than 100M
   reload-on-rss = 100

Let's track it

.. code-block:: sh

   git add uwsgi.ini

Deploying to heroku
*******************

We need to create the last file (required by Heroku). It is the Procfile, that instruct the Heroku system on which process to start for a web application.

We want to spawn uwsgi (installed as a gem via bundler) using the uwsgi.ini config file

.. code-block:: sh

   web: bundle exec uwsgi uwsgi.ini

track it

.. code-block:: sh

   git add Procfile

And let's commit all:

.. code-block:: sh

   git commit -a -m "first attempt"

And push to heroku:

.. code-block:: sh

   git push heroku master

If all goes well, you will see your page under your app url on the /hi path

Remember to run ``heroku logs`` to check if all is ok.

fork() for dummies
******************

uWSGI allows you to choose how to abuse the fork() syscall in your app.

By default the approach is loading the application in the master process and then fork() to the workers
that will inherit a copy of the master process.

This approach speedup startup and can potentially consume less memory. The truth is that often (for the way ruby garbage collection works)
you will get few memory gain. The real advantage in in performance as the vast majority of time during application startup is spent
in (slowly) searching for files. With the fork() early approach you can avoid repeating that slow procedure one time for worker.

Obviously the uWSGI mantra is "do whatever you need, if you can't, it is a uWSGI bug" so if your app is not fork()-friendly
you can add the ``lazy-apps = true`` option that will load your app one time per-worker.

The ruby GC
***********

By default uWSGI, calls the ruby Garbage collector after each request. This ensure an optimal use of memory (remember on Heroku, your memory is limited) you should not touch
the default approach, but if you experience a drop in performance you may want to tune it using the ``ruby-gc-freq = n`` option
where n is the number of requests after the GC is called.

Concurrency
***********

Albeit uWSGI supports lot of different paradigms for concurrency, the multiprocess one is suggested for the vast majority of ruby/rack apps.

Basically all popular ruby-frameworks rely on that. Remember that your app is limited so spawn a number of processes
that can fit in your Heroku dyno.

Starting from uWSGI 1.9.14, native ruby 1.9/2.x threads support has been added. Rails4 (only in production mode !!!) supports them:

.. code-block:: ini

   [uwsgi]
   ...
   ; spawn 8 threads per-process
   threads = 8
   ; maps them as ruby threads
   rbthreads = true
   ; do not forget to set production mode for rails4 apps !!!
   env = RAILS_ENV=production
   ...

Harakiri
********

If you plan to put production-apps on heroku, be sure to understand how dynos and their proxy works. Based on that, try to always set the harakiri parameters to a good value for your app. (do not ask for a default value, IT IS APP-DEPENDENT)

Harakiri, is the maximum time a single request can run, before being destroyed by the master

Static files
************

Generally, serving static files on Heroku is not a good idea (mainly from a design point of view). You could obviously have that need. In such a case remember to use uWSGI facilities for that, in particular offloading is the best way to leave your workers free while you serve big files (in addition to this remember that your static files must be tracked with git)

Try to avoid serving static files from your ruby/rack code. It will be extremely slow (compared to the uWSGI facilities) and can hold your worker busy
for the whole transfer of the file

Adaptive process spawning
*************************

None of the supported algorithms are good for the Heroku approach and, very probably, it makes little sense to use a dynamic process number on such a platform.

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

The --attach-daemon option and its --smart variants work without problems. Just remember you are on a volatile filesystem and you are not free to bind on port/addresses as you may wish
