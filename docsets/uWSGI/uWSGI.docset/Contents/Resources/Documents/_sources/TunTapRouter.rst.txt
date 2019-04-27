The TunTap Router
=================

The TunTap router is an ad-hoc solution for giving network connectivity to Linux processes running in a dedicated network namespace. Well obviously it has other uses, but very probably this is the most interesting one, and the one for which it was developed. Currently it builds only on Linux platforms.


The TunTap router is not compiled in by default.


For having it in one shot:

.. code-block:: sh

   UWSGI_EMBED_PLUGINS=tuntap make
   
(yes the plugin is named only 'tuntap' as effectively it exposes various tuntap devices features)

The best way to use it is binding it to a unix socket, allowing processes in new namespaces to reach it (generally unix sockets are the best communication channel for linux namespaces).


The first config
****************

We want our vassals to live in the 192.168.0.0/24 network, with 192.168.0.1 as default gateway.

The default gateway (read: the tuntap router) is managed by the Emperor itself

.. code-block:: ini

   [uwsgi]
   ; create the tun device 'emperor0' and bind it to a unix socket
   tuntap-router = emperor0 /tmp/tuntap.socket
   ; give it an ip address
   exec-as-root = ifconfig emperor0 192.168.0.1 netmask 255.255.255.0 up
   ; setup nat
   exec-as-root = iptables -t nat -F
   exec-as-root = iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
   ; enable linux ip forwarding
   exec-as-root = echo 1 >/proc/sys/net/ipv4/ip_forward
   ; force vassals to be created in a new network namespace
   emperor-use-clone = net
   emperor = /etc/vassals
   
The vassals spawned by this Emperor will born without network connectivity.

To give them access to the public network we create a new tun device (it will exist only in the vassal network namespace)
instructing it to route traffic to the Emperor tuntap unix socket:

.. code-block:: ini

   [uwsgi]
   ; we need it as the vassal have no way to know it is jailed
   ; without it post_jail plugin hook would be never executed
   jailed = true
   ; create uwsgi0 tun interface and force it to connect to the Emperor exposed unix socket
   tuntap-device = uwsgi0 /tmp/tuntap.socket
   ; bring up loopback
   exec-as-root = ifconfig lo up
   ; bring up interface uwsgi0
   exec-as-root = ifconfig uwsgi0 192.168.0.2 netmask 255.255.255.0 up
   ; and set the default gateway
   exec-as-root = route add default gw 192.168.0.1
   ; classic options
   uid = customer001
   gid = customer001
   socket = /var/www/foobar.socket
   psgi-file = foobar.pl
   ...

The embedded firewall
*********************

The TunTap router includes a very simple firewall for governing vassal's traffic

Firewalling is based on 2 chains (in and out), and each rule is formed by 3 parameters: <action> <src> <dst>

The firewall is applied to traffic from the clients to the tuntap device (out) and the opposite (in)


The first matching rule stops the chain, if no rule applies, the policy is "allow"

the following rules allows access from vassals to the internet, but block vassals intercommunication

.. code-block:: ini

   [uwsgi]
   tuntap-router = emperor0 /tmp/tuntap.socket
   
   tuntap-router-firewall-out = allow 192.168.0.0/24 192.168.0.1
   tuntap-router-firewall-out = deny 192.168.0.0/24 192.168.0.0/24
   tuntap-router-firewall-out = allow 192.168.0.0/24 0.0.0.0
   tuntap-router-firewall-out = deny
   tuntap-router-firewall-in = allow 192.168.0.1 192.168.0.0/24
   tuntap-router-firewall-in = deny 192.168.0.0/24 192.168.0.0/24
   tuntap-router-firewall-in = allow 0.0.0.0 192.168.0.0/24
   tuntap-router-firewall-in = deny
   
   exec-as-root = ifconfig emperor0 192.168.0.1 netmask 255.255.255.0 up
   ; setup nat
   exec-as-root = iptables -t nat -F
   exec-as-root = iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
   ; enable linux ip forwarding
   exec-as-root = echo 1 >/proc/sys/net/ipv4/ip_forward
   ; force vassals to be created in a new network namespace
   emperor-use-clone = net
   emperor = /etc/vassals
   
Security
********

The "switching" part of the TunTap router (read: mapping ip addresses to vassals) is pretty simple: the first packet received from a vassal by the TunTap router
register the vassal for that ip address. A good approach (from a security point of view) is sending a ping packet soon after network setup in the vassal:

.. code-block:: ini

   [uwsgi]
   ; create uwsgi0 tun interface and force it to connect to the Emperor exposed unix socket
   tuntap-device = uwsgi0 /tmp/tuntap.socket
   ; bring up loopback
   exec-as-root = ifconfig lo up
   ; bring up interface uwsgi0
   exec-as-root = ifconfig uwsgi0 192.168.0.2 netmask 255.255.255.0 up
   ; and set the default gateway
   exec-as-root = route add default gw 192.168.0.1
   
   ; ping something to register
   exec-as-root = ping -c 1 192.168.0.1
   
   ; classic options
   ...
   
after a vassal/ip pair is registered, only that combo will be valid (so other vassals will not be able to use that address until the one holding it dies)
   
   
The Future
**********

This is becoming a very important part of the unbit.it networking stack. We are currently working on:

- dynamic firewall rules (luajit resulted a great tool for writing fast networking rules)

- federation/proxy of tuntap router (the tuntaprouter can multiplex vassals networking over a tcp connection to an external tuntap router [that is why you can bind a tuntap router to a tcp address])

- authentication of vassals (maybe the old UNIX ancillary credentials could be enough)

- a stats server for network statistics (rx/tx/errors)

- a bandwidth shaper based on the blastbeat project

