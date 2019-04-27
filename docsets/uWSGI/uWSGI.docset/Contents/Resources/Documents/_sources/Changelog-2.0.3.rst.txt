uWSGI 2.0.3
===========

Changelog 20140317

Bugfixes
********

* fixed spooler 'at' key usage
* fixed a memory and fd leak with on-demand Emperor sokets
* on __APPLE__ use LOG_NOTICE for syslog plugin
* fixed mongrel2 support
* hack for avoiding libmongoclient to crash on broken cursor
* log alarm is now a uwsgi_log_verbose() wrapper
* fixed tuntap router memory corruption
* Set ECDHE curve independently from DHE parameters (Hynek Schlawack)
* do not wait for a whole Emperor cycle before checking for each waitpid
* fix a regression with caller() not indicating the starting *.psgi program (Ævar Arnfjörð Bjarmason)

New features
************

Emperor SIGWINCH and SIGURG
---------------------------

The Emperor now responds to two new signals:

SIGWINCH: force an emperor rescan of vassals

SIGURG: cleanup the Emperor states (for now it only clears its blacklist)

Building plugins on-the-fly from git repositories
-------------------------------------------------

You can now build plugins stored on git servers:

.. code-block:: sh

   uwsgi --build-plugin https://github.com/unbit/uwsgi-bonjour
   
or

.. code-block:: sh

   UWSGI_EMBED_PLUGINS="bonjour=https://github.com/unbit/uwsgi-bonjour" pip install uwsgi

uwsgi.add_var(key, value)
-------------------------

You can now set request variables direcly from your app, for better integration with the internal routing subsystem

.. code-block:: pl

   my $app = sub {
        uwsgi::add_var("newvar","newvalue");
        return [200, ['Content-Type' => 'text/html'], ["Hello"]];
   }
   
.. code-block:: sh

   uwsgi --http-socket :9090 --psgi hello.pl --response-route-run "log:\${newvar}"
   
add_var has been implemented in the CPython and Perl plugins

'disableheaders' routing action
-------------------------------

This new action disables the sending of response headers, independently by the current request state

Smarter Emperor on bad conditions
---------------------------------

Now the Emperor completely destroys internal vassal-related structures when it is impossible to correctly kill a broken vassal
(both for inconsistent Emperor state or for internal system problems)

Availability
************

You can download uWSGI 2.0.3 from: https://projects.unbit.it/downloads/uwsgi-2.0.3.tar.gz
