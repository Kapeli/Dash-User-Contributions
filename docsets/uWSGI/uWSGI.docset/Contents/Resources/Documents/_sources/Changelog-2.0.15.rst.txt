uWSGI 2.0.15
============

[20170330]

Maintenance release

Issues
------

Unfortunately there are still 2 unfixed long standing bugs in this release:

- suwsgi protocol behind nginx does not work reliably when a request body is sent by the client (https://github.com/unbit/uwsgi/issues/1490). As we cannot reproduce it in uWSGI itself, we will start checking in the nginx module too
- There are reports of the "holy" wsgi env allocator crashing on specific conditions, this release includes a bunch of workarounds but they could not be enough

Changes
-------

- workaround for the holy allocator for avoiding crashes with newrelic (see Issues notes)
- avoid time overflow in request logs during (even minimal) clock skew
- fixed python logger with python3
- fixed catch-exceptions with python3
- backported "don't clone $env->{'psgix.io'} on 'PSGI cancel'"
- added support for authentication in the redis logger
- added the spinningfifo action hook to the core
- fixed compilation with php 7.1 (Дамјан Георгиевски)
- correctly returns error code 22 in lazy_apps + master_mode
- fixed compilation for OpenSSL 1.1 (Riccardo Magliocchetti)
- Add a --skip-atexit-teardown option to skip perl/python teardown (Ævar Arnfjörð Bjarmason)
- fixed static file serving over https-socket

Availability
------------

You can download uWSGI 2.0.15 from https://projects.unbit.it/downloads/uwsgi-2.0.15.tar.gz
