The uWSGI build system
======================

- This is updated to 1.9.13

This page describes how the uWSGI build system works and how it can be customized

uwsgiconfig.py
**************

This is the python script aimed at calling the various compile/link stage.

During 2009, when uWSGI guidelines (and mantra) started to be defined, people agreed that autotools, cmake and friends
was not loved by a lot of sysadmins. Albeit they are pretty standardized, the amount of packages needed and the incompatibility
between them (especially in the autotools world) was a problem for a project with fast development/evolution where "compile from sources" was, is and very probably will be the best way
to get the best from the product. In addition to this the build procedure MUST BE fast (less than 1 minute on entry level x86 is the main rule)

For such a reason, to compile uWSGI you only need to have a c compiler suite (gcc, clang...) and a python interpreter. Someone could argue that perl
could have been a better choice, and maybe it is the truth (it is generally installed by default in lot of operating systems), but we decided to stay with python mainly
because when uWSGI started it was a python-only application. (Obviously if you want to develop an alternative build system you are free to do it)

The uwsgiconfig.py basically detects the available features in the system and builds a uwsgi binary (and eventually its plugins) using the
so called 'build profile'

build profiles
**************

First example
*************

CC and CPP
**********

These 2 environment variables tell uwsgiconfig.py to use an alternative C compiler and C preprocessor.

If they are not defined the procedure is the following:

For CC -> try to get the CC config_var from the python binary running uwsgiconfig.py, fallback to 'gcc'

For CPP -> fallback to 'cpp'


As an example, on a system with both gcc and clang you will end with

.. code-block:: sh

   CC=clang CPP=clang-cpp python uwsgiconfig.py --build

CPUCOUNT
********

In the spirit of "easy and fast build even on production systems", uwsgiconfig.py tries to use all of your cpu cores spawning multiple
instances of the c compiler (one per-core).

You can override this system using the CPUCOUNT environment variable, forcing the number of detected cpu cores (setting to 1 will disable parallel build).

.. code-block:: sh

   CPUCOUNT=2 python uwsgiconfig.py --build

UWSGI_FORCE_REBUILD
*******************

Plugins and uwsgiplugin.py
**************************


A uWSGI plugin is a shared library exporting the <name>_plugin symbol. Where <name> is the name of the plugin.

As an example the psgi plugin will export the psgi_plugin symbol as well as pypy will export he pypy_plugin symbol and so on.

This symbol is a uwsgi_plugin C struct defining the hooks of the plugin.

When you ask uWSGI to load a plugin it simply calls dlopen() and get the uwsgi_plugin struct via dlsym().

The vast majority of the uWSGI project is developed as a plugin. This structure ensures a modular approach to configuration and a saner development style.

The sysadmin is free to embed each plugin in the server binary or to build each plugin as an external shared library.

Embedded plugins are defined in the 'embedded_plugins' directive of the build profile. You can add more embedded plugins
from the command line using the UWSGI_EMBED_PLUGINS environment variable (see below).

Instead, if you want to build a plugin as a shared library just run uwsgiconfig.py with the --plugin option

.. code-block:: sh

   python uwsgiconfig.py --plugin plugins/psgi
   
this will build the plugin in plugins/psgi to the psgi_plugin.so file

To specify a build profile when you build a plugin, you can pass the profile as an additional argument

.. code-block:: sh

   python uwsgiconfig.py --plugin plugins/psgi mybuildprofile

UWSGI_INCLUDES
**************

- this has been added in 1.9.13

On startup, the CPP binary is run to detect default include paths. You can add more paths using the UWSGI_INCLUDES environment variable

.. code-block:: sh

   UWSGI_INCLUDES=/usr/local/include,/opt/dev/include python uwsgiconfig.py --build

UWSGI_EMBED_PLUGINS
*******************

UWSGI_EMBED_CONFIG
******************

Allows embedding the specified .ini file in the server binary (currently Linux only)

On startup the server parses the embedded file as soon as possible.

Custom options defined in the embedded config will be available as standard ones.

UWSGI_BIN_NAME
**************

CFLAGS and LDFLAGS
******************

UWSGICONFIG_* for plugins
*************************

libuwsgi.so
***********

uwsgibuild.log
**************

uwsgibuild.lastcflags
*********************

cflags and uwsgi.h magic
************************

embedding files
***************

The fake make
*************
