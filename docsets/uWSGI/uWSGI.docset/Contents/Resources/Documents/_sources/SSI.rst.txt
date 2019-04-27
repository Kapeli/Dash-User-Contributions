SSI (Server Side Includes) plugin
=================================

Server Side Includes are an "old-fashioned" way to write dynamic web pages.

It is generally recognized as a templating system instead of a full featured language.

The main purpose of the uWSGI SSI plugin is to have a fast templating system that has access to the uWSGI API.

At the time of writing, March 2013, the plugin is beta quality and implements less than 30% of the SSI standard, the focus being in exposing uWSGI API as SSI commands.

Using it as a request handler
*****************************

The plugin has an official modifier1, number 19.

.. code-block:: ini

   [uwsgi]
   plugin = ssi
   http = :9090
   http-modifier1 = 19
   http-var = DOCUMENT_ROOT=/var/www

The plugin builds the filename as ``DOCUMENT_ROOT``+``PATH_INFO``. This file is then parsed as a server side include document.

Both ``DOCUMENT_ROOT`` and ``PATH_INFO`` are required, otherwise a 500 error will be returned.

An example configuration for Nginx would be:

.. code-block:: c

   location ~ \.shtml$ {
       root /var/www;
       include uwsgi_params;
       uwsgi_pass 127.0.0.1:3031;
       uwsgi_modifier1 19;
   }

with something like this for uWSGI...

.. code-block:: ini

   [uwsgi]
   plugin = ssi
   socket = 127.0.0.1:3031

Using SSI as a routing action
*****************************

A more versatile approach is using the SSI parser as a routing action.

.. code-block:: ini

   [uwsgi]
   plugin = ssi
   http-socket = :9090
   route = ^/(.*) ssi:/var/www/$1.shtml

.. warning:: As with all of the routing actions, no check on file paths is made to allow a higher level of customization. If you pass untrusted paths to the SSI action, you should sanitize them (you can use routing again, checking for the presence of .. or other dangerous symbols).

And with the above admonition in mind, when used as a routing action, ``DOCUMENT_ROOT`` or ``PATH_INFO`` are not required, as the parameter passed contains the full filesystem path.

Supported SSI commands
**********************

This is the list of supported commands (and their arguments). If a command is not part of the SSI standard (that is, it's uWSGI specific) it will be reported.

echo
^^^^

Arguments: ``var``

Print the content of the specified request variable.

printenv
^^^^^^^^

Print a list of all request variables.

include
^^^^^^^

Arguments: ``file``

Include the specified file (relative to the current directory).

cache
^^^^^

.. note:: This is uWSGI specific/non-standard.

Arguments: ``key`` ``name``

Print the value of the specified cache key in the named cache.

Status
******

* The plugin is fully thread safe and very fast.
* Very few commands are available, more will be added soon.
