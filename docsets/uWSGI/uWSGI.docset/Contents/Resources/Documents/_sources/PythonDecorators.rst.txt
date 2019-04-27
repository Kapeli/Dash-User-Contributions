uWSGI API - Python decorators
=============================

:doc:`The uWSGI API<PythonModule>` is very low-level, as it must be language-independent.

That said, being too low-level is not a Good Thing for many languages, such as Python.

Decorators are, in our humble opinion, one of the more kick-ass features of Python, so in the uWSGI source tree you will find a module exporting a bunch of decorators that cover a good part of the uWSGI API.




Notes
-----

Signal-based decorators execute the signal handler in the first available worker.
If you have enabled the spooler you can execute the signal handlers in it, leaving workers free to manage normal requests. Simply pass ``target='spooler'`` to the decorator.

.. code-block:: py

    @timer(3, target='spooler')
    def hello(signum):
        print("hello")


Example: a Django session cleaner and video encoder
---------------------------------------------------

Let's define a :file:`task.py` module and put it in the Django project directory.

.. code-block:: py

    from uwsgidecorators import *
    from django.contrib.sessions.models import Session
    import os

    @cron(40, 2, -1, -1, -1)
    def clear_django_session(num):
        print("it's 2:40 in the morning: clearing django sessions")
        Session.objects.all().delete()

    @spool
    def encode_video(arguments):
        os.system("ffmpeg -i \"%s\" image%%d.jpg" % arguments['filename'])

The session cleaner will be executed every day at 2:40, to enqueue a video encoding we simply need to spool it from somewhere else.

.. code-block:: py

    from task import encode_video

    def index(request):
        # launching video encoding
        encode_video.spool(filename=request.POST['video_filename'])
        return render_to_response('enqueued.html')

Now run uWSGI with the spooler enabled:

.. code-block:: ini

    [uwsgi]
    ; a couple of placeholder
    django_projects_dir = /var/www/apps
    my_project = foobar
    ; chdir to app project dir and set pythonpath
    chdir = %(django_projects_dir)/%(my_project)
    pythonpath = %(django_projects_dir)
    ; load django
    module = django.core.handlers:WSGIHandler()
    env = DJANGO_SETTINGS_MODULE=%(my_project).settings
    ; enable master
    master = true
    ; 4 processes should be enough
    processes = 4
    ; enable the spooler (the mytasks dir must exist!)
    spooler = %(chdir)/mytasks
    ; load the task.py module
    import = task
    ; bind on a tcp socket
    socket = 127.0.0.1:3031

The only especially relevant option is the ``import`` one. It works in the same way as ``module`` but skips the WSGI callable search.
You can use it to preload modules before the loading of WSGI apps. You can specify an unlimited number of '''import''' directives.

Example: web2py + spooler + timer
---------------------------------

First of all define your spooler and timer functions (we will call it :file:``mytasks.py``)

.. code-block:: py

    from uwsgidecorators import *

    @spool
    def a_long_task(args):
        print(args)

    @spool
    def a_longer_task(args)
        print("longer.....")

    @timer(3)
    def three_seconds(signum):
        print("3 seconds elapsed")

    @timer(10, target='spooler')
    def ten_seconds_in_the_spooler(signum):
        print("10 seconds elapsed in the spooler")

Now run web2py.

.. code-block:: sh

    uwsgi --socket :3031 --spooler myspool --master --processes 4 --import mytasks --module web2py.wsgihandler

As soon as the application is loaded, you will see the 2 timers running in your logs.

Now we want to enqueue tasks from our web2py controllers.

Edit one of them and add

.. code-block:: py

    import mytasks # be sure mytasks is importable!

    def index(): # this is a web2py action
        mytasks.a_long_task.spool(foo='bar')
        return "Task enqueued"


uwsgidecorators API reference
-----------------------------

.. default-domain:: py

.. module:: uwsgidecorators

.. function:: postfork(func)

   uWSGI is a preforking (or "fork-abusing") server, so you might need to execute a fixup task after each ``fork()``. The ``postfork`` decorator is just the ticket.
   You can declare multiple ``postfork`` tasks. Each decorated function will be executed in sequence after each ``fork()``.

   .. code-block:: py

      @postfork
      def reconnect_to_db():
          myfoodb.connect()

      @postfork
      def hello_world():
          print("Hello World")

