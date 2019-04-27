uWSGI 2.0.10
============

[20150317]

Bugfixes
--------

* Don't lower security standards with gcc 4.9 (Riccardo Magliocchetti)
* Perl/PSGI make sure that at least two params are passed to xs_input_seek (Ivan Kruglov)
* Per/PSGI fixed multiple interpreters usage
* spooler: fixed scandir usage
* fixed exception handler arguments management
* fixed 'log-master' + 'daemonize2' disables all logging
* fixed http Range header management


New Features
------------

safeexec hook
**************

this is like 'exec' but do not exit on error even if the executed command returns a non-zero value

backported --emperor-wrapper-fallback and --emperor-wrapper-override
********************************************************************

the --emperor-wrapper-fallback option allows you to specify an alternative binary to execute
when running a vassal and the default binary_path is not found (or returns an error). (you can specify it multiple times)

The --emperor-wrapper-override is similar but 'overrides' the default wrapper (you can specify it multiple times)

added support for UNIX sockets to rsyslog
*****************************************

The rsyslog logger can now get a unix socket as address (arguments starting with a slash are recognized as a unix path)

forcecl transformation
**********************

this transformation works like 'fixcl' but generates the Content-Length header even if Content-Length has been listed for removal.


Availability
------------

You can download uWSGI 2.0.10 from

https://projects.unbit.it/downloads/uwsgi-2.0.10.tar.gz
