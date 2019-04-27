Using OpenBSD httpd as proxy
============================

Starting from version 5.7 OpenBSD includes a minimal (truly minimal) web server with FastCGI support

(http://www.openbsd.org/cgi-bin/man.cgi/OpenBSD-current/man8/httpd.8?query=httpd&sec=8)

The first step to enable it is writing its configuration file ```/etc/httpd.conf```

.. code-block:: c

   server "default" {
       listen on 0.0.0.0 port 80
   
       fastcgi socket ":3031"
   }

then enable and start it with the ```rcctl``` tool:

.. code-block:: sh

   rcctl enable httpd
   rcctl start httpd

this minimal configuration will spawn a chrooted webserver on port 80, running as user 'www' and forwarding every request
to the address 127.0.0.1:3031 using the FastCGI protocol.


Now you only need to spawn uWSGI on the FastCGI address:

.. code-block:: ini

   [uwsgi]
   fastcgi-socket = 127.0.0.1:3031
   ; a simple python app (eventually remember to load the python plugin)
   wsgi-file = app.py


you can obviously use uWSGI as a full-featured CGI server (well, effectively it has way more features than every cgi server out there :P),
just remember to force the modifier1 to the '9' one:

.. code-block:: ini

   [uwsgi]
   fastcgi-socket = 127.0.0.1:3031
   fastcgi-modifier1 = 9
   ; a simple cgi-bin directory (eventually remember to load the cgi plugin)
   cgi = /var/www/cgi-bin

now you can place your cgi scripts in /var/www/cgi-bin (remember to give them the executable permission)

You can use UNIX domain sockets too, just remember the httpd servers runs chrooted in /var/www so you have to bind uWSGI sockets in a dir under it:

.. code-block:: ini

   [uwsgi]
   fastcgi-socket = /var/www/run/uwsgi.socket
   fastcgi-modifier1 = 9
   ; a simple cgi-bin directory
   cgi = /var/www/cgi-bin

.. code-block:: c

   server "default" {
       listen on 0.0.0.0 port 80
   
       fastcgi socket "/run/uwsgi.socket"
   }


If you want to forward only specific paths to uWSGI, you can use a location directive:

.. code-block:: c

   server "default" {
       listen on 0.0.0.0 port 80
   
       location "/foo/*" {
           fastcgi socket ":3031"
       }
       
       location "/cgi-bin/*" {
           fastcgi socket ":3032"
       }
   }
   
Notes
=====

Currently (may 2015) httpd can connect only to tcp fastcgi sockets bound on address 127.0.0.1 and to unix domain sockets
