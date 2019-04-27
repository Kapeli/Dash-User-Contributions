The uWSGI Caching Cookbook
==========================

This is a cookbook of various caching techniques using :doc:`../InternalRouting`, :doc:`../Caching` and :doc:`../Transformations`

The examples assume a modular uWSGI build. You can ignore the 'plugins' option, if you are using a monolithic build.

Recipes are tested over uWSGI 1.9.7. Older versions may not work.

Let's start
***********

This is a simple perl/PSGI Dancer app we deploy on an http-socket with 4 processes.

.. code-block:: pl

   use Dancer;

   get '/' => sub {
           "Hello World!"
   };

   dance;

This is the uWSGI config. Pay attention to the log-micros directive. The objective of uWSGI in-memory caching is generating a response
in less than 1 millisecond (yes, this is true), so we want to get the response time logging in microseconds (thousandths of a millisecond).

.. code-block:: ini

   [uwsgi]
   ; load the PSGI plugin as the default one
   plugins = 0:psgi
   ; load the Dancer app
   psgi = myapp.pl
   ; enable the master process
   master = true
   ; spawn 4 processes
   processes = 4
   ; bind an http socket to port 9090
   http-socket = :9090
   ; log response time with microseconds resolution
   log-micros = true


Run the uWSGI instance in your terminal and just make a bunch of requests to it.

.. code-block:: sh

   curl -D /dev/stdout http://localhost:9090/

If all goes well you should see something similar in your uWSGI logs:

.. code-block:: sh

   [pid: 26586|app: 0|req: 1/1] 192.168.173.14 () {24 vars in 327 bytes} [Wed Apr 17 09:06:58 2013] GET / => generated 12 bytes in 3497 micros (HTTP/1.1 200) 4 headers in 126 bytes (0 switches on core 0)
   [pid: 26586|app: 0|req: 2/2] 192.168.173.14 () {24 vars in 327 bytes} [Wed Apr 17 09:07:14 2013] GET / => generated 12 bytes in 1134 micros (HTTP/1.1 200) 4 headers in 126 bytes (0 switches on core 0)
   [pid: 26586|app: 0|req: 3/3] 192.168.173.14 () {24 vars in 327 bytes} [Wed Apr 17 09:07:16 2013] GET / => generated 12 bytes in 1249 micros (HTTP/1.1 200) 4 headers in 126 bytes (0 switches on core 0)
   [pid: 26586|app: 0|req: 4/4] 192.168.173.14 () {24 vars in 327 bytes} [Wed Apr 17 09:07:17 2013] GET / => generated 12 bytes in 953 micros (HTTP/1.1 200) 4 headers in 126 bytes (0 switches on core 0)
   [pid: 26586|app: 0|req: 5/5] 192.168.173.14 () {24 vars in 327 bytes} [Wed Apr 17 09:07:18 2013] GET / => generated 12 bytes in 1016 micros (HTTP/1.1 200) 4 headers in 126 bytes (0 switches on core 0)


while cURL will return:

.. code-block:: txt

   HTTP/1.1 200 OK
   Server: Perl Dancer 1.3112
   Content-Length: 12
   Content-Type: text/html
   X-Powered-By: Perl Dancer 1.3112

   Hello World!

The first request on a process took about 3 milliseconds (this is normal as lot of code is executed for the first request), but the following run in about 1 millisecond.

Now we want to store the response in the uWSGI cache.

The first recipe
****************

We first create a uWSGI cache named 'mycache' with 100 slots of 64 KiB each (new options are at the end of the config) and for each request for '/' we search in it for a specific item named 'myhome'.

This time we load the ``router_cache`` plugin too (though it is built-in by default in monolithic servers).


