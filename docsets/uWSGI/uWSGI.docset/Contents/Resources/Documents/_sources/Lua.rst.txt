Using Lua/WSAPI with uWSGI
==========================

Updated for uWSGI 2.0

Building the plugin
-------------------

The lua plugin is part of the official uWSGI distribution (official modifier 6) and it is availale in the plugins/lua directory.

The plugin support lua 5.1, lua 5.2 and luajit.

By default lua 5.1 is assumed

As always there are various ways to build and install Lua support:

from sources directory:

.. code-block:: sh

   make lua
   
with the installer (the resulting binary will be in /tmp/uwsgi)

.. code-block:: sh

   curl http://uwsgi.it/install | bash -s lua /tmp/uwsgi
   
or you can build it as a plugin

.. code-block:: sh

   python uwsgiconfig.py --plugin plugins/lua
   
or (if you already have a uwsgi binary)

.. code-block:: sh

   uwsgi --build-plugin plugins/lua
   
The build system (check uwsgiplugin.py in plugins/lua directory for more details) uses pkg-config to find headers and libraries.

You can specify the pkg-config module to use with the UWSGICONFIG_LUAPC environment variable.

As an example

.. code-block:: sh

   UWSGICONFIG_LUAPC=lua5.2 make lua
   
will build a uwsgi binary for lua 5.2

as well as

.. code-block:: sh

   UWSGICONFIG_LUAPC=luajit make lua
   
will build a binary with luajit

If you do not want to rely on the pkg-config tool you can manually specify the includes and library directories as well as the lib name with the following environment vars:

.. code-block:: sh

   UWSGICONFIG_LUAINC=<directory>
   UWSGICONFIG_LUALIBPATH=<directory>
   UWSGICONFIG_LUALIB=<name>
   
Why Lua ?
---------

If you came from other object oriented languages, you may find lua for web development a strange choice.

Well, you have to consider one thing when exploring Lua: it is fast, really fast and consume very few resources.

The uWSGI plugin allows you to write web applications in lua, but another purpose (if not the main one) is using Lua to
extend the uWSGI server (and your application) using the signals framework, the rpc subsystem or the simple hooks engine.

If you have slow-area in your code (independently by the language used) consider rewriting them in Lua (before dealing with C)
and use uWSGI to safely call them.

Your first WSAPI application
----------------------------

We will use the official WSAPI example, let's call it :file:`pippo.lua`:

.. code-block:: lua

  function hello(wsapi_env)
    local headers = { ["Content-type"] = "text/html" }
    local function hello_text()
      coroutine.yield("<html><body>")
      coroutine.yield("<p>Hello Wsapi!</p>")
      coroutine.yield("<p>PATH_INFO: " .. wsapi_env.PATH_INFO .. "</p>")
      coroutine.yield("<p>SCRIPT_NAME: " .. wsapi_env.SCRIPT_NAME .. "</p>")
      coroutine.yield("</body></html>")
    end
    return 200, headers, coroutine.wrap(hello_text)
  end
  
  return hello

Now run uWSGI with the ``lua`` option (remember to add ``--plugins lua`` as the
first command line option if you are using it as a plugin)

.. code-block:: sh

  ./uwsgi --http :8080 --http-modifier1 6 --lua pippo.lua

This command line starts an http router that forward requests to a single worker in which pippo.lua is loaded.

As you can see the modifier 6 is enforced.

Obviously you can directly attach uWSGI to your frontline webserver (like nginx) and bind it to a uwsgi socket:

.. code-block:: sh

  ./uwsgi --socket 127.0.0.1:3031 --lua pippo.lua

(remember to set modifier1 to 6 in your webserver of choice)

Concurrency
-----------

Basically Lua is available in all of the supported uWSGI concurrency models

you can go multiprocess:

.. code-block:: sh

  ./uwsgi --socket 127.0.0.1:3031 --lua pippo.lua --processes 8 --master
  
  
or multithread:

.. code-block:: sh

  ./uwsgi --socket 127.0.0.1:3031 --lua pippo.lua --threads 8 --master
  
