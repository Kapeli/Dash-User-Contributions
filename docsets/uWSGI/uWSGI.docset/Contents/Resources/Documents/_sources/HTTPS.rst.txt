HTTPS support (from 1.3)
============================

Use the ``https <socket>,<certificate>,<key>`` option. This option may be
specified multiple times. First generate your server key, certificate signing
request, and self-sign the certificate using the OpenSSL toolset:

.. note:: You'll want a real SSL certificate for production use.

::
  
  openssl genrsa -out foobar.key 2048
  openssl req -new -key foobar.key -out foobar.csr
  openssl x509 -req -days 365 -in foobar.csr -signkey foobar.key -out foobar.crt

Then start the server using the SSL certificate and key just generated::

  uwsgi --master --https 0.0.0.0:8443,foobar.crt,foobar.key

As port 443, the port normally used by HTTPS, is privileged (ie. non-root
processes may not bind to it), you can use the shared socket mechanism and drop
privileges after binding like thus::

  uwsgi --shared-socket 0.0.0.0:443 --uid roberto --gid roberto --https =0,foobar.crt,foobar.key

uWSGI will bind to 443 on any IP, then drop privileges to those of ``roberto``,
and use the shared socket 0 (``=0``) for HTTPS.

.. note:: The =0 syntax is currently undocumented.

.. note:: In order to use `https` option be sure that you have OpenSSL
   development headers installed (e.g. libssl-dev on Debian). Install them
   and rebuild uWSGI so the build system will automatically detect it.

Setting SSL/TLS ciphers
-----------------------

The ``https`` option takes an optional fourth argument you can use to specify
the OpenSSL cipher suite.

.. code-block:: ini

   [uwsgi]
   master = true
   shared-socket = 0.0.0.0:443
   uid = www-data
   gid = www-data
   
   https = =0,foobar.crt,foobar.key,HIGH
   http-to = /tmp/uwsgi.sock


This will set all of the **HIGHest** ciphers (whenever possible) for your
SSL/TLS transactions.

Client certificate authentication
---------------------------------

The ``https`` option can also take an optional 5th argument. You can use it to
specify a CA certificate to authenticate your clients with. Generate your CA
key and certificate (this time the key will be 4096 bits and
password-protected)::

  openssl genrsa -des3 -out ca.key 4096
  openssl req -new -x509 -days 365 -key ca.key -out ca.crt

Generate the server key and CSR (as before)::

  openssl genrsa -out foobar.key 2048
  openssl req -new -key foobar.key -out foobar.csr

Sign the server certificate with your new CA::

  openssl x509 -req -days 365 -in foobar.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out foobar.crt

Create a key and a CSR for your client, sign it with your CA and package it as
PKCS#12. Repeat these steps for each client.

::

  openssl genrsa -des3 -out client.key 2048
  openssl req -new -key client.key -out client.csr
  openssl x509 -req -days 365 -in client.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out client.crt
  openssl pkcs12 -export -in client.crt -inkey client.key -name "Client 01" -out client.p12


Then configure uWSGI for certificate client authentication

.. code-block:: ini

  [uwsgi]
  master = true
  shared-socket = 0.0.0.0:443
  uid = www-data
  gid = www-data
  https = =0,foobar.crt,foobar.key,HIGH,!ca.crt
  http-to = /tmp/uwsgi.sock

.. note:: If you don't want the client certificate authentication to be
   mandatory, remove the '!' before ca.crt in the https options.
