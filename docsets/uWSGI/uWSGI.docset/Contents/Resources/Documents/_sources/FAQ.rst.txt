Frequently Asked Questions (FAQ)
================================

Why should I choose uWSGI?
--------------------------

Because you can! :) uWSGI wants to be a complete web application deployment
solution with batteries included:

 * :doc:`ProcessManagement`
 * Management of long-running tasks
 * :doc:`RPC`
 * :doc:`Clustering`
 * :doc:`LoadBalancing`
 * :doc:`Monitoring`
 * :doc:`ResourceLimiting`

... and many other annoying everyday tasks that you'd have to delegate to
external scripts and manual sysadmin tasks.

If you are searching for a simple server for your WSGI, PSGI or Rack app, uWSGI
may not be for you. Though, if you are building an app which needs to be rock
solid, fast, and easy to distribute and optimize for various loads, you will
most likely find yourself needing uWSGI. 

The best definition for uWSGI is "Swiss Army Knife for your network applications".

What about the protocol?
------------------------

The uwsgi (all lowercase) protocol is derived from SCGI but with binary string
length representations and a 4-byte header that includes the size of the var
block (16 bit length) and a couple of general-purpose bytes.  We are not
reinventing the wheel. Binary management is much easier and cheaper than string
parsing, and every single bit of power is required for our projects. If you
need proof, look at the :doc:`official protocol documentation<Protocol>` and
you will understand why a new protocol was needed.  Obviously, you are free to
use the other supported protocols. Remember, if you cannot use uWSGI in some
scenario, it is a uWSGI bug.

Can I use it in cluster environments?
-------------------------------------

Yes, this is one of the main features of the uWSGI stack.  You can have
multiple instances bound on different servers, and using the load balancing
facilities of your webserver/proxy/router you can distribute your load.
Systems like :doc:`RPC` allows you to fast call functions on remote nodes, and
:doc:`Legion` allows you to elect a master in a multi-node setup.

So, why all those timeout configuration flags?
----------------------------------------------

Choosing sane timeouts is the key to high availability.  Do not trust network
applications that do not permit you to choose a timeout.

I need help! What do I do?
--------------------------

Post a message on the uWSGI mailing list including your

* Operating system version
* CPU architecture
* Webserver used (if any)
* uWSGI version
* uWSGI command line or config files

You should add the `--show-config` option and post the output in the message.
It will be very useful for finding out just what's wrong with your uWSGI.  You
can also :doc:`rebuild uWSGI<Build>` with debug symbols and run it under a
debugger like `gdb`.

uWSGI is an enormous project with hundreds of options. You should be prepared
that not everything will go right at the first shot. Ask for help, ask for help
and ask for help. If you are frustrated, do not waste time blaming and ranting
- instead simply join the list and ask for help. This is open source, if you
only rant you are doing nothing useful.

I am not a sysadmin, nor a UNIX guru. Can I use uWSGI?
------------------------------------------------------

That's a good question :) But sadly there is no simple answer.  uWSGI has not
been developed with simplicity in mind, but with versatility.  You can try it
by starting with one of the quickstarts and if you have problems, simply ask
for help in the list or on the IRC channel.

How can I buy commercial support for my company?
------------------------------------------------

Send an email to info at unbit.it with the word "uWSGI" in the subject. The
email you send should include your company information and your specific
request. We will reply as soon as possible.

Will this allow me to run my awesome apps on my ancient close-minded ISP?
-------------------------------------------------------------------------

Probably not. The uWSGI server requires a modern platform/environment. 

Where are the benchmarks?
-------------------------

Sorry, we only do "official" benchmarks for regression testing. If benchmarks
are very important to you, you can search on the mailing list, make your own
benchmarks or search on Google.  uWSGI gives precedence to machine health, so
do not expect your `ab` test with an unrealistic number of concurrent
connections to be managed flawlessly without tuning.  Some socket and
networking knowledge is required if you want to make a valid benchmark (and
avoid geek rage in your blog comments ;).  Also remember that uWSGI can be
run in various modes, so avoid comparing it configured in preforking mode
with another server in non-blocking/async mode if you do not want to look
ridiculous.

