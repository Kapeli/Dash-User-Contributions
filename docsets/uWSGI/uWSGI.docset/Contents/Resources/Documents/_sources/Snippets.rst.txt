Snippets
========

This is a collection of some of the most "fun" uses of uWSGI features.

X-Sendfile emulation
--------------------

Even if your frontend proxy/webserver does not support X-Sendfile (or cannot access your static resources) you can emulate
it using uWSGI's internal offloading (your process/thread will delegate the actual static file serving to offload threads).

.. code-block:: ini

   [uwsgi]
   ...
   ; load router_static plugin (compiled in by default in monolithic profiles)
   plugins = router_static
   ; spawn 2 offload threads
   offload-threads = 2
   ; files under /private can be safely served
   static-safe = /private
   ; collect the X-Sendfile response header as X_SENDFILE var
   collect-header = X-Sendfile X_SENDFILE
   ; if X_SENDFILE is not empty, pass its value to the "static" routing action (it will automatically use offloading if available)
   response-route-if-not = empty:${X_SENDFILE} static:${X_SENDFILE}
   

Force HTTPS
-----------

This will force HTTPS for the whole site.

.. code-block:: ini

   [uwsgi]
   ...
   ; load router_redirect plugin (compiled in by default in monolithic profiles)
   plugins = router_redirect
   route-if-not = equal:${HTTPS};on redirect-permanent:https://${HTTP_HOST}${REQUEST_URI}
   
And this only for ``/admin``

.. code-block:: ini

   [uwsgi]
   ...
   ; load router_redirect plugin (compiled in by default in monolithic profiles)
   plugins = router_redirect
   route = ^/admin goto:https
   ; stop the chain
   route-run = last:
   
   route-label = https
   route-if-not = equal:${HTTPS};on redirect-permanent:https://${HTTP_HOST}${REQUEST_URI}
   
Eventually you may want to send HSTS (HTTP Strict Transport Security) header too.

.. code-block:: ini

   [uwsgi]
   ...
   ; load router_redirect plugin (compiled in by default in monolithic profiles)
   plugins = router_redirect
   route-if-not = equal:${HTTPS};on redirect-permanent:https://${HTTP_HOST}${REQUEST_URI}
   route-if = equal:${HTTPS};on addheader:Strict-Transport-Security: max-age=31536000
   
   
Python Auto-reloading (DEVELOPMENT ONLY!)
-----------------------------------------

In production you can monitor file/directory changes for triggering reloads (touch-reload, fs-reload...).

During development having a monitor for all of the loaded/used python modules can be handy. But please use it only during development.

The check is done by a thread that scans the modules list with the specified frequency:

.. code-block:: ini

   [uwsgi]
   ...
   py-autoreload = 2
   
will check for python modules changes every 2 seconds and eventually restart the instance.

And again:

.. warning:: Use this only in development.


Full-Stack CGI setup
--------------------

This example spawned from a uWSGI mailing list thread.

We have static files in /var/www and cgis in /var/cgi. Cgi will be accessed using the /cgi-bin
mountpoint. So /var/cgi/foo.lua will be run on request to /cgi-bin/foo.lua

.. code-block:: ini

   [uwsgi]
   workdir = /var
   ipaddress = 0.0.0.0
 
   ; start an http router on port 8080
   http = %(ipaddress):8080
   ; enable the stats server on port 9191
   stats = 127.0.0.1:9191
   ; spawn 2 threads in 4 processes (concurrency level: 8)
   processes = 4
   threads = 2
   ; drop privileges
   uid = nobody
   gid = nogroup
   
   ; serve static files in /var/www
   static-index = index.html
   static-index = index.htm
   check-static = %(workdir)/www
   
   ; skip serving static files ending with .lua
   static-skip-ext = .lua

   ; route requests to the CGI plugin
   http-modifier1 = 9
   ; map /cgi-bin requests to /var/cgi
   cgi = /cgi-bin=%(workdir)/cgi
   ; only .lua script can be executed
   cgi-allowed-ext = .lua
   ; .lua files are executed with the 'lua' command (it avoids the need of giving execute permission to files)
   cgi-helper = .lua=lua
   ; search for index.lua if a directory is requested
   cgi-index = index.lua
   
   
Multiple flask apps in different mountpoints
--------------------------------------------

Let's write three flask apps:

