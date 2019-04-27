uWSGI Options
^^^^^^^^^^^^^

This is an automatically generated reference list of the uWSGI options.

It is the same output you can get via the ``--help`` option.

This page is probably the worst way to understand uWSGI for newbies. If you are still learning how the project
works, you should read the various quickstarts and tutorials.

Each option has the following attributes:

* argument: it is the struct option (used by getopt()/getopt_long()) has_arg element. Can be 'required_argument', 'no_argument' or 'optional_argument'
* shortcut: some option can be specified with the short form (a dash followed by a single letter)
* parser: this is how uWSGI parses the parameter. There are dozens of way, the most common are 'uwsgi_opt_set_str' when it takes a simple string, 'uwsgi_opt_set_int' when it takes a 32bit number, 'uwsgi_opt_add_string_list' when the parameter can be specified multiple times to build a list.
* help: the help message, the same you get from ``uwsgi --help``
* reference: a link to a documentation page that gives better understanding and context of an option

You can add more detailed infos to this page, editing https://github.com/unbit/uwsgi-docs/blob/master/optdefs.pl (please, double check it before sending a pull request)

uWSGI core
==========
socket
******
``argument``: required_argument

``shortcut``: -s

``parser``: uwsgi_opt_add_socket

``help``: bind to the specified UNIX/TCP socket using default protocol



uwsgi-socket
************
``argument``: required_argument

``shortcut``: -s

``parser``: uwsgi_opt_add_socket

``help``: bind to the specified UNIX/TCP socket using uwsgi protocol



suwsgi-socket
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_ssl_socket

``help``: bind to the specified UNIX/TCP socket using uwsgi protocol over SSL



ssl-socket
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_ssl_socket

``help``: bind to the specified UNIX/TCP socket using uwsgi protocol over SSL



http-socket
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_socket

``help``: bind to the specified UNIX/TCP socket using HTTP protocol



http-socket-modifier1
*********************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: force the specified modifier1 when using HTTP protocol



http-socket-modifier2
*********************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: force the specified modifier2 when using HTTP protocol



http11-socket
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_socket

``help``: bind to the specified UNIX/TCP socket using HTTP 1.1 (Keep-Alive) protocol



https-socket
************
``argument``: required_argument

``parser``: uwsgi_opt_add_ssl_socket

``help``: bind to the specified UNIX/TCP socket using HTTPS protocol



https-socket-modifier1
**********************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: force the specified modifier1 when using HTTPS protocol



https-socket-modifier2
**********************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: force the specified modifier2 when using HTTPS protocol



fastcgi-socket
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_socket

``help``: bind to the specified UNIX/TCP socket using FastCGI protocol



fastcgi-nph-socket
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_socket

``help``: bind to the specified UNIX/TCP socket using FastCGI protocol (nph mode)



fastcgi-modifier1
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: force the specified modifier1 when using FastCGI protocol



fastcgi-modifier2
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: force the specified modifier2 when using FastCGI protocol



scgi-socket
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_socket

``help``: bind to the specified UNIX/TCP socket using SCGI protocol



scgi-nph-socket
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_socket

``help``: bind to the specified UNIX/TCP socket using SCGI protocol (nph mode)



scgi-modifier1
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: force the specified modifier1 when using SCGI protocol



scgi-modifier2
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: force the specified modifier2 when using SCGI protocol



raw-socket
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_socket_no_defer

``help``: bind to the specified UNIX/TCP socket using RAW protocol



raw-modifier1
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: force the specified modifier1 when using RAW protocol



raw-modifier2
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: force the specified modifier2 when using RAW protocol



puwsgi-socket
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_socket

``help``: bind to the specified UNIX/TCP socket using persistent uwsgi protocol (puwsgi)



protocol
********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: force the specified protocol for default sockets



socket-protocol
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: force the specified protocol for default sockets



shared-socket
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_shared_socket

``help``: create a shared socket for advanced jailing or ipc



undeferred-shared-socket
************************
``argument``: required_argument

``parser``: uwsgi_opt_add_shared_socket

``help``: create a shared socket for advanced jailing or ipc (undeferred mode)



processes
*********
``argument``: required_argument

``shortcut``: -p

``parser``: uwsgi_opt_set_int

``help``: spawn the specified number of workers/processes



workers
*******
``argument``: required_argument

``shortcut``: -p

``parser``: uwsgi_opt_set_int

``help``: spawn the specified number of workers/processes



thunder-lock
************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: serialize accept() usage (if possible)

``reference``: :doc:`articles/SerializingAccept`



harakiri
********
``argument``: required_argument

``shortcut``: -t

``parser``: uwsgi_opt_set_int

``help``: set harakiri timeout



harakiri-verbose
****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: enable verbose mode for harakiri



harakiri-no-arh
***************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: do not enable harakiri during after-request-hook



no-harakiri-arh
***************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: do not enable harakiri during after-request-hook



no-harakiri-after-req-hook
**************************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: do not enable harakiri during after-request-hook



backtrace-depth
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set backtrace depth



mule-harakiri
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set harakiri timeout for mule tasks



xmlconfig
*********
``argument``: required_argument

``shortcut``: -x

``parser``: uwsgi_opt_load_xml

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load config from xml file



xml
***
``argument``: required_argument

``shortcut``: -x

``parser``: uwsgi_opt_load_xml

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load config from xml file



config
******
``argument``: required_argument

``parser``: uwsgi_opt_load_config

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load configuration using the pluggable system



fallback-config
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_IMMEDIATE

``help``: re-exec uwsgi with the specified config when exit code is 1



strict
******
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_IMMEDIATE

``help``: enable strict mode (placeholder cannot be used)



skip-zero
*********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: skip check of file descriptor 0



skip-atexit
***********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: skip atexit hooks (ignored by the master)


skip-atexit
***********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: skip atexit teardown (ignored by the master)



set
***
``argument``: required_argument

``shortcut``: -S

``parser``: uwsgi_opt_set_placeholder

``flags``: UWSGI_OPT_IMMEDIATE

``help``: set a placeholder or an option



set-placeholder
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_placeholder

``flags``: UWSGI_OPT_IMMEDIATE

``help``: set a placeholder



set-ph
******
``argument``: required_argument

``parser``: uwsgi_opt_set_placeholder

``flags``: UWSGI_OPT_IMMEDIATE

``help``: set a placeholder



get
***
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_NO_INITIAL

``help``: print the specified option value and exit



declare-option
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_custom_option

``flags``: UWSGI_OPT_IMMEDIATE

``help``: declare a new uWSGI custom option

``reference``: :doc:`CustomOptions`



declare-option2
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_custom_option

``help``: declare a new uWSGI custom option (non-immediate)



resolve
*******
``argument``: required_argument

``parser``: uwsgi_opt_resolve

``flags``: UWSGI_OPT_IMMEDIATE

``help``: place the result of a dns query in the specified placeholder, sytax: placeholder=name (immediate option)



for
***
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) for cycle



for-glob
********
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) for cycle (expand glob)



for-times
*********
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) for cycle (expand the specified num to a list starting from 1)



for-readline
************
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) for cycle (expand the specified file to a list of lines)



endfor
******
``argument``: optional_argument

``parser``: uwsgi_opt_noop

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) end for cycle



end-for
*******
``argument``: optional_argument

``parser``: uwsgi_opt_noop

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) end for cycle



if-opt
******
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) check for option



if-not-opt
**********
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) check for option



if-env
******
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) check for environment variable



if-not-env
**********
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) check for environment variable



ifenv
*****
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) check for environment variable



if-reload
*********
``argument``: no_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) check for reload



if-not-reload
*************
``argument``: no_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) check for reload



if-hostname
***********
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) check for hostname



if-not-hostname
***************
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) check for hostname



if-hostname-match
***********
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) try to match hostname against a regular expression



if-not-hostname-match
***************
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) try to match hostname against a regular expression



if-exists
*********
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) check for file/directory existance



if-not-exists
*************
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) check for file/directory existance



ifexists
********
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) check for file/directory existance



if-plugin
*********
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) check for plugin



if-not-plugin
*************
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) check for plugin



ifplugin
********
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) check for plugin



if-file
*******
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) check for file existance



if-not-file
***********
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) check for file existance



if-dir
******
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) check for directory existance



if-not-dir
**********
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) check for directory existance



ifdir
*****
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) check for directory existance



if-directory
************
``argument``: required_argument

``parser``: uwsgi_opt_logic

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) check for directory existance



endif
*****
``argument``: optional_argument

``parser``: uwsgi_opt_noop

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) end if



end-if
******
``argument``: optional_argument

``parser``: uwsgi_opt_noop

``flags``: UWSGI_OPT_IMMEDIATE

``help``: (opt logic) end if



blacklist
*********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_IMMEDIATE

``help``: set options blacklist context



end-blacklist
*************
``argument``: no_argument

``parser``: uwsgi_opt_set_null

``flags``: UWSGI_OPT_IMMEDIATE

``help``: clear options blacklist context



whitelist
*********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_IMMEDIATE

``help``: set options whitelist context



end-whitelist
*************
``argument``: no_argument

``parser``: uwsgi_opt_set_null

``flags``: UWSGI_OPT_IMMEDIATE

``help``: clear options whitelist context



ignore-sigpipe
**************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: do not report (annoying) SIGPIPE



ignore-write-errors
*******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: do not report (annoying) write()/writev() errors



write-errors-tolerance
**********************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: set the maximum number of allowed write errors (default: no tolerance)



write-errors-exception-only
***************************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: only raise an exception on write errors giving control to the app itself



disable-write-exception
***********************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: disable exception generation on write()/writev()



inherit
*******
``argument``: required_argument

``parser``: uwsgi_opt_load

``help``: use the specified file as config template



include
*******
``argument``: required_argument

``parser``: uwsgi_opt_load

``flags``: UWSGI_OPT_IMMEDIATE

``help``: include the specified file as immediate configuration



inject-before
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_IMMEDIATE

``help``: inject a text file before the config file (advanced templating)



inject-after
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_IMMEDIATE

``help``: inject a text file after the config file (advanced templating)



daemonize
*********
``argument``: required_argument

``shortcut``: -d

``parser``: uwsgi_opt_set_str

``help``: daemonize uWSGI



daemonize2
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: daemonize uWSGI after app loading



stop
****
``argument``: required_argument

``parser``: uwsgi_opt_pidfile_signal

``flags``: UWSGI_OPT_IMMEDIATE

``help``: stop an instance



reload
******
``argument``: required_argument

``parser``: uwsgi_opt_pidfile_signal

``flags``: UWSGI_OPT_IMMEDIATE

``help``: reload an instance



pause
*****
``argument``: required_argument

``parser``: uwsgi_opt_pidfile_signal

``flags``: UWSGI_OPT_IMMEDIATE

``help``: pause an instance



suspend
*******
``argument``: required_argument

``parser``: uwsgi_opt_pidfile_signal

``flags``: UWSGI_OPT_IMMEDIATE

``help``: suspend an instance



resume
******
``argument``: required_argument

``parser``: uwsgi_opt_pidfile_signal

``flags``: UWSGI_OPT_IMMEDIATE

``help``: resume an instance



connect-and-read
****************
``argument``: required_argument

``parser``: uwsgi_opt_connect_and_read

``flags``: UWSGI_OPT_IMMEDIATE

``help``: connect to a socket and wait for data from it



extract
*******
``argument``: required_argument

``parser``: uwsgi_opt_extract

``flags``: UWSGI_OPT_IMMEDIATE

``help``: fetch/dump any supported address to stdout



listen
******
``argument``: required_argument

``shortcut``: -l

``parser``: uwsgi_opt_set_int

``help``: set the socket listen queue size



max-vars
********
``argument``: required_argument

``shortcut``: -v

``parser``: uwsgi_opt_max_vars

``help``: set the amount of internal iovec/vars structures



max-apps
********
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the maximum number of per-worker applications



buffer-size
***********
``argument``: required_argument

``shortcut``: -b

``parser``: uwsgi_opt_set_64bit

``help``: set internal buffer size



Set the max size of a request (request-body excluded), this generally maps to the size of request headers. By default it is 4k. If you receive a bigger request (for example with big cookies or query string) you may need to increase it. It is a security measure too, so adapt to your app needs instead of maxing it out.

memory-report
*************
``argument``: no_argument

``shortcut``: -m

``parser``: uwsgi_opt_true

``help``: enable memory report



profiler
********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: enable the specified profiler



cgi-mode
********
``argument``: no_argument

``shortcut``: -c

``parser``: uwsgi_opt_true

``help``: force CGI-mode for plugins supporting it



abstract-socket
***************
``argument``: no_argument

``shortcut``: -a

``parser``: uwsgi_opt_true

``help``: force UNIX socket in abstract mode (Linux only)



chmod-socket
************
``argument``: optional_argument

``shortcut``: -C

``parser``: uwsgi_opt_chmod_socket

``help``: chmod-socket



chmod
*****
``argument``: optional_argument

``shortcut``: -C

``parser``: uwsgi_opt_chmod_socket

``help``: chmod-socket



chown-socket
************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: chown unix sockets



umask
*****
``argument``: required_argument

``parser``: uwsgi_opt_set_umask

``flags``: UWSGI_OPT_IMMEDIATE

``help``: set umask



freebind
********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: put socket in freebind mode



set the IP_FREEBIND flag to every socket created by uWSGI. This kind of socket can bind to non-existent ip addresses. Its main purpose is for high availability (this is Linux only)

map-socket
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: map sockets to specific workers



enable-threads
**************
``argument``: no_argument

``shortcut``: -T

``parser``: uwsgi_opt_true

``help``: enable threads



no-threads-wait
***************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: do not wait for threads cancellation on quit/reload



auto-procname
*************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: automatically set processes name to something meaningful



procname-prefix
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_PROCNAME

``help``: add a prefix to the process names



procname-prefix-spaced
**********************
``argument``: required_argument

``parser``: uwsgi_opt_set_str_spaced

``flags``: UWSGI_OPT_PROCNAME

``help``: add a spaced prefix to the process names



procname-append
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_PROCNAME

``help``: append a string to process names



procname
********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_PROCNAME

``help``: set process names



procname-master
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_PROCNAME

``help``: set master process name



single-interpreter
******************
``argument``: no_argument

``shortcut``: -i

``parser``: uwsgi_opt_true

``help``: do not use multiple interpreters (where available)



need-app
********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: exit if no app can be loaded



master
******
``argument``: no_argument

``shortcut``: -M

``parser``: uwsgi_opt_true

``help``: enable master process



honour-stdin
************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: do not remap stdin to /dev/null



emperor
*******
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the Emperor

``reference``: :doc:`Emperor`



The Emperor is a special uWSGI instance aimed at governing other uWSGI instances (named: vassals). By default it is configured to monitor a directory containing valid uWSGI config files, whenever a file is created a new instance is spawned, when the file is touched the instance is reloaded, when the file is removed the instance is destroyed. It can be extended to support more paradigms

emperor-proxy-socket
********************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: force the vassal to became an Emperor proxy



emperor-wrapper
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set a binary wrapper for vassals



emperor-nofollow
****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: do not follow symlinks when checking for mtime



emperor-procname
****************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set the Emperor process name