.. function:: spool(func, pass_arguments=False)

   The uWSGI :doc:`spooler<Spooler>` can be very useful. Compared to
   Celery or other queues it is very "raw". The ``spool`` decorator will
   help!

   .. code-block:: py

      @spool
      def a_long_long_task(arguments):
          print(arguments)
          for i in xrange(0, 10000000):
              time.sleep(0.1)

      @spool
      def a_longer_task(args):
          print(args)
          for i in xrange(0, 10000000):
              time.sleep(0.5)

      # enqueue the tasks
      a_long_long_task.spool(foo='bar', hello='world')
      a_longer_task.spool({'pippo':'pluto'})

   .. warning::
      On Python3, only ``bytes`` type arguments are allowed. See below for
      another way of passing arguments.

   When ``pass_arguments`` is set to ``True``, arguments can be of any type
   supported by the :mod:`pickle` module. The following arguments have
   a special meaning:

    * ``spooler``: specify the **absolute** path of the spooler that has to
      manage this task

    * ``at``: unix time at which the task must be executed (read: the task
      will not be run until the ``at`` time is passed)

    * ``priority``: this will be the subdirectory in the spooler directory
      in which the task will be placed, you can use that trick to give
      a good-enough prioritization to tasks (for better approach use
      multiple spoolers)

   .. warning::
      On Python3, the special arguments ``spooler``, ``at``,
      ``priority`` and ``body`` **must** be ``bytes``.

   .. code-block:: py

      @spool(pass_arguments=True)
      def some_task(*args, **kwargs):
          print(args)
          print(kwargs)
          for i in xrange(0, 10000000):
              time.sleep(0.5)

      # enqueue the task
      some_task.spool(id=42, foo=['bar', 'baz'], func=min, at=str(1497023151))

   The functions will automatically return ``uwsgi.SPOOL_OK`` so they will
   be executed one time independently by their return status.

.. XXX: What does the above mean?

.. function:: spoolforever(func, pass_arguments=False)

   Use ``spoolforever`` when you want to continuously execute a spool task.
   A ``@spoolforever`` task will always return ``uwsgi.SPOOL_RETRY``.

   .. code-block:: py

     @spoolforever
     def a_longer_task(args):
         print(args)
         for i in xrange(0, 10000000):
             time.sleep(0.5)

     # enqueue the task
     a_longer_task.spool({'pippo':'pluto'})

   .. warning::
      On Python3, only ``bytes`` type arguments are allowed. See below for
      another way of passing arguments.

   When ``pass_arguments`` is set to ``True``, arguments can be of any type
   supported by the :mod:`pickle` module. The following arguments have
   a special meaning:

    * ``spooler``: specify the **absolute** path of the spooler that has to
      manage this task

    * ``at``: unix time at which the task must be executed (read: the task
      will not be run until the ``at`` time is passed)

    * ``priority``: this will be the subdirectory in the spooler directory
      in which the task will be placed, you can use that trick to give
      a good-enough prioritization to tasks (for better approach use
      multiple spoolers)

   .. warning::
      On Python3, the special arguments ``spooler``, ``at``,
      ``priority`` and ``body`` **must** be ``bytes``.

   .. code-block:: py

     @spoolforever(pass_arguments=True)
     def a_longer_task(*args):
         print(args)
         for i in xrange(0, 10000000):
             time.sleep(0.5)

     # enqueue the task
     a_longer_task.spool('pluto', 42)


.. function:: spoolraw(func, pass_arguments=False)

  Advanced users may want to control the return value of a task.

   .. code-block:: py

      @spoolraw
      def a_controlled_task(args):
          if args['foo'] == 'bar':
              return uwsgi.SPOOL_OK
          return uwsgi.SPOOL_RETRY

      a_controlled_task.spool(foo='bar')

   .. warning::
      On Python3, only ``bytes`` type arguments are allowed. See below for
      another way of passing arguments.

   When ``pass_arguments`` is set to ``True``, arguments can be of any type
   supported by the :mod:`pickle` module. The following arguments have
   a special meaning:

    * ``spooler``: specify the **absolute** path of the spooler that has to
      manage this task

    * ``at``: unix time at which the task must be executed (read: the task
      will not be run until the ``at`` time is passed)

    * ``priority``: this will be the subdirectory in the spooler directory
      in which the task will be placed, you can use that trick to give
      a good-enough prioritization to tasks (for better approach use
      multiple spoolers)

   .. warning::
      On Python3, the special arguments ``spooler``, ``at``,
      ``priority`` and ``body`` **must** be ``bytes``.

   .. code-block:: py

      @spoolraw(pass_arguments=True)
      def a_controlled_task(**kwargs):
          if kwargs['foo'] == 'bar':
              return uwsgi.SPOOL_OK
          return uwsgi.SPOOL_RETRY

      a_controlled_task.spool(foo='bar', age=42)

