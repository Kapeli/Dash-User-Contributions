uwsgi protocol magic variables
==============================

You can dynamically tune or configure various aspects of the uWSGI server using special variables passed by the web server (or in general by a uwsgi compliant client).

* For Nginx, the ``uwsgi_param <name> <value>;`` directive is used.
* For Apache, the ``SetEnv <name> <value>`` directive is used.

``UWSGI_SCHEME``
----------------

Set the URL scheme when it cannot be reliably determined. This may be used to force HTTPS (with the value ``https``), for instance.

``UWSGI_SCRIPT``
----------------

Load the specified script as a new application mapped to ``SCRIPT_NAME``. The app will obviously only be loaded once, not on each request.

::

  uwsgi_param UWSGI_SCRIPT werkzeug.testapp:test_app;
  uwsgi_param SCRIPT_NAME  /testapp;


``UWSGI_MODULE`` and ``UWSGI_CALLABLE``
---------------------------------------

Load a new app (defined as ``module:callable``) mapped into ``SCRIPT_NAME``.

::

  uwsgi_param UWSGI_MODULE werkzeug.testapp;
  uwsgi_param UWSGI_CALLABLE test_app;
  uwsgi_param SCRIPT_NAME  /testapp;


``UWSGI_PYHOME``
----------------

Dynamically set the Python :ref:`Virtualenv` for a :doc:`dynamic application<DynamicApps>`.

.. seealso:: :ref:`DynamicVirtualenv`

``UWSGI_CHDIR``
---------------

``chdir()`` to the specified directory before managing the request.

``UWSGI_FILE``
--------------

Load the specified file as a new dynamic app.

``UWSGI_TOUCH_RELOAD``
----------------------

Reload the uWSGI stack when the specified file's modification time has changed since the last request.

::

  location / {
    include uwsgi_params;
    uwsgi_param UWSGI_TOUCH_RELOAD /tmp/touchme.foo;
    uwsgi_pass /tmp/uwsgi.sock;
  }

``UWSGI_CACHE_GET``
-------------------

.. seealso:: :doc:`Caching`

Check the uWSGI cache for a specified key. If the value is found, it will be returned as raw HTTP output instead of the usual processing of the request.

::

  location / {
    include uwsgi_params;
    uwsgi_param UWSGI_CACHE_GET $request_uri;
    uwsgi_pass 127.0.0.1:3031;
  }


``UWSGI_SETENV``
----------------

Set the specified environment variable for a new dynamic app.

.. note:: To allow this in Python applications you need to enable the ``reload-os-env`` uWSGI option.

Dynamically load a Django app without using a WSGI file/module::

  location / {
    include uwsgi_params;
    uwsgi_param UWSGI_SCRIPT django.core.handlers.wsgi:WSGIHandler();
    uwsgi_param UWSGI_CHDIR /mydjangoapp_path;
    uwsgi_param UWSGI_SETENV DJANGO_SETTINGS_MODULE=myapp.settings;
  }


``UWSGI_APPID``
---------------

.. note:: Available since 0.9.9.

Bypass ``SCRIPT_NAME`` and :doc:`VirtualHosting` to let the user choose the mountpoint without limitations (or headaches).

The concept is very generic: ``UWSGI_APPID`` is the identifier of an application. If it is not found in the internal list of apps, it will be loaded.

::

  server {
      server_name server001;
      location / {
          include uwsgi_params;
          uwsgi_param UWSGI_APPID myfunnyapp;
          uwsgi_param UWSGI_FILE /var/www/app1.py
      }
  }
  
  server {
      server_name server002;
      location / {
          include uwsgi_params;
          uwsgi_param UWSGI_APPID myamazingapp;
          uwsgi_param UWSGI_FILE /var/www/app2.py
      }
  }

