uWSGI Subscription Server
=========================

Some components of the uWSGI stack require a key-value mapping system.

For example the :doc:`Fastrouter` needs to know which server to contact for a specific request.

In big networks with a lot of nodes manually managing this configuration could be a real hell.
uWSGI implements a subscription system where the node itself announces its presence to Subscription Servers, which will in turn populate their internal dictionaries.

.. code-block:: sh

    uwsgi --fastrouter :1717 --fastrouter-subscription-server 192.168.0.100:2626

This will run an uWSGI fastrouter on port 1717 and create an empty dictionary where the hostname is the key and the uwsgi address is the value.

To populate this dictionary you can contact 192.168.0.100:2626, the address of the subscription server.

For every key multiple addresses can exist, enabling load balancing (various algorithms are available).

A node can announce its presence to a Subscription Server using the ``subscribe-to`` or ``subscribe2`` options.

.. code-block:: sh

    uwsgi --socket 192.168.0.10:3031 --wsgi myapp -M --subscribe-to 192.168.0.100:2626:uwsgi.it

The FastRouter will map every request for uwsgi.it to 192.168.0.10:3031.

To now add a second node for uwsgi.it simply run it and subscribe:

.. code-block:: xxx

    uwsgi --socket 192.168.0.11:3031 --wsgi myapp --master --subscribe-to 192.168.0.100:2626:uwsgi.it

Dead nodes are automatically removed from the pool.

The syntax for ``subscribe2`` is similar but it allows far more control since it allows to specify additional options like the address to which all requests should be forwarded. Its value syntax is a string with "key=value" pairs, each separated by a comma.

.. code-block:: sh

    uwsgi -s 192.168.0.10:3031 --wsgi myapp --master --subscribe2 server=192.168.0.100:2626,key=uwsgi.it,addr=192.168.0.10:3031

For a list of the available ``subscribe2`` keys, see below.

The subscription system is currently available for cluster joining (when multicast/broadcast is not available), the Fastrouter, the HTTP/HTTPS/SPDY router, the rawrouter and the sslrouter.

That said, you can create an evented/fast_as_hell HTTP load balancer in no time.

.. code-block:: sh

    uwsgi --http :80 --http-subscription-server 192.168.0.100:2626 --master

Now simply subscribe your nodes to the HTTP subscription server.

You can check the subscription server stats and/or the subscribed nodes through the ``http-stats-server`` option.

.. code-block:: sh

    uwsgi --http :80 --http-subscription-server 192.168.0.100:2626 --http-stats-server 192.168.0.100:5004 --master

You can also forward subscription requests to another server with the option ``http-resubscribe``.

.. code-block:: sh

    uwsgi --http :80 --http-subscription-server 192.168.0.100:2626 --http-resubscribe 192.168.0.101:2627 --master

Securing the Subscription System
--------------------------------

The subscription system is meant for "trusted" networks. All of the nodes in your network can potentially make a total mess with it.

If you are building an infrastructure for untrusted users or you simply need more control over who can subscribe to a Subscription Server you can use openssl rsa public/private key pairs for "signing" you subscription requests.

.. code-block:: sh

    # First, create the private key for the subscriber. DO NOT SET A PASSPHRASE FOR THIS KEY.
    openssl genrsa -out private.pem
    # Generate the public key for the subscription server:
    openssl rsa -pubout -out test.uwsgi.it_8000.pem -in private.pem

The keys must be named after the domain/key we are subscribing to serve, plus the .pem extension.

.. note:: If you're subscribing to a pool for an application listening on a specified port you need to use the ``domain_port.pem`` scheme for your key files. Generally all of the DNS-allowed chars are supported, all of the others are mapped to an underscore.

An example of an RSA protected server looks like this:

.. code-block:: ini

    [uwsgi]
    master = 1
    http = :8000
    http-subscription-server = 127.0.0.1:2626
    subscriptions-sign-check = SHA1:/etc/uwsgi/keys

The last line tells uWSGI that public key files will be stored in /etc/uwsgi/keys.

At each subscription request the server will check for the availability of the public key file and use it, if available, to verify the signature of the packet. Packets that do not correctly verify are rejected.

On the client side you need to pass your private key along with other ``subscribe-to`` options. Here's an example:

.. code-block:: ini

    [uwsgi]
    socket = 127.0.0.1:8080
    subscribe-to = 127.0.0.1:2626:test.uwsgi.it:8000,5,SHA1:/home/foobar/private.pem
    psgi = test.psgi

