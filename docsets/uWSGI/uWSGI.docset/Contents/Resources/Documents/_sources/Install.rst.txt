Installing uWSGI
================

Installing from a distribution package
--------------------------------------

uWSGI is available as a package in several OS/distributions.

Installing from source
----------------------

To build uWSGI you need Python and a C compiler (``gcc`` and ``clang`` are
supported).  Depending on the languages you wish to support you will need their
development headers.  On a Debian/Ubuntu system you can install them (and the
rest of the infrastructure required to build software) with:

.. code-block:: sh

   apt-get install build-essential python

And if you want to build a binary with python/wsgi support (as an example)

.. code-block:: sh

   apt-get install python-dev

On a Fedora/Redhat system you can install them with:

.. code-block:: sh

   yum groupinstall "Development Tools"
   yum install python

For python/wsgi support:

.. code-block:: sh

   yum install python-devel


If you have a variant of `make` available in your system you can simply run
`make`.  If you do not have `make` (or want to have more control) simply run:

.. code-block:: sh

   python uwsgiconfig.py --build

You can also use pip to install uWSGI (it will build a binary with python support). 

.. code-block:: sh

   # Install the latest stable release:
   pip install uwsgi
   # ... or if you want to install the latest LTS (long term support) release,
   pip install https://projects.unbit.it/downloads/uwsgi-lts.tar.gz

Or you can use ruby gems (it will build a binary with ruby/rack support).

.. code-block:: sh

   # Install the latest stable release:
   gem install uwsgi


At the end of the build, you will get a report of the enabled features. If
something you require is missing, just add the development headers and rerun
the build.  For example to build uWSGI with ssl and perl regexp support you
need libssl-dev and pcre headers.

Alternative build profiles
--------------------------

For historical reasons when you run 'make', uWSGI is built with Python as the
only supported language.  You can build customized uWSGI servers using build
profiles, located in the `buildconf/` directory.  You can use a specific
profile with:

.. code-block:: sh

   python uwsgiconfig.py --build <profile>

Or you can pass it via an environment variable:

.. code-block:: sh

   UWSGI_PROFILE=lua make
   # ... or even ...
   UWSGI_PROFILE=gevent pip install uwsgi


Modular builds
--------------

This is the approach your distribution should follow, and this is the approach
you MUST follow if you want to build a commercial service over uWSGI (see
below).  The vast majority of uWSGI features are available as plugins. Plugins
can be loaded using the --plugin option. If you want to give users the maximum
amount of flexibility allowing them to use only the minimal amount of
resources, just create a modular build.  A build profile named "core" is
available.

.. code-block:: sh

   python uwsgiconfig.py --build core

This will build a uWSGi binary without plugins. This is called the "server
core".  Now you can start building all of the plugins you need. Check the
plugins/ directory in the source distribution for a full list.

.. code-block:: sh

   python uwsgiconfig.py --plugin plugins/psgi core
   python uwsgiconfig.py --plugin plugins/rack core
   python uwsgiconfig.py --plugin plugins/python core
   python uwsgiconfig.py --plugin plugins/lua core
   python uwsgiconfig.py --plugin plugins/corerouter core
   python uwsgiconfig.py --plugin plugins/http core
   ...

Remember to always pass the build profile ('core' in this case) as the third
argument.
   
