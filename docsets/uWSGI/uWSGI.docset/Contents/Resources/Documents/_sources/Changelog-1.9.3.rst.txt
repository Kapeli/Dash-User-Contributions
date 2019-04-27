uWSGI 1.9.3
===========

Changelog 20130328


Bugfixes
********

fixed imports in the JVM build system when virtualenvs are used (Ryan Kaskel)

fixed mod_proxy_uwsgi with apache 2.4

fixed php headers generation when Status is created from the php app itself


New features
************

Pluggable configuration system (with Lua support)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

From this version you will be able to implement configurators (like the already available xml, ini, yaml, json, ldap, sqlite...)
as plugins.

The first available configurator is the Lua one (offered by the lua plugin).

This is an example configuration written in lua:

.. code-block:: lua

   config = {}

   config['immediate-uid'] = 'roberto'
   config['immediate-gid'] = 'roberto'
   config['http-socket'] = ':9090'
   config['env'] = { 'FOO=bar', 'TEST=topogigio' }
   config['module'] = 'werkzeug.testapp:test_app'

   return config

you can load it with:

.. code-block:: sh

   uwsgi --plugin lua --config config.lua

The --config option is the way to load pluggable configurators. You can even override the already available embedded configurators
with your own version.

The Emperor has already been extended to support pluggable configurators:

.. code-block:: ini

   [uwsgi]
   emperor = /etc/uwsgi/vassals
   emperor-extra-extension = .lua
   emperor-extra-extension = .foo

adding emperor-extra-extension will allows the emperor to search for the specified extension passing the config file to the vassal with the --config option.

Immediate setuid and setgid
^^^^^^^^^^^^^^^^^^^^^^^^^^^

In a recent uWSGI maling-list thread, the need to not rely on file system permissions for the tyrant mode emerged.

Albeit it is the most secure approach, two new options --immediate-uid and --immediate-gid have been added.

Setting them on top of your vassal file will force the instance to setuid()/setgid() as soon as possible and without the (theoretical) possibility to override them.

The word "theoretical" here is the key, you always need to remember that a security bug in uWSGI could allow a malicious user to change privileges, so if you really
care security (or do not trust uWSGI developers ;) always drop privileges before the vassal/instance is spawned (like in standard tyrant mode)

Honouring symlinks in tyrant mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The option --emperor-tyrant-nofollow has been added forcing the emperor to now follow symlinks when searching for uid/gid in tyrant mode.

This option allows the sysadmin to simply symlink configurations and just change the uid/gid of the symlink it self (remember to
pass the -h option to chown !!!)

The "rpcret" routing action (or usa Lua to write advanced rules)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :doc:`InternalRouting` continue to be improved.

You can already call rpc function for the routing system (to generate response bypassing WSGI/PSGI/Rack/... engines):

.. code-block:: ini

   [uwsgi]
   lua-load = myrpcfunctions.lua
   route = ^/foo/(.+)/call rpc:hello_world ${REMOTE_ADDR} $1

the hello_world rpc function is defined (and registered) in the myrpcfunctions.lua taking two arguments.

The function is called when the routing regexp matches, and its output sent to the client.

The "rpcret" works in similar way, but instead generating a response, you generate a routing return code:

.. code-block:: lua

   function choose(request_uri, remote_addr)
      print( 'REQUEST_URI is ' ..request_uri.. ' (from Lua)')
      if request_uri == '/topogigio' then
        return "goto topogigio"
      end
      return "break 500 Internal server Error !!!"
   end

   print('Hello Hello')
   uwsgi.register_rpc('choose', choose)

and the uWSGI config:

.. code-block:: ini

   [uwsgi]
   route-run = rpcret:choose ${REQUEST_URI} ${REMOTE_ADDR}
   route-run = break

   route-label = topogigio
   route-run = log:i am topogigio !!!

The 'choose' rpc function will be invoked at every request passing REQUEST_URI and REMOTE_ADDR as its argument.

The return string of the function will be used to know what to do next (from the internal ruting point of view).

Currently supported return strings are:

``next`` move to the next rule

``continue`` pass the request to the request handler

``goon`` move to the next rule with a different action

``break`` close the connection with an optional status code

``goto <label>`` goto to the specified label


Obviously rpc functions for rpcret can be written in any language/platform supported by uWSGI, but we strongly suggest to go with Lua for performance reasons
(the inpact compared to pure C code is pretty irrelevant). If you are lucky and can use LuaJit you will experiment even better performance as for this kind of job
a JIT compiler is the best approach.


Availability
************

uWSGI 1.9.3 has been released on 20130328 and can be downloaded from:

https://projects.unbit.it/downloads/uwsgi-1.9.3.tar.gz
