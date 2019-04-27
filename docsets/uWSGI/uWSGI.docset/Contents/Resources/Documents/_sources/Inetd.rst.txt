Socket activation with inetd/xinetd
===================================

Inetd and Xinetd are two daemons used to start network processes on demand.
You can use this in uWSGI too.

Inetd
-----


.. code-block:: inetd

    127.0.0.1:3031 stream tcp wait root /usr/bin/uwsgi uwsgi -M -p 4 --wsgi-file /root/uwsgi/welcome.py --log-syslog=uwsgi

With this config you will run uWSGI on port 3031 as soon as the first
connection is made.  Note: the first argument (the one soon after
/usr/bin/uwsgi) is mapped to ``argv[0]``. Do not forget this -- always set it
to ``uwsgi`` if you want to be sure.

Xinetd 
------

.. code-block:: xinetd

    service uwsgi
    	{
    	        disable         = no
    	        id              = uwsgi-000
    	        type            = UNLISTED
    	        socket_type     = stream
    	        server          = /root/uwsgi/uwsgi
    	        server_args     = --chdir /root/uwsgi/ --module welcome --logto /tmp/uwsgi.log
    	        port            = 3031
    	        bind            = 127.0.0.1
    	        user            = root
    	        wait            = yes
    	}

Again, you do not need to specify the socket in uWSGI, as it will be passed to
the server by xinetd.