.. code-block:: ini

   [uwsgi]
   ; load the PSGI plugin as the default one
   plugins = 0:psgi,router_cache
   ; load the Dancer app
   psgi = myapp.pl
   ; enable the master process
   master = true
   ; spawn 4 processes
   processes = 4
   ; bind an http socket to port 9090
   http-socket = :9090
   ; log response time with microseconds resolution
   log-micros = true

   ; create a cache with 100 items (default size per-item is 64k)
   cache2 = name=mycache,items=100
   ; at each request for / check for a 'myhome' item in the 'mycache' cache
   ; 'route' apply a regexp to the PATH_INFO request var
   route = ^/$ cache:key=myhome,name=mycache

Restart uWSGI and re-run the previous test with cURL. Sadly nothing will change. Why?

Because you did not instruct uWSGI to store the plugin response in the cache. You need to use the ``cachestore`` routing action...


.. code-block:: ini

   [uwsgi]
   ; load the PSGI plugin as the default one
   plugins = 0:psgi,router_cache
   ; load the Dancer app
   psgi = myapp.pl
   ; enable the master process
   master = true
   ; spawn 4 processes
   processes = 4
   ; bind an http socket to port 9090
   http-socket = :9090
   ; log response time with microseconds resolution
   log-micros = true

   ; create a cache with 100 items (default size per-item is 64k)
   cache2 = name=mycache,items=100
   ; at each request for / check for a 'myhome' item in the 'mycache' cache
   ; 'route' apply a regexp to the PATH_INFO request var
   route = ^/$ cache:key=myhome,name=mycache
   ; store each successful request (200 http status code) for '/' in the 'myhome' item
   route = ^/$ cachestore:key=myhome,name=mycache

Now re-run the test, and you should see requests going down to a range of 100-300 microseconds. The gain depends on various factors, but you should gain at least 60% in response time.

The log line reports -1 as the app id:

.. code-block:: sh

   [pid: 26703|app: -1|req: -1/2] 192.168.173.14 () {24 vars in 327 bytes} [Wed Apr 17 09:24:52 2013] GET / => generated 12 bytes in 122 micros (HTTP/1.1 200) 2 headers in 64 bytes (0 switches on core 0)

This is because when a response is served from the cache your app/plugin is not touched (in this case, no perl call is involved).

You will note less headers too:

.. code-block:: txt

   HTTP/1.1 200 OK
   Content-Type: text/html
   Content-Length: 12

   Hello World!

This is because only the body of a response is cached. By default the generated response is set as text/html but you can change it
or let the MIME type engine do the work for you (see later).

Cache them all !!!
******************

We want to cache all of our requests. Some of them returns images and css, while the others are always text/html


.. code-block:: ini

   [uwsgi]
   ; load the PSGI plugin as the default one
   plugins = 0:psgi,router_cache
   ; load the Dancer app
   psgi = myapp.pl
   ; enable the master process
   master = true
   ; spawn 4 processes
   processes = 4
   ; bind an http socket to port 9090
   http-socket = :9090
   ; log response time with microseconds resolution
   log-micros = true

   ; create a cache with 100 items (default size per-item is 64k)
   cache2 = name=mycache,items=100
   ; load the mime types engine
   mime-file = /etc/mime.types

   ; at each request starting with /img check it in the cache (use mime types engine for the content type)
   route = ^/img/(.+) cache:key=/img/$1,name=mycache,mime=1

   ; at each request ending with .css check it in the cache
   route = \.css$ cache:key=${REQUEST_URI},name=mycache,content_type=text/css

   ; fallback to text/html all of the others request
   route = .* cache:key=${REQUEST_URI},name=mycache
   ; store each successful request (200 http status code) in the 'mycache' cache using the REQUEST_URI as key
   route = .* cachestore:key=${REQUEST_URI},name=mycache


Multiple caches
***************

You may want/need to store items in different caches. We can change the previous recipe to use three different caches
for images, css and html responses.

