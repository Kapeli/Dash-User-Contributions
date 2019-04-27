Imperial monitors
=================


``dir://`` -- scan a directory for uWSGI config files
-----------------------------------------------------

Simply put all of your config files in a directory, then point the uWSGI
emperor to it. The Emperor will start scanning this directory. When it finds
a valid config file it will spawn a new uWSGI instance.

For our example, we're deploying a Werkzeug_ test app, a Trac_ instance, a Ruby
on Rails app and a Django_ app.

werkzeug.xml

.. code-block:: xml

  <uwsgi>
      <module>werkzeug.testapp:test_app</module>
      <master/>
      <processes>4</processes>
      <socket>127.0.0.1:3031</socket>
  </uwsgi>

trac.ini

.. code-block:: ini

  [uwsgi]
  master = true
  processes = 2
  module = trac.web.main:dispatch_request
  env = TRAC_ENV=/opt/project001
  socket = 127.0.0.1:3032

rails.yml

.. code-block:: yaml

  uwsgi:
      plugins: rack
      rack: config.ru
      master: 1
      processes: 8
      socket: 127.0.0.1:3033
      post-buffering: 4096
      chdir: /opt/railsapp001

django.ini

.. code-block:: ini

  [uwsgi]
  socket = 127.0.0.1:3034
  threads = 40
  master = 1
  env = DJANGO_SETTINGS_MODULE=myapp.settings
  module = django.core.handlers.wsgi:WSGIHandler()
  chdir = /opt/djangoapp001

Put these 4 files in a directory, for instance :file:`/etc/uwsgi/vassals` in our example, then spawn the Emperor:

.. code-block:: sh

  uwsgi --emperor /etc/uwsgi/vassals

