Configuration logic
===================

Starting from 1.1 certain logic constructs are available.

The following statements are currently supported:

* ``for`` .. ``endfor``
* ``if-dir`` / ``if-not-dir``
* ``if-env`` / ``if-not-env``
* ``if-exists`` / ``if-not-exists``
* ``if-file`` / ``if-not-file``
* ``if-opt`` / ``if-not-opt``
* ``if-reload`` / ``if-not-reload`` -- undocumented

Each of these statements exports a context value you can access with the
special placeholder ``%(_)``. For example, the "for" statement sets ``%(_)`` to
the current iterated value.

.. warning:: Recursive logic is not supported and will cause uWSGI to promptly exit.

for
---

For iterates over space-separated strings. The following three code blocks are equivalent.

.. code-block:: ini

  [uwsgi]
  master = true
  ; iterate over a list of ports
  for = 3031 3032 3033 3034 3035
  socket = 127.0.0.1:%(_)
  endfor =
  module = helloworld


.. code-block:: xml

  <uwsgi>
    <master/>
    <for>3031 3032 3033 3034 3035</for>
      <socket>127.0.0.1:%(_)</socket>
    <endfor/>
    <module>helloworld</module>
  </uwsgi>


.. code-block:: sh

  uwsgi --for="3031 3032 3033 3034 3035" --socket="127.0.0.1:%(_)" --endfor --module helloworld

Note that the for-loop is applied to each line inside the block
separately, not to the block as a whole. For example, this:

.. code-block:: ini

  [uwsgi]
  for = a b c
  socket = /var/run/%(_).socket
  http-socket = /var/run/%(_)-http.socket
  endfor =

is expanded to:

.. code-block:: ini

  [uwsgi]
  socket = /var/run/a.socket
  socket = /var/run/b.socket
  socket = /var/run/c.socket
  http-socket = /var/run/a-http.socket
  http-socket = /var/run/b-http.socket
  http-socket = /var/run/c-http.socket

if-env
------

Check if an environment variable is defined, putting its value in the context
placeholder.

.. code-block:: ini

  [uwsgi]
  if-env = PATH
  print = Your path is %(_)
  check-static = /var/www
  endif =
  socket = :3031

if-exists
---------

Check for the existence of a file or directory. The context placeholder is set
to the filename found.

.. code-block:: ini

  [uwsgi]  
  http = :9090
  ; redirect all requests if a file exists
  if-exists = /tmp/maintenance.txt
  route = .* redirect:/offline
  endif =

.. note:: The above example uses :doc:`InternalRouting`.

if-file
-------

Check if the given path exists and is a regular file. The context placeholder
is set to the filename found.

.. code-block:: xml

  <uwsgi>
    <plugins>python</plugins>
    <http-socket>:8080</http-socket>
    <if-file>settings.py</if-file>
      <module>django.core.handlers.wsgi:WSGIHandler()</module>
    <endif/>
  </uwsgi>

if-dir
------

Check if the given path exists and is a directory. The context placeholder is
set to the filename found.

.. code-block:: yaml

  uwsgi:
    socket: 4040
    processes: 2
    if-dir: config.ru
    rack: %(_)
    endif:

if-opt
------
Check if the given option is set, or has a given value. The context
placeholder is set to the value of the option reference.

To check if an option was set, pass just the option name to ``if-opt``.

.. code-block:: yaml

  uwsgi:
    cheaper: 3
    if-opt: cheaper
    print: Running in cheaper mode, with initially %(_) processes
    endif:

To check if an option was set to a specific value, pass
``option-name=value`` to ``if-opt``.

.. code-block:: yaml

  uwsgi:
    # Set busyness parameters if it was chosen
    if-opt: cheaper-algo=busyness
    cheaper-busyness-max: 25
    cheaper-busyness-min: 10
    endif:

Due to the way uWSGI parses its configs, you can only refer to options
that uWSGI has previously seen. In particular, this means:

* Only options that are set above the ``if-opt`` option are taken into
  account. This includes any options set by previous ``include`` (or
  type specific includes like ``ini``) options, but does not include
  options set by previous ``inherit`` options).
* ``if-opt`` is processed after expanding magic variables, but before
  expanding placeholders and other variables. So if you use ``if-opt``
  to compare the value of an option, check against the value as stated
  in the config file, with only the magic variables filled in.

  If you use the context placeholder ``%(_)`` inside the ``if-opt``
  block, you should be ok: any placeholders will later be expanded.
* If an option is specified multiple times, only the value of the first
  one will be seen by ``if-opt``.
* Only explicitly set values will be seen, not implicit defaults.

.. seealso:: :doc:`ParsingOrder`
