uWSGI 2.0.4
===========

Changelog [20140422]

Bugfixes
--------

- fixed "mime" routing var (Steve Stagg)
- allow duplicate headers in http parsers
- faster on_demand Emperor management
- fixed UWSGI_ADDITIONAL_SOURCES build option
- merge duplicated headers when SPDY is enabled (Łukasz Mierzwa)
- fixed segfault for unnamed loggers
- --need-app works in lazy-apps mode
- fixed fatal hooks management


New features
------------

The experimental asyncio loop engine (CPython >= 3.4)
*****************************************************

asyncio (also known as 'tulip') is the new infrastructure for writing non-blocking/async/callback-based code with Python 3.

This (experimental) plugin allows you to use asyncio as the uWSGI loop engine.

Docs: https://uwsgi-docs.readthedocs.io/en/latest/asyncio.html

httprouter advanced timeout management
**************************************

The HTTP router learned 2 new specific timeouts:

* `--http-headers-timeout <n>`: defines the timeout while waiting for http headers
* `--http-connect-timeout <n>`: defines the timeout when connecting to backend instances

These should help sysadmins to improve security and availability.

Credits: Łukasz Mierzwa

allow disabling cache warnings in --cache2
******************************************

Author: Łukasz Mierzwa

The 'ignore_full' keyval option has been added to cache2. This will disable warnings when a cache is full.

purge LRU cache feature by Yu Zhao (getcwd)
*******************************************

This new mode allows you to configure a cache to automatically expire the least recently used (LRU) items to make space when it's running out.

Just add `purge_lru=1` into your cache2 directive.

support embedded config on FreeBSD
**********************************

You can now embed configuration files into the binary also on FreeBSD systems: 

https://uwsgi-docs.readthedocs.io/en/latest/Embed.html#step-2-embedding-the-config-file

RPC hook
********

Two new hooks have been added:

* 'rpc' -> call the specified RPC function (fails on error)
* 'rpcretry' -> call the specified RPC function (retries on error)

`setmodifier1` and `setmodifier2` routing actions
*************************************************

Having to load the 'uwsgi' routing plugin to simply set modifiers was really annoying.

These two new routing options allow you to dynamically set request modifiers.

`no_headers` option for static router
*************************************

keyval based static routing actions can now avoid rewriting response headers (useful for X-Sendfile), just add no_headers=1 to your keyval options.

Availability
------------

uWSGI 2.0.4 has been released on 20140422, you can download it from:

https://projects.unbit.it/downloads/uwsgi-2.0.4.tar.gz


