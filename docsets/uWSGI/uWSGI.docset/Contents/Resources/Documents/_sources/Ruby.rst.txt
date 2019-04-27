Ruby support
============

.. toctree::
   :maxdepth: 1

   RubyAPI

Starting from version 0.9.7-dev a Ruby (Rack/Rails) plugin is officially available. The official modifier number for Ruby apps is 7, so remember to set it in your web server configuration.

The plugin can be embedded in the uWSGI core or built as a dynamically loaded plugin.

Some uWSGI standard features still aren't supported by the plugin, such as:

* UDP request management
* :doc:`SharedArea` (support on the way)
* :doc:`Queue`

See the :doc:`RubyAPI` page for a list of features currently supported.



Building uWSGI for Ruby support
-------------------------------

You can find :file:`rack.ini` in the :file:`buildconf` directory. This configuration will build uWSGI with a Ruby interpreter embedded. To build uWSGI with this configuration, you'll need the Ruby headers/development package.

.. code-block:: sh

   python uwsgiconfig.py --build rack

The resulting uWSGI binary can run Ruby apps.

A :file:`rackp.ini` build configuration also exists; this will build uWSGI with Ruby support as a plugin; in this case remember to invoke uWSGI with the ``plugins=rack`` option.

A note regarding memory consumption
-----------------------------------

By default the memory management of this plugin is very aggressive (as Ruby can easily devour memory like it was going out of fashion). The Ruby garbage collector is invoked after every request by default. This may hurt your performance if your app creates lots of objects on every request. You can tune the frequency of the collection with the :ref:`OptionRubyGcFreq` option. As usual, there is no one-value-fits-all setting for this, so experiment a bit.

If your app leaks memory without control, consider limiting the number of requests a worker can manage before being restarted with the ``max-requests`` option. Using ``limit-as`` can help too.

A note regarding threads and fibers
-----------------------------------

Adding threading support in Ruby 1.8 is out of discussion. Thread support in this versions is practically useless in a server like uWSGI.
Ruby 1.9 has a threading mode very similar to the Python one, its support is available starting from uWSGI 1.9.14 using the "rbthreads" plugin.

Fibers are a new feature of Ruby 1.9. They are an implementation of coroutines/green threads/stop resume/cooperative multithreading, or whatever you'd like to call this class of funny technologies. See :doc:`FiberLoop`.

Running Rack applications on uWSGI
----------------------------------

This example shows you how to run a Sinatra application on uWSGI.


:file:`config.ru`

.. code-block:: ruby
    
    require 'rubygems'
    require 'sinatra'
    
    get '/hi' do
    "Hello World!"
    end
    
    run Sinatra::Application

Then invoke uWSGI (with ``--plugins`` if you built Ruby support as a plugin):

.. code-block:: sh

    ./uwsgi -s :3031 -M -p 4 -m --post-buffering 4096 --rack config.ru
    ./uwsgi --plugins rack -s :3031 -M -p 4 -m --post-buffering 4096 --rack config.ru

.. note:: ``post-buffering`` is required by the Rack specification.

.. note:: As Sinatra has a built-in logging system, you may wish to disable uWSGI's logging of requests with the ``disable-logging`` option.


Running Ruby on Rails applications on uWSGI
-------------------------------------------

As writing formal documentation isn't very interesting, here's a couple of examples of Rails apps on uWSGI.

Running Typo
^^^^^^^^^^^^

.. code-block:: sh
  
  sudo gem install typo
  typo install /tmp/mytypo
  ./uwsgi -s :3031 --lazy-apps --master --processes 4 --memory-report --rails /tmp/mytypo --post-buffering 4096 --env RAILS_ENV=production

--lazy-apps is vital here as typo (like a lot of apps) is not fork-friendly (it does not expect is loaded in the master and then fork() is called). With this option
the app is fully loaded one-time per-worker.

Nginx configuration:

.. code-block:: nginx

    location / {
      root "/tmp/mytypo/public";
      include "uwsgi_params";
      uwsgi_modifier1 7;
      if (!-f $request_filename) {
        uwsgi_pass 127.0.0.1:3031;
      }
    }

Running Radiant
^^^^^^^^^^^^^^^

.. code-block:: sh

  sudo gem install radiant
  radiant /tmp/myradiant
  cd /tmp/myradiant
  # (edit config/database.yml to fit)
  rake production db:bootstrap
  ./uwsgi -s :3031 -M -p 2 -m --rails /tmp/myradiant --post-buffering 4096 --env RAILS_ENV=production

Apache configuration (with static paths mapped directly):

.. code-block:: apache

  DocumentRoot /tmp/myradiant/public

  <Directory /tmp/myradiant/public>
    Allow from all
  </Directory>

  <Location />
    uWSGISocket 127.0.0.1:3032
    SetHandler uwsgi-handler
    uWSGIForceScriptName /
    uWSGImodifier1 7
  </Location>

  <Location /images>
    SetHandler default-handler
  </Location>
  
  <Location /stylesheets>
    SetHandler default-handler
  </Location>
  
  <Location /javascripts>
    SetHandler default-handler
  </Location>

Rails and SSL
^^^^^^^^^^^^^

You may wish to use the ``HTTPS`` / ``UWSGI_SCHEME https`` uwsgi protocol parameters to inform the app that it is running under HTTPS.

For Nginx:

.. code-block:: nginx
    
    uwsgi_param HTTPS on; # Rails 2.x apps
    uwsgi_param UWSGI_SCHEME https; # Rails 3.x apps
