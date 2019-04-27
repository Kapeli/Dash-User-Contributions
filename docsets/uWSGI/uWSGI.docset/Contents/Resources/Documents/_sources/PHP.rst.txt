Running PHP scripts in uWSGI
============================

You can safely run PHP scripts using uWSGI's :doc:`CGI<CGI>` support. The downside of this approach is the latency caused by the spawn of a new PHP interpreter at each request.

To get far superior performance you will want to embed the PHP interpreter in the uWSGI core and use the PHP plugin.

Building
--------

A bunch of distros (such as Fedora, Red Hat and CentOS) include a ``php-embedded`` package.
Install it, along with ``php-devel`` and you should be able to build the php plugin:

.. code-block:: sh

    python uwsgiconfig.py --plugin plugins/php
    # You can set the path of the php-config script with UWSGICONFIG_PHPPATH.
    UWSGICONFIG_PHPPATH=/opt/php53/bin/php-config python uwsgiconfig.py --plugin plugins/php
    # or directly specify the directory in which you have installed your php environment
    UWSGICONFIG_PHPDIR=/opt/php53 python uwsgiconfig.py --plugin plugins/php

If you get linkage problems (such as libraries not found), install those missing packages (``ncurses-devel``, ``gmp-devel``, ``pcre-devel``...) but be warned that if you add development packages modifying the uWSGI core behaviour (``pcre`` is one of these) you _need_ to recompile the uWSGI server too, or strange problems will arise.

For distros that do not supply a libphp package (all Debian-based distros, for instance), you have to rebuild PHP with the ``--enable-embed`` flag to ``./configure``:

.. code-block:: sh

    ./configure --prefix=/usr/local --with-mysql --with-mysqli --with-pdo-mysql --with-gd --enable-mbstring --enable-embed
    # That's a good starting point

Ubuntu 10.04 (newer versions include official libphp-embed sapi)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: sh

    # Add ppa with libphp5-embed package
    sudo add-apt-repository ppa:l-mierzwa/lucid-php5
    # Update to use package from ppa
    sudo apt-get update
    # Install needed dependencies
    sudo apt-get install php5-dev libphp5-embed libonig-dev libqdbm-dev
    # Compile uWSGI PHP plugin
    python uwsgiconfig --plugin plugins/php

Multiple PHP versions
^^^^^^^^^^^^^^^^^^^^^

Sometimes (always, if you are an ISP) you might have multiple versions of PHP installed in the system. In such a case, you will need one uWSGI plugin for each version of PHP:

.. code-block:: sh

    UWSGICONFIG_PHPDIR=/opt/php51 python uwsgiconfig.py --plugin plugins/php default php51
    UWSGICONFIG_PHPDIR=/opt/php52 python uwsgiconfig.py --plugin plugins/php default php52
    UWSGICONFIG_PHPDIR=/opt/php53 python uwsgiconfig.py --plugin plugins/php default php53

'default' is the build profile of your server core. If you build uWSGI without a specific profile, it will be 'default'.

You can then load a specific plugin with ``plugins php51``, etc. You cannot load multiple PHP versions in the same uWSGI process.

Running PHP apps with nginx
---------------------------

If you have simple apps (based on file extensions) you can use something like this:

.. code-block:: nginx

    location ~ \.php$ {
        root /your_document_root;
        include uwsgi_params;
        uwsgi_modifier1 14;
        uwsgi_pass 127.0.0.1:3030;
    }
    
You might want to check for all of URIs containing the string ``.php``:

.. code-block:: nginx

    location ~ \.php {
        root /your_document_root;
        include uwsgi_params;
        uwsgi_modifier1 14;
        uwsgi_pass 127.0.0.1:3030;
    }
    
Now simply run the uWSGI server with a bunch of processes:

.. code-block:: sh

    uwsgi -s :3030 --plugin php -M -p 4
    # Or abuse the adaptive process spawning with the --cheaper option
    uwsgi -s :3030 --plugin php -M -p 40 --cheaper 4

This will allow up to 40 concurrent php requests but will try to spawn (or destroy) workers only when needed, maintaining a minimal pool of 4 processes.

Advanced configuration
----------------------

By default, the PHP plugin will happily execute whatever script you pass to it. You may want to limit it to only a subset of extensions with the ``php-allowed-ext`` option.

