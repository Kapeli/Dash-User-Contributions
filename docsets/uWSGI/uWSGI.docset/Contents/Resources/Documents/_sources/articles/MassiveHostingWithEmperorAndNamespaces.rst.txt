Massive "secure" Hosting with the Emperor and Linux Namespaces, AKA "Improving unbit.it and pythonanywhere.com"
===============================================================================================================

Author: Roberto De Ioris

*** WORK IN PROGRESS ***

Disclaimer
**********

In the following intro i will mention two companies: Unbit and pythonanywhere.com. I work with both (effectively i own the first one :P).

If you think i am making advertising to both, well you are right.

Intro
*****

Since 2005 i work as chief sysadmin in the italian ISP Unbit (http://unbit.it) and as a consultant for various hosting company worldwide.

Unbit is a developer-oriented service, we allow hosting basically anything you want without forcing you to a VPS, simply abusing Linux kernel facilities (it is very similar to what currently Heroku
does but about 5 years before Heroku existed ;)

In 2009 we started the uWSGI project, initially as a WSGI server, then we slowly realized that its paradigms could be applied to all our infrastructure, so now it is becoming
a sort of "hosting platform" for various languages. We plan to use only uWSGI for the whole Unbit hosting stack by 2014.

Before you get excited, Unbit accepts only Italian customers (we are not racists, it is a policy for avoiding legal problems with the other hosting companies we work with) and our prices
are quite high as we do not make any kind of over-selling (and more important we do not give free-accounts ;)

In more than 8 years me and my co-workers experienced thousands of problems (yes, if you want to enter the internet services market be prepared to invest the vast majority of your time
solving problems created by users without the minimal respect for you as a person ;) so, what you see in the whole uWSGI project is the result of this years
of headaches and non-sleeping nights (and insults by customers)

During summer 2013 i worked a bit with the pythonanywhere.com guys (mainly with Harry Percival).

They heavily use uWSGI features for their service, so they helped popping-up new ideas and solutions in my mind.

In uWSGI 1.9.15 lot of new patches for advanced Linux namespaces usage have been merged, thanks to the collaboration with pythonanywhere.com guys.

Based on the experiences of the two companies, this article will show one of the approaches you can follow to build your service for hosting unreliable webapps (yes, even if you have the largest collection of pacifist customers, they have to be considered 'unreliable' and 'evil', otherwise you are not a good sysadmin).

It is not a step-by-step tutorial, but some kind of cookbook to give you some basis for improving and adapting the concepts for your needs.

What we want to allow to our users
**********************************

- deploy WSGI,PSGI and RACK applications (no CGI and php, albeit technically possible, if you think you can make any kind of money with php hosting you should start finding a second job)
- run cron scripts
- run private services (redis, beanstalkd, memcached...)
- applications can connect to the internet
- multiple domain names can map to the same instance

...and what we want to forbid
*****************************

- users cannot see the processes of the other accounts in the machine. Their init process has to be the uWSGI master
- users cannot see the files of the other accounts in the machine
- users cannot connect to private services (memcached, redis...) of the other accounts in the machine
- users cannot read/write ipc semaphores, shared memory and message queues of the other accounts in the machine
- users cannot allocate more memory than the amount they paid for
- users cannot use more cpu power than the amount they paid for

The Operating System
********************

The Webserver
*************

As we do not need to worry about php and the abuse of .htaccess files, we can choose any server we want.

We prefer nginx (even if we [Unbit] are slowly moving to the uWSGI http/https/spdy router as we only need a minimal proxy with dynamic routing, but for anything more complex nginx is the way to go), but you can use whatever you like.

The "control panel"
*******************

This is the thing you need to develop, the more your panel is usable and powerful the more your users will be happy.

Your control panel is probably the thing will make your hosting company successful.

The objective of your control panel is generating "vassal files" (see below). Vassal files can be .ini, xml, yaml and json (unless you have particular reasons to use other formats).

The vassal file contains the whole structure of a customer micro-system. As soon as a vassal file is created it will be deployed (and when it is changed it will be reloaded)

uWSGI 'language' plugins
************************

We want to support multiple kind of applications. The better approach will be having a single uWSGI binary and a series of 'language plugins' (one for each language you want to support).

You can support multiple versions of the same language. Just build the corresponding plugin.

In Unbit we make an extremely modular uWSGi distribution (basically all is a plugin). This is required as we account any MB of memory
so we allow users to enable only the required features to gain much memory as possible.

If you are still not a black-belt in uWSGI mastering, i suggest you to start with the included 'nolang' build profile.

It will build a standard uwsgi binary without any language builtin.

...

Lazy apps VS prefork
********************

One of the controversial design choices of uWSGI is "preforking by default".

It means your app is loaded on startup and then fork() is called for each worker.

While this is the common approach in the UNIX world and it is an expected behaviour for a Perl developer
(that is historically more near to the UNIX world) it is totally unknown and unexpected by a Python (and maybe Ruby) one.

So one of the choices you need to make when building a uWSGI-based service is how to manage the fork() behaviour.

If you are unsure let me tell you one thing: with preforking behaviour you will make some user very happy, and lot of users
completely lost. With --lazy-apps you will have all of your users totally unconcerned. Trust me, few happy users cannot make you happy too when you have angry customers too.

So, uWSGI default fork() behaviour is generally wrong for massive hosting, so add --lazy-apps and eventually give the advanced users the freedom to change it when needed.


The filesystem layout
*********************

Distro upgrades are always a bloodbath. It is a pretty optimistic analysis. trust me.

But "tempus fugit" so sooner or later one of your customer will start asking for a more recent packages set...

You can upgrade, but you will automatically place the vast majority of your customers in berserk mode, as very probably their apps
will no more work.

A solution for making everyone happy is having different distribution in your system (yes, it sounds silly, but please continue reading).

Debbotstrap is a great tool. Let's create under the /distros directory our set of distributions:

.. code-block:: sh

   debootstrap lucid /distros/lucid
   debootstrap etch /distros/etch
   debootstrap precise /distros/precise
   debootstrap saucy /distros/saucy
   ...
   
Each user will be able to choose (and change) its distro, as thanks to our setup (see below) its root filesystem will be a readonly mount
of one of the available distros.

The final layout will be:

* / (rootfs, mapped readonly to one of the dir in /distros)
* /proc (needed for showing processes and getting system informations)
* /tmp (each user should have a dedicated /tmp)
* /dev (should contain at least zero and null, but can be a bind mount to the system /dev too)
* /dev/pts (required for pseudoterminals, shared by all vassals [til linux pts namespace will be released])
* /var/run (all of the sockets will be bound here, and symlinked by the main rootfs for nginx and ssh access)
* /opt (this could be a bind mount shared by all of the users containing distribution independent files)


Linux namespaces
****************

This is the first step to limit users.

For this setup we will use 5 namespaces: filesystem, sysv ipc, uts, networking and pid

filesystem (fs)
^^^^^^^^^^^^^^^

this allows changing the filesystems layout (mountpoints).

Instead of chroot() in each vassal, we will use the --pivot-root option (it is linux specific) that combined with
mount namespace allows fine-grained configuration of the filesystem layout

sysv ipc (ipc)
^^^^^^^^^^^^^^

sysv ipc exposes 3 primitives: semaphores, shared memory and message queues.

unsharing it creates a dedicated set of this 3 features

uts (uts)
^^^^^^^^^

this namespace allows you to have a dedicated hostname

networking (net)
^^^^^^^^^^^^^^^^

when you unshare for the main network namespace, you will lose access to interface addresses. A new loopback will be allocated.

processes (pid)
^^^^^^^^^^^^^^^

this namespace allows you to hide the user the processes not being part of the user namspace itself.

The uWSGI master process will be the pid 1 for the user.

Namespacing the Emperor
^^^^^^^^^^^^^^^^^^^^^^^

The --emperor-use-clone option allows the Emperor to directly spawn vassals in a new namespace.

Our config will be something like:

.. code-block:: ini

   [uwsgi]
   emperor = /etc/uwsgi/vassals
   emperor-user-clone = fs,ipc,uts,net,pid
  
while each vassal will be

.. code-block:: ini

   [uwsgi]
   ; set the hostname
   exec-as-root = hostname foobar
   ; bring up loopback
   exec-as-root = ifconfig lo up

Linux cgroups
*************

uWSGI Emperor and vassals
*************************

Networking
**********

This is probably the most complex part. The "ortodox" way to give networking to a jailed setup is using veth or macvlan.

The first one is a "network pipe" composed by two virtual interfaces. After the namespace is created you can move one of the end of the pipe to the namespace.

Macvlan, instead works by assigning an additional mac address to the physical interface.

Both solutions are great for VPS-like setups, but here we need networking only to connect to external services (inbound connections are managed by the http proxy).

Both veth and macvlan approaches are hard to manage correctly, and while in 1.9.15 we introduced lot of features to simplify the required steps, in 1.9.16 we decided
to create an ad-hoc solution based on tuntap devices.

Basically for each vassal we create a tun device (it is a virtuale network interface manageable via user space) connected (via unix sockets) to another tun device in the main namespace.

The tuntap-router is a software-based ip router, it mainly get packets fro ma tuntap device and forward them to a unix socket (and the opposite).

This approach simplify the whole setup extremely, and, as a killer feature an ultra simpel firewall is embedded in the process to configure internal rules.

The tuntap router should run in the Emperor (it is a uWSGI gateway so this time we need the master process):

.. code-block:: ini

   [uwsgi]
   emperor = /etc/uwsgi/vassals
   emperor-user-clone = fs,ipc,uts,net,pid
   master = true
   ; create the tun interface 'emperor0' reachable by /var/run/tuntap.socket
   tuntap-router = emperor0 /var/run/tuntap.socket
   ; give an internal ip address to 'emperor0'
   exec-as-root = ifconfig emperor0 192.168.0.1 netmask 255.255.255.0
   ; configure NAT for vassals
   exec-as-root = iptables -t nat -F
   exec-as-root = iptables -t nat -A POSTROUTING -o eth0 -s 192.168.0.0/24 -j MASQUERADE
   exec-as-root = echo 1 > /proc/sys/net/ipv4/ip_forward
   
   ; configure the internal firewall to disallow communication between vassals
   tuntap-router-firewall-out = allow 192.168.0.0/24 192.168.0.1
   tuntap-router-firewall-out = deny 192.168.0.0/24 192.168.0.0/24
   tuntap-router-firewall-out = allow 192.168.0.0/24 0.0.0.0
   ; we need this rule as default policy is 'allow'
   tuntap-router-firewall-out = deny
   tuntap-router-firewall-in = allow 192.168.0.1 192.168.0.0/24
   tuntap-router-firewall-in = deny 192.168.0.0/24 192.168.0.0/24
   tuntap-router-firewall-in = allow 0.0.0.0 192.168.0.0/24
   ; we need this rule as default policy is 'allow'
   tuntap-router-firewall-in = deny
   
and a vassal

.. code-block:: ini

   [uwsgi]
   master = true
   ; set the hostname
   exec-as-root = hostname foobar
   ; bring up loopback
   exec-as-root = ifconfig lo up
   ; bring up the tuntap device and connect to the emperor
   tuntap-device = uwsgi0 /var/run/tuntap.socket
   ; configure the 'uwsgi0' interface
   exec-as-root = ifconfig uwsgi0 192.168.0.2 netmask 255.255.255.0
   ; use the tuntap router as default gw
   exec-as-root = route add default gw 192.168.0.1
   ...

Cron
****

Cron tasks are added to the vassal file, the syntax is a bit different from classic crontabs as intead of * and the , we only use numbers
(yes it is a bit less versatile than classic cron, but uWSGI config files allows for cycle and other constructs)

.. code-block:: ini

   [uwsgi]
   ; run at 23:59 every day
   cron = 59 23 -1 -1 -1 myscript arg1
   ; run every five minutes on saturday
   cron = -5 -1 -1 -1 6

Static file serving
*******************

Additional daemons
******************

SSH
***

Managing ssh could be really tricky with namespace setups. The Linux syscall "setns" allows "attaching" to an already running namespace.

It generally works, but i will now tell you a technical reason why i do not want to use it for my services: i do not like it. period.

We have already seen unix sockets works very well as a communication channel between namespaces, why not use them to "enter" an already running namespace ?

If you work as a unix sysadmin, you cannot ignore pseudoterminals (or terminals in general). It is one of the oldest (and rawest) api of the unix world, by the work by ages. And they works great.

The uWSGI distribution come with 2 pty-related plugin: pty and forkptyrouter.

The first one simply attach a single pseudoterminal to your workers and bind to a network address. Connecting to this address give access
to the pseudoterminal. This trick allows for advanced techniques like shared debugging. The pty plugin exposes the client part too, so you can use the uwsgi binary itself to connect to this pty.

How this can be useful for our ssh access ? It is not.

What we need now is the forkptyrouter (or forkpty-router for better readability). It works very similar to the pty server with the difference
it generate a new pty for each connection. Exacly like ssh does.

The forkpty-router run into the namespace, so any process attached to it will effectively run in the namespace itself.

You should now see the point: our customers login via ssh as non-namespaced account but instead giving them the default shell we force them to connect
to the pty-router.

The "downside" of this approach is that we need two pty for each ssh peer (one for client -> ssh and the other for ssh -> namespace).

To force the ssh server to run a specific command, use the ForceCommand directive in the sshd_config


Bonus: KSM
**********

What is missing
***************

- Accounting network usage
- Scaling to multiple machines
