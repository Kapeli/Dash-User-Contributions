Fallback configuration
======================

(available from 1.9.15-dev)

If you need a "reset to factory defaults", or "show a welcome page if the user has made mess with its config" scenario, fallback configuration
is your silver bullet

Simple case
***********

A very common problem is screwing-up the port on which the instance is listening.

To emulate this kind of error we try to bind on port 80 as an unprivileged user:

.. code-block:: sh

   uwsgi --uid 1000 --http-socket :80
   
uWSGI will exit with:

.. code-block:: sh

   bind(): Permission denied [core/socket.c line 755]
   
Internally (from the kernel point of view) the instance exited with status 1

Now we want to allow the instance to automatically bind on port 8080 when the user supplied config fails.

Let's define a fallback config (you can save it as safe.ini):

.. code-block:: ini

   [uwsgi]
   print = Hello i am the fallback config !!!
   http-socket = :8080
   wsgi-file = welcomeapp.wsgi
   
Now we can re-run the (broken) instance:

.. code-block:: sh

   uwsgi --fallback-config safe.ini --uid 1000 --http-socket :80


Your error will be now something like:

.. code-block:: sh

   bind(): Permission denied [core/socket.c line 755]
   Thu Jul 25 21:55:39 2013 - !!! /home/roberto/uwsgi/uwsgi (pid: 7409) exited with status 1 !!!
   Thu Jul 25 21:55:39 2013 - !!! Fallback config to safe.ini !!!
   [uWSGI] getting INI configuration from safe.ini
   *** Starting uWSGI 1.9.15-dev-a0cb71c (64bit) on [Thu Jul 25 21:55:39 2013] ***
   ...
   
As you can see, the instance has detected the exit code 1 and has binary patched itself with a new config (without changing the pid, or calling fork())


Broken apps
***********

Another common problem is the inability to load an application, but instead of bringing down the whole site we want to load
an alternate application:

.. code-block:: sh

   uwsgi --fallback-config safe.ini --need-app --http-socket :8080 --wsgi-file brokenapp.py
   
Here the key is --need-app. It will call exit(1) if the instance has not been able to load at least one application.

Multiple fallback levels
************************

Your fallback config file can specify a fallback-config directive too, allowing multiple fallback levels. BEWARE OF LOOPS!!!

How it works
************

The objective is catching the exit code of a process before the process itself is destroyed (we do not want to call another fork(), or destroy already opened file descriptors)

uWSGI makes heavy usage of atexit() hooks, so we only need to register the fallback handler as the first one (hooks are executed in reverse order).

In addition to this we need to get the exit code in our atexit() hook, something is not supported by default (the on_exit() function is now deprecated).

The solution is "patching" exit(x) with uwsgi_exit(x) that is a simple wrapper setting uwsgi.last_exit_code memory pointer.

Now the hook only needs to check for uwsgi.last_exit_code == 1 and eventually execve() the binary again passing the fallback config to it

.. code-block:: c

   char *argv[3];
   argv[0] = uwsgi.binary_path;
   argv[1] = uwsgi.fallback_config;
   argv[2] = NULL;
   execvp(uwsgi.binary_path, argv);
   
Notes
*****

Try to place --fallback-config as soon as possible in your config tree. The various config parsers may fail (calling exit(1)) before the fallback file is registered


