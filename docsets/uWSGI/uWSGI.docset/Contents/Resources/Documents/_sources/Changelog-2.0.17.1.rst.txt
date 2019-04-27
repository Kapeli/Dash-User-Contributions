uWSGI 2.0.17.1
=============

[20180708]

Maintenance release


Changes
-------

- Fixed memory leak in HTTPS_CLIENT_CERTIFICATE
- TLSv1 is now disabled by default (you can re-enable it with ssl-enable-tlsv1 at your own risk)
- Improved daemons throttle system
- Add "secs" log formatting variable (André Cruz)
- Improved snprintf() usage to be OpenBSD-friendly (Henrik, http://50hz.ws/)
- Improved glibc crypt/crypt_r management (Jakub Jelen, afazekas)
- Fixed websocket pong timeout check (adrianbg)
- Add the "License" classifier to setup.py (Jon Dufresne)
- Add support for php user.ini (Jacco Koning)
- Official support for Python 3.7 (luchr)

Availability
------------

You can download uWSGI 2.0.17.1 from https://projects.unbit.it/downloads/uwsgi-2.0.17.1.tar.gz