emperor-freq
************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the Emperor scan frequency (default 3 seconds)



emperor-required-heartbeat
**************************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the Emperor tolerance about heartbeats



emperor-curse-tolerance
***********************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the Emperor tolerance about cursed vassals



emperor-pidfile
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: write the Emperor pid in the specified file



emperor-tyrant
**************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: put the Emperor in Tyrant mode



emperor-tyrant-nofollow
***********************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: do not follow symlinks when checking for uid/gid in Tyrant mode



emperor-tyrant-initgroups
*************************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: add additional groups set via initgroups() in Tyrant mode



emperor-stats
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the Emperor stats server



emperor-stats-server
********************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the Emperor stats server



early-emperor
*************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: spawn the emperor as soon as possibile



emperor-broodlord
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: run the emperor in BroodLord mode



emperor-throttle
****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set throttling level (in milliseconds) for bad behaving vassals (default 1000)



emperor-max-throttle
********************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set max throttling level (in milliseconds) for bad behaving vassals (default 3 minutes)



emperor-magic-exec
******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: prefix vassals config files with exec:// if they have the executable bit



emperor-on-demand-extension
***************************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: search for text file (vassal name + extension) containing the on demand socket name



emperor-on-demand-ext
*********************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: search for text file (vassal name + extension) containing the on demand socket name



emperor-on-demand-directory
***************************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: enable on demand mode binding to the unix socket in the specified directory named like the vassal + .socket



emperor-on-demand-dir
*********************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: enable on demand mode binding to the unix socket in the specified directory named like the vassal + .socket



emperor-on-demand-exec
**********************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: use the output of the specified command as on demand socket name (the vassal name is passed as the only argument)



emperor-extra-extension
***********************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: allows the specified extension in the Emperor (vassal will be called with --config)



emperor-extra-ext
*****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: allows the specified extension in the Emperor (vassal will be called with --config)



emperor-no-blacklist
********************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: disable Emperor blacklisting subsystem



emperor-use-clone
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_unshare

``help``: use clone() instead of fork() passing the specified unshare() flags



emperor-use-fork-server
***********************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: connect to the specified fork server instead of using plain fork() for new vassals



vassal-fork-base
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: use plain fork() for the specified vassal (instead of a fork-server)



emperor-subreaper
*****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: force the Emperor to be a sub-reaper (if supported)



emperor-cap
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_emperor_cap

``help``: set vassals capability



vassals-cap
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_emperor_cap

``help``: set vassals capability



vassal-cap
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_emperor_cap

``help``: set vassals capability



emperor-collect-attribute
*************************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: collect the specified vassal attribute from imperial monitors



emperor-collect-attr
********************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: collect the specified vassal attribute from imperial monitors



emperor-fork-server-attr
************************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set the vassal's attribute to get when checking for fork-server



emperor-wrapper-attr
********************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set the vassal's attribute to get when checking for fork-wrapper



emperor-chdir-attr
******************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set the vassal's attribute to get when checking for chdir



imperial-monitor-list
*********************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: list enabled imperial monitors



imperial-monitors-list
**********************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: list enabled imperial monitors



vassals-inherit
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add config templates to vassals config (uses --inherit)



vassals-include
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: include config templates to vassals config (uses --include instead of --inherit)



vassals-inherit-before
**********************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add config templates to vassals config (uses --inherit, parses before the vassal file)



vassals-include-before
**********************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: include config templates to vassals config (uses --include instead of --inherit, parses before the vassal file)



vassals-start-hook
******************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the specified command before each vassal starts



vassals-stop-hook
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the specified command after vassal's death



vassal-sos
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: ask emperor for reinforcement when overloaded



vassal-sos-backlog
******************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: ask emperor for sos if backlog queue has more items than the value specified



vassals-set
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: automatically set the specified option (via --set) for every vassal



vassal-set
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: automatically set the specified option (via --set) for every vassal



heartbeat
*********
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: announce healthiness to the emperor



zeus
****
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: enable Zeus mode



reload-mercy
************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the maximum time (in seconds) we wait for workers and other processes to die during reload/shutdown



worker-reload-mercy
*******************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the maximum time (in seconds) a worker can take to reload/shutdown (default is 60)



mule-reload-mercy
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the maximum time (in seconds) a mule can take to reload/shutdown (default is 60)



exit-on-reload
**************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: force exit even if a reload is requested



die-on-term
***********
``argument``: no_argument

``parser``: uwsgi_opt_deprecated

``help``: exit instead of brutal reload on SIGTERM (no more needed)



force-gateway
*************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: force the spawn of the first registered gateway without a master



help
****
``argument``: no_argument

``shortcut``: -h

``parser``: uwsgi_help

``flags``: UWSGI_OPT_IMMEDIATE

``help``: show this help



usage
*****
``argument``: no_argument

``shortcut``: -h

``parser``: uwsgi_help

``flags``: UWSGI_OPT_IMMEDIATE

``help``: show this help



print-sym
*********
``argument``: required_argument

``parser``: uwsgi_print_sym

``flags``: UWSGI_OPT_IMMEDIATE

``help``: print content of the specified binary symbol



print-symbol
************
``argument``: required_argument

``parser``: uwsgi_print_sym

``flags``: UWSGI_OPT_IMMEDIATE

``help``: print content of the specified binary symbol



reaper
******
``argument``: no_argument

``shortcut``: -r

``parser``: uwsgi_opt_true

``help``: call waitpid(-1,...) after each request to get rid of zombies



max-requests
************
``argument``: required_argument

``shortcut``: -R

``parser``: uwsgi_opt_set_64bit

``help``: reload workers after the specified amount of managed requests



max-requests-delta
******************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: add (worker_id * delta) to the max_requests value of each worker



min-worker-lifetime
*******************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: number of seconds worker must run before being reloaded (default is 60)



max-worker-lifetime
*******************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: reload workers after the specified amount of seconds (default is disabled)



socket-timeout
**************
``argument``: required_argument

``shortcut``: -z

``parser``: uwsgi_opt_set_int

``help``: set internal sockets timeout



no-fd-passing
*************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: disable file descriptor passing



locks
*****
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: create the specified number of shared locks



lock-engine
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set the lock engine



ftok
****
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set the ipcsem key via ftok() for avoiding duplicates



persistent-ipcsem
*****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: do not remove ipcsem's on shutdown



sharedarea
**********
``argument``: required_argument

``shortcut``: -A

``parser``: uwsgi_opt_add_string_list

``help``: create a raw shared memory area of specified pages (note: it supports keyval too)

``reference``: :doc:`SharedArea`



safe-fd
*******
``argument``: required_argument

``parser``: uwsgi_opt_safe_fd

``help``: do not close the specified file descriptor



fd-safe
*******
``argument``: required_argument

``parser``: uwsgi_opt_safe_fd

``help``: do not close the specified file descriptor



cache
*****
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: create a shared cache containing given elements



cache-blocksize
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: set cache blocksize



cache-store
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_MASTER

``help``: enable persistent cache to disk



cache-store-sync
****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set frequency of sync for persistent cache



cache-no-expire
***************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: disable auto sweep of expired items



cache-expire-freq
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the frequency of cache sweeper scans (default 3 seconds)



cache-report-freed-items
************************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: constantly report the cache item freed by the sweeper (use only for debug)



cache-udp-server
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: bind the cache udp server (used only for set/update/delete) to the specified socket



cache-udp-node
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: send cache update/deletion to the specified cache udp server



cache-sync
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: copy the whole content of another uWSGI cache server on server startup



cache-use-last-modified
***********************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: update last_modified_at timestamp on every cache item modification (default is disabled)



add-cache-item
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add an item in the cache



load-file-in-cache
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: load a static file in the cache



load-file-in-cache-gzip
***********************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: load a static file in the cache with gzip compression



cache2
******
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: create a new generation shared cache (keyval syntax)



queue
*****
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: enable shared queue



queue-blocksize
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set queue blocksize



queue-store
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_MASTER

``help``: enable persistent queue to disk



queue-store-sync
****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set frequency of sync for persistent queue



spooler
*******
``argument``: required_argument

``shortcut``: -Q

``parser``: uwsgi_opt_add_spooler

``flags``: UWSGI_OPT_MASTER

``help``: run a spooler on the specified directory



spooler-external
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_spooler

``flags``: UWSGI_OPT_MASTER

``help``: map spoolers requests to a spooler directory managed by an external instance



spooler-ordered
***************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: try to order the execution of spooler tasks



spooler-chdir
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: chdir() to specified directory before each spooler task



spooler-processes
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_IMMEDIATE

``help``: set the number of processes for spoolers



spooler-quiet
*************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: do not be verbose with spooler tasks



spooler-max-tasks
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the maximum number of tasks to run before recycling a spooler



spooler-harakiri
****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set harakiri timeout for spooler tasks



spooler-frequency
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set spooler frequency, default 30 seconds



spooler-freq
************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set spooler frequency, default 30 seconds



mule
****
``argument``: optional_argument

``parser``: uwsgi_opt_add_mule

``flags``: UWSGI_OPT_MASTER

``help``: add a mule



mules
*****
``argument``: required_argument

``parser``: uwsgi_opt_add_mules

``flags``: UWSGI_OPT_MASTER

``help``: add the specified number of mules



farm
****
``argument``: required_argument

``parser``: uwsgi_opt_add_farm

``flags``: UWSGI_OPT_MASTER

``help``: add a mule farm (syntax: <farm_name>:<mule_id>[,<mule_id> ...])



mule-msg-size
*************
``argument``: optional_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_MASTER

``help``: set mule message buffer size



signal
******
``argument``: required_argument

``parser``: uwsgi_opt_signal

``flags``: UWSGI_OPT_IMMEDIATE

``help``: send a uwsgi signal to a server



signal-bufsize
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set buffer size for signal queue



signals-bufsize
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set buffer size for signal queue



signal-timer
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: add a timer (syntax: <signal> <seconds>)



timer
*****
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: add a timer (syntax: <signal> <seconds>)



signal-rbtimer
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: add a redblack timer (syntax: <signal> <seconds>)



rbtimer
*******
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: add a redblack timer (syntax: <signal> <seconds>)



rpc-max
*******
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: maximum number of rpc slots (default: 64)



disable-logging
***************
``argument``: no_argument

``shortcut``: -L

``parser``: uwsgi_opt_false

``help``: disable request logging



flock
*****
``argument``: required_argument

``parser``: uwsgi_opt_flock

``flags``: UWSGI_OPT_IMMEDIATE

``help``: lock the specified file before starting, exit if locked



flock-wait
**********
``argument``: required_argument

``parser``: uwsgi_opt_flock_wait

``flags``: UWSGI_OPT_IMMEDIATE

``help``: lock the specified file before starting, wait if locked



flock2
******
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_IMMEDIATE

``help``: lock the specified file after logging/daemon setup, exit if locked



flock-wait2
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_IMMEDIATE

``help``: lock the specified file after logging/daemon setup, wait if locked



pidfile
*******
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: create pidfile (before privileges drop)



pidfile2
********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: create pidfile (after privileges drop)



safe-pidfile
************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: create safe pidfile (before privileges drop)



safe-pidfile2
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: create safe pidfile (after privileges drop)



chroot
******
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: chroot() to the specified directory



pivot-root
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: pivot_root() to the specified directories (new_root and put_old must be separated with a space)



pivot_root
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: pivot_root() to the specified directories (new_root and put_old must be separated with a space)



uid
***
``argument``: required_argument

``parser``: uwsgi_opt_set_uid

``help``: setuid to the specified user/uid



gid
***
``argument``: required_argument

``parser``: uwsgi_opt_set_gid

``help``: setgid to the specified group/gid



add-gid
*******
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add the specified group id to the process credentials



immediate-uid
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_immediate_uid

``flags``: UWSGI_OPT_IMMEDIATE

``help``: setuid to the specified user/uid IMMEDIATELY



immediate-gid
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_immediate_gid

``flags``: UWSGI_OPT_IMMEDIATE

``help``: setgid to the specified group/gid IMMEDIATELY



no-initgroups
*************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: disable additional groups set via initgroups()



cap
***
``argument``: required_argument

``parser``: uwsgi_opt_set_cap

``help``: set process capability



unshare
*******
``argument``: required_argument

``parser``: uwsgi_opt_set_unshare

``help``: unshare() part of the processes and put it in a new namespace



unshare2
********
``argument``: required_argument

``parser``: uwsgi_opt_set_unshare

``help``: unshare() part of the processes and put it in a new namespace after rootfs change



setns-socket
************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_MASTER

``help``: expose a unix socket returning namespace fds from /proc/self/ns



setns-socket-skip
*****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: skip the specified entry when sending setns file descriptors



setns-skip
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: skip the specified entry when sending setns file descriptors



setns
*****
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: join a namespace created by an external uWSGI instance



setns-preopen
*************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: open /proc/self/ns as soon as possible and cache fds



fork-socket
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: suspend the execution after early initialization and fork() at every unix socket connection



fork-server
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: suspend the execution after early initialization and fork() at every unix socket connection



jailed
******
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: mark the instance as jailed (force the execution of post_jail hooks)



jail
****
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: put the instance in a FreeBSD jail



jail-ip4
********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add an ipv4 address to the FreeBSD jail



jail-ip6
********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add an ipv6 address to the FreeBSD jail



jidfile
*******
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: save the jid of a FreeBSD jail in the specified file



jid-file
********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: save the jid of a FreeBSD jail in the specified file



jail2
*****
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add an option to the FreeBSD jail



libjail
*******
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add an option to the FreeBSD jail



jail-attach
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: attach to the FreeBSD jail



refork
******
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: fork() again after privileges drop. Useful for jailing systems



re-fork
*******
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: fork() again after privileges drop. Useful for jailing systems



refork-as-root
**************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: fork() again before privileges drop. Useful for jailing systems



re-fork-as-root
***************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: fork() again before privileges drop. Useful for jailing systems



refork-post-jail
****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: fork() again after jailing. Useful for jailing systems



re-fork-post-jail
*****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: fork() again after jailing. Useful for jailing systems



hook-asap
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook as soon as possible



hook-pre-jail
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook before jailing



hook-post-jail
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook after jailing



hook-in-jail
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook in jail after initialization



hook-as-root
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook before privileges drop



hook-as-user
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook after privileges drop



hook-as-user-atexit
*******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook before app exit and reload



hook-pre-app
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook before app loading



hook-post-app
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook after app loading



hook-post-fork
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook after each fork



hook-accepting
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook after each worker enter the accepting phase



hook-accepting1
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook after the first worker enters the accepting phase



hook-accepting-once
*******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook after each worker enter the accepting phase (once per-instance)



hook-accepting1-once
********************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook after the first worker enters the accepting phase (once per instance)



hook-master-start
*****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook when the Master starts



hook-touch
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook when the specified file is touched (syntax: <file> <action>)



hook-emperor-start
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook when the Emperor starts



hook-emperor-stop
*****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook when the Emperor send a stop message



hook-emperor-reload
*******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook when the Emperor send a reload message



hook-emperor-lost
*****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook when the Emperor connection is lost



hook-as-vassal
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook before exec()ing the vassal



hook-as-emperor
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook in the emperor after the vassal has been started