.. function:: rpc("name", func)

   uWSGI :doc:`RPC` is the fastest way to remotely call functions in applications hosted in uWSGI instances. You can easily define exported functions with the @rpc decorator.

   .. code-block:: py

      @rpc('helloworld')
      def ciao_mondo_function():
          return "Hello World"

.. function:: signal(num)(func)

   You can register signals for the :doc:`signal framework<Signals>` in one shot.

   .. code-block:: py

       @signal(17)
       def my_signal(num):
           print("i am signal %d" % num)

.. function:: timer(interval, func)

   Execute a function at regular intervals.

   .. code-block:: py

      @timer(3)
      def three_seconds(num):
          print("3 seconds elapsed")

.. function:: rbtimer(interval, func)

   Works like @timer but using red black timers.

.. XXX: What the hell does _that_ mean?

.. function:: cron(min, hour, day, mon, wday, func)


   Easily register functions for the :doc:`CronInterface`.

   .. code-block:: py

      @cron(59, 3, -1, -1, -1)
      def execute_me_at_three_and_fiftynine(num):
          print("it's 3:59 in the morning")

   Since 1.2, a new syntax is supported to simulate ``crontab``-like intervals (every Nth minute, etc.). ``*/5 * * * *`` can be specified in uWSGI like thus:

   .. code-block:: py

      @cron(-5, -1, -1, -1, -1)
      def execute_me_every_five_min(num):
          print("5 minutes, what a long time!")

.. function:: filemon(path, func)

   Execute a function every time a file/directory is modified.

   .. code-block:: py

        @filemon("/tmp")
        def tmp_has_been_modified(num):
            print("/tmp directory has been modified. Great magic is afoot")

.. function:: erlang(process_name, func)

   Map a function as an :doc:`Erlang<Erlang>` process.

   .. code-block:: py

        @erlang('foobar')
        def hello():
            return "Hello"


.. function:: thread(func)

    Mark function to be executed in a separate thread.

    .. important:: Threading must be enabled in uWSGI with the ``enable-threads`` or ``threads <n>`` option.

    .. code-block:: py

        @thread
        def a_running_thread():
            while True:
                time.sleep(2)
                print("i am a no-args thread")

        @thread
        def a_running_thread_with_args(who):
            while True:
                time.sleep(2)
                print("Hello %s (from arged-thread)" % who)

        a_running_thread()
        a_running_thread_with_args("uWSGI")

    You may also combine ``@thread`` with ``@postfork`` to spawn the postfork handler in a new thread in the freshly spawned worker.

    .. code-block:: py

        @postfork
        @thread
        def a_post_fork_thread():
            while True:
                time.sleep(3)
                print("Hello from a thread in worker %d" % uwsgi.worker_id())

.. function:: lock(func)

    This decorator will execute a function in fully locked environment, making it impossible for other workers or threads (or the master, if you're foolish or brave enough) to run it simultaneously.
    Obviously this may be combined with @postfork.

    .. code-block:: py

        @lock
        def dangerous_op():
            print("Concurrency is for fools!")


.. function:: mulefunc([mulespec], func)

    Offload the execution of the function to a :doc:`mule<Mules>`. When the offloaded function is called, it will return immediately and execution is delegated to a mule.

    .. code-block:: py

        @mulefunc
        def i_am_an_offloaded_function(argument1, argument2):
            print argument1,argument2

    You may also specify a mule ID or mule farm to run the function on. Please remember to register your function with a uwsgi import configuration option.

    .. code-block:: py

        @mulefunc(3)
        def on_three():
            print "I'm running on mule 3."

        @mulefunc('old_mcdonalds_farm')
        def on_mcd():
            print "I'm running on a mule on Old McDonalds' farm."

.. function:: harakiri(time, func)

    Starting from uWSGI 1.3-dev, a customizable secondary :term:`harakiri` subsystem has been added. You can use this decorator to kill a worker if the given call is taking too long.

    .. code-block:: py

        @harakiri(10)
        def slow_function(foo, bar):
            for i in range(0, 10000):
                for y in range(0, 10000):
                    pass

        # or the alternative lower level api

        uwsgi.set_user_harakiri(30) # you have 30 seconds. fight!
        slow_function()
        uwsgi.set_user_harakiri(0) # clear the timer, all is well
