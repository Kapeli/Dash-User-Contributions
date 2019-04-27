The uWSGI Legion subsystem
==========================

As of uWSGI 1.9-dev a new subsystem for clustering has been added: The Legion
subsystem. A Legion is a group of uWSGI nodes constantly fighting for
domination. Each node has a valor value (different from the others, if
possible). The node with the highest valor is the Lord of the Legion (or if
you like a less gaming nerd, more engineer-friendly term: the master). This
constant fight generates 7 kinds of events:

1. ``setup`` - when the legion subsystem is started on a node
2. ``join`` - the first time quorum is reached, only on the newly joined node
3. ``lord`` - when this node becomes the lord
4. ``unlord`` - when this node loses the lord title
5. ``death`` - when the legion subsystem is shutting down
6. ``node-joined`` - when any new node joins our legion
7. ``node-left`` - when any node leaves our legion

You can trigger actions every time such an event rises.

**Note**: ``openssl`` headers must be installed to build uWSGI with Legion support.

IP takeover
^^^^^^^^^^^

This is a very common configuration for clustered environments. The IP address
is a resource that must be owned by only one node. For this example, that node
is our Lord. If we configure a Legion right (remember, a single uWSGI
instances can be a member of all of the legions you need) we could easily
implement IP takeover.

.. code-block:: ini

   [uwsgi]

   legion = clusterip 225.1.1.1:4242 98 bf-cbc:hello
   legion-node = clusterip 225.1.1.1:4242

   legion-lord = clusterip cmd:ip addr add 192.168.173.111/24 dev eth0
   legion-lord = clusterip cmd:arping -c 3 -S 192.168.173.111 192.168.173.1

   legion-setup = clusterip cmd:ip addr del 192.168.173.111/24 dev eth0
   legion-unlord = clusterip cmd:ip addr del 192.168.173.111/24 dev eth0
   legion-death = clusterip cmd:ip addr del 192.168.173.111/24 dev eth0

In this example we join a legion named ``clusterip``. To receive messages from
the other nodes we bind on the multicast address 225.1.1.1:4242. The valor of
this node will be 98 and each message will be encrypted using Blowfish in CBC
with the shared secret ``hello``. The ``legion-node`` option specifies the
destination of our announce messages. As we are using multicast we only need to
specify a single "node". The last options are the actions to trigger on the
various states of the cluster. For an IP takeover solution we simply rely on
the Linux ``iproute`` commands to set/unset ip addresses and to send an extra
ARP message to announce the change. Obviously this specific example requires
root privileges or the ``CAP_NET_ADMIN`` Linux capability, so be sure to not
run untrusted applications on the same uWSGI instance managing IP takeover.

The Quorum
**********

To choose a Lord each member of the legion has to cast a vote. When all of the
active members of a legion agree on a Lord, the Lord is elected and the old
Lord is demoted. Every time a new node joins or leaves a legion the quorum is
re-computed and logged to the whole cluster.

Choosing the Lord
*****************

Generally the node with the higher valor is chosen as the Lord, but there can
be cases where multiple nodes have the same valor. When a node is started a
UUID is assigned to it. If two nodes with same valor are found the one with the
lexicographically higher UUID wins.

Split brain
***********

Even though each member of the Legion has to send a checksum of its internal
cluster-membership, the system is still vulnerable to the split brain problem.
If a node loses network connectivity with the cluster, it could believe it is
the only node available and starts going in Lord mode.

For many scenarios this is not optimal. If you have more than 2 nodes in a
legion you may want to consider tuning the quorum level.  The quorum level is
the amount of votes (as opposed to nodes) needed to elect a lord.
``legion-quorum`` is the option for the job. You can reduce the split brain
problem asking the Legion subsystem to check for at least 2 votes:

.. code-block:: ini

   [uwsgi]

   legion = clusterip 225.1.1.1:4242 98 bf-cbc:hello
   legion-node = clusterip 225.1.1.1:4242

   legion-quorum = clusterip 2

   legion-lord = clusterip cmd:ip addr add 192.168.173.111/24 dev eth0
   legion-lord = clusterip cmd:arping -c 3 -S 192.168.173.111 192.168.173.1

   legion-setup = clusterip cmd:ip addr del 192.168.173.111/24 dev eth0
   legion-unlord = clusterip cmd:ip addr del 192.168.173.111/24 dev eth0
   legion-death = clusterip cmd:ip addr del 192.168.173.111/24 dev eth0

As of 1.9.7 you can use nodes with valor 0 (concept similar to MongoDB's
Arbiter Nodes), such nodes will be counted when checking for quorum but may
never become The Lord.  This is useful when you only need a couple nodes while
protecting against split-brain.

Actions
*******

