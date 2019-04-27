uWSGI 2.0.11.1
==============

[20150719]

Bugfixes
********

* fixed HTTPS router resource deallocation and fiel descriptors leak
* do not spit out ssl errors when errno is 0

New Features
************

The unix_signal hook
^^^^^^^^^^^^^^^^^^^^

You can now remap UNIX signals to specific functions symbols:

.. code-block:: c

   #include <stdio.h>

   void hello_world(int signum) {
           printf("Hello World\n");
   }
   
.. code-block:: sh

   gcc -o libhello.so -shared hello.c
   uwsgi --dlopen ./libhello.so --hook-master-start "unix_signal:1 hello_world" ...
   
will run the function hello_world whenever signal 1 (SIGHUP) is raised

Availability
************

You can download uWSGI 2.0.11.1 from

https://projects.unbit.it/downloads/uwsgi-2.0.11.1.tar.gz
