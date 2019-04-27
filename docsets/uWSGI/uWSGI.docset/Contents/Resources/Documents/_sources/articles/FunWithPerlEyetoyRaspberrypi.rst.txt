Fun with Perl, Eyetoy and RaspberryPi
=====================================

Author: Roberto De Ioris

Date: 2013-12-07

.. image:: https://raw.github.com/unbit/uwsgi-capture/master/rpi-examples/rpi_eyetoy.jpg

Intro
*****

This article is the result of various experiments aimed at improving uWSGI performance and usability in various areas before the 2.0 release.

To follow the article you need:

* a Raspberry Pi (any model) with a Linux distribution installed (I used standard Raspbian)
* a PS3 Eyetoy webcam
* a websocket-enabled browser (basically any serious browser)
* a bit of Perl knowledge (really only a bit, there's less than 10 lines of Perl ;)
* Patience (building uWSGI + PSGI + coroae on the RPI requires 13 minutes)

uWSGI subsystems and plugins
****************************

The project makes use of the following uWSGI subsystems and plugins:

* :doc:`../WebSockets`
* :doc:`../SharedArea` (for storing frames)
* :doc:`../Mules` (for gathering frames)
* :doc:`../Symcall`
* :doc:`../Perl`
* :doc:`../Async` (optional, we use ``Coro::Anyevent`` but you can rely on standard processes, though you'll need way more memory)

What we want to accomplish
**************************

We want our RPI to gather frames from the Eyetoy and stream them to various connected clients using websockets, using a HTML5 canvas element to show them.

The whole system must use as little memory as possible, as few CPU cycles as possible, and it should support a large number of clients (... though well, even 10 clients will be a success for the Raspberry Pi hardware ;)

Technical background
********************

The Eyetoy captures frames in YUYV format (known as YUV 4:2:2). This means we need 4 bytes for 2 pixels.

By default the resolution is set to 640x480, so each frame will need 614,400 bytes.

Once we have a frame we need to decode it to RGBA to allow the HTML5 canvas to show it.

The translation between YUYV and RGBA is pretty heavy for the RPI (especially if you need to do it for every connected client) so we will do it
in the browser using Javascript. (There are other approaches we could follow, just check the end of the article for them.)

The uWSGI stack is composed by a mule gathering frames from the Eyetoy and writing them to the uWSGI SharedArea.

Workers constantly read from that SharedArea and send frames as binary websocket messages.

Let's start: the uwsgi-capture plugin
*************************************

uWSGI 1.9.21 introduced a simplified (and safe) procedure to build uWSGI plugins. (Expect more third party plugins soon!)

The project at: https://github.com/unbit/uwsgi-capture shows a very simple plugin using the Video4Linux 2 API to gather frames.

Each frame is written in a shared area initialized by the plugin itself.

The first step is getting uWSGI and building it with the 'coroae' profile:

.. code-block:: sh

   sudo apt-get install git build-essential libperl-dev libcoro-perl
   git clone https://github.com/unbit/uwsgi
   cd uwsgi
   make coroae
   
The procedure requires about 13 minutes. If all goes well you can clone the uwsgi-capture plugin and build it.

.. code-block:: sh

   git clone https://github.com/unbit/uwsgi-capture
   ./uwsgi --build-plugin uwsgi-capture
   
You now have the capture_plugin.so file in your uwsgi directory.

Plug your Eyetoy into an USB port on your RPI and check if it works:

.. code-block:: sh

   ./uwsgi --plugin capture --v4l-capture /dev/video0
   
(the ``--v4l-capture`` option is exposed by the capture plugin)

If all goes well you should see the following lines in uWSGI startup logs:

.. code-block:: sh

   /dev/video0 detected width = 640
   /dev/video0 detected height = 480
   /dev/video0 detected format = YUYV
   sharedarea 0 created at 0xb6935000 (150 pages, area at 0xb6936000)
   /dev/video0 started streaming frames to sharedarea 0
   
(the sharedarea memory pointers will obviously probably be different)

The uWSGI process will exit soon after this as we did not tell it what to do. :)

The ``uwsgi-capture`` plugin exposes 2 functions:

* ``captureinit()``, mapped as the init() hook of the plugin, will be called automatically by uWSGI. If the --v4l-capture option is specified, this function will initialize the specified device and will map it to a uWSGI sharedarea.
* ``captureloop()`` is the function gathering frames and writing them to the sharedarea. This function should constantly run (even if there are no clients reading frames)

We want a mule to run the ``captureloop()`` function.

.. code-block:: sh

   ./uwsgi --plugin capture --v4l-capture /dev/video0 --mule="captureloop()" --http-socket :9090
   
This time we have bound uWSGI to HTTP port 9090 with a mule mapped to the "captureloop()" function. This mule syntax is
exposed by the symcall plugin that takes control of every mule argument ending with "()" (the quoting is required to avoid the shell making a mess of the parentheses).

If all goes well you should see your uWSGI server spawning a master, a mule and a worker.

Step 2: the PSGI app
********************

Time to write our websocket server sending Eyetoy frames (you can find sources for the example here: https://github.com/unbit/uwsgi-capture/tree/master/rpi-examples).

The PSGI app will be very simple:

.. code-block:: pl

   use IO::File;
   use File::Basename;

   my $app = sub {
        my $env = shift;

        # websockets connection happens on /eyetoy
        if ($env->{PATH_INFO} eq '/eyetoy') {
                # complete the handshake
                uwsgi::websocket_handshake($env->{HTTP_SEC_WEBSOCKET_KEY}, $env->{HTTP_ORIGIN});
                while(1) {
                        # wait for updates in the sharedarea
                        uwsgi::sharedarea_wait(0, 50);
                        # send a binary websocket message directly from the sharedarea
                        uwsgi::websocket_send_binary_from_sharedarea(0, 0)
                }
        }
        # other requests generate the html
        else {
                return [200, ['Content-Type' => 'text/html'], new IO::File(dirname(__FILE__).'/eyetoy.html')];
        }
   }

The only interesting parts are:

.. code-block:: pl

   uwsgi::sharedarea_wait(0, 50);
   
This function suspends the current request until the specified shared area (the 'zero' one) gets an update. As this function is basically a busy-loop poll, the second argument specifies the polling frequency in milliseconds. 50 milliseconds gave us good results (feel free to try with other values).

.. code-block:: pl

   uwsgi::websocket_send_binary_from_sharedarea(0, 0)
   
This is a special utility function sending a websocket binary message directly from the sharedarea (yep, zero-copy). The first argument is the sharedarea id (the 'zero' one) and the second is the position
in the sharedarea to start reading from (zero again, as we want a full frame).

Step 3: HTML5
*************

The HTML part (well it would be better to say Javascript part) is very easy, aside from the YUYV to RGB(A) transform voodoo.

.. code-block:: html

   <html>
        <body>
                <canvas id="mystream" width="640" height="480" style="border:solid 1px red"></canvas>

                <script>


                        var canvas = document.getElementById('mystream');
                        var width = canvas.width;
                        var height = canvas.height;
                        var ctx = canvas.getContext("2d");
                        var rgba = ctx.getImageData(0, 0, width, height);

                        // fill alpha (optimization)
                        for(y = 0; y< height; y++) {
                                for(x = 0; x < width; x++) {
                                        pos = (y * width * 4) + (x * 4) ;
                                        rgba.data[pos+3] = 255;
                                }
                        }

                        // connect to the PSGI websocket server
                        var ws = new WebSocket('ws://' + window.location.host + '/eyetoy');
                        ws.binaryType = 'arraybuffer';
                        ws.onopen = function(e) {
                                console.log('ready');
                        };

                        ws.onmessage = function(e) {
                                var x, y;
                                var ycbcr = new Uint8ClampedArray(e.data);
                                // convert YUYV to RGBA
                                for(y = 0; y< height; y++) {
                                        for(x = 0; x < width; x++) {
                                                pos = (y * width * 4) + (x * 4) ;
                                                var vy, cb, cr;
                                                if (x % 2 == 0) {
                                                        ycbcr_pos = (y * width * 2) + (x * 2);
                                                        vy = ycbcr[ycbcr_pos];
                                                        cb = ycbcr[ycbcr_pos+1];
                                                        cr = ycbcr[ycbcr_pos+3];
                                                }
                                                else {
                                                        ycbcr_pos = (y * width * 2) + ((x-1) * 2);
                                                        vy = ycbcr[ycbcr_pos+2];
                                                        cb = ycbcr[ycbcr_pos+1];
                                                        cr = ycbcr[ycbcr_pos+3];
                                                }
                                                var r = (cr + ((cr * 103) >> 8)) - 179;
                                                var g = ((cb * 88) >> 8) - 44 + ((cr * 183) >> 8) - 91;
                                                var b = (cb + ((cb * 198) >> 8)) - 227;
                                                rgba.data[pos] = vy + r;
                                                rgba.data[pos+1] = vy + g;
                                                rgba.data[pos+2] = vy + b;
                                        }
                                }                
                                // draw pixels
                                ctx.putImageData(rgba, 0, 0);
                        };
                        ws.onclose = function(e) { alert('goodbye');}
                        ws.onerror = function(e) { alert('oops');}
                </script>

        </body>
   </html>
   
Nothing special here. The vast majority of the code is related to YUYV->RGBA conversion. Pay attention to set the websocket communication in 'binary' mode (binaryType = 'arraybuffer' is enough) and be sure to use
an Uint8ClampedArray (otherwise performance will be terribly bad)

Ready to watch
**************

.. code-block:: sh

   ./uwsgi --plugin capture --v4l-capture /dev/video0 --http-socket :9090 --psgi uwsgi-capture/rpi-examples/eyetoy.pl --mule="captureloop()"

Connect with your browser to TCP port 9090 of your Raspberry Pi and start watching.

Concurrency
***********

While you watch your websocket stream, you may want to start another browser window to see a second copy of your video. Unfortunately
you spawned uWSGI with a single worker, so only a single client can get the stream.

You can add multiple workers easily:

.. code-block:: sh

   ./uwsgi --plugin capture --v4l-capture /dev/video0 --http-socket :9090 --psgi uwsgi-capture/rpi-examples/eyetoy.pl --mule="captureloop()" --processes 10

Like this up to 10 people will be able to watch the stream.

But coroutines are way better (and cheaper) for I/O bound applications such as this:

.. code-block:: sh

   ./uwsgi --plugin capture --v4l-capture /dev/video0 --http-socket :9090 --psgi uwsgi-capture/rpi-examples/eyetoy.pl --mule="captureloop()" --coroae 10
   
Now, magically, we are able to manage 10 clients with but a single process! The memory on the RPI will be grateful to you.

Zero-copy all the things
************************

Why are we using the SharedArea?

The SharedArea is one of the most advanced uWSGI features. If you give a look at the uwsgi-capture plugin you will see how it easily creates a sharedarea pointing
to a mmap()'ed region. Basically each worker, thread (but please do not use threads with Perl) or coroutine will have access to that memory in a concurrently safe way.

In addition to this, thanks to the websocket/sharedarea cooperation API you can directly send websocket packets from a sharedarea without copying memory (except for the resulting websocket packet).

This is way faster than something like:

.. code-block:: pl

   my $chunk = uwsgi::sharedarea_read(0, 0)
   uwsgi::websocket_send_binary($chunk)
   
We would need to allocate the memory for $chunk at every iteration, copying the sharedarea content into it and finally encapsulating it in a websocket message.

With the sharedarea you remove the need to allocate (and free) memory constantly and to copy it from sharedarea to the Perl VM.

Alternative approaches
**********************

There are obviously other approaches you can follow. 

You could hack uwsgi-capture to allocate a second sharedarea into which it will directly write RGBA frames.

JPEG encoding is relatively fast, you can try encoding frames in the RPI and sending them as MJPEG frames (instead of using websockets):

.. code-block:: pl

   my $writer = $responder->( [200, ['Content-Type' => 'multipart/x-mixed-replace; boundary=uwsgi_mjpeg_frame']]);
   $writer->write("--uwsgi_mjpeg_frame\r\n");
   while(1) {
       uwsgi::sharedarea_wait(0);
       my $chunk = uwsgi::sharedarea_read(0, 0);
       $writer->write("Content-Type: image/jpeg\r\n");
       $writer->write("Content-Length: ".length($chunk)."\r\n\r\n");
       $writer->write($chunk);
       $writer->write("\r\n--uwsgi_mjpeg_frame\r\n");
   }

Other languages
***************

At the time of writing, the uWSGI PSGI plugin is the only one exposing the additional API for websockets+sharedarea. The other language plugins will be updated soon.


More hacking
************

The RPI board is really fun to tinker with and uWSGI is a great companion for it (especially its lower-level API functions).

.. note::

  As an exercise left to the reader: remember you can mmap() the address 0x20200000 to access the Raspberry PI GPIO controller... ready to write a uwsgi-gpio plugin?
