uWSGI Mules
===========

Mules are worker processes living in the uWSGI stack but not reachable via socket connections, that can be used as a generic subsystem to offload tasks. You can see them as a more primitive :doc:`spooler<Spooler>`.

They can access the entire uWSGI API and can manage signals and be communicated with through a simple string-based message system.

To start a mule (you can start an unlimited number of them), use the ``mule`` option as many times as you need.

Mules have two modes,

* Signal only mode (the default). In this mode the mules load your application as normal workers would. They can only respond to :doc:`uWSGI signals<Signals>`.
* Programmed mode. In this mode mules load a program separate from your application. See ProgrammedMules_.

By default each mule starts in signal-only mode. 

.. code-block:: sh

    uwsgi --socket :3031 --mule --mule --mule --mule

.. code-block:: xml

    <uwsgi>
        <socket>:3031</socket>
        <mule/>
        <mule/>
        <mule/>
        <mule/>
    </uwsgi>

Basic usage
-----------

.. code-block:: py

    import uwsgi
    from uwsgidecorators import timer, signal, filemon
    
    # run a timer in the first available mule
    @timer(30, target='mule')
    def hello(signum):
        print "Hi! I am responding to signal %d, running on mule %d" % (signum, uwsgi.mule_id())
    
    # map signal 17 to mule 2
    @signal(17, target='mule2')
    def i_am_mule2(signum):
        print "Greetings! I am running in mule number two."
    
    # monitor /tmp and arouse all of the mules on modifications
    @filemon('/tmp', target='mules')
    def tmp_modified(signum):
        print "/tmp has been modified. I am mule %d!" % uwsgi.mule_id()
    

.. _ProgrammedMules:

Giving a brain to mules
-----------------------

As mentioned before, mules can be programmed. To give custom logic to a mule, give the ``mule`` option a path to
a script (it must end in ".py") or a "package.module:callable" value.

.. code-block:: sh

    uwsgi --socket :3031 --mule=somaro.py --mule=mypkg.myapp:run_mule --mule --mule

This will run 4 mules, 2 in signal-only mode, one running :file:`somaro.py` and one running `mypkg.myapp:run_mule`.

.. code-block:: py

    # somaro.py
    from threading import Thread
    import time
    
    def loop1():
        while True:
            print "loop1: Waiting for messages... yawn."
            message = uwsgi.mule_get_msg()
            print message
    
    def loop2():
        print "Hi! I am loop2."
        while True:
            time.sleep(2)
            print "This is a thread!"
    
    t = Thread(target=loop2)
    t.daemon = True
    t.start()
    
    if __name__ == '__main__':
        loop1()

So as you can see from the example, you can use :py:meth:`uwsgi.mule_get_msg` to receive messages in a programmed mule. Multiple threads in the same programmed mule can wait for messages.

If you want to block a mule to wait on an uWSGI signal instead of a message you can use :py:meth:`uwsgi.signal_wait`.

Use :py:meth:`uwsgi.mule_msg` to send a message to a programmed mule. Mule messages can be sent from anywhere in the uWSGI stack, including but not limited to workers, the spoolers, another mule.

.. code-block:: py

    # Send the string "ciuchino" to mule1.
    # If you do not specify a mule ID, the message will be processed by the first available programmed mule.
    uwsgi.mule_msg("ciuchino", 1)

As you can spawn an unlimited number of mules, you may need some form of synchronization -- for example if you are developing a task management subsystem and do not want two mules to be able to start the same task simultaneously. You're in luck -- see :doc:`Locks`.

Organizing mules
----------------

Messages are eligible to be received by all programmed mules. They can be limited to specified groups of mules by creating mule farms using the ``farm`` option:

.. code-block:: sh

    uwsgi --socket :3031 --mule=feed.py --mule=feed.py --mule=wallow.py --farm=busy:1,2 --farm=idle:3

This will run three mules, where the mules 1 and 2, running ``feed.py``, are members of the ``busy`` farm, and mule 3, running ``wallow.py`` is the sole member of the ``idle`` farm. Messages are retrieved exactly as in ``somaro.py`` above but using :py:meth:`uwsgi.farm_get_msg` in place of :py:meth:`uwsgi.mule_get_msg`. Use :py:meth:`uwsgi.farm_msg` to send a message to a mule in a specified farm:

.. code-block:: py

    # Send the string "eat stuff" to farm "busy"
    uwsgi.farm_msg("busy", "eat stuff")

As with mules, :doc:`Locks` can be used to ensure only a single mule in a farm receives a given message to that farm.
