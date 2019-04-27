Hooks
=====

(updated to uWSGI 1.9.16)

uWSGI's main directive is being "modular". The vast majority of its features are exposed as plugins, both to allow users to optimize
their build and to encourage developers to extend it.

Writing plugins can be an annoying task, especially if you only need to change/implement a single function.

For simple tasks, uWSGI exposes an hook API you can abuse to modify uWSGI's internal behaviors.

The "hookable" uWSGI phases
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before being ready to manage requests, uWSGI goes through various "phases". You can attach one or more "hooks" to these phases.

Each phase can be "fatal", if so, a failing hook will mean failing of the whole uWSGI instance (generally calling ``exit(1)``).

Currently (September 2013) the following phases are available:

* ``asap`` run directly after configuration file has been parsed, before anything else is done. it is fatal.
* ``pre-jail`` run before any attempt to drop privileges or put the process in some form of jail. it is fatal.
* ``post-jail`` run soon after any jailing, but before privileges drop. If jailing requires fork(), the parent process run this phase. it is fatal.
* ``in-jail`` run soon after jayling, but after post-jail. If jailing requires fork(), the chidlren run this phase. it is fatal.
* ``as-root`` run soon before privileges drop (last chance to run something as root). it is fatal.
* ``as-user`` run soon after privileges drop. it is fatal.
* ``pre-app`` run before applications loading. it is fatal.
* ``post-app`` run after applications loading. it is fatal.
* ``accepting`` run before the each worker starts accepting requests (available from uWSGI 1.9.21).
* ``accepting1`` run before the first worker starts accepting requests (available from uWSGI 1.9.21).
* ``accepting-once`` run before the each worker starts accepting requests (available from uWSGI 1.9.21, runs one time per instance).
* ``accepting1-once`` run before the first worker starts accepting requests (available from uWSGI 1.9.21, runs one time per instance).
* ``as-user-atexit`` run before shutdown of the instance. it is non-fatal.
* ``as-emperor`` run soon after the spawn of a vassal in the Emperor process. it is non-fatal.
* ``as-vassal`` run in the vassal before executing the uwsgi binary. it is fatal.

The "hardcoded" hooks
^^^^^^^^^^^^^^^^^^^^^

As said before, the purpose of the hook subsystem is to allow attaching "hooks" to the various uWSGI phases.

There are two kind of hooks. The simple ones are the so-called "hardcoded" ones. They expose common patterns at the cost of versatility.

Currently (September 2013) the following "hardcoded" hooks are available (they run in the order they are shown below):


``mount`` -- mount filesystems
******************************

Arguments: <filesystem> <src> <mountpoint> [flags]

The exposed flags are the ones available for the operating system. As an example on Linux you will options like bind, recursive, readonly etc.

``umount`` -- unmount filesystems
*********************************

Arguments: <mountpoint> [flags]

``exec`` run shell commands
***************************

Arguments: <command> [args...]

Run the command under ``/bin/sh``.

If for some reason you do not want to use ``/bin/sh`` as the running shell, you can override it with the ``--binsh`` option. You can specify multiple ``--binsh`` options -- they will be tried until one valid shell is found.

``call`` call functions in the current process address space
************************************************************

Arguments: <symbol> [args...]

Generally the arguments are ignored (the only exceptions are the emperor/vassal phases, see below) as the system expects to call the symbol without arguments.

``<symbol>`` can be any symbol currently available in the process's address space.

This allows some interesting tricks when combined with the ``--dlopen`` uWSGI option:

.. code-block:: c

   // foo.c
   #include <stdio.h>
   void foo_hello() {
           printf("I am the foo_hello function called by a hook!\n");
   }
   
Build this as a shared library:

.. code-block:: sh

   gcc -o foo.so -shared -fPIC foo.c
   
and load it into the uWSGI symbol table.

.. code-block:: sh

   uwsgi --dlopen ./foo.so ...
   
From now on, the "foo_hello" symbol is available in the uWSGI symbol table, ready to be called by the 'call' hooks.

.. warning::

   As --dlopen is a wrapper for the ``dlopen()`` function, beware of absolute paths and library search paths. If you do not want headaches, use always absolute paths when dealing with shared libraries.

Attaching "hardcoded" hooks
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each hardcoded hook exposes a set of options for each phase (with some exceptions).

Each option is composed by the name of the hook and its phase, so to run a command in the ``as-root`` phase you will use ``--exec-as-root``, or ``--exec-as-user`` for the ``as-user`` phase.

Remember, you can attach all of the hooks you need to a hook-phase pair.

.. code-block:: ini

   [uwsgi]
   ...
   exec-as-root = cat /proc/cpuinfo
   exec-as-root = echo 1 > /proc/sys/net/ipv4/ip_forward
   
   exec-as-user = ls /tmp
   exec-as-user-at-exit = rm /tmp/foobar
   
   dlopen = ./foo.so
   call-as-user = foo_hello
   ...
   
The only exception to the rule are the `as-emperor` and `as-vassal` phases. For various reasons they expose a bunch of handy variants -- see below.

The "advanced" hooks
^^^^^^^^^^^^^^^^^^^^

A problem that limits their versatility (a big no-no in the uWSGI state of mind) with hardcoded hooks, is that you cannot control the order of the whole chain (as each phase executes each hooks grouped by type). If you want more control, "advanced" hooks are the best choice.

Each phase has a single chain in which you specify the hook the call and which handler.

Handlers specify how to run hooks. New handlers can be registered by plugins.

Currently the handlers exposed by the core are:

* ``exec`` - same as the 'exec' hardcoded options
* ``call`` - call the specified symbol ignoring return value
* ``callret`` - call the specified symbol expecting an int return. anything != 0 means failure
* ``callint`` - call the specified symbol parsing the argument as an int
* ``callintret`` - call the specified symbol parsing the argument as an int and expecting an int return.
* ``mount`` - same as 'mount' hardcoded options
* ``umount`` - same as 'umount' hardcoded options
* ``cd`` - convenience handler, same as ``call:chdir <directory>``
* ``exit`` - convenience handler, same as ``callint:exit [num]``
* ``print`` - convenience handler, same as calling the ``uwsgi_log`` symbol
* ``write`` - (from uWSGI 1.9.21), write a string to the specified file using write:<file> <string>
* ``writefifo`` - (from uWSGI 1.9.21), write a string to the specified FIFO using writefifo:<file> <string>
* ``unlink`` - (from uWSGI 1.9.21), unlink the specified file

.. code-block:: ini

   [uwsgi]
   ...
   hook-as-root = mount:proc none /proc
   hook-as-root = exec:cat /proc/self/mounts
   hook-pre-app = callint:putenv PATH=bin:$(PATH)
   hook-post-app = call:uwsgi_log application has been loaded
   hook-as-user-atexit = print:goodbye cruel world
   ...