.. code-block:: sh

    uwsgi --plugin php --master --socket :3030 --processes 4 --php-allowed-ext .php --php-allowed-ext .inc

Run PHP apps without a frontend server
--------------------------------------

This is an example configuration with a "public" uWSGI instance running a PHP app and serving static files. It is somewhat complex for an example, but should be a good starting point for trickier configurations.

.. code-block:: ini

    [uwsgi]
    ; load the required plugins, php is loaded as the default (0) modifier
    plugins = http,0:php
    
    ; bind the http router to port 80
    http = :80
    ; leave the master running as root (to allows bind on port 80)
    master = true
    master-as-root = true
    
    ; drop privileges
    uid = serena
    gid = serena
    
    ; our working dir
    project_dir = /var/www
    
    ; chdir to it (just for fun)
    chdir = %(project_dir)
    ; check for static files in it
    check-static = %(project_dir)
    ; ...but skip .php and .inc extensions
    static-skip-ext = .php
    static-skip-ext = .inc
    ; search for index.html when a dir is requested
    static-index = index.html
    
    ; jail our php environment to project_dir
    php-docroot = %(project_dir)
    ; ... and to the .php and .inc extensions
    php-allowed-ext = .php
    php-allowed-ext = .inc
    ; and search for index.php and index.inc if required
    php-index = index.php
    php-index = index.inc
    ; set php timezone
    php-set = date.timezone=Europe/Rome
    
    ; disable uWSGI request logging
    disable-logging = true
    ; use a max of 17 processes
    processes = 17
    ; ...but start with only 2 and spawn the others on demand
    cheaper = 2
    
A more extreme example that mixes :doc:`CGI <CGI>` with PHP using :doc:`internal routing <InternalRouting>` and a dash of :doc:`configuration logic <ConfigLogic>`.

.. code-block:: ini

    [uwsgi]
    ; load plugins
    plugins-dir = /proc/unbit/uwsgi
    plugins = cgi,php,router_uwsgi
    
    ; set the docroot as a config placeholder
    docroot = /accounts/unbit/www/unbit.it
    
    ; reload whenever this config file changes
    ; %p is the full path of the current config file
    touch-reload = %p
    
    ; set process names to something meaningful
    auto-procname = true
    procname-prefix-spaced = [unbit.it]
    
    ; run with at least 2 processes but increase up to 8 when needed
    master = true
    processes = 8
    cheaper = 2
    
    ; check for static files in the docroot
    check-static = %(docroot)
    ; check for cgi scripts in the docroot
    cgi = %(docroot)
    
    logto = /proc/unbit/unbit.log
    ;rotate logs when filesize is higher than 20 megs
    log-maxsize = 20971520
    
    ; a funny cycle using 1.1 config file logic
    for = .pl .py .cgi
      static-skip-ext = %(_)
      static-index = index%(_)
      cgi-allowed-ext = %(_)
    endfor =
    
    ; map cgi modifier and helpers
    ; with this trick we do not need to give specific permissions to cgi scripts
    cgi-helper = .pl=perl
    route = \.pl$ uwsgi:,9,0
    cgi-helper = .cgi=perl
    route = \.cgi$ uwsgi:,9,0
    cgi-helper = .py=python
    route = \.py$ uwsgi:,9,0
    
    ; map php modifier as the default
    route = .* uwsgi:,14,0
    static-skip-ext = .php
    php-allowed-ext = .php
    php-allowed-ext = .inc
    php-index = index.php
    
    ; show config tree on startup, just to see
    ; how cool is 1.1 config logic
    show-config = true

uWSGI API support
-----------------

Preliminary support for some of the uWSGI API has been added in 1.1. This is the list of supported functions:

* uwsgi_version()
* uwsgi_setprocname($name)
* uwsgi_worker_id()
* uwsgi_masterpid()
* uwsgi_signal($signum)
* uwsgi_rpc($node, $func, ...)
* uwsgi_cache_get($key)
* uwsgi_cache_set($key, $value)
* uwsgi_cache_update($key, $value)
* uwsgi_cache_del($key)

Yes, this means you can call Python functions from PHP using RPC.

.. code-block:: py
    
    from uwsgidecorators import *
    
    # define a python function exported via uwsgi rpc api
    @rpc('hello')
    def hello(arg1, arg2, arg3):
        return "%s-%s-%s" (arg3, arg2, arg1)

