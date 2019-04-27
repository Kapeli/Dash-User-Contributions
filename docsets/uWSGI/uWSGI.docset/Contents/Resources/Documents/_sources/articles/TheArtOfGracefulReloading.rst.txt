The Art of Graceful Reloading
=============================

Author: Roberto De Ioris

The following article is language-agnostic, and albeit uWSGI-specific, some of
its initial considerations apply to other application servers and platforms
too.

All of the described techniques assume a modern (>= 1.4) uWSGI release with
the master process enabled.

What is a "graceful reload"?
****************************

During the life-cycle of your webapp you will reload it hundreds of times.

You need reloading for code updates, you need reloading for changes in the
uWSGI configuration, you need reloading to reset the state of your app.

Basically, reloading is one of the most simple, frequent and **dangerous**
operation you do every time.

So, why "graceful"?

Take a traditional (and highly suggested) architecture: a proxy/load balancer
(like nginx) forwards requests to one or more uWSGI daemons listening on various
addresses.

If you manage your reloads as "stop the instance, start the instance", the time
slice between two phases will result in a brutal disservice for your customers.

The main trick for avoiding it is: not closing the file descriptors mapped to
the uWSGI daemon addresses and abusing the Unix ``fork()`` behaviour (read:
file descriptors are inherited by default) to ``exec()`` the ``uwsgi`` binary
again.

The result is your proxy enqueuing requests to the socket until the latter
will be able to ``accept()`` them again, with the user/customer only seeing
a little slowdown in the first response (the time required for the app to be
fully loaded again).

Another important step of graceful reload is to avoid destroying workers/threads
that are still managing requests. Obviously requests could be stuck, so you
should have a timeout for running workers (in uWSGI it is called the
"worker's mercy" and it has a default value of 60 seconds).

These kind of tricks are pretty easy to accomplish and basically all of the
modern servers/application servers do it (more or less).

But, as always, the world is an ugly place and lot of problems arise, and the
"inherited sockets" approach is often not enough.

Things go wrong
***************

We have seen that holding the uWSGI sockets alive allows the proxy webserver
to enqueue requests without spitting out errors to the clients. This is true
only if your app restarts fast, and, sadly, this may not always happen.

Frameworks like Ruby on Rails or Zope start up really slow by default, your
app could start up slowly by itself, or your machine could be so overloaded that
every process spawn (``fork()``) takes ages.

In addition to this, your site could be so famous that even if your app restarts
in a couple of seconds, the queue of your sockets could be filled up forcing the
proxy server to raise an error.

Do not forget, your workers/threads that are still running requests could block
the reload (for various reasons) for more seconds than your proxy server could
tolerate.

Finally, you could have made an application error in your just-committed code,
so uWSGI will not start, or will start sending wrong things or errors...

Reloads (brutal or graceful) can easily fail.

The listen queue
****************

Let's start with the dream of every webapp developer: *success*.

Your app is visited by thousands of clients and you obviously make money with
it. Unfortunately, it is a very complex app and requires 10 seconds to warm up.

During graceful reloads, you expect new clients to wait 10 seconds (best case)
to start seeing contents, but, unfortunately, you have hundreds of concurrent
requests, so first 100 customers will wait during the server warm-up, while
the others will get an error from the proxy.

This happens because the default size of uWSGI's listen queue is 100 slots.
Before you ask, it is an average value chosen by the maximum value allowed
by default by your kernel.

Each operating system has a default limit (Linux has 128, for example), so
before increasing it you need to increase your kernel limit too.

So, once your kernel is ready, you can increase the listen queue to the
maximum number of users you expect to enqueue during a reload.

To increase the listen queue you use the ``--listen <n>`` option where
``<n>`` is the maximum number of slots.

To raise kernel limits, you should check your OS docs. Some examples:

* sysctl ``kern.ipc.somaxconn`` on FreeBSD
* ``/proc/sys/net/core/somaxconn`` on Linux.

.. note::

   This is only one of the reasons to tune the listen queue, but do not blindly
   set it to huge values as a way to increase availability.

Proxy timeouts
**************

This is another thing you need to check if your reloads take a lot of time.

Generally, proxies allow you to set two timeouts:

connect
    Maximum amount of time the proxy will wait for a successful connection.

read
    Maximum amount of time the server will be able to wait for data before
    giving up.

When tuning the reloads, only the "connection" timeout matters. This timeout
enters the game in the time slice between uWSGI's bind to an interface (or
inheritance of it) and the call to ``accept()``.

Waiting instead of errors is good, no errors and no waiting is even better
**************************************************************************

This is the focus of this article. We have seen how to increase the tolerance
of your proxy during application server reloading. The customers will wait
instead of getting scary errors, but we all want to make money, so why force
them to wait?

