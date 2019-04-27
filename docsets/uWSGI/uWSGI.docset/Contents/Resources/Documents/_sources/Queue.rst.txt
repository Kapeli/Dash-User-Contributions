The uWSGI queue framework
=========================

In addition to the :doc:`caching framework <Caching>`, uWSGI includes a shared queue.

At the low level it is a simple block-based shared array, with two optional counters, one for stack-style, LIFO usage, the other one for FIFO.

The array is circular, so when one of the two pointers reaches the end (or the beginning), it is reset. Remember this!

To enable the queue, use the ``queue`` option. Queue blocks are 8 KiB by default. Use ``queue-blocksize`` to change this.

.. code-block:: sh

    # 100 slots, 8 KiB of data each
    uwsgi --socket :3031 --queue 100
    # 42 slots, 128 KiB of data each
    uwsgi --socket :3031 --queue 42 --queue-blocksize 131072

Using the queue as a shared array
---------------------------------

.. code-block:: py

    # Put a binary string in slot 17.
    uwsgi.queue_set(17, "Hello, uWSGI queue!")
    
    # Get it back.
    print uwsgi.queue_get(17)


Using the queue as a shared stack
---------------------------------

.. warning:: Remember that :py:meth:`uwsgi.queue_pop` and :py:meth:`uwsgi.queue_last` will remove the item or items from the queue.

.. code-block:: py

    # Push a value onto the end of the stack.
    uwsgi.queue_push("Hello, uWSGI stack!")
    
    # Pop it back
    print uwsgi.queue_pop()

    # Get the number of the next available slot in the stack
    print uwsgi.queue_slot()
    
    # Pop the last N items from the stack
    items = uwsgi.queue_last(3)

Using the queue as a FIFO queue    
-------------------------------

.. note:: Currently you can only pull, not push. To enqueue an item, use :py:meth:`uwsgi.queue_set`.

.. code-block:: py

    # Grab an item from the queue
    uwsgi.queue_pull()
    # Get the current pull/slot position (this is independent from the stack-based one)
    print uwsgi.queue_pull_slot()

Notes
-----

* You can get the queue size with :py:data:`uwsgi.queue_size`.
* Use the ``queue-store`` option to persist the queue on disk. Use ``queue-store-sync`` (in master cycles -- usually seconds) to force disk syncing of the queue.
* The ``tests/queue.py`` application is a fully working example.