or both

.. code-block:: sh

  ./uwsgi --socket 127.0.0.1:3031 --lua pippo.lua --processes 4 --threads 8 --master
  
you can run it in coroutine mode (see below) using :doc:`uGreen` as the suspend engine

.. code-block:: sh

  ./uwsgi --socket 127.0.0.1:3031 --lua pippo.lua --async 1000 --ugreen
  
Both threading and async modes will initialize a lua state each (you can see it as a whole independent lua VM)

Abusing coroutines
------------------

One of the most exciting feature of Lua are coroutines (cooperative
multithreading) support. uWSGI can benefit from this using its async engine. The
Lua plugin will initialize a ``lua_State`` for every async core. We will use a
CPU-bound version of our pippo.lua to test it:

.. code-block:: lua

  function hello(wsapi_env)
    local headers = { ["Content-type"] = "text/html" }

    local function hello_text()
      coroutine.yield("<html><body>")
      coroutine.yield("<p>Hello Wsapi!</p>")
      coroutine.yield("<p>PATH_INFO: " .. wsapi_env.PATH_INFO .. "</p>")
      coroutine.yield("<p>SCRIPT_NAME: " .. wsapi_env.SCRIPT_NAME .. "</p>")
      for i=0, 10000, 1 do
          coroutine.yield(i .. "<br/>")
      end
      coroutine.yield("</body></html>")
    end

    return 200, headers, coroutine.wrap(hello_text)
  end

  return hello

and run uWSGI with 8 async cores...

.. code-block:: sh

  ./uwsgi --socket :3031 --lua pippo.lua --async 8

And just like that, you can manage 8 concurrent requests within a single worker!

Lua coroutines do not work over C stacks (meaning you cannot manage them with your C code), but thanks to :doc:`uGreen` (the uWSGI official coroutine/greenthread engine)
you can bypass this limit.

Thanks to uGreen you can use the uWSGI async API in your Lua apps and gain a very high level of concurrency.


.. code-block:: lua

   uwsgi.async_connect
   uwsgi.wait_fd_read
   uwsgi.wait_fd_write
   uwsgi.is_connected
   uwsgi.send
   uwsgi.recv
   uwsgi.close
   uwsgi.ready_fd

Threading example
-----------------

The Lua plugin is "thread-safe" as uWSGI maps a lua_State to each internal
pthread.  For example you can run the Sputnik_ wiki engine very easily.  Use
LuaRocks_ to install Sputnik and ``versium-sqlite3``. A database-backed storage
is required as the default filesystem storage does not support being accessed
by multiple interpreters concurrently.  Create a wsapi compliant file:

.. code-block:: lua

    require('sputnik')
    return sputnik.wsapi_app.new{
      VERSIUM_STORAGE_MODULE = "versium.sqlite3", 
      VERSIUM_PARAMS = {'/tmp/sputnik.db'},
      SHOW_STACK_TRACE = true,
      TOKEN_SALT = 'xxx',
      BASE_URL       = '/',
    }

And run your threaded uWSGI server

.. code-block:: sh

  ./uwsgi --plugins lua --lua sputnik.ws --threads 20 --socket :3031

.. _Sputnik: http://sputnik.freewisdom.org/
.. _LuaRocks: http://www.luarocks.org/

A note on memory
----------------

As we all know, uWSGI is parsimonious with memory. Memory is a precious
resource. Do not trust software that does not care for your memory!  The Lua
garbage collector is automatically called (by default) after each request.

You can tune the frequency of the GC call with the ``--lua-gc-freq <n>`` option, where n
is the number of requests after the GC will be called:

.. code-block:: ini

   [uwsgi]
   plugins = lua
   socket = 127.0.0.1:3031
   processes = 4
   master = true
   lua = foobar.lua
   ; run the gc every 10 requests
   lua-gc-freq = 10
   
RPC and signals
---------------

The Lua shell
-------------

Using Lua as 'configurator'
---------------------------

uWSGI api status
----------------
