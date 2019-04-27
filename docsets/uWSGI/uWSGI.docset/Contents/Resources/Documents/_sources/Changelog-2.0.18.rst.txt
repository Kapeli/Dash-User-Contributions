uWSGI 2.0.18
============

[20190209]

Maintenance release


Changes
-------

- Fixed support for Python 3.7 (Takumi Akiyama)
- Allow to use autoport (socket :0) with custom socket backlog (Pavel Patrin)
- pyuwsgi ported to python3 (thanks lincolnloop)
- pyuwsgi packages fixes (Peter Baumgartner)
- pyuwsginossl build configuration for building pyuwsgi without ssl support (Peter Baumgartner)
- Fix unix socket inheritance after reload on FreeBSD (Anton Yuzhaninov)
- Fix crashes with --wsgi-env-behavior=holy (#1950)
- Fix invalid free in python plugin (Riccardo Magliocchetti, #1942)
- Fix compilation warnings with gcc-8 (Riccardo Magliocchetti, Ruslan Bilovol #1819)
- Fix spooler python references (Brett Rosen)
- Don't generate build warnings in systemd_logger (Chris Mayo)
- Fix segmentation fault during worker shutdown (Allan Feldman, #1651)


Availability
------------

You can download uWSGI 2.0.18 from https://projects.unbit.it/downloads/uwsgi-2.0.18.tar.gz
