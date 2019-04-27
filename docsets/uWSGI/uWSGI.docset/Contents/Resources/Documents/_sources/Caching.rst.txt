The uWSGI caching framework
===========================

.. note::

  This page is about "new-generation" cache introduced in uWSGI 1.9.
  For old-style cache (now simply named "web caching") check :doc:`WebCaching`

uWSGI includes a very fast, all-in-memory, zero-IPC, SMP-safe,
constantly-optimizing, highly-tunable, key-value store simply called "the
caching framework".  A single uWSGI instance can create an unlimited number of
"caches" each one with different setup and purpose.

Creating a "cache"
******************

To create a cache you use the ``--cache2`` option. It takes a dictionary of
arguments specifying the cache configuration.  To have a valid cache you need
to specify its name and the maximum number of items it can contains.

.. code-block:: sh

   uwsgi --cache2 name=mycache,items=100 --socket :3031

this will create a cache named "mycache" with a maximum of 100 items. Each item can be at most 64k.


A sad/weird/strange/bad note about "the maximum number of items"
****************************************************************

If you start with a 100 item cache you will suddenly note that the true maximum number of items you can use is indeed 99.

This is because the first item of the cache is always internally used as "NULL/None/undef" item.

Remember this when you start planning your cache configuration.


Configuring the cache (how it works)
************************************

The uWSGI cache works like a file system. You have an area for storing keys
(metadata) followed by a series of fixed size blocks in which to store the
content of each key.  Another memory area, the hash table is allocated for fast
search of keys.  When you request a key, it is first hashed over the hash
table. Each hash points to a key in the metadata area.  Keys can be linked to
manage hash collisions. Each key has a reference to the block containing its
value.

Single block (faster) vs. bitmaps (slower)
******************************************

.. warning:: Bitmap mode is considered production ready only from uWSGI 2.0.2! (That is, it was buggy before that.)

In the standard ("single block") configuration a key can only map to a single
block. Thus if you have a cache block size of 64k your items can be at most
65,535 bytes long. Conversely items smaller than that will still consume 64k of
memory.  The advantage of this approach is its simplicity and speed. The system
does not need to scan the memory for free blocks every time you insert an
object in the cache.

If you need a more versatile (but relatively slower) approach, you can enable
the "bitmap" mode. Another memory area will be created containing a map of all
of the used and free blocks of the cache. When you insert an item the bitmap is
scanned for contiguous free blocks.  Blocks must be contiguous, this could lead
to a bit of fragmentation but it is not as big a problem as with disk storage,
and you can always tune the block size to reduce fragmentation.

Persistent storage
******************

You can store cache data in a backing store file to implement persistence.  As
this is managed by ``mmap()`` it is almost transparent to the user.  You should
not rely on this for data safety (disk syncing is managed asynchronously); use
it only for performance purposes.

Network access
**************

All of your caches can be accessed over the network. A request plugin named
"cache" (modifier1 111) manages requests from external nodes. On a standard
monolithic build of uWSGI the cache plugin is always enabled.  The cache plugin
works in a fully non-blocking way, and it is greenthreads/coroutine friendly so
you can use technologies like gevent or Coro::AnyEvent with it safely.

UDP sync
********

This technique has been inspired by the STUD project, which uses something like
this for SSL session scaling (and coincidentally the same approach can be used
with uWSGI SSL/HTTPS routers).  Basically whenever you set/update/delete an
item from the cache, the operation is propagated to remote nodes via simple UDP
packets.  There are no built-in guarantees with UDP syncing so use it only for
very specific purposes, like :doc:`SSLScaling`.

--cache2 options
****************

This is the list of all of the options (and their aliases) of ``--cache2``.

name
^^^^

Set the name of the cache. Must be unique in an instance.

max-items || maxitems || items
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Set the maximum number of cache items.

blocksize
^^^^^^^^^

Set the size (in bytes) of a single block.

blocks
^^^^^^

Set the number of blocks in the cache. Useful only in bitmap mode, otherwise
the number of blocks is equal to the maximum number of items.

hash
^^^^

Set the hash algorithm used in the hash table. Currentl options are "djb33x"
(default) and "murmur2".

hashsize || hash_size
^^^^^^^^^^^^^^^^^^^^^

