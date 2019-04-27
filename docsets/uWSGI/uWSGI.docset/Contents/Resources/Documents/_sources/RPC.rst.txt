uWSGI RPC Stack
===============

uWSGI contains a fast, simple, pan-and-cross-language RPC stack.

Although you may fall in love with this subsystem, try to use it only when you need it. There are plenty of higher-level RPC technologies better suited for the vast majority of situations.

That said, the uWSGI RPC subsystem shines with its performance and memory usage. As an example, if you need to split the load of a request to multiple servers, the uWSGI RPC is a great choice, as it allows you to offload tasks with very little effort.

Its biggest limit is in its "typeless" approach.

RPC functions can take up to 254 args. Each argument has to be a string with a 16 bit maximum size (65535 bytes), while the return value has to be a string (this time 64-bit, so that's not a practical limit).

.. warning:: 64 bit response length has been implemented only in uWSGI 1.9.20, older releases have 16 bit response length limit.

.. note:: RPC functions receive arguments in the form of binary strings, so every RPC exportable function must assume that each argument is a string. Every RPC function returns a binary string of 0 or more characters.

So, if you need "elegance" or strong typing, just look in another place (or roll your own typing on top of uWSGI RPC, maybe...).

Since 1.9 the RPC subsystem is fully async-friendly, so you can use it with gevent and Coro::AnyEvent etc.

Learning by example
-------------------

Let's start with a simple RPC call from ``10.0.0.1:3031`` to ``10.0.0.2:3031``.

So let's export a "hello" function on ``.2``.

.. code-block:: py

    import uwsgi

    def hello_world():
        return "Hello World"

    uwsgi.register_rpc("hello", hello_world)

This uses :py:meth:`uwsgi.register_rpc` to declare a function called "hello" to be exported. We'll start the server with ``--socket :3031``.

On the caller's side, on ``10.0.0.1``, let's declare the world's (second) simplest WSGI app.

.. code-block:: py

    import uwsgi

    def application(env, start_response):
        start_response('200 Ok', [('Content-Type', 'text/html')])
        return uwsgi.rpc('10.0.0.2:3031', 'hello')

That's it!

You need Perl?
^^^^^^^^^^^^^^

.. code-block:: perl
    #!/usr/bin/perl

    sub hello_world {
        return("hello world -- the time is: ".time());
        }

    uwsgi::register_rpc("hello",\&hello_world);

Or perhaps you want to call an RPC function from a standalone perl script?

.. code-block:: perl
    #!/usr/bin/perl
    use Net::uwsgi;
    print Dumper(Net::uwsgi::uwsgi_rpc('127.0.0.1:3031','hello'));


What about, let's say, Lua?
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Glad you asked. If you want to export functions in Lua, simply do:

.. code-block:: lua

    function hello_with_args(arg1, arg2)
        return 'args are '..arg1..' '..arg2
    end

    uwsgi.register_rpc('hellolua', hello_with_args)

And in your Python WSGI app:

.. code-block:: py

    import uwsgi

    def application(env, start_response):
        start_response('200 Ok', [('Content-Type', 'text/html')]
        return uwsgi.rpc('10.0.0.2:3031', 'hellolua', 'foo', 'bar')

And other languages/platforms?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Check the language specific docs, basically all of them should support registering and calling RPC functions.

You can build multi-languages app with really no effort at all and will be happily surprised about how easy it is to call :doc:`Java<JVM>` functions from Perl, JavaScript from Python and so on.


Doing RPC locally
-----------------

Doing RPC locally may sound a little silly, but if you need to call a Lua function from Python with the absolute least possible overhead, uWSGI RPC is your man.

If you want to call a RPC defined in the same server (governed by the same master, etc.), simply set the first parameter of ``uwsgi.rpc`` to None or nil, or use the convenience function :py:meth:`uwsgi.call`.

Doing RPC from the internal routing subsystem
---------------------------------------------

The RPC plugin exports a bunch of internal routing actions:

* `rpc` call the specified rpc function and send the response to the client
* `rpcnext/rpcblob` call the specified rpc function, send the response to the client and continue to the next rule
* `rpcret` calls the specified rpc function and uses its return value as the action return code (next, continue, goto ...)

.. code-block:: ini

   [uwsgi]
   route = ^/foo rpc:hello ${REQUEST_URI} ${REMOTE_ADDR}
   ; call on remote nodes
   route = ^/multi rpcnext:part1@192.168.173.100:3031
   route = ^/multi rpcnext:part2@192.168.173.100:3031
   route = ^/multi rpcnext:part3@192.168.173.100:3031


Doing RPC from nginx
--------------------

As Nginx supports low-level manipulation of the uwsgi packets sent to upstream uWSGI servers, you can do RPC directly through it. Madness!

.. code-block:: nginx

    location /call {
        uwsgi_modifier1 173;
        uwsgi_modifier2 1;

        uwsgi_param hellolua foo
        uwsgi_param bar ""

        uwsgi_pass 10.0.0.2:3031;

        uwsgi_pass_request_headers off;
        uwsgi_pass_request_body off;
    }

Zero size strings will be ignored by the uWSGI array parser, so you can safely use them when the numbers of parameters + function_name is not even.

Modifier2 is set to 1 to inform that raw strings (HTTP responses in this case) are received. Otherwise the RPC subsystem would encapsulate the output in an uwsgi protocol packet, and nginx isn't smart enough to read those.


HTTP PATH_INFO -> RPC bridge
----------------------------

XML-RPC -> RPC bridge
---------------------
