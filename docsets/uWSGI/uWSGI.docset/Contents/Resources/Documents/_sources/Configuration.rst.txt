Configuring uWSGI
=================

uWSGI can be configured using several different methods. All configuration methods may be mixed and matched in the same invocation of uWSGI.

.. note:: Some of the configuration methods may require a specific plugin (ie. sqlite and ldap).

.. seealso:: :doc:`ConfigLogic`

The configuration system is unified, so each command line option maps 1:1 with entries in the config files.

Example:

.. code-block:: sh

   uwsgi --http-socket :9090 --psgi myapp.pl
   
can be written as

.. code-block:: ini

   [uwsgi]
   http-socket = :9090
   psgi = myapp.pl


.. _LoadingConfig:

Loading configuration files
---------------------------

uWSGI supports loading configuration files over several methods other than simple disk files::

  uwsgi --ini http://uwsgi.it/configs/myapp.ini # HTTP
  uwsgi --xml - # standard input
  uwsgi --yaml fd://0 # file descriptor
  uwsgi --json 'exec://nc 192.168.11.2:33000' # arbitrary executable

.. note::

  More esoteric file sources, such as the :doc:`Emperor<Emperor>`, embedded
  configuration (in two flavors), dynamic library symbols and ELF sections
  could also be used.

.. _MagicVars:

Magic variables
---------------

uWSGI configuration files can include "magic" variables, prefixed with a
percent sign.  Currently the following magic variables (you can access them in
Python via :py:data:`uwsgi.magic_table`) are defined.

======== ==
%v       the vassals directory (pwd)
%V       the uWSGI version
%h       the hostname
%o       the original config filename, as specified on the command line
%O       same as %o but refer to the first non-template config file
         (version 1.9.18)
%p       the absolute path of the configuration file
%P       same as %p but refer to the first non-template config file
         (version 1.9.18)
%s       the filename of the configuration file
%S       same as %s but refer to the first non-template config file
         (version 1.9.18)
%d       the absolute path of the directory containing the configuration file
%D       same as %d but refer to the first non-template config file
         (version 1.9.18)
%e       the extension of the configuration file
%E       same as %e but refer to the first non-template config file
         (version 1.9.18)
%n       the filename without extension
%N       same as %n but refer to the first non-template config file
         (version 1.9.18)
%c       the name of the directory containing the config file (version 1.3+)
%C       same as %c but refer to the first non-template config file
         (version 1.9.18)
%t       unix time (in seconds, gathered at instance startup) (version 1.9.20-dev+)
%T       unix time (in microseconds, gathered at instance startup) (version 1.9.20-dev+)
%x       the current section identifier, eg. `config.ini:section` (version 1.9-dev+)
%X       same as %x but refer to the first non-template config file
         (version 1.9.18)
