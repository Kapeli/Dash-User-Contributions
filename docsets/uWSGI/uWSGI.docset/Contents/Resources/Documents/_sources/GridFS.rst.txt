The GridFS plugin
=================

Beginning in uWSGI 1.9.5 a "GridFS" plugin is available. It exports both a
request handler and an internal routing function.  Its official modifier is
'25'. The routing instruction is "gridfs" The plugin is written in C++.

Requirements and install
************************

To build the plugin you need the ``libmongoclient`` headers (and a functioning
C++ compiler). On a Debian-like system you can do the following.

.. code-block:: sh

   apt-get install mongodb-dev g++

A build profile for gridfs is available:

.. code-block:: sh

   UWSGI_PROFILE=gridfs make

Or you can build it as plugin:

.. code-block:: sh

   python uwsgiconfig.py --plugin plugins/gridfs

For a fast installation of a monolithic build you can use the network
installer:

.. code-block:: sh

   curl http://uwsgi.it/install | bash -s gridfs /tmp/uwsgi

This will install a gridfs enabled uwsgi binary.


Standalone quickstart
*********************

This is a standalone config that blindly maps the incoming ``PATH_INFO`` to
items in the GridFS db named "test":

.. code-block:: ini

   [uwsgi]
   ; you can remove the plugin directive if you are using a uWSGI gridfs monolithic build
   plugin = gridfs
   ; bind to http port 9090
   http-socket = :9090
   ; force the modifier to be the 25th
   http-socket-modifier1 = 25
   ; map gridfs requests to the "test" db
   gridfs-mount = db=test

Assuming you have the myfile.txt file stored in your GridFS as "/myfile.txt",
run the following:

.. code-block:: sh

   curl -D /dev/stdout http://localhost:9090/myfile.txt

and you should be able to get it.

The initial slash problem
*************************

Generally ``PATH_INFO`` is prefixed with a '/'. This could cause problems in
GridFS path resolution if you are not storing the items with absolute path
names. To counteract this, you can make the ``gridfs`` plugin to skip the
initial slash:

.. code-block:: ini

   [uwsgi]
   ; you can remove the plugin directive if you are using a uWSGI gridfs monolithic build
   plugin = gridfs
   ; bind to http port 9090
   http-socket = :9090
   ; force the modifier to be the 25th
   http-socket-modifier1 = 25
   ; map gridfs requests to the "test" db
   gridfs-mount = db=test,skip_slash=1

Now instead of searching for /myfile.txt it will search for "myfile.txt".

Multiple mountpoints (and servers)
**********************************

You can mount different GridFS databases under different SCRIPT_NAME (or
UWSGI_APPID). If your web server is able to correctly manage the
``SCRIPT_NAME`` variable you do not need any additional setup (other than
--gridfs-mount). Otherwise don't forget to add the --manage-script-name option

.. code-block:: ini

   [uwsgi]
   ; you can remove the plugin directive if you are using a uWSGI gridfs monolithic build
   plugin = gridfs
   ; bind to http port 9090
   http-socket = :9090
   ; force the modifier to be the 25th
   http-socket-modifier1 = 25
   ; map gridfs requests to the "test" db
   gridfs-mount = db=test,skip_slash=1
   ; map /foo to db "wolverine" on server 192.168.173.17:4040
   gridfs-mount = mountpoint=/foo,server=192.168.173.17:4040,db=wolverine
   ; map /bar to db "storm" on server 192.168.173.30:4040
   gridfs-mount = mountpoint=/bar,server=192.168.173.30:4040,db=storm
   ; force management of the SCRIPT_NAME variable
   manage-script-name = true

.. code-block:: sh

    curl -D /dev/stdout http://localhost:9090/myfile.txt
    curl -D /dev/stdout http://localhost:9090/foo/myfile.txt
    curl -D /dev/stdout http://localhost:9090/bar/myfile.txt

This way each request will map to a different GridFS server.

Replica sets
************

If you are using a replica set, you can use it in your uWSGI config with this
syntax: <replica>server1,server2,serverN...

.. code-block:: ini

   [uwsgi]
   http-socket = :9090
   http-socket-modifier1 = 25
   gridfs-mount = server=rs0/ubuntu64.local\,raring64.local\,mrspurr-2.local,db=test

