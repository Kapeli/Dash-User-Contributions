Integrating uWSGI with Erlang
=============================

.. warning:: Erlang support is broken as of 1.9.20. A new solution is being worked on.

The uWSGI server can act as an Erlang C-Node and exchange messages and RPC with Erlang nodes.

Building
--------

First of all you need the ``ei`` libraries and headers. They are included in
the official erlang tarball. If you are on Debian/Ubuntu, install the
``erlang-dev`` package.  Erlang support can be embedded or built as a plugin.
For embedding, add the ``erlang`` and ``pyerl`` plugins to your buildconf.

.. code-block:: ini

    embedded_plugins = python, ping, nagios, rpc, fastrouter, http, ugreen, erlang, pyerl

or build both as plugins

.. code-block:: sh

    python uwsgiconfig --plugin plugins/erlang
    python uwsgiconfig --plugin plugins/pyerl

The Erlang plugin will allow uWSGI to became a Erlang C-Node. The ``pyerl``
plugin will add Erlang functions to the Python plugin.

Activating Erlang support
-------------------------

You only need to set two options to enable Erlang support in your
Erlang-enabled uWSGI build.  The ``erlang`` option sets the Erlang node name of
your uWSGI server. It may be specified in simple or extended format:

* ``nodename@ip``
* ``nodename@address``
* ``nodename``

The ``erlang-cookie`` option sets the cookie for inter-node communications. If
you do not specify it, the value is taken from the :file:`~/.erlang.cookie`
file. 

To run uWSGI with Erlang enabled:

.. code-block:: sh

    uwsgi --socket :3031 --erlang testnode@192.168.173.15 --erlang-cookie UUWSGIUWSGIU -p 2

A simple RPC hello world example
--------------------------------

* Define a new erlang module that exports only a simple function.

  .. code-block:: erlang
      
      -module(uwsgitest).
      -export([hello/0]).
      
      hello() ->
          'hello world !'.
  
* Launch the ``erl`` shell specifying the nodename and (eventually) the cookie:
  
  .. code-block:: sh
  
      erl -name testnode@192.168.173.1
  
* Compile the uwsgitest Erlang module
  
  .. code-block:: erlang
  
      c(uwsgitest).
      {ok,uwsgitest}
  
* ... and try to run the ``hello`` function:
  
  .. code-block:: erlang
  
      uwsgitest:hello().
      'hello world !'

Great - now that our Erlang module is working, we are ready for RPC!  Return to
your uWSGI server machine and define a new WSGI module -- let's call it
:file:`erhello.py`.

.. code-block:: py

    import uwsgi
    
    def application(env, start_response):
        testnode = uwsgi.erlang_connect("testnode@192.168.173.1")
        start_response('200 OK', [('Content-Type', 'text/plain')])
        yield uwsgi.erlang_rpc(testnode, "uwsgitest", "hello", [])
        uwsgi.erlang_close(testnode)

or the fast-style

.. code-block:: py

    import uwsgi
    
    def application(env, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        yield uwsgi.erlang_rpc("testnode@192.168.173.1", "uwsgitest", "hello", [])

Now relaunch the uWSGI server with this new module:

.. code-block:: xxx

    uwsgi --socket :3031 --erlang testnode@192.168.173.15 --erlang-cookie UUWSGIUWSGIU -p 2 -w erhello

Point your browser to your uWSGI enabled webserver and you should see the output of your erlang RPC call.

Python-Erlang mappings
----------------------

The uWSGI server tries to translate Erlang types to Python objects according to the table below.

==========  ====== ====
Python      Erlang note
==========  ====== ====
str         binary
unicode     atom   limited by internal atom size
int/long    int
list        list
tuple       tuple
3-tuple     pid
==========  ====== ====

Sending messages to Erlang nodes
--------------------------------

One of the most powerful features of Erlang is the inter-node message passing
system.  uWSGI can communicate with Erlang nodes as well.  Lets define a new
Erlang module that simply will echo back whatever we send to it.

.. code-block:: erlang

    -module(uwsgiecho).
    -export([start/0, loop/0, echo/1]).
    
    echo(Message) ->
            {i_am_echo , Message}.
    
    loop() ->
            receive
                    Message1 ->
                            io:format("received a message~n"),
                            { useless, 'testnode@192.168.173.15' } ! echo(Message1)
            end,
            loop().
    
    start() ->
            register(echoer, spawn(uwsgiecho, loop, [])).

Remember to register your process with the Erlang ``register`` function. Using
pids to identify processes is problematic.  Now you can send messages with
:py:meth:`uwsgi.erlang_send_message`.

.. code-block:: py

    uwsgi.erlang_send_message(node, "echoer", "Hello echo server !!!" )

The second argument is the registered process name. If you do not specify the
name, pass a 3-tuple of Python elements to be interpreted as a Pid. If your
Erlang server returns messages to your requests you can receive them with
:py:meth:`uwsgi.erlang_recv_message`. Remember that even if Erlang needs a
process name/pid to send messages, they will be blissfully ignored by uWSGI.


Receiving erlang messages
-------------------------

Sometimes you want to directly send messages from an Erlang node to the uWSGI
server. To receive Erlang messages you have to register "Erlang processes" in
your Python code.

.. code-block:: py

    import uwsgi
    
    def erman(arg):
        print "received an erlang message:", arg
    
    uwsgi.erlang_register_process("myprocess", erman)

Now from Erlang you can send messages to the "myprocess" process you registered:

.. code-block:: erlang

    { myprocess, 'testnode@192.168.173.15' } ! "Hello".


RPC
---

You can call uWSGI :doc:`RPC` functions directly from Erlang.

.. code-block:: erlang

    rpc:call('testnode@192.168.173.15', useless, myfunction, []).

this will call the "myfunction" uWSGI RPC function on a uWSGI server configured
as an Erlang node.

Connection persistence
----------------------

On high-loaded sites opening and closing connections for every Erlang
interaction is overkill. Open a connection on your app initialization with
:meth:`uwsgi.erlang_connect` and hold on to the file descriptor.

What about Mnesia?
------------------

We suggest you to use Mnesia_ when you need a high-availability site. Build an
Erlang module to expose all the database interaction you need and use
:py:meth:`uwsgi.erlang_rpc` to interact with it.

.. _Mnesia: http://en.wikipedia.org/wiki/Mnesia


Can I run EWGI_ applications on top of uWSGI?
---------------------------------------------

For now, no. The best way to do this would be to develop a plugin and assign a
special modifier for EWGI apps.

But before that happens, you can wrap the incoming request into EWGI form in
Python code and use :py:meth:`uwsgi.erlang_rpc` to call your Erlang app.

.. _EWGI: http://code.google.com/p/ewgi/wiki/EWGISpecification
