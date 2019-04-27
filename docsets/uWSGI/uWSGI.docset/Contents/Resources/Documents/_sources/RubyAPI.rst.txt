Ruby API support
================

Status
------

The uWSGI API for Ruby is still incomplete (QueueFramework, SharedArea, custom routing and SNMP being the most missing players). The DSL will be extended as soon as the various API calls are ready.

Currently available API functions and constants (available in the UWSGI ruby module) are


* UWSGI.suspend
* UWSGI.masterpid
* UWSGI.async_sleep
* UWSGI.wait_fd_read
* UWSGI.wait_fd_write
* UWSGI.async_connect
* UWSGI.signal
* UWSGI.register_signal
* UWSGI.register_rpc
* UWSGI.signal_registered
* UWSGI.signal_wait
* UWSGI.signal_received
* UWSGI.add_cron
* UWSGI.add_timer
* UWSGI.add_rb_timer
* UWSGI.add_file_monitor
* UWSGI.cache_get
* UWSGI.cache_get!
* UWSGI.cache_exists
* UWSGI.cache_exists?
* UWSGI.cache_del
* UWSGI.cache_set
* UWSGI.cache_set
* UWSGI.cache_set!
* UWSGI.cache_update
* UWSGI.cache_update!
* UWSGI.setprocname
* UWSGI.set_warning_message
* UWSGI.lock
* UWSGI.unlock
* UWSGI.mem
* UWSGI.mule_get_msg
* UWSGI.request_id
* UWSGI.mule_id
* UWSGI.mule_msg
* UWSGI.worker_id
* UWSGI.log
* UWSGI.logsize
* UWSGI.i_am_the_spooler
* UWSGI.send_to_spooler
* UWSGI.spool
* UWSGI::OPT
* UWSGI::VERSION
* UWSGI::HOSTNAME
* UWSGI::NUMPROC
* UWSGI::PIDFILE
* UWSGI::SPOOL_OK
* UWSGI::SPOOL_RETRY
* UWSGI::SPOLL_IGNORE

uWSGI DSL
---------

In parallel to the uWSGI API Python decorators, a DSL for Ruby is available, allowing elegant access to the uWSGI API.

The module is available as :file:`uwsgidsl.rb` in the source distribution. You can put this code in your :file:`config.ru` file, or use the ``rbrequire`` option to auto-include it.

timer(n, block)
---------------

Execute code at regular intervals.

.. code-block:: ruby

  timer 30 do |signum|
    puts "30 seconds elapsed"
  end

rbtimer(n, block)
-----------------

As timer, but using a red-black tree timer.

.. code-block:: ruby

  rbtimer 30 do |signum|
    puts "30 seconds elapsed"
  end

filemon(path, block)
--------------------

Execute code at file modifications.


.. code-block:: ruby

  filemon '/tmp' do |signum|
    puts "/tmp has been modified"
  end

cron(hours, mins, dom, mon, dow, block)
---------------------------------------

Execute a task periodically using the :doc:`CronInterface`.

.. code-block:: ruby

  cron 20,16,-1,-1,-1 do |signum|
    puts "It's time for tea."
  end

signal(signum, block)
---------------------

Register code as a signal handler for the :doc:`SignalFramework`.

.. code-block:: ruby

  signal 17 do |signum|
    puts "Signal #{signum} was invoked."
  end

postfork(block)
---------------

Execute code after each ``fork()``.

.. code-block:: ruby

  postfork do
    puts "uWSGI server called fork()"
  end

rpc(name, block)
----------------

Register code as a :doc:`RPC` function.

.. code-block:: ruby
  
  rpc 'helloworld' do
      return "Hello World"
  end
  
  rpc 'advancedhelloworld' do |x,y|
      return "x = #{x}, y = #{y}"
  end

mule(id?, block)
----------------

Execute code as a :doc:`Mule <Mules>` brain.

.. code-block:: ruby
  
  mule 1 do # Run in mule 1
    puts "I am the mule #{UWSGI.mule_id}"
  end

  mule do # Run in first available mule
    puts "I am the mule #{UWSGI.mule_id}"
  end

After the function returns, the mule will be brainless. To avoid this, put the code in a loop, or use ``muleloop``.

muleloop(id?, block)
--------------------

Execute code in a mule in looped context.

.. code-block:: ruby
  
  muleloop 3 do
    puts "I am the mule #{UWSGI.mule_id}"
    sleep(2)
  end

SpoolProc
---------

A subclass of ``Proc``, allowing you to define a task to be executed in the :doc:`Spooler<Spooler>`.

.. code-block:: ruby

  # define the function
  my_long_running_task = SpoolProc.new {|args|
    puts "I am a task"
    UWSGI::SPOOL_OK
  }

  # spool it
  my_long_running_task.call({'foo' => 'bar', 'one' => 'two'})

MuleFunc
--------

Call a function from any process (such as a worker), but execute in a mule

.. code-block:: ruby

  i_am_a_long_running_function = MuleFunc.new do |pippo, pluto|
    puts "i am mule #{UWSGI.mule_id} #{pippo}, #{pluto}"
  end
  
  i_am_a_long_running_function.call("serena", "alessandro")

The worker calls ``i_am_a_long_running_function()`` but the function will be execute asynchronously in the first available mule.

If you want to run the function on a specific mule, add an ID parameter. The following would only use mule #5.

.. code-block:: ruby

  i_am_a_long_running_function = MuleFunc.new 5 do |pippo,pluto|
    puts "i am mule #{UWSGI.mule_id} #{pippo}, #{pluto}"
  end

  i_am_a_long_running_function.call("serena", "alessandro")

Real world usage
----------------

A simple Sinatra app printing messages every 30 seconds:

.. code-block:: ruby

  # This is config.ru

  require 'rubygems'
  require 'sinatra'
  require 'uwsgidsl'
  
  timer 30 do |signum|
    puts "30 seconds elapsed"
  end
  
  get '/hi' do
    "Hello World!"
  end
  
  run Sinatra::Application

Or you can put your code in a dedicated file (:file:`mytasks.rb` here)

.. code-block:: ruby
  
  require 'uwsgidsl'
  
  timer 30 do |signum|
    puts "30 seconds elapsed"
  end
  
  timer 60 do |signum|
    puts "60 seconds elapsed"
  end

and then load it with

.. code-block:: sh

  uwsgi --socket :3031 --rack config.ru --rbrequire mytasks.rb --master --processes 4
