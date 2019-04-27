WebSocket support
=================

In uWSGI 1.9, a high performance websocket (RFC 6455) implementation has been added.

Although many different solutions exist for WebSockets, most of them rely on a higher-level language implementation, that rarely is good enough for topics like gaming or streaming.

The uWSGI websockets implementation is compiled in by default.

Websocket support is sponsored by 20Tab S.r.l. http://20tab.com/ 

They released a full game (a bomberman clone based on uWSGI websockets api): https://github.com/20tab/Bombertab

An echo server
**************

This is how a uWSGI websockets application looks like:

.. code-block:: python

   def application(env, start_response):
       # complete the handshake
       uwsgi.websocket_handshake(env['HTTP_SEC_WEBSOCKET_KEY'], env.get('HTTP_ORIGIN', ''))
       while True:
           msg = uwsgi.websocket_recv()
           uwsgi.websocket_send(msg) 

You do not need to worry about keeping the connection alive or reject dead peers. The ``uwsgi.websocket_recv()`` function will do all of the dirty work for you in background.

Handshaking
***********

Handshaking is the first phase of a websocket connection.

To send a full handshake response you can use the ``uwsgi.websocket_handshake([key,origin, proto])`` function. Without a correct handshake the connection will never complete.

In the 1.9 series, the key parameter is required. In 2.0+ you can call websocket_handshake without arguments (the response will be built automatically from request's data).

Sending
*******

Sending data to the browser is really easy. ``uwsgi.websocket_send(msg)`` -- nothing more.

Receiving
*********

This is the real core of the whole implementation.

This function actually lies about its real purpose. It does return a websocket message, but it really also holds the connection
opened (using the ping/pong subsystem) and monitors the stream's status. 

``msg = uwsgi.websocket_recv()``

The function can receive messages from a named channel (see below) and automatically forward them to your websocket connection.

It will always return only websocket messages sent from the browser -- any other communication happens in the background.

There is a non-blocking variant too -- ``msg = uwsgi.websocket_recv_nb()``. See: https://github.com/unbit/uwsgi/blob/master/tests/websockets_chat_async.py

PING/PONG
*********

To keep a websocket connection opened, you should constantly send ping (or pong, see later) to the browser and expect
a response from it. If the response from the browser/client does not arrive in a timely fashion the connection is closed (``uwsgi.websocket_recv()`` will raise an exception). In addition to ping, the ``uwsgi.websocket_recv()`` function send the so called 'gratuitous pong'. They are used
to inform the client of server availability.

All of these tasks happen in background. YOU DO NOT NEED TO MANAGE THEM!

Available proxies
*****************

Unfortunately not all of the HTTP webserver/proxies work flawlessly with websockets.

* The uWSGI HTTP/HTTPS/SPDY router supports them without problems. Just remember to add the ``--http-websockets`` option.

  .. code-block:: sh

   uwsgi --http :8080 --http-websockets --wsgi-file myapp.py
   
or

.. code-block:: sh

   uwsgi --http :8080 --http-raw-body --wsgi-file myapp.py
   
This is slightly more "raw", but supports things like chunked input.

* Haproxy works fine.

* nginx >= 1.4 using the ``uwsgi_pass`` directive needs no additional config.

Language support
****************

* Python https://github.com/unbit/uwsgi/blob/master/tests/websockets_echo.py
* Perl https://github.com/unbit/uwsgi/blob/master/tests/websockets_echo.pl
* PyPy https://github.com/unbit/uwsgi/blob/master/tests/websockets_chat_async.py
* Ruby https://github.com/unbit/uwsgi/blob/master/tests/websockets_echo.ru
* Lua https://github.com/unbit/uwsgi/blob/master/tests/websockets_echo.lua

Supported concurrency models
****************************

* Multiprocess
* Multithreaded
* uWSGI native async api
* Coro::AnyEvent
* gevent
* Ruby fibers + uWSGI async
* Ruby threads
* greenlet + uWSGI async
* uGreen + uWSGI async
* PyPy continulets

wss:// (websockets over https)
******************************

The uWSGI HTTPS router works without problems with websockets. Just remember to use wss:// as the connection scheme in your client code.

Websockets over SPDY
********************

n/a

Routing
*******

The http proxy internal router supports websocket out of the box (assuming your front-line proxy already supports them)

.. code-block:: ini

   [uwsgi]
   route = ^/websocket uwsgi:127.0.0.1:3032,0,0
   
or

.. code-block:: ini

   [uwsgi]
   route = ^/websocket http:127.0.0.1:8080

Api
***

uwsgi.websocket_handshake([key, origin, proto])

uwsgi.websocket_recv()

uwsgi.websocket_send(msg)

uwsgi.websocket_send_binary(msg) (added in 1.9.21 to support binary messages)

uwsgi.websocket_recv_nb()

uwsgi.websocket_send_from_sharedarea(id, pos) (added in 1.9.21, allows sending directly from a :doc:`SharedArea`)

uwsgi.websocket_send_binary_from_sharedarea(id, pos) (added in 1.9.21, allows sending directly from a :doc:`SharedArea`)