this is the size of the hash table in bytes. Generally 65536 (the default) is a
good value. Change it only if you know what you are doing or if you have a lot
of collisions in your cache.

keysize || key_size
^^^^^^^^^^^^^^^^^^^

Set the maximum size of a key, in bytes (default 2048)

store
^^^^^

Set the filename for the persistent storage. If it doesn't exist, the system
assumes an empty cache and the file will be created.

store_sync || storesync
^^^^^^^^^^^^^^^^^^^^^^^

Set the number of seconds after which msync() is called to flush memory cache
on disk when in persistent mode.  By default it is disabled leaving the
decision-making to the kernel.

store_delete || storedelete
^^^^^^^^^^^^^^^^^^^^^^^^^^^

uWSGI, by default, will not start if a cache file exists and the store file does not match the configured items/blocksize.
Setting this option will make uWSGI delete the existing file upon mismatch and create a new one.

node || nodes
^^^^^^^^^^^^^

A semicolon separated list of UDP servers which will receive UDP cache updates.

sync
^^^^

A semicolon separated list of uwsgi addresses which the cache subsystem will
connect to for getting a full dump of the cache. It can be used for initial
cache synchronization. The first node sending a valid dump will stop the
procedure.

udp || udp_servers || udp_server || udpserver
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A semicolon separated list of UDP addresses on which to bind the cache to wait for UDP updates.

bitmap
^^^^^^

Set to 1 to enable bitmap mode.

lastmod
^^^^^^^

Setting lastmod to 1 will update last_modified_at timestamp of each cache on
every cache item modification.  Enable it if you want to track this value or if
other features depend on it. This value will then be accessible via the stats
socket.

ignore_full
^^^^^^^^^^^

By default uWSGI will print warning message on every cache set operation if the cache is full. To disable this warning set this option. Available since 2.0.4

purge_lru
^^^^^^^^^

This option allows the caching framework to evict Least Recently Used (LRU)
item when you try to add new item to cache storage that is full. The ``expires``
argument described below will be ignored. An item is considered used when
it's accessed, added and updated by cache_get(), cache_set() and
cache_update(); whereas the existence check by cache_exists() is not.

Accessing the cache from your applications using the cache api
**************************************************************

You can access the various cache in your instance or on remote instances by
using the cache API.  Currently the following functions are exposed (each
language might name them a bit differently from the standard):

 * cache_get(key[,cache])
 * cache_set(key,value[,expires,cache])
 * cache_update(key,value[,expires,cache])
 * cache_exists(key[,cache])
 * cache_del(key[,cache])
 * cache_clear([cache])

If the language/platform calling the cache API differentiates between strings
and bytes (like Python 3 and Java) you have to assume that keys are strings and
values are bytes (or bytearray in the java way). Otherwise keys and values are
both strings in no specific encoding, as internally the cache values and keys
are simple binary blobs.

The ``expires`` argument (default to 0 for disabled) is the number of seconds
after the object is no more valid (and will be removed by the cache sweeper
when ``purge_lru`` is not set, see below)

The ``cache`` argument is the so called "magic identifier". Its syntax is
``cache[@node]``. 

To operate on the local cache "mycache" you set it as "mycache", while to
operate on "yourcache" on the uWSGI server at 192.168.173.22 port 4040 the
value will be ``yourcache@192.168.173.22:4040``.

An empty cache value means the default cache which is generally the first
initialized. The default value is empty.

All of the network operations are transparent, fully non-blocking, and
threads/greenthreads friendly.

The Cache sweeper thread
************************

When at least one cache is configured without ``purge_lru`` and the master
is enabled a thread named "the cache sweeper" is started.  Its main purpose
is deleting expired keys from the cache. So, if you want auto-expiring you
need to enable the master.


Web caching
***********

In its first incarnation the uWSGI caching framework was meant only for caching
of web pages. The old system has been rebuilt. It is now named
:doc:`WebCaching`. Enabling the old-style ``--cache`` option will create a
cache named "default".

Monitoring caches
*****************

The stats server exposes cache information. An ncurses based tool (https://pypi.python.org/pypi/uwsgicachetop) exists that uses that information for real-time monitoring.
