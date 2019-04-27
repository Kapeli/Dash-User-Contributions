On demand vassals via subscriptions
===================================

Spawn an Emperor with a command socket (it is a channel allowing external process to govern vassals) and instruct it to not spawn vassals until a 'spawn' command is received.

.. code-block:: ini

   [uwsgi]
   emperor = /etc/uwsgi/vassals
   emperor-command-socket = /run/emperor.socket
   emperor-wait-for-command = true
   
Spawn a Fastrouter on port :3031 with a subscription server on port :4041 and instruct it to contact the specific emperor socket whenever an inactive instance is found:

.. code-block:: ini

   [uwsgi]
   master = true
   fastrouter = :3031
   fastrouter-subscription-server = 127.0.0.1:4041
   ; the emperor socket to contact
   fastrouter-emperor-socket = /tmp/emperor.socket
   fastrouter-stats-server = 127.0.0.1:4040
   

Place your vassals in /etc/uwsgi/vassals ensuring each of them correctly subscribe to the fastrouter (this subscription is required to mark 'inactive subscruptions' as 'active'

Now you can start putting 'inactive' subscriptions in the fastrouter, using raw datagrams. An example inactive subscription packets can be something like this in the --subscribe2 way:

.. code-block:: sh

   addr=127.0.0.1:3036,vassal=one.ini,inactive=1,server=127.0.0.1:4041,key=127.0.0.1:9090

this will instruct the fastrouter to map the Host 127.0.0.1:9090 to the inactive uWSGI server that will run on 127.0.0.1:3036 and to run the one.ini vassal at the first request.

