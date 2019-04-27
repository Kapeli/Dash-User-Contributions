uWSGI 2.0.9
===========

[20141230]

Bugfixes
--------

* fixed mod_proxy_uwsgi for non-blocking mode (many thanks to Joe cuchac)
* fixed master-fifo + cheaper
* fixed leak on error in bind_to_unix (Riccardo Magliocchetti)
* atexit hooks works in cheaped workers too
* atexit hooks works in gevent mode too during shutdown
* fixed carbon command line option value after reload
* do not honour Emperor throttling on the first run
* fixed Mono plugin
* fixed peer name in corerouters
* fixed stop signal for daemons
* varios ssl/tls fixes in https/spdy router
* fixed python3 --py-auto-reload-ignore
* fixed modifiers in corerouters
* support for yajl from homebrew (OSX)
* psgi: Ensure that we call any DESTROY hooks on psgix.harakiri.commit (Ævar Arnfjörð Bjarmason)
* systemdlogger: fix compilation with -Werror=format-security (Riccardo Magliocchetti)
* fixed unmasked websockets
* perl fixed latent refcounting bug (Mattia Barbon)

New Features
------------

Improved PyPy support for Linux
*******************************

The PyPy team have started building libpypy-c.so in their official releases. Now using pypy with uWSGI should be way easier:

https://uwsgi-docs.readthedocs.io/en/latest/PyPy.html

Fastrouter post-buffering
*************************

The fastrouter got post-buffering:

https://uwsgi-docs.readthedocs.io/en/latest/Fastrouter.html#post-buffering-mode-uwsgi-2-0-9

Perl uwsgi::opt
***************

The psgi/perl plugin exposes the uwsgi::opt hash, reporting the whole instance key-value configuration

--pull-header
*************

This is like --collect-header but the collected header is not returned to the client

active-workers signal target
****************************

This is like the 'workers' target, but forward the signal only to non-cheaper workers

httpdumb routing action
***********************

The http internal router exposes a new mode called 'httpdumb' that does not change  headers before forwarding the request

Availability
------------

uWSGI 2.0.9 has been released on 20141230.

You can download it from:

https://projects.unbit.it/downloads/uwsgi-2.0.9.tar.gz
