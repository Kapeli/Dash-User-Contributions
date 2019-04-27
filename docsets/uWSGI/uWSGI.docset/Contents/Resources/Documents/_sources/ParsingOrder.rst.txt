How uWSGI parses config files
=============================

Until uWSGI 1.1 the parsing order has not been 'stable' or 'reliable'.

Starting from uWSGI 1.1 (thanks to its new options subsystem) we have a general rule: top-bottom and expand asap.

Top-bottom means options are internally ordered as they are parsed, while "expand asap" means to inject the options of a requested config file, interrupting the currently parsed one:

Note that the ``inherit`` option behaves differently from the other include options: It is expanded *after* variable expansion, so any environment variables, external files and placeholders are *not* expanded. Magic variables (*e.g.* ``%n``) are expanded normally.

file1.ini (the one requested from the command line)


.. code-block:: ini

   [uwsgi]
   socket = :3031
   ini = file2.ini
   socket = :3032
   chdir = /var/www
   
file2.ini

.. code-block:: ini

   [uwsgi]
   master = true
   memory-report = true
   processes = 4
   
internally will be assembled in:


.. code-block:: ini

   [uwsgi]
   socket = :3031
   ini = file2.ini
   master = true
   memory-report = true
   processes = 4
   socket = :3032
   chdir = /var/www
   
A more complex example:

file1.ini (the one requested from the command line)

.. code-block:: ini

   [uwsgi]
   socket = :3031
   ini = file2.ini
   socket = :3032
   chdir = /var/www
   
file2.ini

.. code-block:: ini

   [uwsgi]
   master = true
   xml = file3.xml
   memory-report = true
   processes = 4
   
file3.xml

.. code-block:: xml

   <uwsgi>
     <plugins>router_uwsgi</plugins>
     <route>^/foo uwsgi:127.0.0.1:4040,0,0</route>
   </uwsgi>
   
will result in:

.. code-block:: ini

   [uwsgi]
   socket = :3031
   ini = file2.ini
   master = true
   xml = file3.xml
   plugins = router_uwsgi
   route = ^/foo uwsgi:127.0.0.1:4040,0,0
   memory-report = true
   processes = 4
   socket = :3032
   chdir = /var/www
   

Expanding variables/placeholders
********************************

After the internal config tree is assembled, variables and placeholder substitution will be applied.

The first step is substituting all of the $(VALUE) occurrences with the value of the environment variable VALUE.

.. code-block:: ini

   [uwsgi]
   foobar = $(PATH)
   
foobar value will be the content of shell's PATH variable

The second step will expand text files embraced in @(FILENAME)

.. code-block:: ini

   [uwsgi]
   nodename = @(/etc/hostname)
   
nodename value will be the content of /etc/hostname

The last step is placeholder substitution. A placeholder is a reference to another option:

.. code-block:: ini

   [uwsgi]
   socket = :3031
   foobar = %(socket)
   

the content of foobar will be mapped to the content of socket.

A note on magic variables
*************************

Config files, support another form of variables, called 'magic' variables. As they refer to the config file itself, they will be parsed asap:


.. code-block:: ini

   [uwsgi]
   my_config_file = %p
   

The content of my_config_file will be set to %p value (the current file's absolute path) as soon as it is parsed. That means %p (or whatever magic vars you need) will be always be consistent in the currently parsing config file.