hook-as-on-demand-vassal
************************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook whenever a vassal enters on-demand mode



hook-as-on-config-vassal
************************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook whenever the emperor detects a config change for an on-demand vassal



hook-as-emperor-before-vassal
*****************************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook before the new vassal is spawned



hook-as-vassal-before-drop
**************************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook into vassal, before dropping its privileges



hook-as-emperor-setns
*********************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook in the emperor entering vassal namespace



hook-as-mule
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook in each mule



hook-as-gateway
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified hook in each gateway



after-request-hook
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified function/symbol after each request



after-request-call
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified function/symbol after each request



exec-asap
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified command as soon as possible



exec-pre-jail
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified command before jailing



exec-post-jail
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified command after jailing



exec-in-jail
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified command in jail after initialization



exec-as-root
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified command before privileges drop



exec-as-user
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified command after privileges drop



exec-as-user-atexit
*******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified command before app exit and reload



exec-pre-app
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified command before app loading



exec-post-app
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified command after app loading



exec-as-vassal
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified command before exec()ing the vassal



exec-as-emperor
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the specified command in the emperor after the vassal has been started



mount-asap
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: mount filesystem as soon as possible



mount-pre-jail
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: mount filesystem before jailing



mount-post-jail
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: mount filesystem after jailing



mount-in-jail
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: mount filesystem in jail after initialization



mount-as-root
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: mount filesystem before privileges drop



mount-as-vassal
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: mount filesystem before exec()ing the vassal



mount-as-emperor
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: mount filesystem in the emperor after the vassal has been started



umount-asap
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: unmount filesystem as soon as possible



umount-pre-jail
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: unmount filesystem before jailing



umount-post-jail
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: unmount filesystem after jailing



umount-in-jail
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: unmount filesystem in jail after initialization



umount-as-root
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: unmount filesystem before privileges drop



umount-as-vassal
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: unmount filesystem before exec()ing the vassal



umount-as-emperor
*****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: unmount filesystem in the emperor after the vassal has been started



wait-for-interface
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: wait for the specified network interface to come up before running root hooks



wait-for-interface-timeout
**************************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the timeout for wait-for-interface



wait-interface
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: wait for the specified network interface to come up before running root hooks



wait-interface-timeout
**********************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the timeout for wait-for-interface



wait-for-iface
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: wait for the specified network interface to come up before running root hooks



wait-for-iface-timeout
**********************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the timeout for wait-for-interface



wait-iface
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: wait for the specified network interface to come up before running root hooks



wait-iface-timeout
******************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the timeout for wait-for-interface



wait-for-fs
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: wait for the specified filesystem item to appear before running root hooks



wait-for-file
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: wait for the specified file to appear before running root hooks



wait-for-dir
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: wait for the specified directory to appear before running root hooks



wait-for-mountpoint
*******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: wait for the specified mountpoint to appear before running root hooks



wait-for-fs-timeout
*******************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the timeout for wait-for-fs/file/dir



call-asap
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: call the specified function as soon as possible



call-pre-jail
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: call the specified function before jailing



call-post-jail
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: call the specified function after jailing



call-in-jail
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: call the specified function in jail after initialization



call-as-root
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: call the specified function before privileges drop



call-as-user
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: call the specified function after privileges drop



call-as-user-atexit
*******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: call the specified function before app exit and reload



call-pre-app
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: call the specified function before app loading



call-post-app
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: call the specified function after app loading



call-as-vassal
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: call the specified function() before exec()ing the vassal



call-as-vassal1
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: call the specified function before exec()ing the vassal



call-as-vassal3
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: call the specified function(char *, uid_t, gid_t) before exec()ing the vassal



call-as-emperor
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: call the specified function() in the emperor after the vassal has been started



call-as-emperor1
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: call the specified function in the emperor after the vassal has been started



call-as-emperor2
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: call the specified function(char *, pid_t) in the emperor after the vassal has been started



call-as-emperor4
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: call the specified function(char *, pid_t, uid_t, gid_t) in the emperor after the vassal has been started



ini
***
``argument``: required_argument

``parser``: uwsgi_opt_load_ini

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load config from ini file



yaml
****
``argument``: required_argument

``shortcut``: -y

``parser``: uwsgi_opt_load_yml

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load config from yaml file



yml
***
``argument``: required_argument

``shortcut``: -y

``parser``: uwsgi_opt_load_yml

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load config from yaml file



json
****
``argument``: required_argument

``shortcut``: -j

``parser``: uwsgi_opt_load_json

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load config from json file



js
**
``argument``: required_argument

``shortcut``: -j

``parser``: uwsgi_opt_load_json

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load config from json file



weight
******
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: weight of the instance (used by clustering/lb/subscriptions)



auto-weight
***********
``argument``: required_argument

``parser``: uwsgi_opt_true

``help``: set weight of the instance (used by clustering/lb/subscriptions) automatically



no-server
*********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: force no-server mode



command-mode
************
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_IMMEDIATE

``help``: force command mode



no-defer-accept
***************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: disable deferred-accept on sockets



tcp-nodelay
***********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: enable TCP NODELAY on each request



so-keepalive
************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: enable TCP KEEPALIVEs



so-send-timeout
***************
``argument``: no_argument

``parser``: uwsgi_opt_set_int

``help``: set SO_SNDTIMEO



socket-send-timeout
*******************
``argument``: no_argument

``parser``: uwsgi_opt_set_int

``help``: set SO_SNDTIMEO



so-write-timeout
****************
``argument``: no_argument

``parser``: uwsgi_opt_set_int

``help``: set SO_SNDTIMEO



socket-write-timeout
********************
``argument``: no_argument

``parser``: uwsgi_opt_set_int

``help``: set SO_SNDTIMEO



socket-sndbuf
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: set SO_SNDBUF



socket-rcvbuf
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: set SO_RCVBUF



limit-as
********
``argument``: required_argument

``parser``: uwsgi_opt_set_megabytes

``help``: limit processes address space/vsz



limit-nproc
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: limit the number of spawnable processes



reload-on-as
************
``argument``: required_argument

``parser``: uwsgi_opt_set_megabytes

``flags``: UWSGI_OPT_MEMORY

``help``: reload if address space is higher than specified megabytes



reload-on-rss
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_megabytes

``flags``: UWSGI_OPT_MEMORY

``help``: reload if rss memory is higher than specified megabytes



evil-reload-on-as
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_megabytes

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_MEMORY

``help``: force the master to reload a worker if its address space is higher than specified megabytes



evil-reload-on-rss
******************
``argument``: required_argument

``parser``: uwsgi_opt_set_megabytes

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_MEMORY

``help``: force the master to reload a worker if its rss memory is higher than specified megabytes



reload-on-fd
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: reload if the specified file descriptor is ready



brutal-reload-on-fd
*******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: brutal reload if the specified file descriptor is ready



ksm
***
``argument``: optional_argument

``parser``: uwsgi_opt_set_int

``help``: enable Linux KSM



pcre-jit
********
``argument``: no_argument

``parser``: uwsgi_opt_pcre_jit

``flags``: UWSGI_OPT_IMMEDIATE

``help``: enable pcre jit (if available)



never-swap
**********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: lock all memory pages avoiding swapping



touch-reload
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: reload uWSGI if the specified file is modified/touched



touch-workers-reload
********************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: trigger reload of (only) workers if the specified file is modified/touched



touch-chain-reload
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: trigger chain reload if the specified file is modified/touched



touch-logrotate
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_LOG_MASTER

``help``: trigger logrotation if the specified file is modified/touched



touch-logreopen
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_LOG_MASTER

``help``: trigger log reopen if the specified file is modified/touched



touch-exec
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: run command when the specified file is modified/touched (syntax: file command)



touch-signal
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: signal when the specified file is modified/touched (syntax: file signal)



fs-reload
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: graceful reload when the specified filesystem object is modified



fs-brutal-reload
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: brutal reload when the specified filesystem object is modified



fs-signal
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: raise a uwsgi signal when the specified filesystem object is modified (syntax: file signal)



check-mountpoint
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: destroy the instance if a filesystem is no more reachable (useful for reliable Fuse management)



mountpoint-check
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: destroy the instance if a filesystem is no more reachable (useful for reliable Fuse management)



check-mount
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: destroy the instance if a filesystem is no more reachable (useful for reliable Fuse management)



mount-check
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: destroy the instance if a filesystem is no more reachable (useful for reliable Fuse management)



propagate-touch
***************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: over-engineering option for system with flaky signal management



limit-post
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: limit request body



no-orphans
**********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: automatically kill workers if master dies (can be dangerous for availability)



prio
****
``argument``: required_argument

``parser``: uwsgi_opt_set_rawint

``help``: set processes/threads priority



cpu-affinity
************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set cpu affinity



post-buffering
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: enable post buffering



post-buffering-bufsize
**********************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: set buffer size for read() in post buffering mode



body-read-warning
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: set the amount of allowed memory allocation (in megabytes) for request body before starting printing a warning



upload-progress
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: enable creation of .json files in the specified directory during a file upload



no-default-app
**************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: do not fallback to default app



manage-script-name
******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: automatically rewrite SCRIPT_NAME and PATH_INFO



ignore-script-name
******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: ignore SCRIPT_NAME



catch-exceptions
****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: report exception as http output (discouraged, use only for testing)



reload-on-exception
*******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: reload a worker when an exception is raised



reload-on-exception-type
************************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: reload a worker when a specific exception type is raised



reload-on-exception-value
*************************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: reload a worker when a specific exception value is raised



reload-on-exception-repr
************************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: reload a worker when a specific exception type+value (language-specific) is raised



exception-handler
*****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: add an exception handler



enable-metrics
**************
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_MASTER

``help``: enable metrics subsystem



metric
******
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_METRICS|UWSGI_OPT_MASTER

``help``: add a custom metric



metric-threshold
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_METRICS|UWSGI_OPT_MASTER

``help``: add a metric threshold/alarm



metric-alarm
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_METRICS|UWSGI_OPT_MASTER

``help``: add a metric threshold/alarm



alarm-metric
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_METRICS|UWSGI_OPT_MASTER

``help``: add a metric threshold/alarm



metrics-dir
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_METRICS|UWSGI_OPT_MASTER

``help``: export metrics as text files to the specified directory



metrics-dir-restore
*******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_METRICS|UWSGI_OPT_MASTER

``help``: restore last value taken from the metrics dir



metric-dir
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_METRICS|UWSGI_OPT_MASTER

``help``: export metrics as text files to the specified directory



metric-dir-restore
******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_METRICS|UWSGI_OPT_MASTER

``help``: restore last value taken from the metrics dir



metrics-no-cores
****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_METRICS|UWSGI_OPT_MASTER

``help``: disable generation of cores-related metrics

``reference``: :doc:`Metrics`



Do not expose metrics of async cores.

udp
***
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_MASTER

``help``: run the udp server on the specified address



stats
*****
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_MASTER

``help``: enable the stats server on the specified address



stats-server
************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_MASTER

``help``: enable the stats server on the specified address



stats-http
**********
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_MASTER

``help``: prefix stats server json output with http headers



stats-minified
**************
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_MASTER

``help``: minify statistics json output



stats-min
*********
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_MASTER

``help``: minify statistics json output



stats-push
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER|UWSGI_OPT_METRICS

``help``: push the stats json to the specified destination



stats-pusher-default-freq
*************************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_MASTER

``help``: set the default frequency of stats pushers



stats-pushers-default-freq
**************************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_MASTER

``help``: set the default frequency of stats pushers



stats-no-cores
**************
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_MASTER

``help``: disable generation of cores-related stats

``reference``: :doc:`Metrics`



Do not expose the information about cores in the stats server.

stats-no-metrics
****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_MASTER

``help``: do not include metrics in stats output

``reference``: :doc:`Metrics`



Do not expose the metrics at all in the stats server.

multicast
*********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_MASTER

``help``: subscribe to specified multicast group



multicast-ttl
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set multicast ttl



multicast-loop
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set multicast loop (default 1)



master-fifo
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: enable the master fifo



notify-socket
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_MASTER

``help``: enable the notification socket



subscription-notify-socket
**************************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_MASTER

``help``: set the notification socket for subscriptions



subscription-mountpoints
************************
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_MASTER

``help``: enable mountpoints support for subscription system



subscription-mountpoint
***********************
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_MASTER

``help``: enable mountpoints support for subscription system



legion
******
``argument``: required_argument

``parser``: uwsgi_opt_legion

``flags``: UWSGI_OPT_MASTER

``help``: became a member of a legion



legion-mcast
************
``argument``: required_argument

``parser``: uwsgi_opt_legion_mcast

``flags``: UWSGI_OPT_MASTER

``help``: became a member of a legion (shortcut for multicast)



legion-node
***********
``argument``: required_argument

``parser``: uwsgi_opt_legion_node

``flags``: UWSGI_OPT_MASTER

``help``: add a node to a legion



legion-freq
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_MASTER

``help``: set the frequency of legion packets



legion-tolerance
****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_MASTER

``help``: set the tolerance of legion subsystem



legion-death-on-lord-error
**************************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_MASTER

``help``: declare itself as a dead node for the specified amount of seconds if one of the lord hooks fails



legion-skew-tolerance
*********************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_MASTER

``help``: set the clock skew tolerance of legion subsystem (default 30 seconds)



legion-lord
***********
``argument``: required_argument

``parser``: uwsgi_opt_legion_hook

``flags``: UWSGI_OPT_MASTER

``help``: action to call on Lord election



legion-unlord
*************
``argument``: required_argument

``parser``: uwsgi_opt_legion_hook

``flags``: UWSGI_OPT_MASTER

``help``: action to call on Lord dismiss



legion-setup
************
``argument``: required_argument

``parser``: uwsgi_opt_legion_hook

``flags``: UWSGI_OPT_MASTER

``help``: action to call on legion setup



legion-death
************
``argument``: required_argument

``parser``: uwsgi_opt_legion_hook

``flags``: UWSGI_OPT_MASTER

``help``: action to call on legion death (shutdown of the instance)



legion-join
***********
``argument``: required_argument

``parser``: uwsgi_opt_legion_hook

``flags``: UWSGI_OPT_MASTER

``help``: action to call on legion join (first time quorum is reached)



legion-node-joined
******************
``argument``: required_argument

``parser``: uwsgi_opt_legion_hook

``flags``: UWSGI_OPT_MASTER

``help``: action to call on new node joining legion



legion-node-left
****************
``argument``: required_argument

``parser``: uwsgi_opt_legion_hook

``flags``: UWSGI_OPT_MASTER

``help``: action to call node leaving legion



legion-quorum
*************
``argument``: required_argument

``parser``: uwsgi_opt_legion_quorum

``flags``: UWSGI_OPT_MASTER

``help``: set the quorum of a legion



legion-scroll
*************
``argument``: required_argument

``parser``: uwsgi_opt_legion_scroll

``flags``: UWSGI_OPT_MASTER

``help``: set the scroll of a legion



legion-scroll-max-size
**********************
``argument``: required_argument

``parser``: uwsgi_opt_set_16bit

``help``: set max size of legion scroll buffer



legion-scroll-list-max-size
***************************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: set max size of legion scroll list buffer



