Nginx support
=============

Nginx natively includes support for upstream servers speaking the :doc:`uwsgi protocol<Protocol>` since version 0.8.40.


Configuring Nginx
-----------------

Generally you only need to include the uwsgi_params file (included in nginx distribution), and set the address of the uWSGI socket with uwsgi_pass directive

::

    uwsgi_pass unix:///tmp/uwsgi.sock;
    include uwsgi_params;

-- or if you are using TCP sockets,

::

    uwsgi_pass 127.0.0.1:3031;
    include uwsgi_params;


Then simply reload Nginx and you are ready to rock your uWSGI powered applications through Nginx.

What is the ``uwsgi_params`` file?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It's convenience, nothing more! For your reading pleasure, the contents of the file as of uWSGI 1.3::

  uwsgi_param QUERY_STRING $query_string;
  uwsgi_param REQUEST_METHOD $request_method;
  uwsgi_param CONTENT_TYPE $content_type;
  uwsgi_param CONTENT_LENGTH $content_length;
  uwsgi_param REQUEST_URI $request_uri;
  uwsgi_param PATH_INFO $document_uri;
  uwsgi_param DOCUMENT_ROOT $document_root;
  uwsgi_param SERVER_PROTOCOL $server_protocol;
  uwsgi_param REMOTE_ADDR $remote_addr;
  uwsgi_param REMOTE_PORT $remote_port;
  uwsgi_param SERVER_ADDR $server_addr;
  uwsgi_param SERVER_PORT $server_port;
  uwsgi_param SERVER_NAME $server_name;

.. seealso:: :doc:`Vars`

Clustering
----------

Nginx has a beautiful integrated cluster support for all the upstream handlers.

Add an `upstream` directive outside the server configuration block::

    upstream uwsgicluster {
      server unix:///tmp/uwsgi.sock;
      server 192.168.1.235:3031;
      server 10.0.0.17:3017;
    } 


Then modify your uwsgi_pass directive::

    uwsgi_pass uwsgicluster;

Your requests will be balanced between the uWSGI servers configured.


Dynamic apps
------------

The uWSGI server can load applications on demand when passed special vars.

uWSGI can be launched without passing it any application configuration::

  ./uwsgi -s /tmp/uwsgi.sock


If a request sets the ``UWSGI_SCRIPT`` var, the server will load the specified module::

  location / {
    root html;
    uwsgi_pass uwsgicluster;
    uwsgi_param UWSGI_SCRIPT testapp;
    include uwsgi_params;
  }

You can even configure multiple apps per-location::

  location / {
    root html;
    uwsgi_pass uwsgicluster;
    uwsgi_param UWSGI_SCRIPT testapp;
    include uwsgi_params;
  }

  location /django {
    uwsgi_pass uwsgicluster;
    include uwsgi_params;
    uwsgi_param UWSGI_SCRIPT django_wsgi;
  }  
        

Hosting multiple apps in the same process (aka managing SCRIPT_NAME and PATH_INFO)
----------------------------------------------------------------------------------

The WSGI standard dictates that ``SCRIPT_NAME`` is the variable used to select a specific application. Unfortunately
nginx is not able to rewrite PATH_INFO accordingly to SCRIPT_NAME. For such reason you need to instruct uWSGI to map specific apps
in the so called "mountpoint" and rewrite SCRIPT_NAME and PATH_INFO automatically:

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   ; mount apps
   mount = /app1=app1.py
   mount = /app2=app2.py
   ; rewrite SCRIPT_NAME and PATH_INFO accordingly
   manage-script-name = true
   
   
   
Take in account the app itself (eventually using a WSGI/Rack/PSGI middleware) can rewrite SCRIPT_NAME and PATH_INFO.

You can use the internal routing subsystem too to rewrite request vars. Especially for dynamic apps it could be a good approach.

Note: ancient uWSGI versions used to support the so called "uwsgi_modifier1 30" approach. Do not do it. it is a really ugly hack


SCRIPT_NAME is a handy convention, but you are allowed to use any "mapping way", as an example the UWSGI_APPID variable can be used to set a key
in the mountpoints table.


.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   ; mount apps
   mount = the_app1=app1.py
   mount = the_app2=app2.py


.. code-block::

   location /app1 {
    root html;
    uwsgi_pass uwsgicluster;
    uwsgi_param UWSGI_APPID the_app1;
    include uwsgi_params;
   }
   
   location /app2 {
    root html;
    uwsgi_pass uwsgicluster;
    uwsgi_param UWSGI_APPID the_app2;
    include uwsgi_params;
   }
  
  
Remember you can use nginx variables as vars value, so you could implement some form of app routing using the Host header:

.. code-block::

   location / {
    root html;
    uwsgi_pass uwsgicluster;
    uwsgi_param UWSGI_APPID $http_host;
    include uwsgi_params;
   }
   
   
now just mount your apps in uWSGI using the domain name as the mount key

.. code-block:: ini

   [uwsgi]
   socket = 127.0.0.1:3031
   ; mount apps
   mount = example.com=app1.py
   mount = foobar.it=app2.py

Static files
------------

For best performance and security, remember to configure Nginx to serve static files instead of letting your poor application handle that.

The uWSGI server can serve static files flawlessly but not as quickly and efficiently as a dedicated web server like Nginx.

For example, the Django ``/media`` path could be mapped like this::

  location /media {
    alias /var/lib/python-support/python2.6/django/contrib/admin/media;
  }

Some applications need to pass control to the UWSGI server only if the requested filename does not exist::

  location @process_in_app {
    uwsgi_pass uwsgicluster;
  }
  
  location /on-the-fly {
    try_files $uri $uri/ @process_in_app;
  }


.. admonition:: WARNING

  If used incorrectly a configuration like this may cause security problems. For your sanity's sake, double-triple-quadruple check that your application files, configuration files and any other sensitive files are outside of the root of the static files.

Virtual Hosting
---------------

You can use Nginx's virtual hosting without particular problems.

If you run "untrusted" web apps (such as those of your clients if you happen to be an ISP) you should limit their memory/address space usage and use a different `uid` for each host/application::

    server {
      listen 80;
      server_name customersite1.com;
      access_log /var/log/customersite1/access_log;
      location / {
        root /var/www/customersite1;
        uwsgi_pass 127.0.0.1:3031;
    	include uwsgi_params;
      }
    }

    server {
      listen 80;
      server_name customersite2.it;
      access_log /var/log/customersite2/access_log;
      location / {
        root /var/www/customersite2;
        uwsgi_pass 127.0.0.1:3032;
        include uwsgi_params;
      }
    }

    server {
      listen 80;
      server_name sivusto3.fi;
      access_log /var/log/customersite3/access_log;
      location / {
        root /var/www/customersite3;
        uwsgi_pass 127.0.0.1:3033;
        include uwsgi_params;
      }
    }    


The customers' applications can now be run (using the process manager of your choice, such as `rc.local`, :doc:`Upstart`, `Supervisord` or whatever strikes your fancy) with a different uid and a limited (if you want) address space for each socket::

  uwsgi --uid 1001 -w customer1app --limit-as 128 -p 3 -M -s 127.0.0.1:3031
  uwsgi --uid 1002 -w customer2app --limit-as 128 -p 3 -M -s 127.0.0.1:3032
  uwsgi --uid 1003 -w django3app --limit-as 96 -p 6 -M -s 127.0.0.1:3033