The emperor will find the uWSGI instance configuration files in that directory
(the ``dir://`` plugin declaration is implicit) and start the daemons needed to
run them.

.. _Werkzeug: http://werkzeug.pocoo.org/
.. _Trac: http://trac.edgewall.org/
.. _Django: http://djangoproject.com/

``glob://`` -- monitor a shell pattern
--------------------------------------

``glob://`` is similar to ``dir://``, but a glob expression must be specified:

.. code-block:: sh

 uwsgi --emperor "/etc/vassals/domains/*/conf/uwsgi.xml"
 uwsgi --emperor "/etc/vassals/*.ini"

.. note:: Remember to quote the pattern, otherwise your shell will most likely
   interpret it and expand it at invocation time, which is not what you want.

As the Emperor can search for configuration files in subdirectory hierarchies,
you could have a structure like this:

.. code-block:: sh

  /opt/apps/app1/app1.xml
  /opt/apps/app1/...all the app files...
  /opt/apps/app2/app2.ini
  /opt/apps/app2/...all the app files...

and run uWSGI with:

.. code-block:: sh

  uwsgi --emperor /opt/apps/app*/app*.*


``pg://`` -- scan a PostgreSQL table for configuration
------------------------------------------------------

You can specify a query to run against a PostgreSQL database. Its result must
be a list of 3 to 6 fields defining a vassal:

1. The instance name, including a valid uWSGI config file extension. (Such as
   ``django-001.ini``)
2. A ``TEXT`` blob containing the vassal configuration, in the format based on
   the extension in field 1
3. A number representing the modification time of this row in UNIX format
   (seconds since the epoch).
4. The UID of the vassal instance. Required in :ref:`Tyrant` mode only.
5. The GID of the vassal instance. Required in :ref:`Tyrant` mode only.
6. Socket for on demand vassal activation. If specified, vassal will be run
   in on demand mode. If omitted or empty, vassal will be run normally. Go to
   :doc:`OnDemandVassals` for more information.

.. code-block:: sh

  uwsgi --plugin emperor_pg --emperor "pg://host=127.0.0.1 user=foobar dbname=emperor;SELECT name,config,ts FROM vassals"

* Whenever a new tuple is added a new instance is created and spawned with the
  config specified in the second field.
* Whenever the modification time field changes, the instance is reloaded.
* If a tuple is removed, the corresponding vassal will be destroyed.


``mongodb://`` -- Scan MongoDB collections for configuration
------------------------------------------------------------

.. code-block:: sh

  uwsgi --plugin emperor_mongodb --emperor "mongodb://127.0.0.1:27107,emperor.vassals,{enabled:1}"

This will scan all of the documents in the ``emperor.vassals`` collection
having the field ``enabled`` set to 1.  An Emperor-compliant document must
define three fields: ``name``, ``config`` and ``ts``. In :ref:`Tyrant` mode, 2
more fields are required. There is also optional ``socket`` field for on
demand vassal mode.

* ``name`` (string) is the name of the vassal (remember to give it a valid extension, like .ini)
* ``config`` (multiline string) is the vassal config in the format described by the ``name``'s extension.
* ``ts`` (date) is the timestamp of the config (Note: MongoDB internally stores the timestamp in milliseconds.)
* ``uid`` (number) is the UID to run the vassal as. Required in :ref:`Tyrant` mode only.
* ``gid`` (number) is the GID to run the vassal as. Required in :ref:`Tyrant` mode only.
* ``socket`` (string) Socket for on demand vassal activation. If specified,
  vassal will be run in on demand mode. If omitted or empty, vassal will be run
  normally. Go to :doc:`OnDemandVassals` for more information.

``amqp://`` -- Use an AMQP compliant message queue to announce events
---------------------------------------------------------------------

Set your AMQP (RabbitMQ, for instance) server address as the --emperor argument:

.. code-block:: sh

  uwsgi --plugin emperor_amqp --emperor amqp://192.168.0.1:5672

Now the Emperor will wait for messages in the ``uwsgi.emperor`` exchange. This
should be a `fanout` type exchange, but you can use other systems for your
specific needs.  Messages are simple strings containing the absolute path of a
valid uWSGI config file.

.. code-block:: python

  # The pika module is used in this example, but you're free to use whatever adapter you like.
  import pika
  # connect to RabbitMQ server
  connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.0.1'))
  # get the channel
  channel = connection.channel()
  # create the exchange (if not already available)
  channel.exchange_declare(exchange='uwsgi.emperor', type='fanout')
  # publish a new config file
  channel.basic_publish(exchange='uwsgi.emperor', routing_key='', body='/etc/vassals/mydjangoapp.xml')

The first time you launch the script, the emperor will add the new instance (if
the config file is available).  From now on every time you re-publish the
message the app will be reloaded. When you remove the config file the app is
removed too.

.. tip::

  You can subscribe all of your emperors in the various servers to this
  exchange to allow cluster-synchronized reloading/deploy.

AMQP with HTTP
^^^^^^^^^^^^^^

uWSGI :ref:`is capable of loading configuration files over
HTTP<LoadingConfig>`. This is a very handy way to dynamically generate
configuration files for massive hosting.  Simply declare the HTTP URL of the
config file in the AMQP message. Remember that it must end with one of the
valid config extensions, but under the hood it can be generated by a script.
If the HTTP URL returns a non-200 status code, the instance will be removed.

.. code-block:: python

  channel.basic_publish(exchange='uwsgi.emperor', routing_key='', body='http://example.com/confs/trac.ini')

Direct AMQP configuration
^^^^^^^^^^^^^^^^^^^^^^^^^

Configuration files may also be served directly over AMQP. The ``routing_key``
will be the (virtual) config filename, and the message will be the content of
the config file.

.. code-block:: python

  channel.basic_publish(
    exchange='uwsgi.emperor', 
    routing_key='mydomain_trac_config.ini', 
    body="""
  [uwsgi]
  socket=:3031
  env = TRAC_ENV=/accounts/unbit/trac/uwsgi
  module = trac.web.main:dispatch_request
  processes = 4""")

The same reloading rules of previous modes are valid. When you want to remove
an instance simply set an empty body as the "configuration".

.. code-block:: python

  channel.basic_publish(exchange='uwsgi.emperor', routing_key='mydomain_trac_config.ini', body='')

``zmq://`` -- ZeroMQ
--------------------

The Emperor binds itself to a ZeroMQ PULL socket, ready to receive commands.

.. code-block:: sh

   uwsgi --plugin emperor_zeromq --emperor zmq://tcp://127.0.0.1:5252

Each command is a multipart message sent over a PUSH zmq socket.  A command is
composed by at least 2 parts: ``command`` and ``name``. ``command`` is the
action to execute, while ``name`` is the name of the vassal. 4 optional parts
can be specified.

* ``config`` (a string containing the vassal config)
* ``uid`` (the user id to drop priviliges to in case of tyrant mode)
* ``gid`` (the group id to drop priviliges to in case of tyrant mode)
* ``socket`` (socket for on demand vassal activation. If specified,
  vassal will be run in on demand mode. If omitted or empty, vassal will be run
  normally. Go to :doc:`OnDemandVassals` for more information)

There are 2 kind of commands (for now):

* ``touch``
* ``destroy``

The first one is used for creating and reloading instances while the second is
for destroying.  If you do not specify a config string, the Emperor will assume
you are referring to a static file available in the Emperor current directory.

.. code-block:: python

   import zmq
   c = zmq.Context()
   s = zmq.Socket(c, zmq.PUSH)
   s.connect('tcp://127.0.0.1:5252')
   s.send_multipart(['touch','foo.ini',"[uwsgi]\nsocket=:4142"])


``zoo://`` -- Zookeeper
-----------------------

Currently in development.

``ldap://`` -- LDAP
-------------------

Currently in development.
