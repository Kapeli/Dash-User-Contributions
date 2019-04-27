Locks
=====

uWSGI supports a configurable number of locks you can use to synchronize worker
processes.  Lock 0 (zero) is always available, but you can add more with the
``locks`` option.  If your app has a lot of critical areas, holding and
releasing the same lock over and over again can kill performance.

.. code-block:: py

    def use_lock_zero_for_important_things():
        uwsgi.lock() # Implicit parameter 0
        # Critical section
        uwsgi.unlock() # Implicit parameter 0

    def use_another_lock():
        uwsgi.lock(1)
        time.sleep(1) # Take that, performance! Ha!
        uwsgi.unlock(1)