*We want zero-downtime and zero-wait.*

Preforking VS lazy-apps VS lazy
*******************************

This is one of the controversial choices of the uWSGI project.

By default uWSGI loads the whole application in the first process and after
the app is loaded it does ``fork()`` itself multiple times.
This is the common Unix pattern, it may highly reduce the memory usage of your
app, allows lot of funny tricks and on some languages may bring you a lot of
headaches.

Albeit its name, uWSGI was born as a Perl application server (it was not called
uWSGI and it was not open source), and in the Perl world preforking is
generally the blessed way.

This is not true for a lot of other languages, platforms and frameworks, so
before starting dealing with uWSGI you should choose how to manage ``fork()``
in your stack.

Seeing it from the "graceful reloading" point of view, preforking extremely
speeds up things: your app is loaded only one time, and spawning additional
workers will be really fast. Avoiding disk access for each worker of your
stack will decrease startup times, especially for frameworks or languages
doing a lot of disk access to find modules.

Unfortunately, the preforking approach forces you to reload the whole stack
whenever you make code changes instead of reloading only the workers.

In addition to this, your app could need preforking, or could completely
crash due to it because of the way it has been developed.

lazy-apps mode instead loads your application one time per worker. It will
require about O(n) time to load it (where n is the number of workers),
will very probably consume more memory, but will run in a more consistent
and clean environment.

Remember: lazy-apps is different from lazy, the first one only instructs
uWSGI to load the application one time per worker, while the second is
more invasive (and generally discouraged) as it changes a lot of internal
defaults.

The following approaches will show you how to accomplish zero-downtime/wait
reloads in both preforking and lazy modes.

.. note:: 

    Each approach has pros and cons, choose carefully.

Standard (default/boring) graceful reload (aka ``SIGHUP``)
**********************************************************

To trigger it, you can:

* send ``SIGHUP`` to the master
* write ``r`` to :doc:`../MasterFIFO`
* use ``--touch-reload`` option
* call ``uwsgi.reload()`` API.

In preforking and lazy-apps mode, it will:

1. Wait for running workers.
2. Close all of the file descriptors except the ones mapped to sockets.
3. Call ``exec()`` on itself.

In lazy mode, it will:

1. Wait for running workers.
2. Restart all of them (this means you cannot change uWSGI options during
   this kind of reload).

.. warning::

    lazy is discouraged!

Pros:

* easy to manage
* no corner-case problems
* no inconsistent states
* basically full reset of the instance.

Cons:

* the ones we seen before
* listen queue filling up
* stuck workers
* potentially long waiting times.

Workers reloading in lazy-apps mode
***********************************

Requires ``--lazy-apps`` option.

To trigger it:

* write ``w`` to :doc:`../MasterFIFO`
* use ``--touch-workers-reload`` option.

It will wait for running workers and then restart each of them.

Pros:

* avoids restarting the whole instance.

Cons:

* no user-experience improvements over standard graceful reload, it is
  only a shortcut for situation when code updates do not imply instance
  reconfiguration.

Chain reloading (lazy apps)
***************************

Requires ``--lazy-apps`` option.

To trigger it:

* write ``c`` to :doc:`../MasterFIFO`
* use ``--touch-chain-reload`` option.

This is the first approach that improves user experience. When triggered,
it will restart one worker at time, and the following worker is not reloaded
until the previous one is ready to accept new requests.

Pros:

* potentially highly reduces waiting time for clients
* reduces the load of the machine during reloads (no multiple processes loading
  the same code).

Cons:

* only useful for code updates
* you need a good amount of workers to get a better user experience.

Zerg mode
*********

Requires a zerg server or a zerg pool.

To trigger it, run the instance in zerg mode.

This is the first approach that uses multiple instances of the same application
to increase user experience.

Zerg mode works by making use of the venerable "fd passing over Unix sockets"
technique.

Basically, an external process (the zerg server/pool) binds to the various
sockets required by your app. Your uWSGI instance, instead of binding by
itself, asks the zerg server/pool to pass it the file descriptor. This means
multiple unrelated instances can ask for the same file descriptors and work
together.

Zerg mode was born to improve auto-scalability, but soon became one of the most
loved approaches for zero-downtime reloading.

Now, examples.

Spawn a zerg pool exposing ``127.0.0.1:3031`` to the Unix socket
``/var/run/pool1``:

.. code-block:: ini

   [uwsgi]
   master = true
   zerg-pool = /var/run/pool1:127.0.0.1:3031

Now spawn one or more instances attached to the zerg pool:

.. code-block:: ini

   [uwsgi]
   ; this will give access to 127.0.0.1:3031 to the instance
   zerg = /var/run/pool1