Each one of the four phases of a legion can trigger an action. The actions
system is modular so you can add new kinds of actions.  Currently the supported
actions are:

``cmd:<command>``
^^^^^^^^^^^^^

Run a shell command.

``signal:<num>``
^^^^^^^^^^^^^^^^

Raise a uWSGI signal.

``log:<msg>``
^^^^^^^^^^^^^

Log a message. For example you could combine the log action with the alarm subsystem to have cluster monitoring for free.

``Multicast, broadcast and unicast``
************************************

Even if multicast is probably the easiest way to implement clustering it is not
available in all networks.  If multicast is not an option, you can rely on
normal IP addresses. Just bind to an address and add all of the legion-node
options you need:

.. code-block:: ini

   [uwsgi]

   legion = mycluster 192.168.173.17:4242 98 bf-cbc:hello
   legion-node = mycluster 192.168.173.22:4242
   legion-node = mycluster 192.168.173.30:4242
   legion-node = mycluster 192.168.173.5:4242

This is for a cluster of 4 nodes (this node + 3 other nodes)

Multiple Legions
****************

You can join multiple legions in the same instance. Just remember to use
different addresses (ports in case of multicast) for each legion.

.. code-block:: ini

   [uwsgi]

   legion = mycluster 192.168.173.17:4242 98 bf-cbc:hello
   legion-node = mycluster 192.168.173.22:4242
   legion-node = mycluster 192.168.173.30:4242
   legion-node = mycluster 192.168.173.5:4242

   legion = mycluster2 225.1.1.1:4243 99 aes-128-cbc:secret
   legion-node = mycluster2 225.1.1.1:4243

   legion = anothercluster 225.1.1.1:4244 91 aes-256-cbc:secret2
   legion-node = anothercluster 225.1.1.1:4244

Security
********

Each packet sent by the Legion subsystem is encrypted using a specified cipher,
a preshared secret, and an optional IV (initialization vector). Depending on
cipher, the IV may be a required parameter.  To get the list of supported
ciphers, run ``openssl enc -h``.

.. important:: Each node of a Legion has to use the same encryption parameters.

To specify the IV just add another parameter to the **legion** option.

.. code-block:: ini

   [uwsgi]

   legion = mycluster 192.168.173.17:4242 98 bf-cbc:hello thisistheiv
   legion-node = mycluster 192.168.173.22:4242
   legion-node = mycluster 192.168.173.30:4242
   legion-node = mycluster 192.168.173.5:4242

To reduce the impact of replay-based attacks, packets with a timestamp lower
than 30 seconds are rejected. This is a tunable parameter. If you have no
control on the time of all of the nodes you can increase the clock skew
tolerance.

Tuning and Clock Skew
*********************

Currently there are three parameters you can tune. These tuables affect all
Legions in the system. The frequency (in seconds) at which each packet is sent
(**legion-freq <secs>**), the amount of seconds after a node not sending
packets is considered dead (**legion-tolerance <secs>**), and the amount of
clock skew between nodes (**legion-skew-tolerance <secs>**). The Legion
subsystem requires tight time synchronization, so the use of NTP or similar is
highly recommended.  By default each packet is sent every 3 seconds, a node is
considered dead after 15 seconds, and a clock skew of 30 seconds is tolerated.
Decreasing skew tolerance should increase security against replay attacks.

Lord scroll (coming soon)
*************************

The Legion subsystem can be used for a variety of purposes ranging from master
election to node autodiscovery or simple monitoring.  One example is to assign
a "blob of data" (a scroll) to every node, One use of this is to pass
reconfiguration parameters to your app, or to log specific messages.  Currently
the scroll system is being improved upon, so if you have ideas join our mailing
list or IRC channel.

Legion API
**********

You can know if the instance is a lord of a Legion by simply calling

.. code-block:: c

   int uwsgi_legion_i_am_the_lord(char *legion_name);

It returns 1 if the current instance is the lord for the specified Legion.

* The Python plugin exposes it as ``uwsgi.i_am_the_lord(name)``
* The PSGI plugin exposes it as ``uwsgi::i_am_the_lord(name)``
* The Rack plugin exposes it as ``UWSGI::i_am_the_lord(name)``

Obviously more API functions will be added in the future, feel free to expose your ideas.

Stats
*****

The Legion information is available in the :doc:`StatsServer`.  Be sure to
understand the difference between "nodes" and "members". Nodes are the peer you
configure with the **legion-node** option while members are the effective nodes
that joined the cluster.

The old clustering subsystem
****************************

During 0.9 development cycle a clustering subsystem (based on multicast) was
added. It was very raw, unreliable and very probably no-one used it seriously.
The new method is transforming it in a general API that can use different
backends.  The Legion subsystem can be one of those backends, as well as
projects like corosync or the redhat cluster suite.
