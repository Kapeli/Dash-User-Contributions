Serving static files with uWSGI (updated to 1.9)
================================================

Unfortunately you cannot live without serving static files via some protocol (HTTP, SPDY or something else).

Fortunately uWSGI has a wide series of options and micro-optimizations for serving static files.

Generally your webserver of choice (Nginx, Mongrel2, etc.) will serve static files efficiently and quickly and will simply forward dynamic requests to uWSGI backend nodes.

The uWSGI project has ISPs and PaaS (that is, the hosting market) as the main target, where generally you would want to avoid
generating disk I/O on a central server and have each user-dedicated area handle (and account for) that itself. More importantly still, you want to allow customers to customize the way they serve static assets without bothering your system administrator(s).

Mode 1: Check for a static resource before passing the request to your app
**************************************************************************

This a fairly common way of managing static files in web apps. Frameworks like Ruby on Rails and many PHP apps have used this method for ages.

Suppose your static assets are under ``/customers/foobar/app001/public``. You want to check each request has a corresponding file in that directory before passing the request to your dynamic app. The ``--check-static`` option is for you:

.. code-block:: sh

   --check-static /customers/foobar/app001/public

If uWSGI receives a request for ``/foo.png`` will first check for the existence of ``/customers/foobar/app001/public/foo.png`` and if it is not found it will invoke your app.

You can specify ``--check-static`` multiple times to specify multiple possible root paths.

.. code-block:: sh

   --check-static /customers/foobar/app001/public --check-static /customers/foobar/app001/static

uWSGI will first check for ``/customers/foobar/app001/public/foo.png``; if it does not find it it will try ``/customers/foobar/app001/static/foo.png`` before finally delegating the request to your app.

Mode 2: trust frontend's DOCUMENT_ROOT
**************************************

If your frontend (a webserver, a uWSGI corerouters...) set the ``DOCUMENT_ROOT`` value, you can instruct uWSGI to trust it as a valid directory for checking for static files with the ``--check-static-docroot`` option.

Mode 3: using static file mount points
**************************************

A more general approach is "mapping" specific request prefixes to physical directories on your file system.

The ``--static-map mountpoint=path`` is the option for you.

.. code-block:: sh

   --static-map /images=/var/www/img

If you get a request for ``/images/logo.png`` and ``/var/www/img/logo.png`` exists, it will be served. Otherwise your app will manage the request.

You can specify multiple ``--static-map`` options, even for the same mountpoint.

.. code-block:: sh

   --static-map /images=/var/www/img --static-map /images=/var/www/img2 --static-map /images=/var/www/img3

The file will be searched in each directory until it's found, or if it's not, the request will be managed by your app.

In some specific cases you may want to build the internal path in a different way, retaining the original path portion of the request. The ``--static-map2`` option will do this.

.. code-block:: sh

   --static-map2 /images=/var/www/img

A request for ``/images/logo.png`` will be looked for as ``/var/www/img/images/logo.png``.

You can ``map`` (or ``map2``) both directories and files.

.. code-block:: sh

   --static-map /images/logo.gif=/tmp/oldlogo.gif
   # (psst: put favicons here)


Mode 4: using advanced internal routing
***************************************

When mappings are not enough, advanced internal routing (available from 1.9) will be your last resort.

Thanks to the power of regular expressions you will be able to build very complex mappings.

.. code-block:: ini

   [uwsgi]
   route = /static/(.*)\.png static:/var/www/images/pngs/$1/highres.png
   route = *\.jpg static:/var/www/always_the_same_photo.jpg

Setting the index page
**********************

By default, requests for a "directory" (like / or /foo) are bypassed (if advanced internal routing is not in place).

If you want to map specific files to a "directory" request (like the venerable index.html) just use the ``--static-index`` option.

.. code-block:: sh

   --static-index index.html --static-index index.htm --static-index home.html

As with the other options, the first one matching will stop the chain.

MIME types
**********

Your HTTP/SPDY/whateveryouwant responses for static files should always return the correct mime type for the specific file to let user agents handle them correctly.

By default uWSGI builds its list of MIME types from the ``/etc/mime.types`` file. You can load additional files with the ``--mime-file``
option.

.. code-block:: sh

   --mime-file /etc/alternatives.types --mime-file /etc/apache2/mime.types

All of the files will be combined into a single auto-optimizing linked list.

Skipping specific extensions
****************************

Some platforms/languages, most-notably CGI based ones, like PHP are deployed in a very simple manner.

You simply drop them in the document root and they are executed whenever you call them.

This approach, when combined with static file serving, requires a bit of attention for avoiding your CGI/PHP/whatever to be served like static files.

The ``--static-skip-ext`` will do the trick.

A very common pattern on CGI and PHP deployment is this:

.. code-block:: sh

   --static-skip-ext .php --static-skip-ext .cgi --static-skip-ext .php4


Setting the Expires headers
***************************

When serving static files, abusing client browser caching is the path to wisdom. By default uWSGI will add a ``Last-Modified``
header to all static responses, and will honor the ``If-Modified-Since`` request header.

This might be not enough for high traffic sites. You can add automatic ``Expires`` headers using one of the following options:

* ``--static-expires-type`` will set the Expires header to the specified number of seconds for the specified MIME type.
* ``--static-expires-type-mtime`` is similar, but based on file modification time, not the current time.
* ``--static-expires`` (and ``-mtime``) will set Expires header for all of the filenames (after finishing mapping to the filesystem) matching the specified regexp.
* ``--static-expires-uri`` (and ``-mtime``) match regexps against ``REQUEST_URI``
* ``--static-expires-path-info`` (and ``-mtime``) match regexps against ``PATH_INFO``

.. code-block:: sh

   # Expire an hour from now
   --static-expires-type text/html=3600
   # Expire an hour from the file's modification time
   --static-expires-type-mtime text/html=3600
   # Same as static-expires-type, but based on a regexp:
   --static-expires /var/www/static/foo*\.jpg 3600

Transfer modes
**************

If you have developed an asynchronous/nonblocking application, serving static files directly from uWSGI is not a big problem.

All of the transfers are managed in the async way, so your app will not block during them.

In multi-process/multi-threaded modes, your processes (or threads) will be blocked during the whole transfer of the file.

For smaller files this is not a problem, but for the bigger one it's a great idea to offload their transfer to something else.

You have various ways to do this:

X-Sendfile
^^^^^^^^^^

If your web server supports the X-Sendfile header and has access to the file you want to send (for example it is on the same machine
of your application or can access it via NFS) you can avoid the transfer of the file from your app with the ``--file-serve-mode x-sendfile`` option.

With this, uWSGI will only generate response headers and the web server will be delegated to transferring the physical file.

X-Accel-Redirect
^^^^^^^^^^^^^^^^

This is currently (January 2013) supported only on Nginx. Works in the same way as X-Sendfile, the only difference
is in the option argument.

.. code-block:: sh

   --file-serve-mode x-accel-redirect

Offloading
^^^^^^^^^^ 

This is the best approach if your frontend server has no access to the static files.
It uses the :doc:`OffloadSubsystem` to delegate the file transfer to a pool of non-blocking threads.

Each one of these threads can manage thousands of file transfers concurrently.

To enable file transfer offloading just use the option ``--offload-threads`` specifying the number of threads to spawn (try to set it to the number of CPU cores to take advantage of SMP).

GZIP (uWSGI 1.9)
****************

uWSGI 1.9 can check for a ``*.gz`` variant of a static file.

Many users/sysadmins underestimate the CPU impact of on-the-fly Gzip encoding.

Compressing files every time (unless your webservers is caching them in some way) will use CPU
and you will not be able to use advanced (zero-copy) techniques like ``sendfile()``. For a very loaded site (or network) this could
be a problem (especially when gzip encoding is a need for a better, more responsive user experience).

Although uWSGI is able to compress contents on the fly (this is used in the HTTP/HTTPS/SPDY router for example), the best approach
for serving gzipped static files is generating them "manually" (but please use a script, not an intern to do this), and let uWSGI
choose if it is best to serve the uncompressed or the compressed one every time.

In this way serving gzip content will be no different from serving standard static files (sendfile, offloading...)

To trigger this behavior you have various options:

* ``static-gzip <regexp>`` checks for .gz variant for all of the requested files matching the specified regexp (the regexp is applied to the full filesystem path of the file)
* ``static-gzip-dir <dir>``/``static-gzip-prefix <prefix>`` checks for .gz variant for all of the files under the specified directory
* ``static-gzip-ext <ext>``/``static-gzip-suffix <suffix>`` check for .gz variant for all of the files with the specified extension/suffix
* ``static-gzip-all`` check for .gz variant for all requested static files

So basically if you have ``/var/www/uwsgi.c`` and ``/var/www/uwsgi.c.gz``, clients accepting gzip as their Content-Encoding will be transparently served the gzipped version instead.

Security
********

Every static mapping is fully translated to the "real" path (so symbolic links are translated too).

If the resulting path is not under the one specified in the option, a security error will be triggered and the request refused.

If you trust your UNIX skills and know what you are doing, you can add a list of "safe" paths. If a translated path
is not under a configured directory but it is under a safe one, it will be served nevertheless.

Example:

.. code-block:: sh

   --static-map /foo=/var/www/

``/var/www/test.png`` is a symlink to ``/tmp/foo.png``

After the translation of ``/foo/test.png``, uWSGI will raise a security error as ``/tmp/foo.png`` is not under ``/var/www/``.

Using

.. code-block:: sh

   --static-map /foo=/var/www/ --static-safe /tmp

will bypass that limit.

You can specify multiple ``--static-safe`` options.

Caching paths mappings/resolutions
**********************************

One of the bottlenecks in static file serving is the constant massive amount of ``stat()`` syscalls.

You can use the uWSGI caching subsystem to store mappings from URI to filesystem paths.

.. code-block:: sh

   --static-cache-paths 30

will cache each static file translation for 30 seconds in the uWSGI cache. 

From uWSGI 1.9 an updated caching subsystem has been added, allowing you to create multiple caches. If you want to store translations in a specific cache you can use ``--static-cache-paths-name <cachename>``.

Bonus trick: storing static files in the cache
**********************************************

You can directly store a static file in the uWSGI cache during startup using the option ``--load-file-in-cache <filename>`` (you can specify it multiple times). The content of the file will be stored under the key <filename>.

So please pay attention -- ``load-file-in-cache ./foo.png`` will store the item as ``./foo.png``, not its full path.

Notes
*****

* The static file serving subsystem automatically honours the If-Modified-Since HTTP request header
