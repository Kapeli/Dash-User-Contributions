Cherokee support
================

.. note::

  Recent official versions of Cherokee have an uWSGI configuration wizard. If
  you want to use it you have to install uWSGI in a directory included in your
  system ``PATH``.

* Set the UWSGI handler for your target.
* If you are using the default target (``/``) remember to uncheck the ``check_file`` property.
* Configure an "information source" of type "Remote", specifying the socket name of uWSGI. If your uWSGI has TCP support, you can build a cluster by spawning the uWSGI server on a different machine.

.. note::

  Remember to add a target for all of your URI containing static files (ex.
  /media /images ...) using an appropriate handler

Dynamic apps
------------

If you want to hot-add apps specify the ``UWSGI_SCRIPT`` var in the uWSGI handler options:

* In the section: `Add new custom environment variable` specify ``UWSGI_SCRIPT`` as name and the name of your WSGI script (without the .py extension) as the value.

Your app will be loaded automatically at the first request.