.. code-block:: ini

   [uwsgi]
   ; load the PSGI plugin as the default one
   plugins = 0:psgi,router_cache
   ; load the Dancer app
   psgi = myapp.pl
   ; enable the master process
   master = true
   ; spawn 4 processes
   processes = 4
   ; bind an http socket to port 9090
   http-socket = :9090
   ; log response time with microseconds resolution
   log-micros = true

   ; create a cache with 100 items (default size per-item is 64k)
   cache2 = name=mycache,items=100

   ; create a cache for images with dynamic size (images can be big, so do not waste memory)
   cache2 = name=images,items=20,bitmap=1,blocks=100

   ; a cache for css (20k per-item is more than enough)
   cache2 = name=stylesheets,items=30,blocksize=20000

   ; load the mime types engine
   mime-file = /etc/mime.types

   ; at each request starting with /img check it in the 'images' cache (use mime types engine for the content type)
   route = ^/img/(.+) cache:key=/img/$1,name=images,mime=1

   ; at each request ending with .css check it in the 'stylesheets' cache
   route = \.css$ cache:key=${REQUEST_URI},name=stylesheets,content_type=text/css

   ; fallback to text/html all of the others request
   route = .* cache:key=${REQUEST_URI},name=mycache

   ; store each successful request (200 http status code) in the 'mycache' cache using the REQUEST_URI as key
   route = .* cachestore:key=${REQUEST_URI},name=mycache
   ; store images and stylesheets in the corresponding caches
   route = ^/img/ cachestore:key=${REQUEST_URI},name=images
   route = ^/css/ cachestore:key=${REQUEST_URI},name=stylesheets


Important, every matched 'cachestore' will overwrite the previous one. So we are adding .* as the first rule.

Being more aggressive, the Expires HTTP header
**********************************************

You can set an expiration for each cache item. If an item has an expire, it will be translated to HTTP Expires headers.
This means that once you have sent a cache item to the browser, it will not request it until it expires!

We use the previous recipe simply adding different expires to the items.


.. code-block:: ini

   [uwsgi]
   ; load the PSGI plugin as the default one
   plugins = 0:psgi,router_cache
   ; load the Dancer app
   psgi = myapp.pl
   ; enable the master process
   master = true
   ; spawn 4 processes
   processes = 4
   ; bind an http socket to port 9090
   http-socket = :9090
   ; log response time with microseconds resolution
   log-micros = true

   ; create a cache with 100 items (default size per-item is 64k)
   cache2 = name=mycache,items=100

   ; create a cache for images with dynamic size (images can be big, so do not waste memory)
   cache2 = name=images,items=20,bitmap=1,blocks=100

   ; a cache for css (20k per-item is more than enough)
   cache2 = name=stylesheets,items=30,blocksize=20000

   ; load the mime types engine
   mime-file = /etc/mime.types

   ; at each request starting with /img check it in the 'images' cache (use mime types engine for the content type)
   route = ^/img/(.+) cache:key=/img/$1,name=images,mime=1

   ; at each request ending with .css check it in the 'stylesheets' cache
   route = \.css$ cache:key=${REQUEST_URI},name=stylesheets,content_type=text/css

   ; fallback to text/html all of the others request
   route = .* cache:key=${REQUEST_URI},name=mycache

   ; store each successful request (200 http status code) in the 'mycache' cache using the REQUEST_URI as key
   route = .* cachestore:key=${REQUEST_URI},name=mycache,expires=60
   ; store images and stylesheets in the corresponding caches
   route = ^/img/ cachestore:key=${REQUEST_URI},name=images,expires=3600
   route = ^/css/ cachestore:key=${REQUEST_URI},name=stylesheets,expires=3600

images and stylesheets are cached for 1 hour, while html response are cached for 1 minute

Monitoring Caches
*****************

The stats server exposes cache information.

