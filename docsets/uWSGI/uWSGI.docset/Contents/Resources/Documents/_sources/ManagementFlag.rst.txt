Management Flags
================

.. warning:: This feature may be currently broken or deprecated.

You can modify the behavior of some aspects of the uWSGI stack remotely, without taking the server offline using the Management Flag system.

.. note:: A more comprehensive re-setup system may be in the works.

All the flags take an unsigned 32-bit value (so the block size is always 4) that contains the value to set for the flag.
If you do not specify this value, only sending the uWSGI header, the server will count it as a read request.


====    =============== ===========
Flag    Action          Description
====    =============== ===========
0       logging         enable/disable logging  
1       max_requests    set maximum number of requests per worker       
2       socket_timeout  modify the internal socket timeout      
3       memory_debug    enable/disable memory debug/report      
4       master_interval set the master process check interval   
5       harakiri        set/unset the harakiri timeout  
6       cgi_mode        enable/disable cgi mode 
7       threads         enable/disable threads (currently unimplemented)        
8       reaper          enable/disable process reaper   
9       log-zero        enable/disable logging of request with zero response size       
10      log-slow        set/unset logging of slow requests      
11      log-4xx         enable/disable logging of request with 4xx response status      
12      log-5xx         enable/disable logging of request with 5xx response status      
13      log-big         set/unset logging of request with big response size     
14      log-sendfile    set/unset logging of sendfile requests  
15      backlog-status  report the current size of the backlog queue (linux on tcp only)        
16      backlog-errors  report the number of errors in the backlog queue (linux on tcp only)    
====    =============== ===========

myadmin tool
------------

A simple (and ugly) script, ``myadmin``, is included to remotely change management flags:

.. code-block:: sh

    # disable logging on the uWSGI server listening on 192.168.173.17 port 3031
    ./uwsgi --no-server -w myadmin --pyargv "192.168.173.17:3031 0 0"
    # re-enable logging
    ./uwsgi --no-server -w myadmin --pyargv "192.168.173.17:3031 0 1"
    # read a value:
    ./uwsgi --no-server -w myadmin --pyargv "192.168.173.17:3031 15"