.. code-block:: php

    Python says the value is <? echo uwsgi_rpc("", "hello", "foo", "bar", "test"); ?>

Setting the first argument of ``uwsgi_rpc`` to empty, will trigger local rpc.

Or you can share the uWSGI :doc:`cache <Caching>`...

.. code-block:: py
    
    uwsgi.cache_set("foo", "bar")

.. code-block:: php

    <? echo uwsgi_cache_get("foo"); ?>
    
    
Sessions over uWSGI caches (uWSGI >=2.0.4)
------------------------------------------

Starting from uWSGI 2.0.4, you can store PHP sessions in uWSGI caches.

.. code-block:: ini

   [uwsgi]
   plugins = php
   http-socket = :9090
   http-socket-modifier1 = 14
   ; create a cache with 1000 items named 'mysessions'
   cache2 = name=mysessions,items=1000
   ; set the 'uwsgi' session handler
   php-set = session.save_handler=uwsgi
   ; use the 'mysessions' cache for storing sessions
   php-set = session.save_path=mysessions
   
   ; or to store sessions in remote caches...
   ; use the 'foobar@192.168.173.22:3030' cache for storing sessions
   php-set = session.save_path=foobar@192.168.173.22:3030

Zend Opcode Cache (uWSGI >= 2.0.6)
----------------------------------

For some mysterious reason, the opcode cache is disabled in the embed SAPI.

You can bypass the problem by telling the PHP engine that is running under the apache SAPI (using the ``php-sapi-name`` option):

.. code-block:: ini

   [uwsgi]
   plugins = php
   php-sapi-name = apache
   http-socket = :9090
   http-socket-modifier1 = 14

ForkServer (uWSGI >= 2.1)
-------------------------

:doc:`ForkServer` is one of the main features of the 2.1 branch. It allows you to inherit your vassals from specific parents instead of the Emperor.

The PHP plugin has been extended to support a fork-server so you can have a pool of php base instances from which vassals can `fork()`. This means you can share the opcode cache and do other tricks.

Thanks to the vassal attributes in uWSGI 2.1 we can choose from which parent a vassal will call fork().

.. note::

    You need Linux kernel >= 3.4 (the feature requires ``PR_SET_CHILD_SUBREAPER``) for "solid" use. Otherwise your Emperor will not be able to correctly wait() on children (and this will slow-down your vassal's respawns, and could lead to various form of race conditions).

In the following example we will spawn 3 vassals, one (called base.ini) will initialize a PHP engine, while the others two will `fork()` from it.

.. code-block:: ini

   [uwsgi]
   ; base.ini
   
   ; force the sapi name to 'apache', this will enable the opcode cache
   early-php-sapi-name = apache
   ; load a php engine as soon as possible
   early-php = true
   
   ; ... and wait for fork() requests on /run/php_fork.socket
   fork-server = /run/php_fork.socket
   
then the 2 vassals

.. code-block:: ini

   [emperor]
   ; tell the emperor the address of the fork server
   fork-server = /run/php_fork.socket

   [uwsgi]
   ; bind to port :4001
   socket = 127.0.0.1:4001
   ; force all requests to be mapped to php
   socket-modifier1 = 14
   ; enforce a DOCUMENT_ROOT
   php-docroot = /var/www/one
   ; drop privileges
   uid = one
   gid = one


   
.. code-block:: ini

   [emperor]
   ; tell the emperor the address of the fork server
   fork-server = /run/php_fork.socket

   [uwsgi]
   ; bind to port :4002
   socket = 127.0.0.1:4002
   ; force all requests to be mapped to php
   socket-modifier1 = 14
   ; enforce a DOCUMENT_ROOT
   php-docroot = /var/www/two
   ; drop privileges
   uid = two
   gid = two
   
The two vassals are completely unrelated (even if they fork from the same parent), so you can drop privileges, have different process policies and so on.

Now spawn the Emperor:
 
 .. code-block:: sh
 
    uwsgi --emperor phpvassals/ --emperor-collect-attr fork-server --emperor-fork-server-attr fork-server
    
The ``--emperor-collect-attr`` forces the Emperor to search for the 'fork-server' attribute in the [emperor] section of the vassal file, while ``--emperor-fork-server-attr`` tells it to use this parameter as the address of the fork server.

Obviously if a vassal does not expose such an attribute, it will normally fork() from the Emperor.
