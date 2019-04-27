The uWSGI FastRouter
====================

For advanced setups uWSGI includes the "fastrouter" plugin, a
proxy/load-balancer/router speaking the uwsgi protocol. It is built in by
default.  You can put it between your webserver and real uWSGI instances to
have more control over the routing of HTTP requests to your application
servers.

Getting started
---------------

First of all you have to run the fastrouter, binding it to a specific address.
Multiple addresses are supported as well.

.. code-block:: sh

    uwsgi --fastrouter 127.0.0.1:3017 --fastrouter /tmp/uwsgi.sock --fastrouter @foobar

.. note:: This is the most useless Fastrouter setup in the world.

Congratulations! You have just run the most useless Fastrouter setup in the
world. Simply binding the fastrouter to a couple of addresses will not instruct
it on how to route requests. To give it intelligence you have to tell it how to
route requests.

Way 1: --fastrouter-use-base
----------------------------

This option will tell the fastrouter to connect to a UNIX socket with the same
name of the requested host in a specified directory.

.. code-block:: sh

    uwsgi --fastrouter 127.0.0.1:3017 --fastrouter-use-base /tmp/sockets/

If you receive a request for ``example.com`` the fastrouter will forward the
request to ``/tmp/sockets/example.com``.

Way 2: --fastrouter-use-pattern
-------------------------------

Same as the previous setup but you will be able to use a pattern, with ``%s``
mapping to the requested key/hostname.

.. code-block:: sh

    uwsgi --fastrouter 127.0.0.1:3017 --fastrouter-use-pattern /tmp/sockets/%s/uwsgi.sock

Requests for ``example.com`` will be mapped to
``/tmp/sockets/example.com/uwsgi.sock``.

Way 3: --fastrouter-use-cache
-----------------------------

You can store the key/value mappings in the :doc:`uWSGI cache <Caching>`.
Choose a way to fill the cache, for instance a Python script like this...

.. code-block:: py

    import uwsgi
    # Requests for example.com on port 8000 will go to 127.0.0.1:4040
    uwsgi.cache_set("example.com:8000", "127.0.0.1:4040")
    # Requests for unbit.it will go to 127.0.0.1:4040 with the modifier1 set to 5 (perl/PSGI)
    uwsgi.cache_set("unbit.it", "127.0.0.1:4040,5")

Then run your Fastrouter-enabled server, telling it to run the script first.

.. code-block:: sh

    uwsgi --fastrouter 127.0.0.1:3017 --fastrouter-use-cache --cache 100 --file foobar.py

Way 4: --fastrouter-subscription-server
---------------------------------------

This is probably one of the best way for massive auto-scaling hosting. It uses
the :doc:`subscription server <SubscriptionServer>` to allow instances to
announce themselves and subscribe to the fastrouter.

.. code-block:: sh

    uwsgi --fastrouter 127.0.0.1:3017 --fastrouter-subscription-server 192.168.0.100:7000
    
This will spawn a subscription server on address 192.168.0.100 port 7000

Now you can spawn your instances subscribing to the fastrouter:

.. code-block:: sh

    uwsgi --socket :3031 -M --subscribe-to 192.168.0.100:7000:example.com
    uwsgi --socket :3032 -M --subscribe-to 192.168.0.100:7000:unbit.it,5 --subscribe-to 192.168.0.100:7000:uwsgi.it

As you probably noted, you can subscribe to multiple fastrouters, with multiple
keys. Multiple instances subscribing to the same fastrouter with the same key
will automatically get load balanced and monitored. Handy, isn't it?  Like with
the caching key/value store, ``modifier1`` can be set with a comma. (``,5``
above) Another feature of the subscription system is avoiding to choose ports.
You can bind instances to random port and the subscription system will send the
real value to the subscription server.

.. code-block:: sh

    uwsgi --socket 192.168.0.100:0 -M --subscribe-to 192.168.0.100:7000:example.com


Mapping files
^^^^^^^^^^^^^

If you need to specify a massive amount of keys, you can use a mapping file
instead.

.. code-block:: plain

    # mappings.txt
    unbit.it
    unbit.it:8000,5
    uwsgi.it
    projects.unbit.it

.. code-block:: sh

    uwsgi --socket :3031 -M --subscribe-to 192.168.0.100:7000:@mappings.txt

Way 5: --fastrouter-use-code-string
-----------------------------------

If Darth Vader wears a t-shirt with your face (and in some other corner cases
too), you can customize the fastrouter with code-driven mappings.  Choose a
uWSGI-supported language (like Python or Lua) and define your mapping function.

.. code-block:: py

    def get(key):
        return '127.0.0.1:3031'

.. code-block:: sh

    uwsgi --fastrouter 127.0.0.1:3017 --fastrouter-use-code-string 0:mapper.py:get

This will instruct the fastrouter to load the script ``mapper.py`` using plugin
(modifier1) 0 and call the 'get' global, passing it the key.  In the previous
example you will always route requests to 127.0.0.1:3031. Let's create
a more advanced system, for fun!

