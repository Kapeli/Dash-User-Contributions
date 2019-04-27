Embedding an application in uWSGI
=================================

Starting from uWSGI 0.9.8.2, you can embed files in the server binary. These
can be any file type, including configuration files.  You can embed directories
too, so by hooking the Python module loader you can transparently import
packages, too.  In this example we'll be embedding a full Flask project.

Step 1: creating the build profile
----------------------------------

We're assuming you have your uWSGI source at the ready.

In the ``buildconf`` directory, define your profile -- let's call it flask.ini:

.. code-block:: ini

    [uwsgi]
    inherit = base
    main_plugin = python
    bin_name = myapp
    embed_files = bootstrap.py,myapp.py

``myapp.py`` is a simple flask app.

.. code-block:: py

    from flask import Flask
    app = Flask(__name__)
    app.debug = True
    
    @app.route('/')
    def index():
        return "Hello World"

``bootstrap.py`` is included in the source distribution. It will extend the python import subsystem to use files embedded in uWSGI.

Now compile your app-inclusive server. Files will be embedded as symbols in the
executable. Dots and dashes, etc. in filenames are thus transformed to
underscores.

.. code-block:: xxx

    python uwsgiconfig.py --build flask

As ``bin_name`` was ``myapp``, you can now run

.. code-block:: sh

    ./myapp --socket :3031 --import sym://bootstrap_py --module myapp:app

The ``sym://`` pseudoprotocol enables uWSGI to access the binary's embedded
symbols and data, in this case importing bootstrap.py directly from the binary
image.

Step 2: embedding the config file
---------------------------------

We want our binary to automatically load our Flask app without having to pass a long command line.

Let's create the configuration -- flaskconfig.ini:

.. code-block:: ini

    [uwsgi]
    socket = 127.0.0.1:3031
    import = sym://bootstrap_py
    module = myapp:app

And add it to the build profile as a config file.

.. code-block:: ini

    [uwsgi]
    inherit = default
    bin_name = myapp
    embed_files = bootstrap.py,myapp.py
    embed_config = flaskconfig.ini

Then, after you rebuild the server

.. code-block:: sh

    python uwsgiconfig.py --build flask

you can now simply launch

.. code-block:: sh

    ./myapp
    # Remember that this new binary continues to be able to take parameters and config files:
    ./myapp --master --processes 4

Step 3: embedding flask itself
------------------------------

Now, we are ready to kick asses with uWSGI ninja awesomeness.  We want a single
binary embedding all of the Flask modules, including Werkzeug and Jinja2,
Flask's dependencies.  We need to have these packages' directories and then
specify them in the build profile.

.. code-block:: ini

    [uwsgi]
    inherit = default
    bin_name = myapp
    embed_files = bootstrap.py,myapp.py,werkzeug=site-packages/werkzeug,jinja2=site-packages/jinja2,flask=site-packages/flask
    embed_config = flaskconfig.ini

.. note:: This time we have used the form "name=directory" to force symbols to
   a specific names to avoid ending up with a clusterfuck like
   ``site_packages_flask___init___py``.

Rebuild and re-run. We're adding --no-site when running to show you that the
embedded modules are being loaded.

.. code-block:: sh

    python uwsgiconfig.py --build flask
    ./myapp --no-site --master --processes 4

Step 4: adding templates
------------------------

Still not satisfied? WELL YOU SHOULDN'T BE.

.. code-block:: ini

    [uwsgi]
    inherit = default
    bin_name = myapp
    embed_files = bootstrap.py,myapp.py,werkzeug=site-packages/werkzeug,jinja2=site-packages/jinja2,flask=site-packages/flask,templates
    embed_config = flaskconfig.ini

Templates will be added to the binary... but we'll need to instruct Flask on
how to load templates from the binary image by creating a custom Jinja2
template loader.

.. code-block:: py

    from flask import Flask, render_template
    from flask.templating import DispatchingJinjaLoader
    
    class SymTemplateLoader(DispatchingJinjaLoader):
    
        def symbolize(self, name):
            return name.replace('.','_').replace('/', '_').replace('-','_')
    
        def get_source(self, environment, template):
            try:
                import uwsgi
                source = uwsgi.embedded_data("templates_%s" % self.symbolize(template))
                return source, None, lambda: True
            except:
                pass
            return super(SymTemplateLoader, self).get_source(environment, template)
    
    app = Flask(__name__)
    app.debug = True
    
    app.jinja_env.loader = SymTemplateLoader(app)
    
    @app.route('/')
    def index():
        return render_template('hello.html')
    
    @app.route('/foo')
    def foo():
        return render_template('bar/foo.html')

POW! BIFF! NINJA AWESOMENESS.
