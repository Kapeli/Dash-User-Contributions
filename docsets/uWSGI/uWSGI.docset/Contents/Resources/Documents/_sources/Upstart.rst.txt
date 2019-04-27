Running uWSGI via Upstart
=========================

Upstart is the init system of Ubuntu-like distributions.

It is based on declarative configuration files -- not shell scripts of yore -- that are put in the :file:`/etc/init` directory.

A simple script (/etc/init/uwsgi.conf)
--------------------------------------

.. code-block:: upstart

    # simple uWSGI script
    
    description "uwsgi tiny instance"
    start on runlevel [2345]
    stop on runlevel [06]
    
    respawn
    
    exec uwsgi --master --processes 4 --die-on-term --socket :3031 --wsgi-file /var/www/myapp.wsgi
    
Using the Emperor
-----------------

.. seealso:: :doc:`Emperor`

A better approach than init files for each app would be to only start an Emperor via Upstart and let it deal with the rest.

.. code-block:: upstart

    # Emperor uWSGI script
    
    description "uWSGI Emperor"
    start on runlevel [2345]
    stop on runlevel [06]
    
    respawn
    
    exec uwsgi --emperor /etc/uwsgi

If you want to run the Emperor under the master process (for accessing advanced features) remember to add --die-on-term


.. code-block:: upstart

    # Emperor uWSGI script
    
    description "uWSGI Emperor"
    start on runlevel [2345]
    stop on runlevel [06]
    
    respawn
    
    exec uwsgi --master --die-on-term --emperor /etc/uwsgi
    
What is --die-on-term?
----------------------

By default uWSGI maps the SIGTERM signal to "a brutal reload procedure".

However, Upstart uses SIGTERM to completely shutdown processes. ``die-on-term`` inverts the meanings of SIGTERM and SIGQUIT to uWSGI.

The first will shutdown the whole stack, the second one will brutally reload it.

Socket activation (from Ubuntu 12.04)
-------------------------------------

Newer Upstart releases have an Inetd-like feature that lets processes start when connections are made to specific sockets.

You can use this feature to start uWSGI only when a client (or the webserver) first connects to it.

The 'start on socket' directive will trigger the behaviour.

You do not need to specify the socket in uWSGI as it will be passed to it by Upstart itself.

.. code-block:: upstart

    # simple uWSGI script
    
    description "uwsgi tiny instance"
    start on socket PROTO=inet PORT=3031
    stop on runlevel [06]
    
    respawn
    
    exec uwsgi --master --processes 4 --die-on-term --wsgi-file /var/www/myapp.wsgi