.. code-block:: py
    
    domains = {}
    domains['example.com'] = {'nodes': ('127.0.0.1:3031', '192.168.0.100:3032'), 'node': 0}
    domains['unbit.it'] = {'nodes': ('127.0.0.1:3035,5', '192.168.0.100:3035,5'), 'node': 0}
    
    DEFAULT_NODE = '192.168.0.1:1717'
    
    def get(key):
        if key not in domains:
            return DEFAULT_NODE
    
        # get the node to forward requests to
        nodes = domains[key]['nodes']
        current_node = domains[key]['node']
        value = nodes[current_node]
    
        # round robin :P
        next_node = current_node + 1
        if next_node >= len(nodes):
            next_node = 0
    
        domains[key]['node'] = next_node
    
        return value

.. code-block:: sh

    uwsgi --fastrouter 127.0.0.1:3017 --fastrouter-use-code-string 0:megamapper.py:get

With only few lines we have implemented round-robin load-balancing with a
fallback node. Pow!  You could add some form of node monitoring, starting
threads in the script, or other insane things. (Be sure to add them to the
docs!)

.. attention:: Remember to not put blocking code in your functions. The
   fastrouter is totally non-blocking, do not ruin it!

Cheap mode and shared sockets
-----------------------------

A common setup is having a webserver/proxy connected to a fastrouter and a
series of uWSGI instances subscribed to it.  Normally you'd use the webserver
node as a uWSGI instance node. This node will subscribe to the local
fastrouter. Well... don't waste cycles on that!  Shared sockets are a way to
share sockets among various uWSGI components. Let's use that to share a socket
between the fastrouter and uWSGI instance.

.. code-block:: ini

    [uwsgi]
    ;create a shared socket (the webserver will connect to it)
    shared-socket = 127.0.0.1:3031
    
    ; bind the fastrouter to the shared socket
    fastrouter = =0
    ; bind an instance to the same socket
    socket = =0
    
    ; having a master is always a good thing...
    master = true
    ; our subscription server
    fastrouter-subscription-server = 192.168.0.100:4040
    ; our app
    wsgi-file = /var/www/myheavyapp.wsgi
    ; a bunch of processes
    processes = 4
    ; and put the fastrouter in cheap mode
    fastrouter-cheap = true
    

With this setup your requests will go directly to your app (no proxy overhead)
or to the fastrouter (to pass requests to remote nodes).  When the fastrouter
is in cheap mode, it will not respond to requests until a node is available.
This means that when there are no nodes subscribed, only your local app will
respond.  When all of the nodes go down, the fastrouter will return in cheap
mode. Seeing a pattern? Another step to awesome autoscaling.


Post-buffering mode (uWSGI >= 2.0.9)
------------------------------------

The fastrouter is (by default) a streaming proxy. This means that as soon as the uwsgi packet (read: the request headers) is parsed, it is forwarded to the backend/backends.

Now, if your web-proxy is a streaming-one too (like apache, or the uWSGI http router), your app could be blocked for ages in case of a request with a body. To be more clear:

* the client starts the request sending http headers
* the web proxy receives it and send to the fastrouter
* the fastrouter receives it and send to the backend
* the client starts sending chunks of the request body (like a file upload)
* the web proxy receives them and forward to the fastrouter
* the fastrouter receives them and forward to the backend and so on

now, imagine 10 concurrent clients doing this thing and you will end with 10 application server workers (or threads) busy for un undefined amount of time. (note: this problem is amplified by the fact that generally the number of threads/process is very limited, even in async modes you have a limited of concurrent requests but it is generally so high that the problem is not so relevant)

Web-proxies like nginx are "buffered", so they wait til the whole request (and its body) has been read, and then it sends it to the backends.

You can instruct the fastrouter to behave like nginx with the ``--fastrouter-post-buffering <n>`` option, where <n> is the size of the request body after which the body will be stored to disk (as a temporary file) instead of memory:

.. code-block:: ini

   [uwsgi]
   fastrouter = 127.0.0.1:3031
   fastrouter-to = /var/run/app.socket
   fastrouter-post-buffering = 8192
   
will put the fastrouter in buffered mode, storing on a temp file every body bigger than 8192 bytes, and on memory everything lower (or equal)

Remember that post-buffering, is not a good-for-all solution (otherwise it would be the default), enabling it breaks websockets, chunked input, upload progress, iceast streaming and so on. Enable it only when needed.

Notes
-----

* The fastrouter uses the following vars (in order of precedence) to choose a key to use:

  * ``UWSGI_FASTROUTER_KEY`` - the most versatile, as it doesn't depend on the request in any way
  * ``HTTP_HOST``
  * ``SERVER_NAME``

* You can increase the number of async events the fastrouter can manage (by
  default it is system-dependent) using --fastrouter-events 

You can change the default timeout with --fastrouter-timeout By default the
fastrouter will set fd socket passing when used over unix sockets. If you do
not want it add --no-fd-passing