subscriptions-sign-check
************************
``argument``: required_argument

``parser``: uwsgi_opt_scd

``flags``: UWSGI_OPT_MASTER

``help``: set digest algorithm and certificate directory for secured subscription system



subscriptions-sign-check-tolerance
**********************************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_MASTER

``help``: set the maximum tolerance (in seconds) of clock skew for secured subscription system



subscriptions-sign-skip-uid
***************************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: skip signature check for the specified uid when using unix sockets credentials



subscriptions-credentials-check
*******************************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: add a directory to search for subscriptions key credentials



subscriptions-use-credentials
*****************************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: enable management of SCM_CREDENTIALS in subscriptions UNIX sockets



subscription-algo
*****************
``argument``: required_argument

``parser``: uwsgi_opt_ssa

``help``: set load balancing algorithm for the subscription system



subscription-dotsplit
*********************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: try to fallback to the next part (dot based) in subscription key



subscribe-to
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: subscribe to the specified subscription server



st
**
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: subscribe to the specified subscription server



subscribe
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: subscribe to the specified subscription server



subscribe2
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: subscribe to the specified subscription server using advanced keyval syntax



subscribe-freq
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: send subscription announce at the specified interval



subscription-tolerance
**********************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set tolerance for subscription servers



unsubscribe-on-graceful-reload
******************************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: force unsubscribe request even during graceful reload



start-unsubscribed
******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: configure subscriptions but do not send them (useful with master fifo)



subscribe-with-modifier1
************************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_MASTER

``help``: force the specififed modifier1 when subscribing



snmp
****
``argument``: optional_argument

``parser``: uwsgi_opt_snmp

``help``: enable the embedded snmp server



snmp-community
**************
``argument``: required_argument

``parser``: uwsgi_opt_snmp_community

``help``: set the snmp community string



ssl-verbose
***********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: be verbose about SSL errors



ssl-sessions-use-cache
**********************
``argument``: optional_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_MASTER

``help``: use uWSGI cache for ssl sessions storage



ssl-session-use-cache
*********************
``argument``: optional_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_MASTER

``help``: use uWSGI cache for ssl sessions storage



ssl-sessions-timeout
********************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set SSL sessions timeout (default: 300 seconds)



ssl-session-timeout
*******************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set SSL sessions timeout (default: 300 seconds)



sni
***
``argument``: required_argument

``parser``: uwsgi_opt_sni

``help``: add an SNI-governed SSL context



sni-dir
*******
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: check for cert/key/client_ca file in the specified directory and create a sni/ssl context on demand



sni-dir-ciphers
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set ssl ciphers for sni-dir option



ssl-enable3
***********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: enable SSLv3 (insecure)



ssl-option
**********
``argument``: no_argument

``parser``: uwsgi_opt_add_string_list

``help``: set a raw ssl option (numeric value)



sni-regexp
**********
``argument``: required_argument

``parser``: uwsgi_opt_sni

``help``: add an SNI-governed SSL context (the key is a regexp)



ssl-tmp-dir
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: store ssl-related temp files in the specified directory



check-interval
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_MASTER

``help``: set the interval (in seconds) of master checks



forkbomb-delay
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_MASTER

``help``: sleep for the specified number of seconds when a forkbomb is detected



binary-path
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: force binary path



privileged-binary-patch
***********************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: patch the uwsgi binary with a new command (before privileges drop)



unprivileged-binary-patch
*************************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: patch the uwsgi binary with a new command (after privileges drop)



privileged-binary-patch-arg
***************************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: patch the uwsgi binary with a new command and arguments (before privileges drop)



unprivileged-binary-patch-arg
*****************************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: patch the uwsgi binary with a new command and arguments (after privileges drop)



async
*****
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: enable async mode with specified cores



disable-async-warn-on-queue-full
********************************
``argument``: no_argument

``parser``: uwsgi_opt_false

``help``: Disable printing 'async queue is full' warning messages.



max-fd
******
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set maximum number of file descriptors (requires root privileges)



logto
*****
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set logfile/udp address



logto2
******
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: log to specified file or udp address after privileges drop



log-format
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set advanced format for request logging



logformat
*********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set advanced format for request logging



logformat-strftime
******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: apply strftime to logformat output



log-format-strftime
*******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: apply strftime to logformat output



logfile-chown
*************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: chown logfiles



logfile-chmod
*************
``argument``: required_argument

``parser``: uwsgi_opt_logfile_chmod

``help``: chmod logfiles



log-syslog
**********
``argument``: optional_argument

``parser``: uwsgi_opt_set_logger

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_LOG_MASTER

``help``: log to syslog



log-socket
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_logger

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_LOG_MASTER

``help``: send logs to the specified socket



req-logger
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_req_logger

``flags``: UWSGI_OPT_REQ_LOG_MASTER

``help``: set/append a request logger



logger-req
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_req_logger

``flags``: UWSGI_OPT_REQ_LOG_MASTER

``help``: set/append a request logger



logger
******
``argument``: required_argument

``parser``: uwsgi_opt_set_logger

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_LOG_MASTER

``help``: set/append a logger



logger-list
***********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: list enabled loggers



loggers-list
************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: list enabled loggers



threaded-logger
***************
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_LOG_MASTER

``help``: offload log writing to a thread



log-encoder
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_LOG_MASTER

``help``: add an item in the log encoder chain



log-req-encoder
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_LOG_MASTER

``help``: add an item in the log req encoder chain



log-drain
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_regexp_list

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_LOG_MASTER

``help``: drain (do not show) log lines matching the specified regexp



log-filter
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_regexp_list

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_LOG_MASTER

``help``: show only log lines matching the specified regexp



log-route
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_regexp_custom_list

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_LOG_MASTER

``help``: log to the specified named logger if regexp applied on logline matches



log-req-route
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_regexp_custom_list

``flags``: UWSGI_OPT_REQ_LOG_MASTER

``help``: log requests to the specified named logger if regexp applied on logline matches



use-abort
*********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: call abort() on segfault/fpe, could be useful for generating a core dump



alarm
*****
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: create a new alarm, syntax: <alarm> <plugin:args>



alarm-cheap
***********
``argument``: required_argument

``parser``: uwsgi_opt_true

``help``: use main alarm thread rather than create dedicated threads for curl-based alarms



alarm-freq
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: tune the anti-loop alam system (default 3 seconds)



alarm-fd
********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: raise the specified alarm when an fd is read for read (by default it reads 1 byte, set 8 for eventfd)



alarm-segfault
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: raise the specified alarm when the segmentation fault handler is executed



segfault-alarm
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: raise the specified alarm when the segmentation fault handler is executed



alarm-backlog
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: raise the specified alarm when the socket backlog queue is full



backlog-alarm
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: raise the specified alarm when the socket backlog queue is full



lq-alarm
********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: raise the specified alarm when the socket backlog queue is full



alarm-lq
********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: raise the specified alarm when the socket backlog queue is full



alarm-listen-queue
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: raise the specified alarm when the socket backlog queue is full



listen-queue-alarm
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: raise the specified alarm when the socket backlog queue is full



log-alarm
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_LOG_MASTER

``help``: raise the specified alarm when a log line matches the specified regexp, syntax: <alarm>[,alarm...] <regexp>



alarm-log
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_LOG_MASTER

``help``: raise the specified alarm when a log line matches the specified regexp, syntax: <alarm>[,alarm...] <regexp>



not-log-alarm
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list_custom

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_LOG_MASTER

``help``: skip the specified alarm when a log line matches the specified regexp, syntax: <alarm>[,alarm...] <regexp>



not-alarm-log
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list_custom

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_LOG_MASTER

``help``: skip the specified alarm when a log line matches the specified regexp, syntax: <alarm>[,alarm...] <regexp>



alarm-list
**********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: list enabled alarms



alarms-list
***********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: list enabled alarms



alarm-msg-size
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: set the max size of an alarm message (default 8192)



log-master
**********
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_MASTER|UWSGI_OPT_LOG_MASTER

``help``: delegate logging to master process



log-master-bufsize
******************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: set the buffer size for the master logger. bigger log messages will be truncated



log-master-stream
*****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: create the master logpipe as SOCK_STREAM



log-master-req-stream
*********************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: create the master requests logpipe as SOCK_STREAM



log-reopen
**********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: reopen log after reload



log-truncate
************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: truncate log on startup



log-maxsize
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``flags``: UWSGI_OPT_MASTER|UWSGI_OPT_LOG_MASTER

``help``: set maximum logfile size



log-backupname
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set logfile name after rotation



logdate
*******
``argument``: optional_argument

``parser``: uwsgi_opt_log_date

``help``: prefix logs with date or a strftime string



log-date
********
``argument``: optional_argument

``parser``: uwsgi_opt_log_date

``help``: prefix logs with date or a strftime string



log-prefix
**********
``argument``: optional_argument

``parser``: uwsgi_opt_log_date

``help``: prefix logs with a string



log-zero
********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: log responses without body



log-slow
********
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: log requests slower than the specified number of milliseconds



log-4xx
*******
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: log requests with a 4xx response



log-5xx
*******
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: log requests with a 5xx response



log-big
*******
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: log requestes bigger than the specified size



log-sendfile
************
``argument``: required_argument

``parser``: uwsgi_opt_true

``help``: log sendfile requests



log-ioerror
***********
``argument``: required_argument

``parser``: uwsgi_opt_true

``help``: log requests with io errors



log-micros
**********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: report response time in microseconds instead of milliseconds



log-x-forwarded-for
*******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: use the ip from X-Forwarded-For header instead of REMOTE_ADDR



master-as-root
**************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: leave master process running as root



drop-after-init
***************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: run privileges drop after plugin initialization



drop-after-apps
***************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: run privileges drop after apps loading



force-cwd
*********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: force the initial working directory to the specified value



binsh
*****
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: override /bin/sh (used by exec hooks, it always fallback to /bin/sh)



chdir
*****
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: chdir to specified directory before apps loading



chdir2
******
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: chdir to specified directory after apps loading



lazy
****
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: set lazy mode (load apps in workers instead of master)



lazy-apps
*********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: load apps in each worker instead of the master



cheap
*****
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_MASTER

``help``: set cheap mode (spawn workers only after the first request)



cheaper
*******
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_CHEAPER

``help``: set cheaper mode (adaptive process spawning)



cheaper-initial
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_CHEAPER

``help``: set the initial number of processes to spawn in cheaper mode



cheaper-algo
************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_MASTER

``help``: choose to algorithm used for adaptive process spawning



cheaper-step
************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_CHEAPER

``help``: number of additional processes to spawn at each overload



cheaper-overload
****************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_CHEAPER

``help``: increase workers after specified overload


cheaper-idle
****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_CHEAPER

``help``: decrease workers after specified idle (algo: spare2) (default: 10)


cheaper-algo-list
*****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: list enabled cheapers algorithms



cheaper-algos-list
******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: list enabled cheapers algorithms



cheaper-list
************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: list enabled cheapers algorithms



cheaper-rss-limit-soft
**********************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_CHEAPER

``help``: don't spawn new workers if total resident memory usage of all workers is higher than this limit



cheaper-rss-limit-hard
**********************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_CHEAPER

``help``: if total workers resident memory usage is higher try to stop workers



idle
****
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_MASTER

``help``: set idle mode (put uWSGI in cheap mode after inactivity)



die-on-idle
***********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: shutdown uWSGI when idle



mount
*****
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: load application under mountpoint



worker-mount
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: load application under mountpoint in the specified worker or after workers spawn



threads
*******
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_THREADS

``help``: run each worker in prethreaded mode with the specified number of threads



thread-stacksize
****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_THREADS

``help``: set threads stacksize



threads-stacksize
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_THREADS

``help``: set threads stacksize



thread-stack-size
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_THREADS

``help``: set threads stacksize



threads-stack-size
******************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_THREADS

``help``: set threads stacksize



vhost
*****
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: enable virtualhosting mode (based on SERVER_NAME variable)



vhost-host
**********
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_VHOST

``help``: enable virtualhosting mode (based on HTTP_HOST variable)



route
*****
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a route



route-host
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a route based on Host header



route-uri
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a route based on REQUEST_URI



route-qs
********
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a route based on QUERY_STRING



route-remote-addr
*****************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a route based on REMOTE_ADDR



route-user-agent
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a route based on HTTP_USER_AGENT



route-remote-user
*****************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a route based on REMOTE_USER



route-referer
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a route based on HTTP_REFERER



route-label
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a routing label (for use with goto)



route-if
********
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a route based on condition



route-if-not
************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a route based on condition (negate version)



route-run
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: always run the specified route action



final-route
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a final route



final-route-status
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a final route for the specified status



final-route-host
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a final route based on Host header



final-route-uri
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a final route based on REQUEST_URI



final-route-qs
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a final route based on QUERY_STRING



final-route-remote-addr
***********************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a final route based on REMOTE_ADDR



final-route-user-agent
**********************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a final route based on HTTP_USER_AGENT



final-route-remote-user
***********************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a final route based on REMOTE_USER



final-route-referer
*******************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a final route based on HTTP_REFERER



final-route-label
*****************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a final routing label (for use with goto)



final-route-if
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a final route based on condition



final-route-if-not
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a final route based on condition (negate version)



final-route-run
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: always run the specified final route action



error-route
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add an error route



error-route-status
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add an error route for the specified status



error-route-host
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add an error route based on Host header



error-route-uri
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add an error route based on REQUEST_URI



error-route-qs
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add an error route based on QUERY_STRING



error-route-remote-addr
***********************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add an error route based on REMOTE_ADDR



error-route-user-agent
**********************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add an error route based on HTTP_USER_AGENT



error-route-remote-user
***********************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add an error route based on REMOTE_USER



error-route-referer
*******************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add an error route based on HTTP_REFERER



error-route-label
*****************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add an error routing label (for use with goto)



error-route-if
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add an error route based on condition



error-route-if-not
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add an error route based on condition (negate version)



error-route-run
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: always run the specified error route action



response-route
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a response route



response-route-status
*********************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a response route for the specified status



response-route-host
*******************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a response route based on Host header



response-route-uri
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a response route based on REQUEST_URI



response-route-qs
*****************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a response route based on QUERY_STRING



response-route-remote-addr
**************************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a response route based on REMOTE_ADDR



response-route-user-agent
*************************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a response route based on HTTP_USER_AGENT



response-route-remote-user
**************************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a response route based on REMOTE_USER



response-route-referer
**********************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a response route based on HTTP_REFERER



response-route-label
********************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a response routing label (for use with goto)



response-route-if
*****************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a response route based on condition



response-route-if-not
*********************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: add a response route based on condition (negate version)



response-route-run
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_route

``help``: always run the specified response route action



router-list
***********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: list enabled routers



routers-list
************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: list enabled routers



error-page-403
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add an error page (html) for managed 403 response



error-page-404
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add an error page (html) for managed 404 response



error-page-500
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add an error page (html) for managed 500 response



websockets-ping-freq
********************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the frequency (in seconds) of websockets automatic ping packets



websocket-ping-freq
*******************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the frequency (in seconds) of websockets automatic ping packets



websockets-pong-tolerance
*************************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the tolerance (in seconds) of websockets ping/pong subsystem



