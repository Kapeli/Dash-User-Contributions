uWSGI 1.9.10
============

Changelog [20130511]

Bugfixes
********

* fixed alarm threads during reloads
* fixed uninitialized memory in --touch-* options
* fixed a regression in --attach-daemon

New Features
************

Welcome to gccgo
^^^^^^^^^^^^^^^^

Go support in gcc 4.8 is amazing, thanks to the split-stack feature you can now have goroutines without allocating a whole pthread.

As Go 1.1 will be no no more compatible with uWSGI, gccgo will became the official way for running go apps.

The gccgo plugin is in early stage of development but it is already able to run in preforking mode.

We are heavy working on a true "goroutines" Loop engine. Stay tuned.

Final routes
^^^^^^^^^^^^

You can now run routing rules after a request. Obviously not all of the exposed actions make sense after the request but you should be able
to write even more complex setup.

Check this request limiter based on HTTP response status (a value you can get only after a request):

https://github.com/unbit/uwsgi/blob/master/t/routing/errorlimiter.ini

Availability
************

uWSGI 1.9.10 will be available since 20130511 at the following url:

https://projects.unbit.it/downloads/uwsgi-1.9.10.tar.gz
