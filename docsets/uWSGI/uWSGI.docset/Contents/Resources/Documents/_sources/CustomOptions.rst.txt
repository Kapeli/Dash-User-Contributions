Defining new options for your instances
=======================================

Sometimes the built-in options are not enough. For example, you may need to
give your customers custom options for configuring their apps on your platform.
Or you need to configure so many instances you want to simplify things such as
per-datacenter or per-server-type options.  Declaring new options for your
config files/command-line is a good way of achieving these goals.

To define new options use ``--declare-option``::

  --declare-option <option_name>=<option1=value1>[;<option2=value2>;<option3=value3>...]


An useful example could be defining a "redirect" option, using the redirect
plugin of the InternalRouting subsystem::

  --declare-option "redirect=route=\$1 redirect:\$2"


This will declare a new option called ``redirect`` that takes 2 arguments.
Those arguments will be expanded using the $-prefixed variables. Like shell
scripts, *the backslash is required to make your shell not expand these
values*.

Now you will be able to define a redirect in your config files:

.. code-block:: sh

  uwsgi --declare-option "redirect=route=\$1 redirect:\$2" --ini config.ini

Config.ini:

.. code-block:: ini

  [uwsgi]
  socket = :3031
  ; define my redirects
  redirect = ^/foo http://unbit.it
  redirect = \.jpg$ http://uwsgi.it/test
  redirect = ^/foo/bar/ /test

or directly on the command line:

.. code-block:: sh

  uwsgi --declare-option "redirect=route=\$1 redirect:\$2" --socket :3031 --redirect "^/foo http://unbit.it" --redirect "\.jpg$ http://uwsgi.it/test" --redirect "^/foo/bar/ /test"

More fun: a bunch of shortcuts
------------------------------

Now we will define new options for frequently-used apps.

Shortcuts.ini:

.. code-block:: ini

  [uwsgi]
  ; let's define a shortcut for trac (new syntax: trac=<path_to_trac_instance>)
  declare-option = trac=plugin=python;env=TRAC_ENV=$1;module=trac.web.main:dispach_request
  ; one for web2py (new syntax: web2py=<path_to_web2_py_dir>)
  declare-option = web2py=plugin=python;chdir=$1;module=wsgihandler
  ; another for flask (new syntax: flask=<path_to_your_app_entry_point>)
  declare-option = flask=plugin=python;wsgi-file=$1;callable=app

To hook up a Trac instance on /var/www/trac/fooenv:

.. code-block:: ini

  [uwsgi]
  ; include new shortcuts
  ini = shortcuts.ini
  
  ; classic options
  http = :8080
  master = true
  threads = 4
  
  ; our new option
  trac = /var/www/trac/fooenv

A config for Web2py, in XML:

.. code-block:: xml

  <uwsgi>
    <!-- import shortcuts -->
    <ini>shortcuts.ini</ini>
    <!-- run the https router with HIGH ciphers -->
    <https>:443,test.crt,test.key,HIGH</https>
  
    <master/>
    <processes>4</processes>
  
    <!-- load web2py from /var/www/we2py -->
    <web2py>/var/www/we2py</web2py>
  </uwsgi>

A trick for the Emperor: automatically import shortcuts for your vassals
------------------------------------------------------------------------

If you manage your customers/users with the :doc:`Emperor<Emperor>`, you can
configure it to automatically import your shortcuts in each vassal.

.. code-block:: sh

  uwsgi --emperor /etc/uwsgi/vassals --vassals-include /etc/uwsgi/shortcuts.ini


For multiple shortcuts use:

.. code-block:: sh

  uwsgi --emperor /etc/uwsgi/vassals --vassals-include /etc/uwsgi/shortcuts.ini --vassals-include /etc/uwsgi/shortcuts2.ini --vassals-include /etc/uwsgi/shortcuts3.ini

Or (with a bit of :doc:`configuration logic magic<ConfigLogic>`):

.. code-block:: ini

  [uwsgi]
  emperor = /etc/uwsgi/vassals
  
  for = shortcuts shortcuts2 shortcuts3
    vassals-include = /etc/uwsgi/%(_).ini
  endfor =

An advanced trick: embedding shortcuts in your uWSGI binary
-----------------------------------------------------------

uWSGI's build system allows you to embed files, be they generic files or
configuration, in the server binary.  Abusing this feature will enable you to
embed your new option shortcuts into the server binary, automagically allowing
users to use them.  To embed your shortcuts file, edit your build profile (like
:file:`buildconf/base.ini`) and set ``embed_config`` to the path of the
shortcuts file.  Rebuild your server and your new options will be available.

.. seealso:: :doc:`BuildConf`