%i       inode number of the file (version 2.0.1)
%I       same as %i but refer to the first non-template config file
%0..%9   a specific component of the full path of the directory containing the config file (version 1.3+)
%[       ANSI escape "\\033" (useful for printing colors)
%k       detected cpu cores (version 1.9.20-dev+)
%u       uid of the user running the process (version 2.0)
%U       username (if available, otherwise fallback to uid) of the user running the process (version 2.0)
%g       gid of the user running the process (version 2.0)
%G       group name (if available, otherwise fallback to gid) of the user running the process (version 2.0)
%j       HEX representation of the djb33x hash of the full config path
%J       same as %j but refer to the first non-template config file

======== ==

Note that most of these refer to the file they appear in, even if that
file is included from another file.

An exception are most of the uppercase versions, which refer to the
first non-template config file loaded. This means the first config file
not loaded through ``--include`` or ``--inherit``, but through for
example ``--ini``, ``--yaml`` or ``--config``. These are intended to use
with the emperor, to refer to the actual vassal config file instead of
templates included with ``--vassals-include`` or ``--vassals-inherit``.

For example, here's :file:`funnyapp.ini`.

.. code-block:: ini

  [uwsgi]
  socket = /tmp/%n.sock
  module = werkzeug.testapp:test_app
  processes = 4
  master = 1

``%n`` will be replaced with the name of the config file, without extension, so the result in this case will be

.. code-block:: ini

  [uwsgi]
  socket = /tmp/funnyapp.sock
  module = werkzeug.testapp:test_app
  processes = 4
  master = 1

.. _Placeholders:

Placeholders
------------

Placeholders are custom magic variables defined during configuration time by
setting a new configuration variable of your own devising.

.. code-block:: ini

  [uwsgi]
  ; These are placeholders...
  my_funny_domain = uwsgi.it
  set-ph = max_customer_address_space=64
  set-placeholder = customers_base_dir=/var/www
  ; And these aren't.
  socket = /tmp/sockets/%(my_funny_domain).sock
  chdir = %(customers_base_dir)/%(my_funny_domain)
  limit-as = %(max_customer_address_space)

Placeholders can be assigned directly, or using the ``set-placeholder``
/ ``set-ph`` option. These latter options can be useful to:

* Make it more explicit that you're setting placeholders instead of
  regular options.
* Set options on the commandline, since unknown options like
  ``--foo=bar`` are rejected but ``--set-placeholder foo=bar`` is ok.
* Set placeholders when strict mode is enabled.

Placeholders are accessible, like any uWSGI option, in your application code
via :py:data:`uwsgi.opt`.

.. code-block:: python

  import uwsgi
  print uwsgi.opt['customers_base_dir']

This feature can be (ab)used to reduce the number of configuration files
required by your application.

Similarly, contents of environment variables and external text files can
be included using the `$(ENV_VAR)` and `@(file_name)` syntax. See also
:doc:`ParsingOrder`.

Placeholders math (from uWSGI 1.9.20-dev)
-----------------------------------------

You can apply math formulas to placeholders using this special syntax:

.. code-block:: ini

   [uwsgi]
   foo = 17
   bar = 30
   ; total will be 50
   total = %(foo + bar + 3)
   
Remember to not miss spaces between operations.

Operations are executed in a pipeline (not in common math style):

.. code-block:: ini

   [uwsgi]
   foo = 17
   bar = 30
   total = %(foo + bar + 3 * 2)
   
'total' will be evaluated as 100:

 (((foo + bar) + 3) * 2)
 
Incremental and decremental shortcuts are available

.. code-block:: ini

   [uwsgi]
   foo = 29
   ; remember the space !!!
   bar = %(foo ++)

bar will be 30

If you do not specify an operation between two items, 'string concatenation' is assumed:

.. code-block:: ini

   [uwsgi]
   foo = 2
   bar = 9
   ; remember the space !!!
   bar = %(foo bar ++)
   
the first two items will be evaluated as '29' (not 11 as no math operation has been specified)

The '@' magic
-------------

We have already seen we can use the form @(filename) to include the contents of a file

.. code-block:: ini

   [uwsgi]
   foo = @(/tmp/foobar)
   
the truth is that '@' can read from all of the supported uwsgi schemes

.. code-block:: ini

   [uwsgi]
   ; read from a symbol
   foo = @(sym://uwsgi_funny_function)
   ; read from binary appended data
   bar = @(data://0)
   ; read from http
   test = @(http://example.com/hello)
   ; read from a file descriptor
   content = @(fd://3)
   ; read from a process stdout
   body = @(exec://foo.pl)
   ; call a function returning a char *
   characters = @(call://uwsgi_func)


Command line arguments
----------------------

Example::

  uwsgi --socket /tmp/uwsgi.sock --socket 127.0.0.1:8000 --master --workers 3

.. _ConfigEnv:

Environment variables
---------------------

When passed as environment variables, options are capitalized and prefixed with
`UWSGI_`, and dashes are substituted with underscores.

.. note::

   Several values for the same configuration variable are not supported with
   this method.

Example::

   UWSGI_SOCKET=127.0.0.1 UWSGI_MASTER=1 UWSGI_WORKERS=3 uwsgi

INI files
---------

.INI files are a standard de-facto configuration format used by many
applications. It consists of ``[section]``\ s and ``key=value`` pairs.

An example uWSGI INI configuration:

.. code-block:: ini

  [uwsgi]
  socket = /tmp/uwsgi.sock
  socket = 127.0.0.1:8000
  workers = 3
  master = true

By default, uWSGI uses the ``[uwsgi]`` section, but you can specify another
section name while loading the INI file with the syntax ``filename:section``,
that is::

  uwsgi --ini myconf.ini:app1

Alternatively, you can load another section from the same file by
omitting the filename and specifying just the section name. Note that
technically, this loads the named section from the last .ini file loaded
instead of the current one, so be careful when including other files.

.. code-block:: ini

  [uwsgi]
  # This will load the app1 section below
  ini = :app1
  # This will load the defaults.ini file
  ini = defaults.ini
  # This will load the app2 section from the defaults.ini file!
  ini = :app2

  [app1]
  plugin = rack

  [app2]
  plugin = php

* Whitespace is insignificant within lines.
* Lines starting with a semicolon (``;``) or a hash/octothorpe (``#``) are ignored as comments.
* Boolean values may be set without the value part. Simply ``master`` is thus equivalent to ``master=true``. This may not be compatible with other INI parsers such as ``paste.deploy``.
* For convenience, uWSGI recognizes bare ``.ini`` arguments specially, so the invocation ``uwsgi myconf.ini``  is equal to ``uwsgi --ini myconf.ini``.

XML files
---------

The root node should be ``<uwsgi>`` and option values text nodes.


An example:

.. code-block:: xml

  <uwsgi>
    <socket>/tmp/uwsgi.sock</socket>
    <socket>127.0.0.1:8000</socket>
    <master/>
    <workers>3</workers>
  </uwsgi>

You can also have multiple ``<uwsgi>`` stanzas in your file, marked with
different ``id`` attributes. To choose the stanza to use, specify its id after
the filename in the ``xml`` option, using a colon as a separator.  When using
this `id` mode, the root node of the file may be anything you like. This will
allow you to embed ``uwsgi`` configuration nodes in other XML files.

.. code-block:: xml

  <i-love-xml>
    <uwsgi id="turbogears"><socket>/tmp/tg.sock</socket></uwsgi>
    <uwsgi id="django"><socket>/tmp/django.sock</socket></uwsgi>
  </i-love-xml>

* Boolean values may be set without a text value.
* For convenience, uWSGI recognizes bare ``.xml`` arguments specially, so the invocation ``uwsgi myconf.xml``  is equal to ``uwsgi --xml myconf.xml``.

JSON files
----------

The JSON file should represent an object with one key-value pair, the key being
`"uwsgi"` and the value an object of configuration variables. Native JSON
lists, booleans and numbers are supported.

An example:

.. code-block:: json

  {"uwsgi": {
    "socket": ["/tmp/uwsgi.sock", "127.0.0.1:8000"],
    "master": true,
    "workers": 3
  }}

Again, a named section can be loaded using a colon after the filename.

.. code-block:: json

  {"app1": {
    "plugin": "rack"
  }, "app2": {
    "plugin": "php"
  }}

And then load this using::

  uwsgi --json myconf.json:app2

.. note::

   The `Jansson`_ library is required during uWSGI build time to enable JSON
   support.  By default the presence of the library will be auto-detected and
   JSON support will be automatically enabled, but you can force JSON support
   to be enabled or disabled by editing your build configuration.

   .. seealso:: :doc:`Install`

.. _Jansson: http://www.digip.org/jansson/

YAML files
----------

The root element should be `uwsgi`. Boolean options may be set as `true` or `1`.

An example:

.. code-block:: yaml

  uwsgi:
    socket: /tmp/uwsgi.sock
    socket: 127.0.0.1:8000
    master: 1
    workers: 3

Again, a named section can be loaded using a colon after the filename.

.. code-block:: yaml

  app1:
    plugin: rack
  app2:
    plugin: php

And then load this using::

  uwsgi --yaml myconf.yaml:app2


SQLite configuration
--------------------

.. note::

  Under construction.

LDAP configuration
------------------

LDAP is a flexible way to centralize configuration of large clusters of uWSGI
servers. Configuring it is a complex topic. See :doc:`LDAP` for more
information.