When you want to make update of code or options, just spawn a new instance
attached to the zerg, and shut down the old one when the new one is ready to
accept requests.

The so-called "zerg dance" is a trick for automation of this kind of reload.
There are various ways to accomplish it, the objective is to automatically
"pause" or "destroy" the old instance when the new one is fully ready and able
to accept requests. More on this below.

Pros:

* potentially the silver bullet
* allows instances with different options to cooperate for the same app.

Cons:

* requires an additional process
* can be hard to master
* reload requires copy of the whole uWSGI stack.

The Zerg Dance: Pausing instances
*********************************

We all make mistakes, sysadmins must improve their skill of fast disaster
recovery. Focusing on avoiding them is a waste of time. Unfortunately, we
are all humans.

Rolling back deployments could be your life-safer.

We have seen how zerg mode allows us to have multiple instances asking on
the same socket. In the previous section we used it to spawn a new instance
working together with the old one. Now, instead of shutting down the old
instance, why not "pause" it? A paused instance is like the standby mode
of your TV. It consumes very few resources, but you can bring it back very
quickly.

"Zerg Dance" is the battle-name for the procedure of continuous swapping of
instances during reloads. Every reload results in a "sleeping" instance and
a running one. Following reloads destroy the old sleeping instance and
transform the old running to the sleeping one and so on.

There are literally dozens of ways to accomplish the "Zerg Dance", the fact
that you can easily use scripts in your reloading procedures makes this
approach extremely powerful and customizable.

Here we will see the one that requires zero scripting, it could be the less
versatile (and requires at least uWSGI 1.9.21), but should be a good starting
point for the improvements.

:doc:`../MasterFIFO` is the best way to manage instances instead of relying
on Unix signals. Basically, you write single-char commands to govern the
instance.

The funny thing about the Master FIFOs is that you can have many of them
configured for your instance and swap one with another very easily.

An example will clarify things.

We spawn an instance with 3 Master FIFOs: new (the default one), running
and sleeping:

.. code-block:: ini

   [uwsgi]
   ; fifo '0'
   master-fifo = /var/run/new.fifo
   ; fifo '1'
   master-fifo = /var/run/running.fifo
   ; fifo '2'
   master-fifo = /var/run/sleeping.fifo
   ; attach to zerg
   zerg = /var/run/pool1
   ; other options ...
   
By default the "new" one will be active (read: will be able to process
commands).

Now we want to spawn a new instance, that once is ready to accept requests will
put the old one in sleeping mode. To do it, we will use uWSGI's advanced hooks.
Hooks allow you to "make things" at various phases of uWSGI's life cycle.
When the new instance is ready, we want to force the old instance to start
working on the sleeping FIFO and be in "pause" mode:

.. code-block:: ini

    [uwsgi]
    ; fifo '0'
    master-fifo = /var/run/new.fifo
    ; fifo '1'
    master-fifo = /var/run/running.fifo
    ; fifo '2'
    master-fifo = /var/run/sleeping.fifo
    ; attach to zerg
    zerg = /var/run/pool1

    ; hooks

    ; destroy the currently sleeping instance
    if-exists = /var/run/sleeping.fifo
      hook-accepting1-once = writefifo:/var/run/sleeping.fifo Q
    endif =
    ; force the currently running instance to became sleeping (slot 2) and place it in pause mode
    if-exists = /var/run/running.fifo
      hook-accepting1-once = writefifo:/var/run/running.fifo 2p
    endif =
    ; force this instance to became the running one (slot 1)
    hook-accepting1-once = writefifo:/var/run/new.fifo 1

The ``hook-accepting1-once`` phase is run one time per instance soon after the
first worker is ready to accept requests.
The ``writefifo`` command allows writing to FIFOs  without failing if the
other peers are not connected (this is different from a simple ``write``
command that would fail or completely block when dealing with bad FIFOs).

.. note::

    Both features have been added only in uWSGI 1.9.21, with older releases you can
    use the ``--hook-post-app`` option instead of ``--hook-accepting1-once``, but
    you will lose the "once" feature, so it will work reliably only in preforking
    mode.

    Instead of ``writefifo`` you can use the shell variant:
    ``exec:echo <string> > <fifo>``.

Now start running instances with the same config files over and over again.
If all goes well, you should always end with two instances, one sleeping and
one running.

Finally, if you want to bring back a sleeping instance, just do:

.. code-block:: sh

   # destroy the running instance
   echo Q > /var/run/running.fifo

   # unpause the sleeping instance and set it as the running one
   echo p1 > /var/run/sleeping.fifo
   
Pros:

* truly zero-downtime reload.

Cons:

* requires high-level uWSGI and Unix skills.

