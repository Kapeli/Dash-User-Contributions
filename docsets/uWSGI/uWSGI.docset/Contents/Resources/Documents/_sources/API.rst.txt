The uWSGI api
=============

Language plugins should expose the following api. Each language has its conventions, limits and strength's point.

When porting the api to a specific language try to be friendly to the language style.

This is the "official" list of functions exposed by the uWSGI api, functions not appearing here are not standardized
so they could change their semanthics in future uWSGI relases.


The syntax proposed here is a pseudo-python, each language will expose each function with its specific style

When not_defined is used, it means the language-specific NULL representation (like None in python or undef in perl)

uwsgi.signal(signum)
********************

raise the specified uwsgi signal

uwsgi.register_rpc(name, func, argc=0)
**************************************

register the function "func" as an RPC one with the specified "name"

argc will force the accepted number of arguments

uwsgi.rpc(node, name, *args)
****************************

call the uWSGI RPC function "name" on server "node" with the supplied args (if any)

if node is not_defined a "local" RPC will be made

uwsgi.call(name, *args)
***********************

call the uWSGI RPC function "name" locally with the supplied args (if any)

uwsgi.cache_get(key[, cache])
*****************************

get "key" from the specified "cache". If "cache" is not_defined, the default local cache will be used.

To get an item from a remote cache use the cachename@addr:port syntax for the "cache" value

returns not_defined if the item is not found or an error has occurred

uwsgi.add_timer(signum, secs)
*****************************

register a timer raising "signum" every "secs"

uwsgi.add_rb_timer(signum, secs[, iterations])
**********************************************

register a redblack timer raising "signum" every "secs"

uwsgi.lock(num=0)
*****************

acquire the specified user lock

uwsgi.unlock(num=0)
*******************

release the specified user lock

uwsgi.masterpid()
*****************

return the current pid of the master process

uwsgi.alarm(alarm, msg)
***********************

raise the specified "alarm" with the message "msg"

uwsgi.suspend()
***************

suspend the current async core and give cpu to the next core in the schedule chain

uwsgi.async_sleep(secs)
***********************

suspend the current async core for the specified number of seconds

(requires uwsgi.suspend() or form of "yield" to be committed)

uwsgi.connection_fd()
*********************

returns the file descriptor of the connection opened with the client

uwsgi.async_connect(addr)
*************************

returns the file descriptor of a non-blocking connection to the specified "addr"

will raise an exception on error

uwsgi.wait_fd_read(fd[, timeout])
*********************************

(requires uwsgi.suspend() or form of "yield" to be committed)

will raise an exception on error

uwsgi.wait_fd_write(fd[, timeout])
**********************************

(requires uwsgi.suspend() or form of "yield" to be committed)

will raise an exception on error

uwsgi.ready_fd()
****************

after resume from suspend() returns the currently available file descriptor or -1 if a timeout was the cause of resume

uwsgi.send([fd,] data)
**********************

send the specified "data" to the file descriptor "fd".

If "fd" is not specified the output of uwsgi.connection_fd() will be used

The position of arguments is a bit strange, but allows easier integration with POSIX write()

uwsgi.recv([fd,] len)
*********************

receive at most "len" bytes from the specified "fd"

If "fd" is not specified the output of uwsgi.connection_fd() will be used

The position of arguments is a bit strange, but allows easier integration with POSIX read()

uwsgi.close(fd)
***************

close the specified file descriptor

uwsgi.setprocname(name)
***********************

set the name of the calling process

uwsgi.add_cron(signum, minute, hour, day, month, week)
******************************************************

register a cron raising the uwsgi signal "signum"


uwsgi.disconnect()
******************

disconnect the client without stopping the request handler


uwsgi.worker_id()
*****************

returns the current worker id (as integer).

0 means the calling process is not a worker

uwsgi.mule_id()
*****************

returns the current mule id (as integer).

0 means the calling process is not a mule

uwsgi.signal_registered(signum)
*******************************

check if "signum" is registered

returns boolean

uwsgi.opt
*********

This is a hash/dictionary of all the specified options for the instance (both registered and virtuals)

uwsgi.version
*************

the uWSGI version string

uwsgi.hostname
**************

the server hostname

uwsgi.register_signal(signum, kind, handler)
********************************************

register the uwsgi signal "signum" of the specified "kind" mapped to "handler"

raise an Exception on error

uwsgi.set_user_harakiri(sec)
****************************

set the user harakiri (for workers, mules and spoolers).

A value of 0, reset the timer
