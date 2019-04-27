Writing uWSGI plugins
=====================

This tutorial will introduce you to uWSGI hacking. A bit of C knowledge and UNIX theory is required.

The simplified (and safe) build system used in the tutorial has been added in uWSGI 1.9.21, on older versions you need the raw
procedure (described at the end of the tutorial)

What is an uWSGI plugin?
************************

uWSGI plugins are standard shared libraries (with the classic .so extension) exposing a specific C structure named "uwsgi_plugin".

This structure exposes a bunch of handy information (like the name of the plugin) and "hooks".

Hooks are simple functions registered to be run at specific server phases.

The minimal plugin you can write it is something like this (the 'foobar' plugin):

.. code-block:: c

   #include <uwsgi.h>
   
   struct uwsgi_plugin foobar_plugin = {
           .name ="foobar",
   };
   
It announces itself as 'foobar' and exposes no hooks (yes, it is the most useless plugin out there, except for adding a teensy bit of memory use to uWSGI).

Plugins are not required to define hooks -- they can simply expose functions that can be called using uWSGI advanced facilities (read: :doc:`Hooks`).

Why (and when) plugins?
***********************

Even if uWSGI is able to directly load shared libraries (with ``--dlopen``) and call their functions as hooks, sometimes you want to interface with
uWSGI's internal structures.

The first plugin
****************

Our first plugin will be a simple "Hello world" one:

.. code-block:: c

   #include <uwsgi.h>
   
   static int foo_init() {
         uwsgi_log("Hello World\n");
         return 0;
   }
   
   struct uwsgi_plugin foobar_plugin = {
           .name = "foobar",
           .init = foo_init,
   };
   
Save it as ``foobar.c``.

Build it:

.. code-block:: sh

   uwsgi --build-plugin foobar.c
   
You will end up with a ``foobar_plugin.so`` that you can load in your uWSGI binary.

.. code-block:: sh

   uwsgi --plugin ./foobar_plugin.so
   
If all goes well, you should see "Hello World" on your terminal before uWSGI exiting with an error (as no socket is defined).

The uwsgiplugin.py file
***********************

How does the magic happen?
**************************

As you have seen, the uwsgi binary by itself is able to build plugins without forcing the user/developer to care about build profiles, #ifdef or platform-specific configurations.

This is possible because the uwsgi binary itself contains the raw 'uwsgi.h' file as well as the 'uwsgiconfig.py' script.

In addition to this the CFLAGS used when building the binary are stored too.

With these 3 components you have all you need to safely build a uWSGI plugin tuned for your uwsgi binary.

General plugins VS request plugins
**********************************

The wsgi_request struct
***********************

Headers, body and sendfile
**************************

Offloading
**********

Available hooks
***************

Defining options
****************

Using C++
*********

Using Objective-C
*****************

socket I/O
**********

Whenever you make I/O operations on a socket you have to be sure to not-block the currently running thread/core/worker.

The uwsgi API exposes some functions to ensure safety when dealing with I/O. They would be documented here, but aren't, yet.

