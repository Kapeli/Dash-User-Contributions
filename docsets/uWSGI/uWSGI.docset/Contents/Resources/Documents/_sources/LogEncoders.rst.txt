Log encoders
============

uWSGI 1.9.16 got the "log encoding" feature.

An encoder receives a logline and give back a "transformation" of it.

Encoders can be added by plugins, and can be enabled in chain (the output of an encoder will be the input of the following one and so on).

.. code-block:: ini

   [uwsgi]
   ; send logs to udp address 192.168.173.13:1717
   logger = socket:192.168.173.13:1717
   ; before sending a logline to the logger encode it in gzip
   log-encoder = gzip
   ; after gzip add a 'clear' prefix to easy decode
   log-encoder = prefix i am gzip encoded
   ...


   
   
with this configuration the log server will receive the "i am gzip encoded" string followed by the tru log message encoded in gzip

The log encoder syntax is the following:

log-encoder = <encoder>[ args]

so args (if any) are separated by a single space

Request logs VS stdout/stderr
*****************************

The --log-encoder option encodes only the stdout/stderr logs.

If you want to encode request logs to use --log-req-encoder:

.. code-block:: ini

   [uwsgi]
   ; send request logs to udp address 192.168.173.13:1717
   req-logger = socket:192.168.173.13:1717
   ; before sending a logline to the logger encode it in gzip
   log-req-encoder = gzip
   ; after gzip add a 'clear' prefix to easy decode
   log-req-encoder = prefix i am gzip encoded
   ...
   
Routing encoders
****************

Log routing allows sending each logline to a different log engine based on regexps. You can use the same system with encoders too:

.. code-block:: ini

   [uwsgi]
   ; by default send logs to udp address 192.168.173.13:1717
   logger = socket:192.168.173.13:1717
   ; an alternative logger using the same address
   logger = secondlogger socket:192.168.173.13:1717
   ; use 'secondlogger' for the logline containing 'uWSGI'
   log-route = secondlogger uWSGI
   ; before sending a logline to the 'secondlogger' logger encode it in gzip
   log-encoder = gzip:secondlogger
   ...

   
``Core`` encoders
*****************

The following encoders are available in the uwsgi 'core':

``prefix`` add a raw prefix to each log msg

``suffix`` add a raw suffix to each log msg

``nl`` add a newline char to each log msg

``gzip`` compress each msg with gzip (requires zlib)

``compress`` compress each msg with zlib compress (requires zlib)

``format`` apply the specified format to each log msg:

.. code-block:: ini

   [uwsgi]
   ...
   log-encoder = format [FOO ${msg} BAR]
   ...
   
``json`` like ``format`` but each variable is json escaped

.. code-block:: ini

   [uwsgi]
   ...
   log-encoder = json {"unix":${unix}, "msg":"${msg}"}
   ...
   
The following variables (for format and json) are available:

``${msg}`` the raw log message (newline stripped)

``${msgnl}`` the raw log message (with newline)

``${unix}`` the current unix time

``${micros}`` the current unix time in microseconds

``${strftime:xxx}`` strftime using the xxx format:



.. code-block:: ini

   [uwsgi]
   ...
   ; we need to escape % to avoid magic vars nameclash
   log-encoder = json {"unix":${unix}, "msg":"${msg}", "date":"${strftime:%%d/%%m/%%Y %%H:%%M:%%S}"}
   ...

  
The ``msgpack`` encoder
***********************

This is the first log-encoder plugin officially added to uWSGI sources. It allows encoding of loglines in msgpack (http://msgpack.org/) format.

The syntax is pretty versatile as it has been developed for adding any information to a single packet

``log-encoder = msgpack <format>``

format is pretty complex as it is a list of the single items in the whole packet.

For example if you want to encode the {'foo':'bar', 'test':17} dictionary you need to read it as:

a map of 2 items | the string foo | the string bar | the string test | the integer 17

for a total of 5 items.

A more complex structure {'boo':30, 'foo':'bar', 'test': [1,3,3,17.30,nil,true,false]}

will be

a map of 3 items | the string boo | the number 30| the string foo| the string bar | the string test | an array of 7 items | the integer 1 | the integer 3 | the integer 3 | the float 17.30 | a nil | a true | a false

The <format> string is a representation of this way:

.. code-block:: sh
   
   map:2|str:foo|str:bar|str:test|int:17

The pipe is the seprator of each item. The string before the colon is the type of item, followed by the optional argument

The following item types are supported:

``map`` a dictionary, the argument is the number of items

``array`` an array, the argument is the number of items

``str`` a string, the argument is the string itself

``bin`` a byte array, the argument is the binary stream itself

``int`` an integer, the argument is the number

``float`` a float, the argument is the number

``nil`` undefined/NULL

``true`` boolean TRUE

``false`` boolean FALSE

in addition to msgpack types, a series of dynamic types are available:

``msg`` translate the logline to a msgpack string with newline chopped

``msgbin`` translate the logline to a msgpack byte array with newline chopped

``msgnl`` translate the logline to a msgpack string (newline included)

``msgbin`` translate the logline to a msgpack byte array (newline included)

``unix`` translate to an integer of the unix time

``micros`` translate to an integer of the unix time in microseconds

``strftime`` translate to a string using strftime syntax. The strftime format is the argument

As an example you can send logline to a logstash server via udp:


(logstash debug configuration):

.. code-block:: c

   input {
        udp {
                codec =>   msgpack {}
                port => 1717
        }
   }
   output {
        stdout { debug => true }
        elasticsearch { embedded => true }
   }


.. code-block:: ini

   [uwsgi]
   logger = socket:192.168.173.13:1717
   log-encoder = msgpack map:4|str:message|msg|str:hostname|str:%h|str:version|str:%V|str:appname|str:myapp
   ...
   
this will generate the following structure:

.. code-block:: js

   {
      "message": "*** Starting uWSGI 1.9.16-dev-29d80ce (64bit) on [Sat Sep  7 15:04:32 2013] ***",
      "hostname": "unbit.it",
      "version": "1.9.16-dev",
      "appname": "myapp"
   }
   
that will be stored in elasticsearch

Notes
*****

Encoders automatically enable --log-master

For best performance consider allocating a thread for log sending with --threaded-logger