``SO_REUSEPORT`` (Linux >= 3.9 and BSDs)
****************************************

On recent Linux kernels and modern BSDs you may try ``--reuse-port`` option.
This option allows multiple unrelated instances to bind on the same network
address. You may see it as a kernel-level zerg mode. Basically, all of the Zerg
approaches can be followed.

Once you add ``--reuse-port`` to you instance, all of the sockets will have
the ``SO_REUSEPORT`` flag set.

Pros:

* similar to zerg mode, could be even easier to manage.

Cons:

* requires kernel support
* could lead to inconsistent states
* you lose ability to use TCP addresses as a way to avoid incidental multiple
  instances running.

The Black Art (for rich and brave people): master forking
*********************************************************

To trigger it, write ``f`` to :doc:`../MasterFIFO`.

This is the most dangerous of the ways to reload, but once mastered, it could
lead to pretty cool results.

The approach is: call ``fork()`` in the master, close all of the file
descriptors except the socket-related ones, and ``exec()`` a new uWSGI
instance.

You will end with two specular uWSGI instances working on the same set of
sockets.

The scary thing about it is how easy (just write a single char to the master
FIFO) is to trigger it...

With a bit of mastery you can implement the zerg dance on top of it.

Pros:

* does not require kernel support nor an additional process
* pretty fast.

Cons:

* a whole copy for each reload
* inconstent states all over the place (pidfiles, logging, etc.: the master
  FIFO commands could help fix them).

Subscription system
*******************

This is probably the best approach when you can count on multiple servers.
You add the "fastrouter" between your proxy server (e.g., nginx) and your
instances.

Instances will "subscribe" to the fastrouter that will pass requests
from proxy server (nginx) to them while load balancing and constantly
monitoring all of them.

Subscriptions are simple UDP packets that instruct the fastrouter which
domain maps to which instance or instances.

As you can subscribe, you can unsubscribe too, and this is where the magic
happens:

.. code-block:: ini

   [uwsgi]
   subscribe-to = 192.168.0.1:4040:unbit.it
   unsubscribe-on-graceful-reload = true
   ; all of the required options ...
   
Adding ``unsubscribe-on-graceful-reload`` will force the instance to send an
"unsubscribe" packet to the fastrouter, so until it will not be back no request
will be sent to it.

Pros:

* low-cost zero-downtime
* a KISS approach (*finally*).

Cons:

* requires a subscription server (like the fastrouter) that introduces overhead
  (even if we are talking about microseconds).

Inconsistent states
*******************

Sadly, most of the approaches involving copies of the whole instance (like
Zerg Dance or master forking) lead to inconsistent states.

Take, for example, an instance writing pidfiles: when starting a copy of it,
that pidfile will be overwritten.

If you carefully plan your configurations, you can avoid inconsistent states,
but thanks to :doc:`../MasterFIFO` you can manage some of them (read: the most
common ones):

* ``l`` command will reopen logfiles
* ``P`` command will update all of the instance pidfiles.

Fighting inconsistent states with the Emperor
*********************************************

If you manage your instances with the :doc:`Emperor<../Emperor>`, you can
use its features to avoid (or reduce number of) inconsistent states.

Giving each instance a different symbolic link name will allow you to map
files (like pidfiles or logs) to different paths:

.. code-block:: ini

    [uwsgi]
    logto = /var/log/%n.log
    safe-pidfile = /var/run/%n.pid
    ; and so on ...

The ``safe-pidfile`` option works similar to ``pidfile`` but performs the write
a little later in the loading process. This avoids overwriting the value when
app loading fails, with the consequent loss of a valid PID number.

Dealing with ultra-lazy apps (like Django)
******************************************

Some applications or frameworks (like Django) may load the vast majority of
their code only at the first request. This means that customer will continue
to experience slowdowns during reload even when using things like zerg mode
or similar.

This problem is hard to solve (impossible?) in the application server itself,
so you should find a way to force your app to load itself ASAP. A good trick
(read: works with Django) is to call the entry-point function (like the WSGI
callable) in the app itself:

.. code-block:: python

    def application(environ, sr):
        sr('200 OK', [('Content-Type', 'text/plain')])
        yield "Hello"

    application({}, lambda x, y: None)  # call the entry-point function

You may need to pass CGI vars to the environ to make a true request: it depends
on the WSGI app.

Finally: Do not blindly copy & paste!
*************************************

Please, turn on your brain and try to adapt shown configs to your needs, or
invent new ones.

Each app and system is different from the others.

Experiment before making a choice.

References
**********

:doc:`../MasterFIFO`

:doc:`../Hooks`

:doc:`../Zerg`

:doc:`../Fastrouter`

:doc:`../SubscriptionServer`