websocket-pong-tolerance
************************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the tolerance (in seconds) of websockets ping/pong subsystem



websockets-max-size
*******************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: set the max allowed size of websocket messages (in Kbytes, default 1024)



websocket-max-size
******************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: set the max allowed size of websocket messages (in Kbytes, default 1024)



chunked-input-limit
*******************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: set the max size of a chunked input part (default 1MB, in bytes)



chunked-input-timeout
*********************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set default timeout for chunked input



clock
*****
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set a clock source



clock-list
**********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: list enabled clocks



clocks-list
***********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: list enabled clocks



add-header
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: automatically add HTTP headers to response



rem-header
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: automatically remove specified HTTP header from the response



del-header
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: automatically remove specified HTTP header from the response



collect-header
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: store the specified response header in a request var (syntax: header var)



response-header-collect
***********************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: store the specified response header in a request var (syntax: header var)



pull-header
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: store the specified response header in a request var and remove it from the response (syntax: header var)



check-static
************
``argument``: required_argument

``parser``: uwsgi_opt_check_static

``flags``: UWSGI_OPT_MIME

``help``: check for static files in the specified directory



check-static-docroot
********************
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_MIME

``help``: check for static files in the requested DOCUMENT_ROOT



static-check
************
``argument``: required_argument

``parser``: uwsgi_opt_check_static

``flags``: UWSGI_OPT_MIME

``help``: check for static files in the specified directory



static-map
**********
``argument``: required_argument

``parser``: uwsgi_opt_static_map

``flags``: UWSGI_OPT_MIME

``help``: map mountpoint to static directory (or file)



static-map2
***********
``argument``: required_argument

``parser``: uwsgi_opt_static_map

``flags``: UWSGI_OPT_MIME

``help``: like static-map but completely appending the requested resource to the docroot



static-skip-ext
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: skip specified extension from staticfile checks



static-index
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: search for specified file if a directory is requested



static-safe
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: skip security checks if the file is under the specified path



static-cache-paths
******************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_MIME|UWSGI_OPT_MASTER

``help``: put resolved paths in the uWSGI cache for the specified amount of seconds



static-cache-paths-name
***********************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_MIME|UWSGI_OPT_MASTER

``help``: use the specified cache for static paths



mimefile
********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: set mime types file path (default /etc/apache2/mime.types)



mime-file
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: set mime types file path (default /etc/apache2/mime.types)



mimefile
********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: set mime types file path (default /etc/mime.types)



mime-file
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: set mime types file path (default /etc/mime.types)



static-expires-type
*******************
``argument``: required_argument

``parser``: uwsgi_opt_add_dyn_dict

``flags``: UWSGI_OPT_MIME

``help``: set the Expires header based on content type



static-expires-type-mtime
*************************
``argument``: required_argument

``parser``: uwsgi_opt_add_dyn_dict

``flags``: UWSGI_OPT_MIME

``help``: set the Expires header based on content type and file mtime



static-expires
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_regexp_dyn_dict

``flags``: UWSGI_OPT_MIME

``help``: set the Expires header based on filename regexp



static-expires-mtime
********************
``argument``: required_argument

``parser``: uwsgi_opt_add_regexp_dyn_dict

``flags``: UWSGI_OPT_MIME

``help``: set the Expires header based on filename regexp and file mtime



static-expires-uri
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_regexp_dyn_dict

``flags``: UWSGI_OPT_MIME

``help``: set the Expires header based on REQUEST_URI regexp



static-expires-uri-mtime
************************
``argument``: required_argument

``parser``: uwsgi_opt_add_regexp_dyn_dict

``flags``: UWSGI_OPT_MIME

``help``: set the Expires header based on REQUEST_URI regexp and file mtime



static-expires-path-info
************************
``argument``: required_argument

``parser``: uwsgi_opt_add_regexp_dyn_dict

``flags``: UWSGI_OPT_MIME

``help``: set the Expires header based on PATH_INFO regexp



static-expires-path-info-mtime
******************************
``argument``: required_argument

``parser``: uwsgi_opt_add_regexp_dyn_dict

``flags``: UWSGI_OPT_MIME

``help``: set the Expires header based on PATH_INFO regexp and file mtime



static-gzip
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_regexp_list

``flags``: UWSGI_OPT_MIME

``help``: if the supplied regexp matches the static file translation it will search for a gzip version



static-gzip-all
***************
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_MIME

``help``: check for a gzip version of all requested static files



static-gzip-dir
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: check for a gzip version of all requested static files in the specified dir/prefix



static-gzip-prefix
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: check for a gzip version of all requested static files in the specified dir/prefix



static-gzip-ext
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: check for a gzip version of all requested static files with the specified ext/suffix



static-gzip-suffix
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: check for a gzip version of all requested static files with the specified ext/suffix



honour-range
************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: enable support for the HTTP Range header



offload-threads
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the number of offload threads to spawn (per-worker, default 0)



offload-thread
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the number of offload threads to spawn (per-worker, default 0)



file-serve-mode
***************
``argument``: required_argument

``parser``: uwsgi_opt_fileserve_mode

``flags``: UWSGI_OPT_MIME

``help``: set static file serving mode



fileserve-mode
**************
``argument``: required_argument

``parser``: uwsgi_opt_fileserve_mode

``flags``: UWSGI_OPT_MIME

``help``: set static file serving mode



disable-sendfile
****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: disable sendfile() and rely on boring read()/write()



check-cache
***********
``argument``: optional_argument

``parser``: uwsgi_opt_set_str

``help``: check for response data in the specified cache (empty for default cache)



close-on-exec
*************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: set close-on-exec on connection sockets (could be required for spawning processes in requests)



close-on-exec2
**************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: set close-on-exec on server sockets (could be required for spawning processes in requests)



mode
****
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set uWSGI custom mode



env
***
``argument``: required_argument

``parser``: uwsgi_opt_set_env

``help``: set environment variable



ienv
****
``argument``: required_argument

``parser``: uwsgi_opt_set_env

``flags``: UWSGI_OPT_IMMEDIATE

``help``: set environment variable (IMMEDIATE version)



envdir
******
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: load a daemontools compatible envdir



early-envdir
************
``argument``: required_argument

``parser``: uwsgi_opt_envdir

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load a daemontools compatible envdir ASAP



unenv
*****
``argument``: required_argument

``parser``: uwsgi_opt_unset_env

``help``: unset environment variable



vacuum
******
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: try to remove all of the generated file/sockets



file-write
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: write the specified content to the specified file (syntax: file=value) before privileges drop



cgroup
******
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: put the processes in the specified cgroup



cgroup-opt
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: set value in specified cgroup option



cgroup-dir-mode
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set permission for cgroup directory (default is 700)



namespace
*********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run in a new namespace under the specified rootfs



namespace-keep-mount
********************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: keep the specified mountpoint in your namespace



ns
**
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run in a new namespace under the specified rootfs



namespace-net
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: add network namespace



ns-net
******
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: add network namespace



enable-proxy-protocol
*********************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: enable PROXY1 protocol support (only for http parsers)



reuse-port
**********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: enable REUSE_PORT flag on socket (BSD only)



tcp-fast-open
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: enable TCP_FASTOPEN flag on TCP sockets with the specified qlen value



tcp-fastopen
************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: enable TCP_FASTOPEN flag on TCP sockets with the specified qlen value



tcp-fast-open-client
********************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: use sendto(..., MSG_FASTOPEN, ...) instead of connect() if supported



tcp-fastopen-client
*******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: use sendto(..., MSG_FASTOPEN, ...) instead of connect() if supported



zerg
****
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: attach to a zerg server



zerg-fallback
*************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: fallback to normal sockets if the zerg server is not available



zerg-server
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_MASTER

``help``: enable the zerg server on the specified UNIX socket



cron
****
``argument``: required_argument

``parser``: uwsgi_opt_add_cron

``flags``: UWSGI_OPT_MASTER

``help``: add a cron task



cron2
*****
``argument``: required_argument

``parser``: uwsgi_opt_add_cron2

``flags``: UWSGI_OPT_MASTER

``help``: add a cron task (key=val syntax)



unique-cron
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_unique_cron

``flags``: UWSGI_OPT_MASTER

``help``: add a unique cron task



cron-harakiri
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the maximum time (in seconds) we wait for cron command to complete



legion-cron
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_legion_cron

``flags``: UWSGI_OPT_MASTER

``help``: add a cron task runnable only when the instance is a lord of the specified legion



cron-legion
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_legion_cron

``flags``: UWSGI_OPT_MASTER

``help``: add a cron task runnable only when the instance is a lord of the specified legion



unique-legion-cron
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_unique_legion_cron

``flags``: UWSGI_OPT_MASTER

``help``: add a unique cron task runnable only when the instance is a lord of the specified legion



unique-cron-legion
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_unique_legion_cron

``flags``: UWSGI_OPT_MASTER

``help``: add a unique cron task runnable only when the instance is a lord of the specified legion



loop
****
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: select the uWSGI loop engine



loop-list
*********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: list enabled loop engines



loops-list
**********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: list enabled loop engines



worker-exec
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the specified command as worker



worker-exec2
************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the specified command as worker (after post_fork hook)



attach-daemon
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_daemon

``flags``: UWSGI_OPT_MASTER

``help``: attach a command/daemon to the master process (the command has to not go in background)



attach-control-daemon
*********************
``argument``: required_argument

``parser``: uwsgi_opt_add_daemon

``flags``: UWSGI_OPT_MASTER

``help``: attach a command/daemon to the master process (the command has to not go in background), when the daemon dies, the master dies too



smart-attach-daemon
*******************
``argument``: required_argument

``parser``: uwsgi_opt_add_daemon

``flags``: UWSGI_OPT_MASTER

``help``: attach a command/daemon to the master process managed by a pidfile (the command has to daemonize)



smart-attach-daemon2
********************
``argument``: required_argument

``parser``: uwsgi_opt_add_daemon

``flags``: UWSGI_OPT_MASTER

``help``: attach a command/daemon to the master process managed by a pidfile (the command has to NOT daemonize)



legion-attach-daemon
********************
``argument``: required_argument

``parser``: uwsgi_opt_add_daemon

``flags``: UWSGI_OPT_MASTER

``help``: same as --attach-daemon but daemon runs only on legion lord node



legion-smart-attach-daemon
**************************
``argument``: required_argument

``parser``: uwsgi_opt_add_daemon

``flags``: UWSGI_OPT_MASTER

``help``: same as --smart-attach-daemon but daemon runs only on legion lord node



legion-smart-attach-daemon2
***************************
``argument``: required_argument

``parser``: uwsgi_opt_add_daemon

``flags``: UWSGI_OPT_MASTER

``help``: same as --smart-attach-daemon2 but daemon runs only on legion lord node



daemons-honour-stdin
********************
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_MASTER

``help``: do not change the stdin of external daemons to /dev/null



attach-daemon2
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_daemon2

``flags``: UWSGI_OPT_MASTER

``help``: attach-daemon keyval variant (supports smart modes too)



plugins
*******
``argument``: required_argument

``parser``: uwsgi_opt_load_plugin

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load uWSGI plugins



plugin
******
``argument``: required_argument

``parser``: uwsgi_opt_load_plugin

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load uWSGI plugins



need-plugins
************
``argument``: required_argument

``parser``: uwsgi_opt_load_plugin

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load uWSGI plugins (exit on error)



need-plugin
***********
``argument``: required_argument

``parser``: uwsgi_opt_load_plugin

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load uWSGI plugins (exit on error)



plugins-dir
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_IMMEDIATE

``help``: add a directory to uWSGI plugin search path



plugin-dir
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_IMMEDIATE

``help``: add a directory to uWSGI plugin search path



plugins-list
************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: list enabled plugins



plugin-list
***********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: list enabled plugins



autoload
********
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_IMMEDIATE

``help``: try to automatically load plugins when unknown options are found



dlopen
******
``argument``: required_argument

``parser``: uwsgi_opt_load_dl

``flags``: UWSGI_OPT_IMMEDIATE

``help``: blindly load a shared library



allowed-modifiers
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: comma separated list of allowed modifiers



remap-modifier
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: remap request modifier from one id to another



dump-options
************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: dump the full list of available options



show-config
***********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: show the current config reformatted as ini



binary-append-data
******************
``argument``: required_argument

``parser``: uwsgi_opt_binary_append_data

``flags``: UWSGI_OPT_IMMEDIATE

