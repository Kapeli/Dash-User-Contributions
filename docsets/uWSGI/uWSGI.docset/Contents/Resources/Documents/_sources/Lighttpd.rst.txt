Lighttpd support
================

lighttpd >= 1.4.42 supports the uwsgi protocol with Python WSGI backends.
The uwsgi protocol is similar to the SCGI protocol, and lighttpd supports
both protocols in mod_scgi.

Configuring Lighttpd
--------------------

Modify your lighttpd.conf configuration file:

::
  
  server.modules += ( "mod_scgi" )
  scgi.protocol = "uwsgi"
  scgi.server = (
    "/" => (( "host" => "127.0.0.1", "port" => 3031, "check-local" => "disable" )),
  )

Further doc on configuring lighttpd and Python WSGI can be found at
https://redmine.lighttpd.net/projects/lighttpd/wiki/HowToPythonWSGI
including examples configuring uWSGI servers.
