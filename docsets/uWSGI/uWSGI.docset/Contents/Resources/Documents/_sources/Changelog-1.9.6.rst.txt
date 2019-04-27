uWSGI 1.9.6
===========

Changelog 20130409

Bugfixes
********

* workaround for building the python plugin with gcc 4.8

Sorry, this is not a real bugfix, but making a release without bugfixes seems wrong...

New Features
************

Sqlite and LDAP pluginization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Storing configurations in sqlite databases or LDAP tree is a pretty "uncommon" way to configure uWSGI
instances. For such a reason they have been moved to dedicated plugins.

If you store config in a sqlite database, just add --plugin sqlite3. For LDAP, just add --plugin ldap:

.. code-block:: sh

   uwsgi --plugin sqlite --sqlite config.db

Configuring dynamic apps with internal routing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

'Til now, you need to configure your webserver to load apps dinamically.

Three new instructions have been added to load application on demand.

Check the example:

.. code-block:: ini

   [uwsgi]

   http-socket = :9090

   route = ^/foo chdir:/tmp
   route = ^/foo log:SCRIPT_NAME=${SCRIPT_NAME}
   route = ^/foo log:URI=${REQUEST_URI}
   route = ^/foo sethome:/var/uwsgi/venv001
   route = ^/foo setfile:/var/uwsgi/app001.py
   route = ^/foo break:

   route = ^/bar chdir:/var
   route = ^/bar addvar:SCRIPT_NAME=/bar
   route = ^/bar sethome:/var/uwsgi/venv002
   route = ^/bar setfile:/var/uwsgi/app002.py
   route = ^/bar break:

as you can see, rewriting SCRIPT_NAME is now very easy. The sethome instruction is currently available only for python application
(it means 'virtualenv')

Carbon avg computation (Author: Łukasz Mierzwa)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can now configure how the carbon plugin send the response average when no requests have been managed.

You have three ways:

   --carbon-idle-avg none - don't push any avg_rt value if no requests were made

   --carbon-idle-avg last - use last computed avg_rt value (default)

   --carbon-idle-avg zero - push 0 if no requests were made



Numeric checks for the internal routing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

New check are available:

ishigher or '>'

islower or '<'

ishigherequal or '>='

islowerequal or '<='

Example:

.. code-block:: ini

   [uwsgi]
   route-if = ishigher:${CONTENT_LENGTH};1000 break:403 Forbidden


Math and time for the internal routing subsystem
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you build uWSGI with matheval support (matheval-dev on debian/ubuntu) you will get
math support in your routing system via the 'math' routing var.

The 'time' routing var has been added currently exporting only the 'unix' field returning the epoch.

Check this crazy example:

.. code-block:: ini

   [uwsgi]
   http-socket = :9090
   route-run = addvar:TEMPO=${time[unix]}
   route-run = log:inizio = ${TEMPO}
   route-run = addvar:TEMPO=${math[TEMPO+1]}
   route-run = log:tempo = ${TEMPO}


As you can see the routing subsystem can store values in request variables (here we create a 'TEMPO' var, and you will be able to access it even in your app request vars)

The 'math' operations can reference request vars

Check the matheval docs for the supported operations: http://matheval.sourceforge.net/docs/index.htm

Added non-standard seek() and tell() to wsgi.input (post-buffering required)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

