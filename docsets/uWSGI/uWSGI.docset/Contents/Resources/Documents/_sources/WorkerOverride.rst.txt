Overriding Workers
==================

You can override the code run by each uWSGI worker thanks to the "worker" hook exposed to plugins.

Currently the python plugin is the only one exposing it:

.. code-block:: ini

   [uwsgi]
   ; create a bunch of sockets
   socket = 127.0.0.1:3031
   socket = 127.0.0.1:3032
   ; spawn the master
   master = true
   ; spawn 4 processes
   processes = 4
   ; load a python script as the worker code
   python-worker-override = aioserver.py


The python script has access to the uwsgi module so it can control/change its internals.

The following examples shows the use of aiohttp (requires python 3.5)

.. code-block:: python

   import asyncio
   from aiohttp import web

   import uwsgi
   import socket
   import sys
   import signal

   async def handle(request):
      name = request.match_info.get('name', "Anonymous")
      text = "Hello, " + name
      return web.Response(body=text.encode('utf-8'))

   async def wshandler(request):
      ws = web.WebSocketResponse()
      await ws.prepare(request)

      async for msg in ws:
        if msg.tp == web.MsgType.text:
            ws.send_str("Hello, {}".format(msg.data))
        elif msg.tp == web.MsgType.binary:
            ws.send_bytes(msg.data)
        elif msg.tp == web.MsgType.close:
            break

      return ws

    async def init(loop, fd):
       app = web.Application(loop=loop)
       app.router.add_route('GET', '/echo', wshandler)
       app.router.add_route('GET', '/{name}', handle)

       srv = await loop.create_server(app.make_handler(),
                                      sock=socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM))
       print("asyncio server started on uWSGI {0}".format(uwsgi.version))
       return srv

   def destroy():
      print("destroy worker {0}".format(uwsgi.worker_id()))
      sys.exit(0)

   def graceful_reload():
      print("graceful reload for worker {0}".format(uwsgi.worker_id()))
      # TODO do somethign meaningful
      sys.exit(0)

   loop = asyncio.get_event_loop()
   loop.add_signal_handler(signal.SIGINT, destroy)
   loop.add_signal_handler(signal.SIGHUP, graceful_reload)
   # spawn a handler for every uWSGI socket
   for fd in uwsgi.sockets:
      loop.run_until_complete(init(loop, fd))
   uwsgi.accepting()
   loop.run_forever()


In the example (taken from the official aiohttp docs) we see the uwsgi.sockets list (holding the list of uWSGI sockets file descriptors), and the override of SIGINT and SIGHUP to support reloading (SIGHUP should be adapted to support waiting for all the queued requests)

:py:func:`uwsgi.accepting()` is called to notify the master that the worker is accepting requests, this is required for touch-chain-reload to work.

The script should be extended to call uwsgi.log(...) after every request and to (eventually) update some metrics
