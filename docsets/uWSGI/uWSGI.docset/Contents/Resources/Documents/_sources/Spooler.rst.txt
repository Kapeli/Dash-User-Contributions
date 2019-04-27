The uWSGI Spooler
=================

Updated to uWSGI 2.0.1

Supported on: Perl, Python, Ruby

The Spooler is a queue manager built into uWSGI that works like a printing/mail system. 

You can enqueue massive sending of emails, image processing, video encoding, etc. and let the spooler do the hard work in background while your users get their requests served by normal workers.

A spooler works by defining a directory in which "spool files" will be written, every time the spooler find a file in its directory it will parse it and will run a specific function.

You can have multiple spoolers mapped to different directories and even multiple spoolers mapped to the same one.

The ``--spooler <directory>`` option allows you to generate a spooler process, while the ``--spooler-processes <n>`` allows you to set how many processes to spawn for every spooler.

The spooler is able to manage uWSGI signals too, so you can use it as a target for your handlers.

This configuration will generate a spooler for your instance (myspool directory must exists)

.. code-block:: ini

   [uwsgi]
   spooler = myspool
   ...
   
while this one will create two spoolers:

.. code-block:: ini

   [uwsgi]
   spooler = myspool
   spooler = myspool2
   ...

having multiple spoolers allows you to prioritize tasks (and eventually parallelize them)

Spool files
-----------

Spool files are serialized hashes/dictionaries of strings. The spooler will parse them and pass the resulting hash/dictionary to the spooler function (see below).

The serialization format is the same used for the 'uwsgi' protocol, so you are limited to 64k (even if there is a trick for passing bigger values, see the 'body' magic key below). The modifier1
for spooler packets is the 17, so a {'hello' => 'world'} hash will be encoded as:

========= ============== ==============
header    key1           value1
========= ============== ==============
17|14|0|0 |5|0|h|e|l|l|o |5|0|w|o|r|l|d
========= ============== ==============

A locking system allows you to safely manually remove spool files if something goes wrong, or to move them between spooler directories.

Spool dirs over NFS are allowed, but if you do not have proper NFS locking in place, avoid mapping the same spooler NFS directory to spooler on different machines.

Setting the spooler function/callable
-------------------------------------

Because there are dozens of different ways to enqueue spooler requests, we're going to cover receiving the requests first. 

To have a fully operational spooler you need to define a "spooler function/callable" to process the requests. 

Regardless of the the number of configured spoolers, the same function will be executed.
It is up to the developer to instruct it to recognize tasks.
If you don't process requests, the spool directory will just fill up.

This function must returns an integer value:

* -2 (SPOOL_OK) -- the task has been completed, the spool file will be removed
* -1 (SPOOL_RETRY) -- something is temporarily wrong, the task will be retried at the next spooler iteration
* 0 (SPOOL_IGNORE) -- ignore this task, if multiple languages are loaded in the instance all of them will fight for managing the task. This return values allows you to skip a task in specific languages.

Any other value will be interpreted as -1 (retry).

Each language plugin has its own way to define the spooler function:

Perl:

.. code-block:: pl

   uwsgi::spooler(
       sub {
           my ($env) = @_;
           print $env->{foobar};
           return uwsgi::SPOOL_OK;
       }
   );
   # hint - uwsgi:: is available when running using perl-exec= or psgi= 
   # no don't need to use "use" or "require" it, it's already there.
   
Python:

.. code-block:: py

   import uwsgi
   
   def my_spooler(env):
       print env['foobar']
       return uwsgi.SPOOL_OK
       
   uwsgi.spooler = my_spooler
    
Ruby:

.. code-block:: rb

   module UWSGI
        module_function
        def spooler(env)
                puts env.inspect
                return UWSGI::SPOOL_OK
        end
   end


Spooler functions must be defined in the master process, so if you are in lazy-apps mode, be sure to place it in a file that is parsed
early in the server setup. (in Python you can use --shared-import, in Ruby --shared-require, in Perl --perl-exec).

Python has support for importing code directly in the spooler with the ``--spooler-python-import`` option.

Enqueueing requests to a spooler
--------------------------------

The 'spool' api function allows you to enqueue a hash/dictionary into the spooler specified by the instance:

.. code-block:: ini

   # add this to your instance .ini file
   spooler=/path/to/spooler
   # that's it! now use one of the code blocks below to send requests
   # note: you'll still need to register some sort of receiving function (specified above)

.. code-block:: py

   # python
   import uwsgi
   uwsgi.spool({'foo': 'bar', 'name': 'Kratos', 'surname': 'the same of Zeus'})
   # or
   uwsgi.spool(foo='bar', name='Kratos', surname='the same of Zeus')
   # for python3 use bytes instead of strings !!!


.. code-block:: pl

   # perl 
   uwsgi::spool({foo => 'bar', name => 'Kratos', surname => 'the same of Zeus'})
   # the uwsgi:: functions are available when executed within psgi or perl-exec

.. code-block:: rb

   # ruby
   UWSGI.spool(foo => 'bar', name => 'Kratos', surname => 'the same of Zeus')
   
Some keys have a special meaning:

* 'spooler' => specify the ABSOLUTE path of the spooler that has to manage this task
* 'at' => unix time at which the task must be executed (read: the task will not be run until the 'at' time is passed)
* 'priority' => this will be the subdirectory in the spooler directory in which the task will be placed, you can use that trick to give a good-enough prioritization to tasks (for better approach use multiple spoolers)
* 'body' => use this key for objects bigger than 64k, the blob will be appended to the serialzed uwsgi packet and passed back to the spooler function as the 'body' argument

.. note::

   Spool arguments must be strings (or bytes for python3). The API functions will try to cast non-string values to strings/bytes, but do not rely on that functionality!

External spoolers
-----------------

You could want to implement a centralized spooler for your server across many uWSGI instances.

A single instance will manage all of the tasks enqueued by multiple uWSGI instances.

To accomplish this setup, each uWSGI instance has to know which spooler directories are valid (consider it a form of security).

To add an external spooler directory use the ``--spooler-external <directory>`` option, then add to it using the spool function.

The spooler locking subsystem will avoid any messes that you might think could occur.

.. code-block:: ini

   [uwsgi]
   spooler-external = /var/spool/uwsgi/external
   ...

.. code-block:: py

   # python
   import uwsgi
   uwsgi.spool({'foo': 'bar',  'spooler': '/var/spool/uwsgi/external'})
   # or
   uwsgi.spool(foo='bar', spooler='/var/spool/uwsgi/external')
   # for python3 use bytes instead of strings !!!



Networked spoolers
------------------

You can even enqueue tasks over the network (be sure the 'spooler' plugin is loaded in your instance, but generally it is built in by default).

As we have already seen, spooler packets have modifier1 17, you can directly send those packets to an uWSGI socket of an instance with a spooler enabled.

We will use the Perl ``Net::uwsgi`` module (exposing a handy uwsgi_spool function) in this example (but feel free to use whatever you want to write the spool files).

.. code-block:: perl

   #!/usr/bin/perl
   use Net::uwsgi;
   uwsgi_spool('localhost:3031', {'test'=>'test001','argh'=>'boh','foo'=>'bar'});
   uwsgi_spool('/path/to/my.sock', {'test'=>'test001','argh'=>'boh','foo'=>'bar'});
   
.. code-block:: ini

   [uwsgi]
   socket = /path/to/my.sock
   socket = localhost:3031
   spooler = /path/for/files
   spooler-processes=1
   perl-exec = /path/for/script-which-registers-spooler-sub.pl  
   ...
   
(thanks brianhorakh for the example)

Priorities
----------

We have already seen that you can use the 'priority' key to give order in spooler parsing.

While having multiple spoolers would be an extremely better approach, on system with few resources 'priorities' are a good trick.

They works only if you enable the ``--spooler-ordered`` option. This option allows the spooler to scan directories entry in alphabetical order.

If during the scan a directory with a 'number' name is found, the scan is suspended and the content of this subdirectory will be explored for tasks.

.. code-block:: sh

   /spool
   /spool/ztask
   /spool/xtask
   /spool/1/task1
   /spool/1/task0
   /spool/2/foo
   
With this layout the order in which files will be parsed is:

.. code-block:: sh

   /spool/1/task0
   /spool/1/task1
   /spool/2/foo
   /spool/xtask
   /spool/ztask
   
Remember, priorities only work for subdirectories named as 'numbers' and you need the ``--spooler-ordered`` option.

The uWSGI spooler gives special names to tasks so the ordering of enqueuing is always respected.

Options
-------
``spooler=directory``
run a spooler on the specified directory

``spooler-external=directory``
map spoolers requests to a spooler directory managed by an external instance

``spooler-ordered``
try to order the execution of spooler tasks (uses scandir instead of readdir)

``spooler-chdir=directory``
call chdir() to specified directory before each spooler task

``spooler-processes=##``
set the number of processes for spoolers

``spooler-quiet``
do not be verbose with spooler tasks

``spooler-max-tasks=##``
set the maximum number of tasks to run before recycling a spooler (to help alleviate memory leaks)

``spooler-signal-as-task``
combined use with ``spooler-max-tasks``. enable this, spooler will treat signal events as task.
run signal handler will also increase the spooler task count.

``spooler-harakiri=##``
set harakiri timeout for spooler tasks, see [harakiri] for more information.

``spooler-frequency=##``
set the spooler frequency

``spooler-python-import=???``
import a python module directly in the spooler

Tips and tricks
---------------

You can re-enqueue a spooler request by returning ``uwsgi.SPOOL_RETRY`` in your callable:

.. code-block:: py

    def call_me_again_and_again(env):
        return uwsgi.SPOOL_RETRY
    
You can set the spooler poll frequency using the ``--spooler-frequency <secs>`` option (default 30 seconds).

You could use the :doc:`Caching` or :doc:`SharedArea` to exchange memory structures between spoolers and workers.

Python (uwsgidecorators.py) and Ruby (uwsgidsl.rb) exposes higher-level facilities to manage the spooler, try to use them instead of the low-level approach described here.

When using a spooler as a target for a uWSGI signal handler you can specify which one to route signal to using its ABSOLUTE directory name.
