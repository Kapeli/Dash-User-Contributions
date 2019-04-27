uWSGI 1.9.8
===========

Changelog [20130423]

Note: this is an "emergency" release fixing 2 regressions causing a crash during reloads and when using async+uGreen

Bugfixes
********

 - fixed a crash when reloading the master
 - fixed a crash in async mode + uGreen
 - the 'mime' routing var requires a request var (not a raw string)

Availability
************

You can download uWSGi 1.9.8 from https://projects.unbit.it/downloads/uwsgi-1.9.8.tar.gz