There is an ncurses-based tool (https://pypi.python.org/pypi/uwsgicachetop) using that information.


Storing GZIP variant of an object
*********************************

Back to the first recipe. We may want to store two copies of a response. The "clean" one and a gzipped one for clients supporting gzip encoding.

To enable the gzip copy you only need to choose a name for the item and pass it as the 'gzip' option of the cachestore action.

Then check for HTTP_ACCEPT_ENCODING request header. If it contains the 'gzip' word you can send it the gzip variant.

.. code-block:: ini

   [uwsgi]
   ; load the PSGI plugin as the default one
   plugins = 0:psgi,router_cache
   ; load the Dancer app
   psgi = myapp.pl
   ; enable the master process
   master = true
   ; spawn 4 processes
   processes = 4
   ; bind an http socket to port 9090
   http-socket = :9090
   ; log response time with microseconds resolution
   log-micros = true

   ; create a cache with 100 items (default size per-item is 64k)
   cache2 = name=mycache,items=100
   ; if the client support GZIP give it the gzip body
   route-if = contains:${HTTP_ACCEPT_ENCODING};gzip cache:key=gzipped_myhome,name=mycache,content_encoding=gzip
   ; else give it the clear version
   route = ^/$ cache:key=myhome,name=mycache

   ; store each successful request (200 http status code) for '/' in the 'myhome' item in gzip too
   route = ^/$ cachestore:key=myhome,gzip=gzipped_myhome,name=mycache


Storing static files in the cache for fast serving
**************************************************

You can populate a uWSGI cache on server startup with static files for fast serving them. The option --load-file-in-cache is the right tool for the job

.. code-block:: ini

   [uwsgi]
   plugins = 0:notfound,router_cache
   http-socket = :9090
   cache2 = name=files,bitmap=1,items=1000,blocksize=10000,blocks=2000
   load-file-in-cache = files /usr/share/doc/socat/index.html
   route-run = cache:key=${REQUEST_URI},name=files

You can specify all of the --load-file-in-cache directive you need but a better approach would be

.. code-block:: ini

   [uwsgi]
   plugins = router_cache
   http-socket = :9090
   cache2 = name=files,bitmap=1,items=1000,blocksize=10000,blocks=2000
   for-glob = /usr/share/doc/socat/*.html
      load-file-in-cache = files %(_)
   endfor =
   route-run = cache:key=${REQUEST_URI},name=files

this will store all of the html files in /usr/share/doc/socat.

Items are stored with the path as the key.

When a non-existent item is requested the connection is closed and you should get an ugly

.. code-block:: sh

   -- unavailable modifier requested: 0 --


This is because the internal routing system failed to manage the request, and no request plugin is available to manage the request.

You can build a better infrastructure using the simple 'notfound' plugin (it will always return a 404)

.. code-block:: ini

   [uwsgi]
   plugins = 0:notfound,router_cache
   http-socket = :9090
   cache2 = name=files,bitmap=1,items=1000,blocksize=10000,blocks=2000
   for-glob = /usr/share/doc/socat/*.html
      load-file-in-cache = files %(_)
   endfor =
   route-run = cache:key=${REQUEST_URI},name=files


You can store file in the cache as gzip too using --load-file-in-cache-gzip

This option does not allow to set the name of the cache item, so to support client iwith and without gzip support we can use 2 different caches

.. code-block:: ini

   [uwsgi]
   plugins = 0:notfound,router_cache
   http-socket = :9090
   cache2 = name=files,bitmap=1,items=1000,blocksize=10000,blocks=2000
   cache2 = name=compressedfiles,bitmap=1,items=1000,blocksize=10000,blocks=2000
   for-glob = /usr/share/doc/socat/*.html
      load-file-in-cache = files %(_)
      load-file-in-cache-gzip = compressedfiles %(_)
   endfor =
   ; take the item from the compressed cache
   route-if = contains:${HTTP_ACCEPT_ENCODING};gzip cache:key=${REQUEST_URI},name=compressedfiles,content_encoding=gzip
   ; fallback to the uncompressed one
   route-run = cache:key=${REQUEST_URI},name=files

Caching for authenticated users
*******************************

If you authenticate users with http basic auth, you can differentiate caching for each one using the ${REMOTE_USER} request variable:


.. code-block:: ini

   [uwsgi]
   ; load the PSGI plugin as the default one
   plugins = 0:psgi,router_cache
   ; load the Dancer app
   psgi = myapp.pl
   ; enable the master process
   master = true
   ; spawn 4 processes
   processes = 4
   ; bind an http socket to port 9090
   http-socket = :9090
   ; log response time with microseconds resolution
   log-micros = true

   ; create a cache with 100 items (default size per-item is 64k)
   cache2 = name=mycache,items=100
   ; check if the user is authenticated
   route-if-not = empty:${REMOTE_USER} goto:cacheme
   route-run = break:

   ; the following rules are executed only if REMOTE_USER is defined
   route-label = cacheme
   route = ^/$ cache:key=myhome_for_${REMOTE_USER},name=mycache
   ; store each successful request (200 http status code) for '/'
   route = ^/$ cachestore:key=myhome_for_${REMOTE_USER},name=mycache


Cookie-based authentication is generally more complex, but the vast majority of time a session id is passed as a cookie.

You may want to use this session_id as the key

.. code-block:: ini

   [uwsgi]
   ; load the PHP plugin as the default one
   plugins = 0:php,router_cache
   ; enable the master process
   master = true
   ; spawn 4 processes
   processes = 4
   ; bind an http socket to port 9090
   http-socket = :9090
   ; log response time with microseconds resolution
   log-micros = true

   ; create a cache with 100 items (default size per-item is 64k)
   cache2 = name=mycache,items=100
   ; check if the user is authenticated
   route-if-not = empty:${cookie[PHPSESSID]} goto:cacheme
   route-run = break:

   ; the following rules are executed only if the PHPSESSID cookie is defined
   route-label = cacheme
   route = ^/$ cache:key=myhome_for_${cookie[PHPSESSID]},name=mycache
   ; store each successful request (200 http status code) for '/'
   route = ^/$ cachestore:key=myhome_for_${cookie[PHPSESSID]},name=mycache


Obviously a malicious user could build a fake session id and could potentially fill your cache. You should always check
the session id. There is no single solution, but a good example for file-based php session is the following one:

.. code-block:: ini

   [uwsgi]
   ; load the PHP plugin as the default one
   plugins = 0:php,router_cache
   ; enable the master process
   master = true
   ; spawn 4 processes
   processes = 4
   ; bind an http socket to port 9090
   http-socket = :9090
   ; log response time with microseconds resolution
   log-micros = true

   ; create a cache with 100 items (default size per-item is 64k)
   cache2 = name=mycache,items=100
   ; check if the user is authenticated
   route-if-not = empty:${cookie[PHPSESSID]} goto:cacheme
   route-run = break:

   ; the following rules are executed only if the PHPSESSID cookie is defined
   route-label = cacheme
   ; stop if the session file does not exist
   route-if-not = isfile:/var/lib/php5/sessions/sess_${cookie[PHPSESSID]} break:
   route = ^/$ cache:key=myhome_for_${cookie[PHPSESSID]},name=mycache
   ; store each successful request (200 http status code) for '/'
   route = ^/$ cachestore:key=myhome_for_${cookie[PHPSESSID]},name=mycache

Caching to files
****************

Sometimes, instead of caching in memory you want to store static files.

The transformation_tofile plugin allows you to store responses in files:

.. code-block:: ini

   [uwsgi]
   ; load the PHP plugin as the default one
   plugins = 0:psgi,transformation_tofile,router_static
   ; load the Dancer app
   psgi = myapp.pl
   ; enable the master process
   master = true
   ; spawn 4 processes
   processes = 4
   ; bind an http socket to port 9090
   http-socket = :9090
   ; log response time with microseconds resolution
   log-micros = true

   ; check if a file exists
   route-if = isfile:/var/www/cache/${hex[PATH_INFO]}.html static:/var/www/cache/${hex[PATH_INFO]}.html
   ; otherwise store the response in it
   route-run = tofile:/var/www/cache/${hex[PATH_INFO]}.html

the hex[] routing var take a request variable content and encode it in hexadecimal. As PATH_INFO tend to contains / it is a better approach than storing
full path names (or using other encoding scheme like base64 that can include slashes too)
