uWSGI 2.0.2
===========


Changelog 20140226


Bugfixes
--------

* fixed python3 support on older compilers/libc
* allow starting in spooler-only mode
* fixed cache bitmap support and added test suite (credits: Danila Shtan)
* fixed ftime log var
* added async remote signal management
* fixed end-for and end-if
* fixed loop in internal-routing response chain
* fixed pypy execute_source usage
* logpipe: Don't setsid() twice (credits: INADA Naoki)

New features and improvements
-----------------------------

CGI plugin
**********

The plugin has been improved to support streaming.

In addition to this the long-awaited async support is finally ready. Now you can have CGI concurrency
without spawning a gazillion of expensive threads/processes

Check: :doc:`CGI`

PSGI loading improvements
*************************

The PSGI loader now tries to use Plack::Util::load_psgi() function instead of simple eval. This addresses various inconsistences
in the environment (like the double parsing/compilation/execution of psgi scripts).

If the Plack module is not available, a simple do-based code is used (very similar to load_psgi)

Many thanks to Ævar Arnfjörð Bjarmason of booking.com for having discovered the problem

Availability
************

uWSGI 2.0.2 can be downloaded from: https://projects.unbit.it/downloads/uwsgi-2.0.2.tar.gz