.. code-block:: py

   #app1.py
   from flask import Flask
   app = Flask(__name__)

   @app.route("/")
   def hello():
       return "Hello World! i am app1"
       

.. code-block:: py

   #app2.py
   from flask import Flask
   app = Flask(__name__)

   @app.route("/")
   def hello():
       return "Hello World! i am app2"
       
       
.. code-block:: py

   #app3.py
   from flask import Flask
   app = Flask(__name__)

   @app.route("/")
   def hello():
       return "Hello World! i am app3"

each will be mounted respectively in /app1, /app2, /app3

To mount an application with a specific "key" in uWSGI, you use the --mount option:

```
--mount <mountpoint>=<app>
```

in our case we want to mount 3 python apps, each keyed with what will be the WSGI SCRIPT_NAME variable:

.. code-block :: ini
   
   [uwsgi]
   plugin = python
   mount = /app1=app1.py
   mount = /app2=app2.py
   mount = /app3=app3.py
   ; generally flask apps expose the 'app' callable instead of 'application'
   callable = app

   ; tell uWSGI to rewrite PATH_INFO and SCRIPT_NAME according to mount-points
   manage-script-name = true

   ; bind to a socket
   socket = /var/run/uwsgi.sock



now directly point your webserver.proxy to the instance socket (without doing additional configurations)

Note: by default every app is loaded in a new python interpreter (that means a pretty-well isolated namespace for each app).
If you want all of the app to be loaded in the same python vm, use the --single-interpreter option.

Another note: you may find reference to an obscure "modifier1 30" trick. It is deprecated and extremely ugly. uWSGI is able to rewrite request variables in lot of advanced ways

Final note: by default, the first loaded app is mounted as the "default one". That app will be served when no mountpoint matches.


rbenv on OSX (should work on other platforms too)
-------------------------------------------------

install rbenv

.. code-block:: sh

   brew update
   brew install rbenv ruby-build
   
(do not set the magic line in .bash_profile as described in the classic howto, as we want to not clobber the environment, and allow uWSGI to get rid of it)

get a uWSGI tarball and build the 'nolang' version (it is a monolithic one without language plugins compiled in)

.. code-block:: sh

   wget https://projects.unbit.it/downloads/uwsgi-latest.tar.gz
   tar zxvf uwsgi-latest.tar.gz
   cd uwsgi-xxx
   make nolang
   
now start installing the ruby versions you need

.. code-block:: sh

   rbenv install 1.9.3-p551
   rbenv install 2.1.5
   
and install the gems you need (sinatra in this case):

.. code-block:: sh

   # set the current ruby env
   rbenv local 1.9.3-p551
   # get the path of the gem binary
   rbenv which gem
   # /Users/roberta/.rbenv/versions/1.9.3-p551/bin/gem
   /Users/roberta/.rbenv/versions/1.9.3-p551/bin/gem install sinatra
   # from the uwsgi sources directory, build the rack plugin for 1.9.3-p551, naming it rack_193_plugin.so
   # the trick here is changing PATH to find the right ruby binary during the build procedure
   PATH=/Users/roberta/.rbenv/versions/1.9.3-p551/bin:$PATH ./uwsgi --build-plugin "plugins/rack rack_193"
   # set ruby 2.1.5
   rbenv local 2.1.5
   rbenv which gem
   # /Users/roberta/.rbenv/versions/2.1.5/bin/gem
   /Users/roberta/.rbenv/versions/2.1.5/bin/gem install sinatra
   PATH=/Users/roberta/.rbenv/versions/2.1.5/bin:$PATH ./uwsgi --build-plugin "plugins/rack rack_215"
   
now to switch from one ruby to another, just change the plugin:

.. code-block:: ini

   [uwsgi]
   plugin = rack_193
   rack = config.ru
   http-socket = :9090
   
or 

.. code-block:: ini

   [uwsgi]
   plugin = rack_215
   rack = config.ru
   http-socket = :9090

ensure plugins are stored in the current working directory, or set the plugins-dir directive or specify them with absolute path like

.. code-block:: ini

   [uwsgi]
   plugin = /foobar/rack_215_plugin.so
   rack = config.ru
   http-socket = :9090


Authenticated WebSocket Proxy
-----------------------------

App server identifies websocket traffic, authenticates/authorizes the user using whatever CGI variables against the
app's own policies/infrastructure, then offloads/proxies the request to a simple kafka-websocket backend.

First create ``auth_kafka.py``:

.. code-block:: python

   from pprint import pprint
   
   def application(environ, start_response):
       start_response('200 OK', [('Content-Type', 'text/plain')])
       return ['It Works!']
   
   def auth_kafka(request_uri, http_cookie, http_authorization):
       pprint(locals())
       return 'true'
   
   import uwsgi
   uwsgi.register_rpc('auth_kafka', auth_kafka)
   
Then create ``auth_kafka.ini``:

.. code-block:: ini

   [uwsgi]
   
   ; setup
   http-socket = 127.0.0.1:8000
   master = true
   module = auth_kafka
   
   ; critical! else worker timeouts apply to proxied websocket connections
   offload-threads = 2
   
   ; match websocket protocol
   kafka-ws-upgrade-regex = ^[Ww]eb[Ss]ocket$
   
   ; DRY place for websocket check
   is-kafka-ws-request =  regexp:${HTTP_UPGRADE};%(kafka-ws-upgrade-regex)
   
   ; location of the kafka-ws server
   kafka-ws-host = 127.0.0.1:7080
   
   ; base endpoint uri for websocket server
   kafka-ws-endpoint-uri = /v2/broker/
   
   ; call auth_kafka(...); if AUTH_KAFKA gets set, request is good!
   route-if = %(is-kafka-ws-request) rpcvar:AUTH_KAFKA auth_kafka ${REQUEST_URI} ${HTTP_COOKIE} ${HTTP_AUTHORIZATION}
   
   ; update request uri to websocket endpoint (rewrite only changes PATH_INFO?)
   route-if-not = empty:${AUTH_KAFKA} seturi:%(kafka-ws-endpoint-uri)?${QUERY_STRING}
   
   ; route the request to our websocket server
   route-if-not = empty:${AUTH_KAFKA} httpdumb:%(kafka-ws-host)
   
Start a "kafka-websocket" server:

.. code-block:: bash

   nc -l -k -p 7080
   
Now go to ``http://127.0.0.1:8000`` in a web browser! You should see ``Hello!``. Open chrome inspector or firebug and type:

.. code-block:: javascript

   ws = new WebSocket('ws://127.0.0.1:8000/?subscribe=true')
   
You should see this request proxied to your ``nc`` command! This pattern allows the internal network to host a more-or-less
wide-open/generic kafka -> websocket gateway and delegates auth needs to the app server. Using ``offload-threads`` means
proxied requests do *NOT* block workers; using ``httpdumb`` prevents mangling the request (``http`` action forces ``HTTP/1.0``)


SELinux and uWSGI
-----------------

SELinux allows you to isolate web application processes from each other, and limits each program to its purpose only. The applications can be placed into strongly isolated individual sandboxes, separating them from one another and from the underlying operating system. Since SELinux is implemented within the kernel, applications do not need to be specifically written or modified to work under SELinux. There is an `SELinux security policy for web applications  <https://github.com/reinow/sepwebapp>`_ at github well suited for uWSGI. This security policy also supports the uWSGI emperor process running in one domain, and each web application's worker processes running in a separate domain, requiring only minimal privileges for the worker processes even if Linux namespaces are used. Of course, there is no requirement for emperor mode, or Linux namespaces, to use SELinux with uWSGI.

On Linux it is possible to run each vassal with a dedicated view of the filesystems, ipc, uts, networking, pids and uids. Then each vassal can, for example, modify the filesystem layout, networking, and hostname without damaging the main system. With this setup, privileged tasks, like mounting filesystems, setting hostnames, configuring the network, and setting gid and uid of the worker processes can be done before changing the SELinux security context of the vassals' process ensuring that only minimal privileges are required for the worker processes.

First configure, compile and load the SELinux web application security policy. Then, relabel the application files. Further information on how to configure web application policies can be found in the README.md included in the `SELinux security policy for web applications <https://github.com/reinow/sepwebapp>`_. Finally, in each vassall's configuration file, call the setcon function in libselinux to set the web application's SELinux security context:

.. code-block:: ini

	[uwsgi]
	...
	hook-as-user = callret:setcon system_u:system_r:webapp_id_t:s0

where id is the identity of the domain. Example, foo is the identity of the webapp_foo_t domain.

It may be required to load libselinux in the uWSGI address space with the --dlopen option:

.. code-block:: ini

	/path/to/uwsgi --dlopen /path/to/libselinux.so
