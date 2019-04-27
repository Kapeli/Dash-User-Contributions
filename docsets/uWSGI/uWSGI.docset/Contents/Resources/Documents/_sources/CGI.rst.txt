Running CGI scripts on uWSGI
============================

The CGI plugin provides the ability to run CGI scripts using the uWSGI server.

Web servers/clients/load balancers send requests to the uWSGI server using modifier ``9``. uWSGI then uses the variables passed from the client as CGI variables (on occasion fixing them) and calls the corresponding script/executable, re-forwarding its output to the client.

The plugin tries to resemble Apache's behavior, allowing you to run CGI scripts even on webservers that do not support CGI natively, such as Nginx.

Enabling the plugin
-------------------

The CGI plugin is by default not built in to the core. You need to build a binary with cgi embedded or build the cgi plugin.

To build a single binary with CGI support:

.. code-block:: sh

   curl http://uwsgi.it/install | bash -s cgi /tmp/uwsgi

To compile it as a plugin,

.. code-block:: sh

   python uwsgiconfig.py --plugin plugins/cgi
   
or, from sources directory:

.. code-block:: sh

   make PROFILE=cgi

Configuring CGI mode
--------------------

The ``cgi <[mountpoint=]path>`` option is the main entry point for configuring your CGI environment.

``path`` may be a directory or an executable file.
In the case of a directory, the CGI plugin will use the URI to find the path of the script. If an executable is passed, it will be run, with ``SCRIPT_NAME``, ``SCRIPT_FILENAME`` and ``PATH_INFO`` set in its environment.

The ``mountpoint`` is optional. You can use it to map different URIs to different CGI directories/scripts.


Notes
-----

* Remember to use uWSGI's resource limiting and jailing techniques (namespaces, chroot, capability, unshare....) with your CGI apps to limit the damage they might cause.
* Starting from uWSGI 2.0.2 you can have even more cheap concurrency by using async mode.
* If not mapped to a helper, each CGI script must have read and execution permissions.

Examples
--------

Example 1: Dumb CGI-enabled directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: ini

  [uwsgi]
  plugins = cgi
  socket = uwsgi.sock
  cgi = /var/www/cgi-bin

Each request will search for the specified file in :file:`/var/www/cgi-bin` and execute it.

A request to ``http://example.com/foo.cgi`` would run ``/var/www/cgi-bin/foo.cgi``.

Example 2: old-style cgi-bin directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: ini

  [uwsgi]
  plugins = cgi
  socket = uwsgi.sock
  cgi = /cgi-bin=/var/lib/cgi-bin

A call to ``http://example.com/cgi-bin/foo`` will run ``/var/lib/cgi-bin/foo``.

Example 3: restricting usage to certain extensions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We want only .cgi and .pl files to be executed:

.. code-block:: ini
  
  [uwsgi]
  plugins = cgi
  socket = uwsgi.sock
  cgi = /cgi-bin=/var/lib/cgi-bin
  cgi-allowed-ext = .cgi
  cgi-allowed-ext = .pl

Example 4: mapping scripts to interpreters using their extension
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We want to run files ending with ``.php`` in the directory ``/var/www`` via the ``php5-cgi`` binary:

.. code-block:: ini

  [uwsgi]
  plugins = cgi
  socket = uwsgi.sock
  cgi = /var/www
  cgi-allowed-ext = .php
  cgi-helper = .php=php5-cgi

If a file is run with an helper, the file to be run will not require the execute permission bit. The helper of course does.

Extension comparison is not case sensitive.

Example 5: running PHP scripts as CGI via Nginx
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Configure Nginx to pass .php requests to uWSGI, with :file:`/var/www/foo` as the document root.

.. code-block:: nginx

  location ~ .php$ {
    include uwsgi_params;
    uwsgi_param REDIRECT_STATUS 200; # required by php 5.3
    uwsgi_modifier1 9;
    uwsgi_pass 127.0.0.1:3031;
  }

And configure uWSGI like this:

.. code-block:: ini

  [uwsgi]
  plugins = cgi
  socket = 127.0.0.1:3031
  cgi = /var/www/foo
  cgi-allowed-ext = .php
  cgi-helper = .php=php5-cgi

Example 6: Concurrency
^^^^^^^^^^^^^^^^^^^^^^

By default each uWSGI worker will be able to run a single CGI script.
This mean that using one process, will block your incoming requests until the first request has been ended. 

Adding more workers will mitigate the problem, but will consume a lot of memory.

Threads are a better choice. Let's configure each worker process to run 20 worker threads and thus run 20 CGI scripts concurrently.

.. code-block:: ini

  [uwsgi]
  plugins = cgi
  threads = 20
  socket = 127.0.0.1:3031
  cgi = /var/www/foo
  cgi-allowed-ext = .php
  cgi-helper = .php=php5-cgi
  
  
Using async mode to have even more cheap concurrency:


.. code-block:: ini

  [uwsgi]
  plugins = cgi
  async = 200
  ugreen = true
  socket = 127.0.0.1:3031
  cgi = /var/www/foo
  cgi-allowed-ext = .php
  cgi-helper = .php=php5-cgi
  
this will spawn 200 coroutines, each able to manage a CGI script (with few K of memory)
  

Example 7: Mailman web interface behind Nginx
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: nginx

  location /cgi-bin/mailman {
      include uwsgi_params;
      uwsgi_modifier1 9;
      uwsgi_pass 127.0.0.1:3031;
  }


.. code-block:: ini

  [uwsgi]
  plugins = cgi
  threads = 20
  socket = 127.0.0.1:3031
  cgi = /cgi-bin/mailman=/usr/lib/cgi-bin/mailman
  cgi-index = listinfo

The ``cgi-index`` directive specifies which script is run when a path ending with a slash is requested. This way ``/cgi-bin/mailman/`` will be mapped to the ``/cgi-bin/mailman/listinfo`` script.

Example 8: Viewvc as CGI in a subdir
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using the Mountpoint option.

.. code-block:: ini

  [uwsgi]
  plugins = cgi
  threads = 20
  socket = 127.0.0.1:3031
  cgi = /viewvc=/usr/lib/cgi-bin/viewvc.cgi

Example 9: using the uWSGI HTTP router and the ``check-static`` option
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is pretty much a full-stack solution using only uWSGI running on port 8080.


.. code-block:: ini

  [uwsgi]
  plugins = http, cgi
  
  ; bind on port 8080 and use the modifier 9
  http = :8080
  http-modifier1 = 9
  
  ; set the document_root as a placeholder
  my_document_root = /var/www
  
  ; serve static files, skipping .pl and .cgi files
  check-static = %(my_document_root)
  static-skip-ext = .pl
  static-skip-ext = .cgi
  
  ; run cgi (ending in .pl or .cgi) in the document_root
  cgi = %(my_document_root)
  cgi-index = index.pl
  cgi-index = index.cgi
  cgi-allowed-ext = .pl
  cgi-allowed-ext = .cgi

Example 10: optimizing CGIs (advanced)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can avoid the overhead of re-running interpreters at each request, loading the interpreter(s) on startup and calling a function in them instead of ``execve()`` ing the interpreter itself.

The :file:`contrib/cgi_python.c` file in the source distribution is a tiny example on how to optimize Python CGI scripts.

The Python interpreter is loaded on startup, and after each ``fork()``,  ``uwsgi_cgi_run_python`` is called.

To compile the library you can use something like this:


.. code-block:: sh

  gcc -shared -o cgi_python.so -fPIC -I /usr/include/python2.7/ cgi_python.c -lpython2.7

And then map ``.py`` files to the ``uwsgi_cgi_run_python`` function.


.. code-block:: ini

  [uwsgi]
  plugins = cgi
  
  cgi = /var/www
  cgi-loadlib = ./cgi_python.so:uwsgi_cgi_load_python
  cgi-helper = .py=sym://uwsgi_cgi_run_python

}}}

Remember to prefix the symbol in the helper with ``sym://`` to enable uWSGI to find it as a loaded symbol instead of a disk file.
