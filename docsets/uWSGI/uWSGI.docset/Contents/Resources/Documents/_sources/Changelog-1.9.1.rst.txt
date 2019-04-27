uWSGI 1.9.1
===========

First minor release for the 1.9 tree.

Bugfixes
********

Fixed --req-logger after a graceful reload

Fixed a crash with the carbon plugin

Fixed signal handling when multiple workers + copy on write is in place

Fixed exception handling in the Rack plugin

The XSLT plugin
***************

The :doc:`XSLT<XSLT>` plugin has been added. It allows to apply XML transformation via request plugin or :doc:`InternalRouting`

Legion scrolls api
******************

Scrolls are text blob attached to each member of a :doc:`Legion<Legion>` cluster. We are slowly defining an api allowing developers to directly
use the legion subsystem in their apps and configurations. The addition in 1.9.1 is the uwsgi.scrolls(legion) function returning a list/array
of the current scrolls defined by the whole cluster. This is still not something fully usable (and useful) more to come soon...

On demand vassals
*****************

Another step in better resource usage for massive hosting. You can now tell the :doc:`Emperor<Emperor>` to start vassals only after the first request
to a specific socket. Combined with --idle/--die-on-idle options, you can have truly on-demand applications.

To define the socket to wait for for each vassal you have 3 options:

--emperor-on-demand-extension <ext>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

this will instruct the Emperor to check for a file named <vassal>+<ext>, if the file is available it will be read and its content used as the socket to wait for:

.. code-block:: sh

   uwsgi --emperor /etc/uwsgi/vassals --emperor-on-demand-extension .socket

supposing a myapp.ini file in /etc/uwsgi/vassals, a /etc/uwsgi/vassals/myapp.ini.socket will be searched for (and its content used as the socket name)

At the first connection, the vassal is spawned and the socket passed as the file descriptor 0. File descriptor 0 is always checked by uWSGI
so you do not need to specify a --socket option in the vassal file. This works automagically for uwsgi sockets, if you use
other protocols (like http or fastcgi) you have to specify it with the --protocol option

--emperor-on-demand-directory <dir>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is a less-versatile approach supporting only UNIX sockets. Basically the name (without extension and path) of the vassal is appended
to the specified directory + the .socket extension and used as the on-demand socket:

.. code-block:: sh

   uwsgi --emperor /etc/uwsgi/vassals --emperor-on-demand-directory /var/tmp

using the previous example, the socket /var/tmp/myapp.socket will be automatically bound

--emperor-on-demand-exec <cmd>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is what (very probably) you will use in very big deployments. Every time a new vassal is added the supplied command is run passing the vassal name
as the first argument. The STDOUT of the command is used as the socket name.

The --exec-post-app hook
************************

In addition to the other --exec-* options (used to run commands at the various server stages), a new one has been added
allowing you to run commands after the load of an application.

The pyring build profile
************************

This is a very specific build profile allowing you to automatically build a uWSGI stack with monolithic python support and modular jvm + ring honouring virtualenvs.

The cache router plugin
***********************

This has been improved, and in next releases we should be able to directly store response in the uWSGI cache only using the internal routing subsystem

Docs will be available soon

The crypto logger
*****************

If you host your applications on cloud services without persistent storage you may want to send your logs to external
systems. Sadly logs often contain sensible informations you should not transfer in clear. The new crypto logger try to solve
this issue allowing you to encrypt each log packet and send it over udp to a server able to decrypt it.

The following example

.. code-block:: sh

   uwsgi --plugin logcrypto --logger crypto:addr=192.168.173.22:1717,algo=bf-cbc,secret=ciaociao -M -p 4 -s :3031

will send each log packet to the udp server available at 192.168.173.22:1717 encrypting the text with 'ciaociao' secret key using
the blowfish cbc algorithm.

An example server is available here:

https://github.com/unbit/uwsgi/blob/master/contrib/cryptologger.rb


The rpc internal routing instruction
************************************

The "rpc" routing instruction has been added, allowing you to call rpc functions directly from the routing subsystem
and forward they output to the client.

Check the following examples:

.. code-block:: ini

   [uwsgi]
   http-socket = :9090
   route = ^/foo addheader:Content-Type: text/html
   route = ^/foo rpc:hello ${REQUEST_URI} ${HTTP_USER_AGENT}
   route = ^/bar/(.+)$ rpc:test $1 ${REMOTE_ADDR} uWSGI %V
   route = ^/pippo/(.+)$ rpc:test@127.0.0.1:4141 $1 ${REMOTE_ADDR} uWSGI %V
   import = funcs.py

Preliminary support for name resolving in the carbon plugin
***********************************************************

You can specify carbon servers using hostnames. The current code is pretty simple. Future updates will support round robin queries.

New routing conditions
**********************

New routing conditions have been added (equal,startswith,endswith,regexp) check the updated docs:

https://uwsgi-docs.readthedocs.io/en/latest/InternalRouting.html#the-internal-routing-table

The 'V' magic var
*****************

You can reference the uWSGI version string using the %V magic var in your configurations

The 'mongodb' generic plugin
****************************

This is a commodity plugin for packagers not able to access a shared libmongoclient. This basically link it in a new shared object
that can be used by the others mongodb plugin

Build profiles over network
***************************

You can now reference build profiles using urls (http, https and ftp are supported):

.. code-block:: sh

   UWSGI_PROFILE=http://uwsgi.it/psgi.ini make


Get it
******

uWSGI 1.9.1 will be available since 20130324 at this url:

https://projects.unbit.it/downloads/uwsgi-1.9.1.tar.gz