Let's analyze the ``subscribe-to`` usage:

* ``127.0.0.1:2626`` is the subscription server we want to subscribe to.
* ``test.uwsgi.it:8000`` is the subscription key.
* ``5`` is the modifier1 value for our psgi app
* ``SHA1:/home/private/test.uwsgi.it_8000.pem`` is the <digest>:<rsa> couple for authenticating to the server (the <rsa> field is the private key path).

.. note:: Please make sure you're using the same digest method (SHA1 in the examples above) both on the server and on the client.

To avoid replay attacks, each subscription packet has an increasing number (normally the unix time) avoiding the allowance of duplicated packets.
Even if an attacker manages to sniff a subscription packet it will be unusable as it is already processed previously.
Obviously if someone manages to steal your private key he will be able to build forged packets.

Using SSH keys
**************

SSH-formatted keys are generally loved by developers (well, more than classic PEM files).

Both --subscribe-to and --subscribe2 (see below) support SSH private keys, while for the server part you have the encode the public key in pkcs8:

.. code-block:: sh

   ssh-keygen -f chiavessh001.pub -e -m pkcs8
   
--subscribe2
------------

This is the keyval version of --subscribe-to. It supports more tricks and a (generally) more readable syntax:

.. code-block:: sh

   uwsgi --socket 127.*:0 --subscribe2 server=127.0.0.1:7171,key=ubuntu64.local:9090,sign=SHA1:chiavessh001
   
   
Supported fields are:

* ``server`` the address of the subscription server
* ``key`` the key to subscribe (generally the domain name)
* ``addr`` the address to subscribe (the value of the item)
* ``socket`` the socket number (zero-based), this is like 'addr' by take the uWSGI internal socket number
* ``weight`` the load balancing value
* ``modifier1`` and ``modifier2``
* ``sign`` <algo>:<file> the signature for the secured system
* ``check`` it takes a file as argument. If it exists the packet is sent, otherwise it is skipped
* ``sni_key`` set the keyfile to use for SNI proxy management
* ``sni_crt`` set the crt file to use for SNI proxy management
* ``sni_ca`` set the ca file to use for SNI proxy management
* ``algo`` (uWSGI 2.1) set the load balancing algorithm to use (they are pluggable, included are wrr, lrc, wlrc and iphash)
* ``proto`` (uWSGI 2.1) the protocol to use, by default it is 'uwsgi'
* ``backup`` (uWSGI 2.1) set the backup level (change meaning based on algo)

Notifications
-------------

When you subscribe to a server, you can ask it to "acknowledge" the acceptance of your request.

Just add ``--subscription-notify-socket <addr>`` pointing to a datagram (Unix or UDP) address, on which your instance will bind and the subscription server will send acknowledgements to.

Mountpoints (uWSGI 2.1)
-----------------------

Generally you subscribe your apps to specific domains.

Thanks to the mountpoint support introduced in uWSGI 2.1, you can now subscribe each node to a specific directory (you need to specify how much levels you want to support):

First of all you need to tell the subscription server to accept (and manage) mountpoint requests:

.. code-block:: sh

   uwsgi --master --http :8080 --http-subscription-server 127.0.0.1:4040 --subscription-mountpoints 1
   
Then you can start subscribing to mountpoints.
   
.. code-block:: sh

   uwsgi --socket 127.0.0.1:0 --subscribe2 server=127.0.0.1:4040,key=mydomain.it/foo
   uwsgi --socket 127.0.0.1:0 --subscribe2 server=127.0.0.1:4040,key=mydomain.it/bar
   uwsgi --socket 127.0.0.1:0 --subscribe2 server=127.0.0.1:4040,key=mydomain.it/foo
   uwsgi --socket 127.0.0.1:0 --subscribe2 server=127.0.0.1:4040,key=mydomain.it

The first and the third instance will answer to all of the requests for /foo, the second will answer for /bar and the last one will manage all of the others.

For the secured subscription system, you only need to use the domain key (you do not need to generate a certificate for each mountpoint).

If you want to support mountpoints in the form /one/two instead of /one, just pass '2' to --subscription-mountpoints and so on. For performance reason you need to choose how much elements your path can support, and you cannot mix them (read: if --subscription-mountpoints is 2 you can support /one/two or /foo/bar but not /foobar)
