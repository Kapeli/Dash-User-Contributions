
uWSGI 2.0.17
============

[20180226]

Maintenance release


Changes
-------

- The Emperor throttling subsystem does not make use anymore of blocking functions, like usleep(), this should fix stats serving and should improve vassals startup time
- [Security/PHP] enforce DOCUMENT_ROOT check when using --php-docroot to avoid directory traversal (Marios Nicolaides) 
- added --shutdown-sockets to improve graceful shutdowns (Andrew Wason)

Availability
------------

You can download uWSGI 2.0.17 from https://projects.unbit.it/downloads/uwsgi-2.0.17.tar.gz