While testing the 'smart mode' of the 'Klaus' project (https://github.com/jonashaag/klaus) we noticed it was violating
the WSGI standard calling seek() and tell() when in smart mode.

We have added support for both methods when post-buffering is enabled.

REMEMBER: they violate the WSGI standard, so try to avoid them (if you can). There are better ways to accomplish that.

Pyshell improvements, AKA Welcome IPython (Idea: C Anthony Risinger)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can invoke the ipython shell instead of the default one when using --pyshell:

.. code-block:: sh

   uwsgi -s :3031 --pyshell="from IPython import embed; embed()"

Obviously you can pass whatever code to --pyshell

The 'rpcraw' routing instruction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Another powerful and extremely dangerous routing action. It will call a rpc function
sending its return value directly to the client (without further processing).

Empty return values means "go to the next routing rule".

Return values must be valid HTTP:

.. code-block:: js

   uwsgi.register_rpc('myrules', function(uri) {
        if (uri == '/foo') {
                return "HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\nServer: uWSGI\r\nFoo: bar\r\n\r\nCiao Ciao";
        }
        return "";
   });

.. code-block:: ini

   [uwsgi]
   plugin = v8
   v8-load = rules.js
   route = ^/foo rpcraw:myrules ${REQUEST_URI}


Preliminary support for the HTTP Range header
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The range request header allows requesting only part of a resource (like a limited set of bytes of a static file).

The system can be used when serving static files, but it is disabled by default. Just add --honour-range to enable it.

In the future it will be used for file wrappers (like wsgi.file_wrapper) and for :doc:`GridFS` (this is the reason for not enabling it by default
as you could have already implemented range management in your app)


The 'lord' routing condition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We are working hard on making a truly amazing cluster subsystem using :doc:`Legion`

You can now execute internal routing rules when an instance is a lord:

.. code-block:: ini

   [uwsgi]
   ...
   route-if = lord:mylegion log:I AM THE LORD !!!

the "I AM THE LORD !!!" logline will be printed only when the instance is a lord of the legion 'mylegion'

GridFS authentication
^^^^^^^^^^^^^^^^^^^^^

You can now connect to authenticated MongoDB servers when using :doc:`GridFS`

Just add the username and password parameters to the mount definition

The --for-times config logic
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can use --for-times for running uWSGI options the specified number of times:

.. code-block:: ini

   [uwsgi]
   for-times = 8
      mule = true
   endfor =

this will spawn 8 mules

The 'uwsgi' routing var
^^^^^^^^^^^^^^^^^^^^^^^

Accessing uWSGI internal parameters when defining routing rules could be handy. The 'uwsgi' routing var
is the container for such vars.

Currently it exports 'wid' (the id of the worker running the rule) and 'pid' (the pid of the worker running the rule)

.. code-block:: ini

   [uwsgi]
   master = true
   processes = 4
   ; stupid rule... break connections to the worker 4
   route-if = ishigher:${uwsgi[wid]};3 break:403 Forbidden

The 'alarm' routing action
^^^^^^^^^^^^^^^^^^^^^^^^^^

You can now trigger alarms from the routing subsystem:

.. code-block:: ini

   [uwsgi]

   alarm = pippo cmd:cat

   route = ^/help alarm:pippo ${uwsgi[wid]} ${uwsgi[pid]}
   http-socket = :9090

when /help is requested the 'pippo' alarm is triggered passing the wid and the pid as the message

Welcome to the ruby shell
^^^^^^^^^^^^^^^^^^^^^^^^^

As well as the --pyshell we now have the ruby shell:

.. code-block:: sh

   uwsgi --rbshell -s :3031

or

.. code-block:: sh

   uwsgi --rbshell="require 'pry';binding.pry" -s :3031

for using the pry shell: http://pryrepl.org/

... and welcome to the Lua shell
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As python and ruby, even Lua got its shell. Just add --lua-shell

Goodbye to the old (and useless) probe subsystem
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The probe subsystem was added during 0.9 development cycle but it was badly designed and basically broken.

It has been definitely removed (the deprecation phase has been skipped as 1.9 is not an LTS release and 1.4 still support it)


Improvements in the Legion subsystem (Author: Łukasz Mierzwa)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Two new hooks have been added: --legion-node-joined and --legion-node-left

More fine-tuning
^^^^^^^^^^^^^^^^

--socket-sndbuf and --socket-rcvbuf have been added to allow tuning of the send a receive buffer of the uWSGI sockets (use with caution)

V8 improvements and TeaJS integration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :doc:`V8` plugin continue to improve. The main target is still :doc:`InternalRouting` but JSGI support is almost complete
and we are working for TeaJS (old v8cgi) integration: http://code.google.com/p/teajs/

more to come soon...


Availability
************

uWSGI 1.9.6 will be available since 20130409 at this url:

https://projects.unbit.it/downloads/uwsgi-1.9.6.tar.gz