Pay attention to the backslashes used to escape the server list.

Prefixes
********

As well as removing the initial slash, you may need to prefix each item name:

.. code-block:: ini

   [uwsgi]
   http-socket = :9090
   http-socket-modifier1 = 25
   gridfs-mount = server=rs0/ubuntu64.local\,raring64.local\,mrspurr-2.local,db=test,prefix=/foobar___

A request for /test.txt will be mapped to /foobar___/test.txt

while 

.. code-block:: ini

   [uwsgi]
   http-socket = :9090
   http-socket-modifier1 = 25
   gridfs-mount = server=rs0/ubuntu64.local\,raring64.local\,mrspurr-2.local,db=test,prefix=/foobar___,skip_slash=1

will map to /foobar___test.txt

MIME types and filenames
************************

By default the MIME type of the file is derived from the filename stored in
GridFS. This filename might not map to the effectively requested URI or you may
not want to set a ``content_type`` for your response. Or you may want to allow
some other system to set it.  If you want to disable MIME type generation just
add ``no_mime=1`` to the mount options.

.. code-block:: ini

   [uwsgi]
   http-socket = :9090
   http-socket-modifier1 = 25
   gridfs-mount = server=ubuntu64.local,db=test,skip_slash=1,no_mime=1

If you want your response to set the filename using the original value (the one
stored in GridFS) add ``orig_filename=1``

.. code-block:: ini

   [uwsgi]
   http-socket = :9090
   http-socket-modifier1 = 25
   gridfs-mount = server=ubuntu64.local,db=test,skip_slash=1,no_mime=1,orig_filename=1

Timeouts
********

You can set the timeout of the low-level MongoDB operations by adding
``timeout=N`` to the options:

.. code-block:: ini

   [uwsgi]
   http-socket = :9090
   http-socket-modifier1 = 25
   ; set a 3 seconds timeout
   gridfs-mount = server=ubuntu64.local,db=test,skip_slash=1,timeout=3

MD5 and ETag headers
********************

GridFS stores an MD5 hash of each file. You can add this info to your response
headers both as ETag (MD5 in hex format) or Content-MD5 (in Base64).  Use
``etag=1`` for adding ETag header and ``md5=1`` for adding Content-MD5. There's
nothing stopping you from adding both headers to the response.

.. code-block:: ini

   [uwsgi]
   http-socket = :9090
   http-socket-modifier1 = 25
   ; set a 3 seconds timeout
   gridfs-mount = server=ubuntu64.local,db=test,skip_slash=1,timeout=3,etag=1,md5=1

Multithreading
**************

The plugin is fully thread-safe, so consider using multiple threads for
improving concurrency:

.. code-block:: ini

   [uwsgi]
   http-socket = :9090
   http-socket-modifier1 = 25
   ; set a 3 seconds timeout
   gridfs-mount = server=ubuntu64.local,db=test,skip_slash=1,timeout=3,etag=1,md5=1
   master = true
   processes = 2
   threads = 8

This will spawn 2 processes monitored by the master with 8 threads each for a
total of 16 threads.

Combining with Nginx
********************

This is not different from the other plugins:

.. code-block:: c

   location / {
       include uwsgi_params;
       uwsgi_pass 127.0.0.1:3031;
       uwsgi_modifier1 25;
   }

Just be sure to set the ``uwsgi_modifier1`` value to ensure all requests get
routed to GridFS.

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   gridfs-mount = server=ubuntu64.local,db=test,skip_slash=1,timeout=3,etag=1,md5=1
   master = true
   processes = 2
   threads = 8

The 'gridfs' internal routing action
************************************

The plugin exports a 'gridfs' action simply returning an item:

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   route = ^/foo/(.+).jpg gridfs:server=192.168.173.17,db=test,itemname=$1.jpg

The options are the same as the request plugin's, with "itemname" being the
only addition. It specifies the name of the object in the GridFS db.

Notes
*****

* If you do not specify a server address, 127.0.0.1:27017 is assumed.
* The use of the plugin in async modes is not officially supported, but may work.
* If you do not get why a request is not serving your GridFS item, consider
  adding the ``--gridfs-debug`` option. It will print the requested item in uWSGI
  logs.