.. note::

  If you see your tests failing at higher concurrency rates you are probably
  hitting your OS socket backlog queue limit (maximum of 128 slots on Linux,
  tunable via `/proc/sys/net/somaxconn` and
  `/proc/sys/net/ipv4/tcp_max_syn_backlog` for TCP sockets).

  You can set this value in uWSGI with the `listen` configuration option.


Ha! Server XXX is faster than uWSGI! Take that!
-----------------------------------------------

As already stated uWSGI is not a silver bullet, it is not meant to be liked by
the whole world and it is obviously not the fastest server out there.  It is a
piece of software following an "approach" to problems you may not like or that
you may conversely love. The approach taken will work better for certain cases
than others, and each application should be analyzed on it's own merits using
appropriate and accruate real-world benchmarks.

What is 'Harakiri mode'?
------------------------

At Unbit we host hundreds of unreliable web apps on our servers. All of them
run on hardly constrained (at kernel level) environments where having processes
block due to an implementation error will result in taking down an entire site.
The harakiri mode has two operational modes:

* one that we define as "raw and a bit unreliable" (used for simple setup without a process manager) 
* and another one that we define as "reliable" that depends on the presence of the uWSGI process manager (see :doc:`ProcessManagement`).

The first one sets a simple alarm at the start of every request. If the process
gets a `SIGALRM` signal, it terminates itself. We call this unreliable, because
your app or some module you use could overwrite or simply cancel the alarm with
a simple call to `alarm()`.

The second one uses a master process shared memory area (via `mmap`) that
maintains statistics on every worker in the pool. At the start of every
request, the worker sets a timestamp representing the time after which the process
will be killed in its dedicated area. This timestamp is zeroed after every
successful request. If the master process finds a worker with a timestamp in
the past it will mercilessly kill it.

Will my app run faster with uWSGI?
----------------------------------

It's unlikely. The biggest bottleneck in web app deployment is the application
itself. If you want a faster environment, optimize your code or use techniques
such as clustering or caching. We say that uWSGI is fast because it introduces
a very little overhead in the deployment structure.

What are the most important options for performance and robustness in the uWSGI environment?
--------------------------------------------------------------------------------------------

By default, uWSGI is configured with sane "almost-good-for-all" values. But if
and when things start going wild, tuning is a must.

* Increasing (or decreasing) timeout is important, as is modifying the socket listen queue size.
* Think about threading. If you do not need threads, do not enable them.
* If you are running only a single application you can disable multiple interpreters.
* Always remember to enable the master process in production environments. See :doc:`ProcessManagement`.
* Adding workers does not mean "increasing performance", so choose a good value
  for the `workers` option based on the nature of your app (IO bound, CPU bound,
  IO waiting...)

Why not simply use HTTP as the protocol?
----------------------------------------

A good question with a simple answer: HTTP parsing is slow, really slow.  Why
should we do a complex task twice? The web server has already parsed the
request! The :doc:`uwsgi protocol<Protocol>` is very simple to parse for a
machine, while HTTP is very easy to parse for a human.  As soon as humans are
being used as servers, we will abandon the uwsgi protocol in favor of the HTTP
protocol.  All this said, you can use uWSGI via :doc:`HTTP`, :doc:`FastCGI`,
:doc:`ZeroMQ` and other protocols as well. 

Why do you support multiple methods of configuration?
-----------------------------------------------------

System administration is all about skills and taste. uWSGI tries to give
sysadmins as many choices as possible for integration with whatever
infrastructure is already available.  Having multiple methods of configuration is
just one way we achieve this.

What is the best webserver handler?
-----------------------------------

See :doc:`WebServers`.