``help``: return the content of a resource to stdout for appending to a uwsgi binary (for data:// usage)



print
*****
``argument``: required_argument

``parser``: uwsgi_opt_print

``help``: simple print



iprint
******
``argument``: required_argument

``parser``: uwsgi_opt_print

``flags``: UWSGI_OPT_IMMEDIATE

``help``: simple print (immediate version)



exit
****
``argument``: optional_argument

``parser``: uwsgi_opt_exit

``flags``: UWSGI_OPT_IMMEDIATE

``help``: force exit() of the instance



cflags
******
``argument``: no_argument

``parser``: uwsgi_opt_cflags

``flags``: UWSGI_OPT_IMMEDIATE

``help``: report uWSGI CFLAGS (useful for building external plugins)



dot-h
*****
``argument``: no_argument

``parser``: uwsgi_opt_dot_h

``flags``: UWSGI_OPT_IMMEDIATE

``help``: dump the uwsgi.h used for building the core  (useful for building external plugins)



config-py
*********
``argument``: no_argument

``parser``: uwsgi_opt_config_py

``flags``: UWSGI_OPT_IMMEDIATE

``help``: dump the uwsgiconfig.py used for building the core  (useful for building external plugins)



build-plugin
************
``argument``: required_argument

``parser``: uwsgi_opt_build_plugin

``flags``: UWSGI_OPT_IMMEDIATE

``help``: build a uWSGI plugin for the current binary



version
*******
``argument``: no_argument

``parser``: uwsgi_opt_print

``help``: print uWSGI version




plugin: airbrake
================

plugin: alarm_curl
==================

plugin: alarm_speech
====================

plugin: alarm_xmpp
==================

plugin: asyncio
===============
asyncio
*******
``argument``: required_argument

``parser``: uwsgi_opt_setup_asyncio

``flags``: UWSGI_OPT_THREADS

``help``: a shortcut enabling asyncio loop engine with the specified number of async cores and optimal parameters




plugin: cache
=============

plugin: carbon
==============
carbon
******
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: push statistics to the specified carbon server



carbon-timeout
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set carbon connection timeout in seconds (default 3)



carbon-freq
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set carbon push frequency in seconds (default 60)



carbon-id
*********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set carbon id



carbon-no-workers
*****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: disable generation of single worker metrics



carbon-max-retry
****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set maximum number of retries in case of connection errors (default 1)



carbon-retry-delay
******************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set connection retry delay in seconds (default 7)



carbon-root
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set carbon metrics root node (default 'uwsgi')



carbon-hostname-dots
********************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set char to use as a replacement for dots in hostname (dots are not replaced by default)



carbon-name-resolve
*******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: allow using hostname as carbon server address (default disabled)



carbon-resolve-names
********************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: allow using hostname as carbon server address (default disabled)



carbon-idle-avg
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: average values source during idle period (no requests), can be "last", "zero", "none" (default is last)



carbon-use-metrics
******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: don't compute all statistics, use metrics subsystem data instead (warning! key names will be different)




plugin: cgi
===========
cgi
***
``argument``: required_argument

``parser``: uwsgi_opt_add_cgi

``help``: add a cgi mountpoint/directory/script



cgi-map-helper
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_cgi_maphelper

``help``: add a cgi map-helper



cgi-helper
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_cgi_maphelper

``help``: add a cgi map-helper



cgi-from-docroot
****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: blindly enable cgi in DOCUMENT_ROOT



cgi-buffer-size
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: set cgi buffer size



cgi-timeout
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set cgi script timeout



cgi-index
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add a cgi index file



cgi-allowed-ext
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: cgi allowed extension



cgi-unset
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: unset specified environment variables



cgi-loadlib
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: load a cgi shared library/optimizer



cgi-optimize
************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: enable cgi realpath() optimizer



cgi-optimized
*************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: enable cgi realpath() optimizer



cgi-path-info
*************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: disable PATH_INFO management in cgi scripts



cgi-do-not-kill-on-error
************************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: do not send SIGKILL to cgi script on errors



cgi-async-max-attempts
**********************
``argument``: no_argument

``parser``: uwsgi_opt_set_int

``help``: max waitpid() attempts in cgi async mode (default 10)




plugin: cheaper_backlog2
========================

plugin: cheaper_busyness
========================

plugin: clock_monotonic
=======================

plugin: clock_realtime
======================

plugin: corerouter
==================

plugin: coroae
==============
coroae
******
``argument``: required_argument

``parser``: uwsgi_opt_setup_coroae

``help``: a shortcut enabling Coro::AnyEvent loop engine with the specified number of async cores and optimal parameters




plugin: cplusplus
=================

plugin: curl_cron
=================
curl-cron
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_cron_curl

``flags``: UWSGI_OPT_MASTER

``help``: add a cron task invoking the specified url via CURL



cron-curl
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_cron_curl

``flags``: UWSGI_OPT_MASTER

``help``: add a cron task invoking the specified url via CURL



legion-curl-cron
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_legion_cron_curl

``flags``: UWSGI_OPT_MASTER

``help``: add a cron task invoking the specified url via CURL runnable only when the instance is a lord of the specified legion



legion-cron-curl
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_legion_cron_curl

``flags``: UWSGI_OPT_MASTER

``help``: add a cron task invoking the specified url via CURL runnable only when the instance is a lord of the specified legion



curl-cron-legion
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_legion_cron_curl

``flags``: UWSGI_OPT_MASTER

``help``: add a cron task invoking the specified url via CURL runnable only when the instance is a lord of the specified legion



cron-curl-legion
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_legion_cron_curl

``flags``: UWSGI_OPT_MASTER

``help``: add a cron task invoking the specified url via CURL runnable only when the instance is a lord of the specified legion




plugin: dumbloop
================
dumbloop-modifier1
******************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the modifier1 for the code_string



dumbloop-code
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set the script to load for the code_string



dumbloop-function
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set the function to run for the code_string




plugin: dummy
=============

plugin: echo
============

plugin: emperor_amqp
====================

plugin: emperor_mongodb
=======================

plugin: emperor_pg
==================

plugin: emperor_zeromq
======================

plugin: example
===============

plugin: exception_log
=====================

plugin: fastrouter
==================
fastrouter
**********
``argument``: required_argument

``parser``: uwsgi_opt_corerouter

``help``: run the fastrouter on the specified port

``reference``: :doc:`Fastrouter`



fastrouter-processes
********************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: prefork the specified number of fastrouter processes



fastrouter-workers
******************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: prefork the specified number of fastrouter processes



fastrouter-zerg
***************
``argument``: required_argument

``parser``: uwsgi_opt_corerouter_zerg

``help``: attach the fastrouter to a zerg server



fastrouter-use-cache
********************
``argument``: optional_argument

``parser``: uwsgi_opt_set_str

``help``: use uWSGI cache as hostname->server mapper for the fastrouter



fastrouter-use-pattern
**********************
``argument``: required_argument

``parser``: uwsgi_opt_corerouter_use_pattern

``help``: use a pattern for fastrouter hostname->server mapping



fastrouter-use-base
*******************
``argument``: required_argument

``parser``: uwsgi_opt_corerouter_use_base

``help``: use a base dir for fastrouter hostname->server mapping



fastrouter-fallback
*******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: fallback to the specified node in case of error



fastrouter-use-code-string
**************************
``argument``: required_argument

``parser``: uwsgi_opt_corerouter_cs

``help``: use code string as hostname->server mapper for the fastrouter



fastrouter-use-socket
*********************
``argument``: optional_argument

``parser``: uwsgi_opt_corerouter_use_socket

``help``: forward request to the specified uwsgi socket



fastrouter-to
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: forward requests to the specified uwsgi server (you can specify it multiple times for load balancing)



fastrouter-gracetime
********************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: retry connections to dead static nodes after the specified amount of seconds



fastrouter-events
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the maximum number of concurrent events



fastrouter-quiet
****************
``argument``: required_argument

``parser``: uwsgi_opt_true

``help``: do not report failed connections to instances



fastrouter-cheap
****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: run the fastrouter in cheap mode



fastrouter-subscription-server
******************************
``argument``: required_argument

``parser``: uwsgi_opt_corerouter_ss

``help``: run the fastrouter subscription server on the specified address



fastrouter-subscription-slot
****************************
``argument``: required_argument

``parser``: uwsgi_opt_deprecated

``help``: *** deprecated ***



fastrouter-timeout
******************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set fastrouter timeout



fastrouter-post-buffering
*************************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: enable fastrouter post buffering



fastrouter-post-buffering-dir
*****************************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: put fastrouter buffered files to the specified directory (noop, use TMPDIR env)



fastrouter-stats
****************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the fastrouter stats server



fastrouter-stats-server
***********************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the fastrouter stats server



fastrouter-ss
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the fastrouter stats server



fastrouter-harakiri
*******************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: enable fastrouter harakiri



fastrouter-uid
**************
``argument``: required_argument

``parser``: uwsgi_opt_uid

``help``: drop fastrouter privileges to the specified uid



fastrouter-gid
**************
``argument``: required_argument

``parser``: uwsgi_opt_gid

``help``: drop fastrouter privileges to the specified gid



fastrouter-resubscribe
**********************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: forward subscriptions to the specified subscription server



fastrouter-resubscribe-bind
***************************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: bind to the specified address when re-subscribing



fastrouter-buffer-size
**********************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: set internal buffer size (default: page size)



fastrouter-fallback-on-no-key
*****************************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: move to fallback node even if a subscription key is not found



fastrouter-force-key
********************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: skip uwsgi parsing and directly set a key




plugin: fiber
=============
fiber
*****
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: enable ruby fiber as suspend engine




plugin: forkptyrouter
=====================
forkptyrouter
*************
``argument``: required_argument

``parser``: uwsgi_opt_undeferred_corerouter

``help``: run the forkptyrouter on the specified address



forkpty-router
**************
``argument``: required_argument

``parser``: uwsgi_opt_undeferred_corerouter

``help``: run the forkptyrouter on the specified address



forkptyurouter
**************
``argument``: required_argument

``parser``: uwsgi_opt_forkpty_urouter

``help``: run the forkptyrouter on the specified address



forkpty-urouter
***************
``argument``: required_argument

``parser``: uwsgi_opt_forkpty_urouter

``help``: run the forkptyrouter on the specified address



forkptyrouter-command
*********************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the specified command on every connection (default: /bin/sh)



forkpty-router-command
**********************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the specified command on every connection (default: /bin/sh)



forkptyrouter-cmd
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the specified command on every connection (default: /bin/sh)



forkpty-router-cmd
******************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the specified command on every connection (default: /bin/sh)



forkptyrouter-rows
******************
``argument``: required_argument

``parser``: uwsgi_opt_set_16bit

``help``: set forkptyrouter default pty window rows



forkptyrouter-cols
******************
``argument``: required_argument

``parser``: uwsgi_opt_set_16bit

``help``: set forkptyrouter default pty window cols



forkptyrouter-processes
***********************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: prefork the specified number of forkptyrouter processes



forkptyrouter-workers
*********************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: prefork the specified number of forkptyrouter processes



forkptyrouter-zerg
******************
``argument``: required_argument

``parser``: uwsgi_opt_corerouter_zerg

``help``: attach the forkptyrouter to a zerg server



forkptyrouter-fallback
**********************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: fallback to the specified node in case of error



forkptyrouter-events
********************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the maximum number of concufptyent events



forkptyrouter-cheap
*******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: run the forkptyrouter in cheap mode



forkptyrouter-timeout
*********************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set forkptyrouter timeout



forkptyrouter-stats
*******************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the forkptyrouter stats server



forkptyrouter-stats-server
**************************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the forkptyrouter stats server



forkptyrouter-ss
****************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the forkptyrouter stats server



forkptyrouter-harakiri
**********************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: enable forkptyrouter harakiri




plugin: gccgo
=============
go-load
*******
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: load a go shared library in the process address space, eventually patching main.main and __go_init_main



gccgo-load
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: load a go shared library in the process address space, eventually patching main.main and __go_init_main



go-args
*******
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set go commandline arguments



gccgo-args
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set go commandline arguments



goroutines
**********
``argument``: required_argument

``parser``: uwsgi_opt_setup_goroutines

``flags``: UWSGI_OPT_THREADS

``help``: a shortcut setting optimal options for goroutine-based apps, takes the number of max goroutines to spawn as argument




plugin: geoip
=============
geoip-country
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: load the specified geoip country database



geoip-city
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: load the specified geoip city database



geoip-use-disk
**************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: do not cache geoip databases in memory




plugin: gevent
==============
gevent
******
``argument``: required_argument

``parser``: uwsgi_opt_setup_gevent

``flags``: UWSGI_OPT_THREADS

``help``: a shortcut enabling gevent loop engine with the specified number of async cores and optimal parameters



gevent-monkey-patch
*******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: call gevent.monkey.patch_all() automatically on startup



gevent-early-monkey-patch
*************************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: call gevent.monkey.patch_all() automatically before app loading



gevent-wait-for-hub
*******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: wait for gevent hub's death instead of the control greenlet




plugin: glusterfs
=================
glusterfs-mount
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: virtual mount the specified glusterfs volume in a uri



glusterfs-timeout
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: timeout for glusterfs async mode




plugin: graylog2
================

plugin: greenlet
================
greenlet
********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: enable greenlet as suspend engine




plugin: gridfs
==============
gridfs-mount
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: mount a gridfs db on the specified mountpoint



gridfs-debug
************
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_MIME

``help``: report gridfs mountpoint and itemname for each request (debug)




plugin: http
============
http
****
``argument``: required_argument

``parser``: uwsgi_opt_corerouter

``help``: add an http router/server on the specified address



httprouter
**********
``argument``: required_argument

``parser``: uwsgi_opt_corerouter

``help``: add an http router/server on the specified address



https
*****
``argument``: required_argument

``parser``: uwsgi_opt_https

``help``: add an https router/server on the specified address with specified certificate and key



https2
******
``argument``: required_argument

``parser``: uwsgi_opt_https2

``help``: add an https/spdy router/server using keyval options



https-export-cert
*****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: export uwsgi variable HTTPS_CC containing the raw client certificate



https-session-context
*********************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set the session id context to the specified value



http-to-https
*************
``argument``: required_argument

``parser``: uwsgi_opt_http_to_https

``help``: add an http router/server on the specified address and redirect all of the requests to https



http-processes
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the number of http processes to spawn



http-workers
************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the number of http processes to spawn



http-var
********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add a key=value item to the generated uwsgi packet



http-to
*******
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: forward requests to the specified node (you can specify it multiple time for lb)



http-zerg
*********
``argument``: required_argument

``parser``: uwsgi_opt_corerouter_zerg

``help``: attach the http router to a zerg server



http-fallback
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: fallback to the specified node in case of error



http-modifier1
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set uwsgi protocol modifier1



http-modifier2
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set uwsgi protocol modifier2



http-use-cache
**************
``argument``: optional_argument

``parser``: uwsgi_opt_set_str

``help``: use uWSGI cache as key->value virtualhost mapper



http-use-pattern
****************
``argument``: required_argument

``parser``: uwsgi_opt_corerouter_use_pattern

``help``: use the specified pattern for mapping requests to unix sockets



http-use-base
*************
``argument``: required_argument

``parser``: uwsgi_opt_corerouter_use_base

``help``: use the specified base for mapping requests to unix sockets



http-events
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the number of concurrent http async events



http-subscription-server
************************
``argument``: required_argument

``parser``: uwsgi_opt_corerouter_ss

``help``: enable the subscription server



http-timeout
************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set internal http socket timeout



http-manage-expect
******************
``argument``: optional_argument

``parser``: uwsgi_opt_set_64bit

``help``: manage the Expect HTTP request header (optionally checking for Content-Length)



http-keepalive
**************
``argument``: optional_argument

``parser``: uwsgi_opt_set_int

``help``: HTTP 1.1 keepalive support (non-pipelined) requests



http-auto-chunked
*****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: automatically transform output to chunked encoding during HTTP 1.1 keepalive (if needed)



http-auto-gzip
**************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: automatically gzip content if uWSGI-Encoding header is set to gzip, but content size (Content-Length/Transfer-Encoding) and Content-Encoding are not specified



http-raw-body
*************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: blindly send HTTP body to backends (required for WebSockets and Icecast support in backends)



http-websockets
***************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: automatically detect websockets connections and put the session in raw mode



http-chunked-input
******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: automatically detect chunked input requests and put the session in raw mode



http-use-code-string
********************
``argument``: required_argument

``parser``: uwsgi_opt_corerouter_cs

``help``: use code string as hostname->server mapper for the http router



http-use-socket
***************
``argument``: optional_argument

``parser``: uwsgi_opt_corerouter_use_socket

``help``: forward request to the specified uwsgi socket



http-gracetime
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: retry connections to dead static nodes after the specified amount of seconds



http-quiet
**********
``argument``: required_argument

``parser``: uwsgi_opt_true

``help``: do not report failed connections to instances



http-cheap
**********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: run the http router in cheap mode



http-stats
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the http router stats server



http-stats-server
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the http router stats server



http-ss
*******
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the http router stats server



http-harakiri
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: enable http router harakiri



http-stud-prefix
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_addr_list

``help``: expect a stud prefix (1byte family + 4/16 bytes address) on connections from the specified address



http-uid
********
``argument``: required_argument

``parser``: uwsgi_opt_uid

``help``: drop http router privileges to the specified uid



http-gid
********
``argument``: required_argument

``parser``: uwsgi_opt_gid

``help``: drop http router privileges to the specified gid



http-resubscribe
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: forward subscriptions to the specified subscription server



http-buffer-size
****************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: set internal buffer size (default: page size)



http-server-name-as-http-host
*****************************
``argument``: required_argument

``parser``: uwsgi_opt_true

``help``: force SERVER_NAME to HTTP_HOST



http-headers-timeout
********************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set internal http socket timeout for headers



http-connect-timeout
********************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set internal http socket timeout for backend connections



http-manage-source
******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: manage the SOURCE HTTP method placing the session in raw mode



http-enable-proxy-protocol
**************************
``argument``: optional_argument

``parser``: uwsgi_opt_true

``help``: manage PROXY protocol requests



http-backend-http
*****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: use plain http protocol instead of uwsgi for backend nodes



http-manage-rtsp
****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: manage RTSP sessions



0x1f
****
``argument``: 0x8b

``shortcut``: -Z_DEFLATED

``help``: 0




plugin: jvm
===========
jvm-main-class
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: load the specified class and call its main() function



jvm-opt
*******
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add the specified jvm option



jvm-class
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: load the specified class



jvm-classpath
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add the specified directory to the classpath




plugin: jwsgi
=============
jwsgi
*****
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: load the specified JWSGI application (syntax class:method)




plugin: ldap
============
ldap
****
``argument``: required_argument

``parser``: uwsgi_opt_load_ldap

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load configuration from ldap server



ldap-schema
***********
``argument``: no_argument

``parser``: uwsgi_opt_ldap_dump

``flags``: UWSGI_OPT_IMMEDIATE

``help``: dump uWSGI ldap schema



ldap-schema-ldif
****************
``argument``: no_argument

``parser``: uwsgi_opt_ldap_dump_ldif

``flags``: UWSGI_OPT_IMMEDIATE

``help``: dump uWSGI ldap schema in ldif format




plugin: legion_cache_fetch
==========================

plugin: libffi
==============

plugin: libtcc
==============

plugin: logcrypto
=================

plugin: logfile
===============

plugin: logpipe
===============

plugin: logsocket
=================

plugin: logzmq
==============
log-zeromq
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_logger

``flags``: UWSGI_OPT_MASTER | UWSGI_OPT_LOG_MASTER

``help``: send logs to a zeromq server




plugin: lua
===========
lua
***
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: load lua wsapi app



lua-load
********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: load a lua file



lua-shell
*********
``argument``: no_argument

``parser``: uwsgi_opt_luashell

``help``: run the lua interactive shell (debug.debug())



luashell
********
``argument``: no_argument

``parser``: uwsgi_opt_luashell

``help``: run the lua interactive shell (debug.debug())



lua-gc-freq
***********
``argument``: no_argument

``parser``: uwsgi_opt_set_int

``help``: set the lua gc frequency (default: 0, runs after every request)




plugin: matheval
================

plugin: mongodb
===============

plugin: mongodblog
==================

plugin: mongrel2
================
zeromq
******
``argument``: required_argument

``parser``: uwsgi_opt_add_lazy_socket

``help``: create a mongrel2/zeromq pub/sub pair



zmq
***
``argument``: required_argument

``parser``: uwsgi_opt_add_lazy_socket

``help``: create a mongrel2/zeromq pub/sub pair



zeromq-socket
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_lazy_socket

``help``: create a mongrel2/zeromq pub/sub pair



zmq-socket
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_lazy_socket

``help``: create a mongrel2/zeromq pub/sub pair



mongrel2
********
``argument``: required_argument

``parser``: uwsgi_opt_add_lazy_socket

``help``: create a mongrel2/zeromq pub/sub pair




plugin: mono
============
mono-app
********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: load a Mono asp.net app from the specified directory



mono-gc-freq
************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: run the Mono GC every <n> requests (default: run after every request)



mono-key
********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: select the ApplicationHost based on the specified CGI var



mono-version
************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set the Mono jit version



mono-config
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set the Mono config file



mono-assembly
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: load the specified main assembly (default: uwsgi.dll)



mono-exec
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: exec the specified assembly just before app loading



mono-index
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add an asp.net index file




plugin: msgpack
===============

plugin: nagios
==============
nagios
******
``argument``: no_argument

``parser``: uwsgi_opt_true

``flags``: UWSGI_OPT_NO_INITIAL

``help``: nagios check




plugin: notfound
================
notfound-log
************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: log requests to the notfound plugin




plugin: objc_gc
===============

plugin: pam
===========
pam
***
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set the pam service name to use



pam-user
********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set a fake user for pam




plugin: php
===========
php-ini
*******
``argument``: required_argument

``parser``: uwsgi_opt_php_ini

``help``: set php.ini path



php-config
**********
``argument``: required_argument

``parser``: uwsgi_opt_php_ini

``help``: set php.ini path



php-ini-append
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: set php.ini path (append mode)



php-config-append
*****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: set php.ini path (append mode)



php-set
*******
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: set a php config directive



php-index
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: list the php index files



php-docroot
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: force php DOCUMENT_ROOT



php-allowed-docroot
*******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: list the allowed document roots



php-allowed-ext
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: list the allowed php file extensions



php-allowed-script
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: list the allowed php scripts (require absolute path)



php-server-software
*******************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: force php SERVER_SOFTWARE



php-app
*******
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: force the php file to run at each request



php-app-qs
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: when in app mode force QUERY_STRING to the specified value + REQUEST_URI



php-fallback
************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the specified php script when the request one does not exist



php-app-bypass
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_regexp_list

``help``: if the regexp matches the uri the --php-app is bypassed



php-var
*******
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add/overwrite a CGI variable at each request



php-dump-config
***************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: dump php config (if modified via --php-set or append options)



php-exec-before
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run specified php code before the requested script



php-exec-begin
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run specified php code before the requested script



php-exec-after
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run specified php code after the requested script



php-exec-end
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run specified php code after the requested script



php-sapi-name
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: hack the sapi name (required for enabling zend opcode cache)



early-php
*********
``argument``: no_argument

``parser``: uwsgi_opt_early_php

``flags``: UWSGI_OPT_IMMEDIATE

``help``: initialize an early perl interpreter shared by all loaders



early-php-sapi-name
*******************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_IMMEDIATE

``help``: hack the sapi name (required for enabling zend opcode cache)




plugin: ping
============
ping
****
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_NO_INITIAL | UWSGI_OPT_NO_SERVER

``help``: ping specified uwsgi host



ping-timeout
************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set ping timeout




plugin: psgi
============
psgi
****
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: load a psgi app



psgi-enable-psgix-io
********************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: enable psgix.io support



perl-no-die-catch
*****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: do not catch $SIG{__DIE__}



perl-local-lib
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set perl locallib path



perl-version
************
``argument``: no_argument

``parser``: uwsgi_opt_print

``flags``: UWSGI_OPT_IMMEDIATE

``help``: print perl version



perl-args
*********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: add items (space separated) to @ARGV



perl-arg
********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add an item to @ARGV



perl-exec
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: exec the specified perl file before fork()



perl-exec-post-fork
*******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: exec the specified perl file after fork()



perl-auto-reload
****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_MASTER

``help``: enable perl auto-reloader with the specified frequency



perl-auto-reload-ignore
***********************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER

``help``: ignore the specified files when auto-reload is enabled



plshell
*******
``argument``: optional_argument

``parser``: uwsgi_opt_plshell

``help``: run a perl interactive shell



plshell-oneshot
***************
``argument``: no_argument

``parser``: uwsgi_opt_plshell

``help``: run a perl interactive shell (one shot)



perl-no-plack
*************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: force the use of do instead of Plack::Util::load_psgi



early-perl
**********
``argument``: required_argument

``parser``: uwsgi_opt_early_perl

``flags``: UWSGI_OPT_IMMEDIATE

``help``: initialize an early perl interpreter shared by all loaders



early-psgi
**********
``argument``: required_argument

``parser``: uwsgi_opt_early_psgi

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load a psgi app soon after uWSGI initialization



early-perl-exec
***************
``argument``: required_argument

``parser``: uwsgi_opt_early_exec

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load a perl script soon after uWSGI initialization




plugin: pty
===========
pty-socket
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: bind the pty server on the specified address



pty-log
*******
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: send stdout/stderr to the log engine too



pty-input
*********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: read from original stdin in addition to pty



pty-connect
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_NO_INITIAL

``help``: connect the current terminal to a pty server



pty-uconnect
************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_NO_INITIAL

``help``: connect the current terminal to a pty server (using uwsgi protocol)



pty-no-isig
***********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: disable ISIG terminal attribute in client mode



pty-exec
********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the specified command soon after the pty thread is spawned




plugin: pypy
============
pypy-lib
********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set the path/name of the pypy library



pypy-setup
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set the path of the python setup script



pypy-home
*********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set the home of pypy library



pypy-wsgi
*********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: load a WSGI module



pypy-wsgi-file
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: load a WSGI/mod_wsgi file



pypy-ini-paste
**************
``argument``: required_argument

``parser``: uwsgi_opt_pypy_ini_paste

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load a paste.deploy config file containing uwsgi section



pypy-paste
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: load a paste.deploy config file



pypy-eval
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: evaluate pypy code before fork()



pypy-eval-post-fork
*******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: evaluate pypy code soon after fork()



pypy-exec
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: execute pypy code from file before fork()



pypy-exec-post-fork
*******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: execute pypy code from file soon after fork()



pypy-pp
*******
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add an item to the pythonpath



pypy-python-path
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add an item to the pythonpath



pypy-pythonpath
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add an item to the pythonpath




plugin: python
==============
wsgi-file
*********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: load .wsgi file



file
****
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: load .wsgi file



eval
****
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: eval python code



module
******
``argument``: required_argument

``shortcut``: -w

``parser``: uwsgi_opt_set_str

``help``: load a WSGI module



wsgi
****
``argument``: required_argument

``shortcut``: -w

``parser``: uwsgi_opt_set_str

``help``: load a WSGI module



callable
********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set default WSGI callable name



test
****
``argument``: required_argument

``shortcut``: -J

``parser``: uwsgi_opt_set_str

``help``: test a module import



home
****
``argument``: required_argument

``shortcut``: -H

``parser``: uwsgi_opt_set_str

``help``: set PYTHONHOME/virtualenv



virtualenv
**********
``argument``: required_argument

``shortcut``: -H

``parser``: uwsgi_opt_set_str

``help``: set PYTHONHOME/virtualenv



venv
****
``argument``: required_argument

``shortcut``: -H

``parser``: uwsgi_opt_set_str

``help``: set PYTHONHOME/virtualenv



pyhome
******
``argument``: required_argument

``shortcut``: -H

``parser``: uwsgi_opt_set_str

``help``: set PYTHONHOME/virtualenv



py-programname
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set python program name



py-program-name
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set python program name



pythonpath
**********
``argument``: required_argument

``parser``: uwsgi_opt_pythonpath

``help``: add directory (or glob) to pythonpath



python-path
***********
``argument``: required_argument

``parser``: uwsgi_opt_pythonpath

``help``: add directory (or glob) to pythonpath



pp
**
``argument``: required_argument

``parser``: uwsgi_opt_pythonpath

``help``: add directory (or glob) to pythonpath



pymodule-alias
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add a python alias module



post-pymodule-alias
*******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add a python module alias after uwsgi module initialization



import
******
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: import a python module



pyimport
********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: import a python module



py-import
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: import a python module



python-import
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: import a python module



shared-import
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: import a python module in all of the processes



shared-pyimport
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: import a python module in all of the processes



shared-py-import
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: import a python module in all of the processes



shared-python-import
********************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: import a python module in all of the processes



pyargv
******
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: manually set sys.argv



optimize
********
``argument``: required_argument

``shortcut``: -O

``parser``: uwsgi_opt_set_int

``help``: set python optimization level



pecan
*****
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: load a pecan config file



paste
*****
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: load a paste.deploy config file



paste-logger
************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: enable paste fileConfig logger



web3
****
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: load a web3 app



pump
****
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: load a pump app



wsgi-lite
*********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: load a wsgi-lite app



ini-paste
*********
``argument``: required_argument

``parser``: uwsgi_opt_ini_paste

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load a paste.deploy config file containing uwsgi section



ini-paste-logged
****************
``argument``: required_argument

``parser``: uwsgi_opt_ini_paste

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load a paste.deploy config file containing uwsgi section (load loggers too)



reload-os-env
*************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: force reload of os.environ at each request



no-site
*******
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: do not import site module



pyshell
*******
``argument``: optional_argument

``parser``: uwsgi_opt_pyshell

``help``: run an interactive python shell in the uWSGI environment



pyshell-oneshot
***************
``argument``: optional_argument

``parser``: uwsgi_opt_pyshell

``help``: run an interactive python shell in the uWSGI environment (one-shot variant)



python
******
``argument``: required_argument

``parser``: uwsgi_opt_pyrun

``help``: run a python script in the uWSGI environment



py
**
``argument``: required_argument

``parser``: uwsgi_opt_pyrun

``help``: run a python script in the uWSGI environment



pyrun
*****
``argument``: required_argument

``parser``: uwsgi_opt_pyrun

``help``: run a python script in the uWSGI environment



py-tracebacker
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_THREADS|UWSGI_OPT_MASTER

``help``: enable the uWSGI python tracebacker



py-auto-reload
**************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_THREADS|UWSGI_OPT_MASTER

``help``: monitor python modules mtime to trigger reload (use only in development)



py-autoreload
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_THREADS|UWSGI_OPT_MASTER

``help``: monitor python modules mtime to trigger reload (use only in development)



python-auto-reload
******************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_THREADS|UWSGI_OPT_MASTER

``help``: monitor python modules mtime to trigger reload (use only in development)



python-autoreload
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``flags``: UWSGI_OPT_THREADS|UWSGI_OPT_MASTER

``help``: monitor python modules mtime to trigger reload (use only in development)



py-auto-reload-ignore
*********************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_THREADS|UWSGI_OPT_MASTER

``help``: ignore the specified module during auto-reload scan (can be specified multiple times)



wsgi-env-behaviour
******************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set the strategy for allocating/deallocating the WSGI env, can be: "cheat" or "holy"

``reference``: :doc:`articles/WSGIEnvBehaviour`


wsgi-env-behavior
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set the strategy for allocating/deallocating the WSGI env, can be: "cheat" or "holy"

``reference``: :doc:`articles/WSGIEnvBehaviour`

start_response-nodelay
**********************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: send WSGI http headers as soon as possible (PEP violation)



wsgi-strict
***********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: try to be fully PEP compliant disabling optimizations



wsgi-accept-buffer
******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: accept CPython buffer-compliant objects as WSGI response in addition to string/bytes



wsgi-accept-buffers
*******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: accept CPython buffer-compliant objects as WSGI response in addition to string/bytes



python-version
**************
``argument``: no_argument

``parser``: uwsgi_opt_pyver

``flags``: UWSGI_OPT_IMMEDIATE

``help``: report python version



python-raw
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: load a python file for managing raw requests



py-sharedarea
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: create a sharedarea from a python bytearray object of the specified size



py-call-osafterfork
*******************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: enable child processes running cpython to trap OS signals



early-python
************
``argument``: no_argument

``parser``: uwsgi_early_python

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load the python VM as soon as possible (useful for the fork server)



early-pyimport
**************
``argument``: required_argument

``parser``: uwsgi_early_python_import

``flags``: UWSGI_OPT_IMMEDIATE

``help``: import a python module in the early phase



early-python-import
*******************
``argument``: required_argument

``parser``: uwsgi_early_python_import

``flags``: UWSGI_OPT_IMMEDIATE

``help``: import a python module in the early phase



early-pythonpath
****************
``argument``: required_argument

``parser``: uwsgi_opt_pythonpath

``flags``: UWSGI_OPT_IMMEDIATE

``help``: add directory (or glob) to pythonpath (immediate version)



early-python-path
*****************
``argument``: required_argument

``parser``: uwsgi_opt_pythonpath

``flags``: UWSGI_OPT_IMMEDIATE

``help``: add directory (or glob) to pythonpath (immediate version)




plugin: pyuwsgi
===============

plugin: rack
============
rails
*****
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_POST_BUFFERING

``help``: load a rails <= 2.x app



rack
****
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_POST_BUFFERING

``help``: load a rack app



ruby-gc-freq
************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set ruby GC frequency



rb-gc-freq
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set ruby GC frequency



rb-lib
******
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add a directory to the ruby libdir search path



ruby-lib
********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add a directory to the ruby libdir search path



rb-require
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: import/require a ruby module/script



ruby-require
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: import/require a ruby module/script



rbrequire
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: import/require a ruby module/script



rubyrequire
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: import/require a ruby module/script



require
*******
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: import/require a ruby module/script



shared-rb-require
*****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: import/require a ruby module/script (shared)



shared-ruby-require
*******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: import/require a ruby module/script (shared)



shared-rbrequire
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: import/require a ruby module/script (shared)



shared-rubyrequire
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: import/require a ruby module/script (shared)



shared-require
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: import/require a ruby module/script (shared)



gemset
******
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: load the specified gemset (rvm)



rvm
***
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: load the specified gemset (rvm)



rvm-path
********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: search for rvm in the specified directory



rbshell
*******
``argument``: optional_argument

``parser``: uwsgi_opt_rbshell

``help``: run  a ruby/irb shell



rbshell-oneshot
***************
``argument``: no_argument

``parser``: uwsgi_opt_rbshell

``help``: set ruby/irb shell (one shot)




plugin: rados
=============
rados-mount
***********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: virtual mount the specified rados volume in a uri



rados-timeout
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: timeout for async operations




plugin: rawrouter
=================
rawrouter
*********
``argument``: required_argument

``parser``: uwsgi_opt_undeferred_corerouter

``help``: run the rawrouter on the specified port



rawrouter-processes
*******************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: prefork the specified number of rawrouter processes



rawrouter-workers
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: prefork the specified number of rawrouter processes



rawrouter-zerg
**************
``argument``: required_argument

``parser``: uwsgi_opt_corerouter_zerg

``help``: attach the rawrouter to a zerg server



rawrouter-use-cache
*******************
``argument``: optional_argument

``parser``: uwsgi_opt_set_str

``help``: use uWSGI cache as hostname->server mapper for the rawrouter



rawrouter-use-pattern
*********************
``argument``: required_argument

``parser``: uwsgi_opt_corerouter_use_pattern

``help``: use a pattern for rawrouter hostname->server mapping



rawrouter-use-base
******************
``argument``: required_argument

``parser``: uwsgi_opt_corerouter_use_base

``help``: use a base dir for rawrouter hostname->server mapping



rawrouter-fallback
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: fallback to the specified node in case of error



rawrouter-use-code-string
*************************
``argument``: required_argument

``parser``: uwsgi_opt_corerouter_cs

``help``: use code string as hostname->server mapper for the rawrouter



rawrouter-use-socket
********************
``argument``: optional_argument

``parser``: uwsgi_opt_corerouter_use_socket

``help``: forward request to the specified uwsgi socket



rawrouter-to
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: forward requests to the specified uwsgi server (you can specify it multiple times for load balancing)



rawrouter-gracetime
*******************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: retry connections to dead static nodes after the specified amount of seconds



rawrouter-events
****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the maximum number of concurrent events



rawrouter-max-retries
*********************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the maximum number of retries/fallbacks to other nodes



rawrouter-quiet
***************
``argument``: required_argument

``parser``: uwsgi_opt_true

``help``: do not report failed connections to instances



rawrouter-cheap
***************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: run the rawrouter in cheap mode



rawrouter-subscription-server
*****************************
``argument``: required_argument

``parser``: uwsgi_opt_corerouter_ss

``help``: run the rawrouter subscription server on the spcified address



rawrouter-subscription-slot
***************************
``argument``: required_argument

``parser``: uwsgi_opt_deprecated

``help``: *** deprecated ***



rawrouter-timeout
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set rawrouter timeout



rawrouter-stats
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the rawrouter stats server



rawrouter-stats-server
**********************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the rawrouter stats server



rawrouter-ss
************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the rawrouter stats server



rawrouter-harakiri
******************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: enable rawrouter harakiri



rawrouter-xclient
*****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: use the xclient protocol to pass the client address



rawrouter-buffer-size
*********************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: set internal buffer size (default: page size)




plugin: rbthreads
=================
rbthreads
*********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: enable ruby native threads



rb-threads
**********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: enable ruby native threads



rbthread
********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: enable ruby native threads



rb-thread
*********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: enable ruby native threads




plugin: redislog
================

plugin: ring
============
ring-load
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: load the specified clojure script



clojure-load
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: load the specified clojure script



ring-app
********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: map the specified ring application (syntax namespace:function)




plugin: router_access
=====================

plugin: router_basicauth
========================

plugin: router_cache
====================

plugin: router_expires
======================

plugin: router_hash
===================

plugin: router_http
===================

plugin: router_memcached
========================

plugin: router_metrics
======================

plugin: router_radius
=====================

plugin: router_redirect
=======================

plugin: router_redis
====================

plugin: router_rewrite
======================

plugin: router_spnego
=====================

plugin: router_static
=====================

plugin: router_uwsgi
====================

plugin: router_xmldir
=====================

plugin: rpc
===========

plugin: rrdtool
===============
rrdtool
*******
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MASTER|UWSGI_OPT_METRICS

``help``: store rrd files in the specified directory



rrdtool-freq
************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set collect frequency



rrdtool-lib
***********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set the name of rrd library (default: librrd.so)




plugin: rsyslog
===============
rsyslog-packet-size
*******************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set maximum packet size for syslog messages (default 1024) WARNING! using packets > 1024 breaks RFC 3164 (#4.1)



rsyslog-split-messages
**********************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: split big messages into multiple chunks if they are bigger than allowed packet size (default is false)




plugin: ruby19
==============

plugin: servlet
===============

plugin: signal
==============

plugin: spooler
===============

plugin: sqlite3
===============
sqlite3
*******
``argument``: required_argument

``parser``: uwsgi_opt_load_sqlite3

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load config from sqlite3 db



sqlite
******
``argument``: required_argument

``parser``: uwsgi_opt_load_sqlite3

``flags``: UWSGI_OPT_IMMEDIATE

``help``: load config from sqlite3 db




plugin: ssi
===========

plugin: sslrouter
=================
sslrouter
*********
``argument``: required_argument

``parser``: uwsgi_opt_sslrouter

``help``: run the sslrouter on the specified port



sslrouter2
**********
``argument``: required_argument

``parser``: uwsgi_opt_sslrouter2

``help``: run the sslrouter on the specified port (key-value based)



sslrouter-session-context
*************************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set the session id context to the specified value



sslrouter-processes
*******************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: prefork the specified number of sslrouter processes



sslrouter-workers
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: prefork the specified number of sslrouter processes



sslrouter-zerg
**************
``argument``: required_argument

``parser``: uwsgi_opt_corerouter_zerg

``help``: attach the sslrouter to a zerg server



sslrouter-use-cache
*******************
``argument``: optional_argument

``parser``: uwsgi_opt_set_str

``help``: use uWSGI cache as hostname->server mapper for the sslrouter



sslrouter-use-pattern
*********************
``argument``: required_argument

``parser``: uwsgi_opt_corerouter_use_pattern

``help``: use a pattern for sslrouter hostname->server mapping



sslrouter-use-base
******************
``argument``: required_argument

``parser``: uwsgi_opt_corerouter_use_base

``help``: use a base dir for sslrouter hostname->server mapping



sslrouter-fallback
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: fallback to the specified node in case of error



sslrouter-use-code-string
*************************
``argument``: required_argument

``parser``: uwsgi_opt_corerouter_cs

``help``: use code string as hostname->server mapper for the sslrouter



sslrouter-use-socket
********************
``argument``: optional_argument

``parser``: uwsgi_opt_corerouter_use_socket

``help``: forward request to the specified uwsgi socket



sslrouter-to
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: forward requests to the specified uwsgi server (you can specify it multiple times for load balancing)



sslrouter-gracetime
*******************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: retry connections to dead static nodes after the specified amount of seconds



sslrouter-events
****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the maximum number of concurrent events



sslrouter-max-retries
*********************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set the maximum number of retries/fallbacks to other nodes



sslrouter-quiet
***************
``argument``: required_argument

``parser``: uwsgi_opt_true

``help``: do not report failed connections to instances



sslrouter-cheap
***************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: run the sslrouter in cheap mode



sslrouter-subscription-server
*****************************
``argument``: required_argument

``parser``: uwsgi_opt_corerouter_ss

``help``: run the sslrouter subscription server on the spcified address



sslrouter-timeout
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set sslrouter timeout



sslrouter-stats
***************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the sslrouter stats server



sslrouter-stats-server
**********************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the sslrouter stats server



sslrouter-ss
************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the sslrouter stats server



sslrouter-harakiri
******************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: enable sslrouter harakiri



sslrouter-sni
*************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: use SNI to route requests



sslrouter-buffer-size
*********************
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: set internal buffer size (default: page size)




plugin: stackless
=================
stackless
*********
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: use stackless as suspend engine




plugin: stats_pusher_file
=========================

plugin: stats_pusher_mongodb
============================

plugin: stats_pusher_socket
===========================

plugin: stats_pusher_statsd
===========================

plugin: symcall
===============
symcall
*******
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: load the specified C symbol as the symcall request handler (supports <mountpoint=func> too)



symcall-use-next
****************
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: use RTLD_NEXT when searching for symbols



symcall-register-rpc
********************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: load the specified C symbol as an RPC function (syntax: name function)



symcall-post-fork
*****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: call the specified C symbol after each fork()




plugin: syslog
==============

plugin: systemd_logger
======================

plugin: tornado
===============
tornado
*******
``argument``: required_argument

``parser``: uwsgi_opt_setup_tornado

``flags``: UWSGI_OPT_THREADS

``help``: a shortcut enabling tornado loop engine with the specified number of async cores and optimal parameters




plugin: transformation_chunked
==============================

plugin: transformation_gzip
===========================

plugin: transformation_offload
==============================

plugin: transformation_template
===============================

plugin: transformation_tofile
=============================

plugin: transformation_toupper
==============================

plugin: tuntap
==============
tuntap-router
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: run the tuntap router (syntax: <device> <socket> [stats] [gateway])



tuntap-device
*************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add a tuntap device to the instance (syntax: <device>[ <socket>])



tuntap-use-credentials
**********************
``argument``: optional_argument

``parser``: uwsgi_opt_set_str

``help``: enable check of SCM_CREDENTIALS for tuntap client/server



tuntap-router-firewall-in
*************************
``argument``: required_argument

``parser``: uwsgi_tuntap_opt_firewall

``help``: add a firewall rule to the tuntap router (syntax: <action> <src/mask> <dst/mask>)



tuntap-router-firewall-out
**************************
``argument``: required_argument

``parser``: uwsgi_tuntap_opt_firewall

``help``: add a firewall rule to the tuntap router (syntax: <action> <src/mask> <dst/mask>)



tuntap-router-route
*******************
``argument``: required_argument

``parser``: uwsgi_tuntap_opt_route

``help``: add a routing rule to the tuntap router (syntax: <src/mask> <dst/mask> <gateway>)



tuntap-router-stats
*******************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: run the tuntap router stats server



tuntap-device-rule
******************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add a tuntap device rule (syntax: <direction> <src/mask> <dst/mask> <action> [target])




plugin: ugreen
==============
ugreen
******
``argument``: no_argument

``parser``: uwsgi_opt_true

``help``: enable ugreen coroutine subsystem



ugreen-stacksize
****************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: set ugreen stack size in pages




plugin: v8
==========
v8-load
*******
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: load a javascript file



v8-preemptive
*************
``argument``: required_argument

``parser``: uwsgi_opt_set_int

``help``: put v8 in preemptive move (single isolate) with the specified frequency



v8-gc-freq
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_64bit

``help``: set the v8 garbage collection frequency



v8-module-path
**************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: set the v8 modules search path



v8-jsgi
*******
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: load the specified JSGI 3.0 application




plugin: webdav
==============
webdav-mount
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: map a filesystem directory as a webdav store



webdav-css
**********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: add a css url for automatic webdav directory listing



webdav-javascript
*****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: add a javascript url for automatic webdav directory listing



webdav-js
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: add a javascript url for automatic webdav directory listing



webdav-class-directory
**********************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_MIME

``help``: set the css directory class for automatic webdav directory listing



webdav-div
**********
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_MIME

``help``: set the div id for automatic webdav directory listing



webdav-lock-cache
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_MIME

``help``: set the cache to use for webdav locking



webdav-principal-base
*********************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``flags``: UWSGI_OPT_MIME

``help``: enable WebDAV Current Principal Extension using the specified base



webdav-add-option
*****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: add a WebDAV standard to the OPTIONS response



webdav-add-prop
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: add a WebDAV property to all resources



webdav-add-collection-prop
**************************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: add a WebDAV property to all collections



webdav-add-object-prop
**********************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: add a WebDAV property to all objects



webdav-add-prop-href
********************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: add a WebDAV property to all resources (href value)



webdav-add-collection-prop-href
*******************************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: add a WebDAV property to all collections (href value)



webdav-add-object-prop-href
***************************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: add a WebDAV property to all objects (href value)



webdav-add-prop-comp
********************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: add a WebDAV property to all resources (xml value)



webdav-add-collection-prop-comp
*******************************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: add a WebDAV property to all collections (xml value)



webdav-add-object-prop-comp
***************************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: add a WebDAV property to all objects (xml value)



webdav-add-rtype-prop
*********************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: add a WebDAV resourcetype property to all resources



webdav-add-rtype-collection-prop
********************************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: add a WebDAV resourcetype property to all collections



webdav-add-rtype-object-prop
****************************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: add a WebDAV resourcetype property to all objects



webdav-skip-prop
****************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``flags``: UWSGI_OPT_MIME

``help``: do not add the specified prop if available in resource xattr




plugin: xattr
=============

plugin: xslt
============
xslt-docroot
************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: add a document_root for xslt processing



xslt-ext
********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: search for xslt stylesheets with the specified extension



xslt-var
********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: get the xslt stylesheet path from the specified request var



xslt-stylesheet
***************
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: if no xslt stylesheet file can be found, use the specified one



xslt-content-type
*****************
``argument``: required_argument

``parser``: uwsgi_opt_set_str

``help``: set the content-type for the xslt rsult (default: text/html)




plugin: zabbix
==============
zabbix-template
***************
``argument``: optional_argument

``parser``: uwsgi_opt_zabbix_template

``flags``: UWSGI_OPT_METRICS

``help``: print (or store to a file) the zabbix template for the current metrics setup




plugin: zergpool
================
zergpool
********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: start a zergpool on specified address for specified address



zerg-pool
*********
``argument``: required_argument

``parser``: uwsgi_opt_add_string_list

``help``: start a zergpool on specified address for specified address



