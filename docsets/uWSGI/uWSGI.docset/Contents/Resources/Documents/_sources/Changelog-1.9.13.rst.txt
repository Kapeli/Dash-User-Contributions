uWSGI 1.9.13
============

Changelog [20130622]

Bugfixes
^^^^^^^^

- Fixed a corner case bug when response offloading is enabled, but no request plugin is loaded
- Fixed harakiri routing when multiple rules are in place (return NEXT instead of CONTINUE)
- Fixed curl crashing master on slow dns responses (Łukasz Mierzwa)
- Removed PTRACE check in uwsgi.h (it is no more needed since uWSGI 1.0)
- Fixed --print-sym
- Added a newline in --cflags
- Improved python3 detection and compilation
- Fixed Coro::AnyEvent loop engine (John Berthels)
- Rack api functions are now static
- Better fastcgi handling of big uploads
- Improved GCC usage on Darwin for Python non-apple builds
- Fixed XCLIENT usage in rawrouter
- Use the clang preprocessor instead of hardcoded 'cpp' when CC=clang is used
- Set 16bit options to 65535 when higher values are requested
- Fixed virtualhosting (it is now compatible with 1.4 configurations)

New features
^^^^^^^^^^^^

PyPy performance and features improvents
****************************************

The PyPy plugin has been improved a lot. The amount of C code has been reduced by 70%, so, now, the vast majority of the plugin is
written in python. The c helpers have been removed allowing the python part to directly call native uWSGI functions via cffi.

Support for PyPy continulets (and their greenlet abstraction) has been added (while waiting for a solid gevent port for pypy) and a chat example is already available
(using the uwsgi async api):

https://github.com/unbit/uwsgi/tree/master/t/pypy

https://github.com/unbit/uwsgi/blob/master/contrib/pypy/uwsgi_pypy_greenlets.py

The pypy uwsgi api has been improved and now you can use the uwsgidecorators module (even if the spooler subsystem is still missing)


Chunked input api
*****************

In the last days there have been a bunch of discussions on how to correctly manage chunked input. As basically none
of the available standards support it in a "definitive" way, we have defined a low-level api (so we can easily adapt it
in the feature).

The api exposes two functions:

uwsgi.chunked_read()

and

uwsgi.chunked_read_nb()

A non blocking chat example:

.. code-block:: py

   import uwsgi
   def application(e, sr):
       while True:
           uwsgi.wait_fd_read(uwsgi.connection_fd())
           uwsgi.suspend()
           msg = uwsgi.chunked_read_nb()
           if msg: print "core %d" % e['uwsgi.core'], msg


Toward better third-party plugins management: the --dot-h option
****************************************************************

As the --cflags option shows the CFLAGS used to build the server, the --dot-h option shows the content of uwsgi.h

This means the content of uwsgi.h is now embedded in the binary (compressed where available).

It could look a bizarre choice but the objective is to allow easy compilation of plugins out of the uwsgi sources
(somethign that will be available in 2.0 for sure)

setmethod, seturi and setpathinfo routing action
************************************************

we continue extending the routing api.

Three new actions have been added to dinamically modify the request

UWSGI_INCLUDES
**************

You can now ovverride the include search path (while building uWSGI) with this environment variable.

Improved set_user_harakiri api function
***************************************

Now the uwsgi.set_user_harakiri automatically recognize mules and spoolers. It has been added to the ruby/rack, pypy and perl/psgi plugins

--add-cache-item [cache ]KEY=VALUE
**********************************

this is a commodity option (mainly useful for testing) allowing you to store an item in a uWSGI cache during startup

the router_xmldir plugin
************************

This is a proof of concept plugin aimed at stressing the transformation api.

It basically generates an xml representation of a directory. This could be useful to
implement apache-style directoryindex:

Check this example using xslt:

https://github.com/unbit/uwsgi/issues/271#issuecomment-19820204

Implement __call__ for @spool* decorators
*****************************************

Thanks to 'anaconda', you can now directly call functions mapped to the spooler, so instead of

.. code-block:: py

    myfunc.spool(args)
    
you can directly do:

.. code-block:: py

    myfunc(args)
    
the old way is obviously supported

the uwsgi[lq] routing var
*************************

this routing var exports the current size of the listen_queue:

.. code-block:: ini

   [uwsgi]
   ...
   route-if = higher:${uwsgi[lq]};70 break:503 Server Overload
   ...

--use-abort
***********

On some system the SEGV signal handler cannot be correctly restored after the uWSGI backtrace.

If you want to generate a core file, you may want to trigger a SIGABRT soon after the backtrace.

Availability
^^^^^^^^^^^^

uWSGI 1.9.13 will be available 22th June 2013 at this url:

https://projects.unbit.it/downloads/uwsgi-1.9.13.tar.gz
