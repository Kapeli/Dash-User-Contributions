The JWSGI interface
===================

.. note:: JWSGI is not a standard. Yet. If you like JWSGI, why not send an RFC to the uWSGI mailing list. We have no specific interest in a standard, but who knows...

JWSGI is a port of the WSGI/PSGI/Rack way of thinking for Java.

If, for some obscure reason, you'd feel like developing apps with JVM languages
and you don't feel like deploying a huge servlet stack, JWSGI should be up your
alley.

It is a very simple protocol: you call a public method that takes a ``HashMap``
as its sole argument.  This HashMap contains CGI style variables and
``jwsgi.input`` containing a Java InputStream object.

The function has to returns an array of 3 Objects:

* ``status`` (java.lang.Integer) (example: 200)
* ``headers`` (HashMap) (example: {"Content-type": "text/html", "Server":
  "uWSGI", "Foo": ["one","two"]})
* ``body`` (may be a String, an array of Strings, a File or an InputStream
  object)

Example
-------

A simple JWSGI app looks like this:

.. code-block:: java

   import java.util.*;
   public class MyApp {

       public static Object[] application(HashMap env) {

           int status = 200;

           HashMap<String,Object> headers = new HashMap<String,Object>();
           headers.put("Content-type", "text/html");
           // a response header can have multiple values
           String[] servers = {"uWSGI", "Unbit"};
           headers.put("Server", servers);

           String body = "<h1>Hello World</h1>" + env.get("REQUEST_URI");

           Object[] response = { status, headers, body };

           return response;
       }
   }



How to use it ?
***************

You need both the 'jvm' plugin and the 'jwsgi' plugin. A build profile named
'jwsgi', is available in the project to allow a monolithic build with
jvm+jwsgi:

.. code-block:: sh

   UWSGI_PROFILE=jwsgi make


1. Compile your class with ``javac``.

   .. code-block:: sh

      javac MyApp.java

4. Run uWSGI and specify the method to run (in the form class:method)

   .. code-block:: sh

      ./uwsgi --socket /tmp/uwsgi.socket --plugins jvm,jwsgi --jwsgi
      MyApp:application --threads 40

  This will run a JWSGI application on UNIX socket /tmp/uwsgi.socket with 40
  threads.

Reading request body
********************

The ``jwsgi.input`` item is an ``uwsgi.RequestBody`` object (subclass of
java/io/InputStream). You it to access the request body.

.. code-block:: java

   import java.util.*;
   public class MyApp {

       public static Object[] application(HashMap env) {

           int status = 200;

           HashMap<String,Object> headers = new HashMap<String,Object>();
           headers.put("Content-type", "text/plain");

           int body_len = Integer.parseInt((String) env.get("CONTENT_LENGTH"));
           byte[] chunk = new byte[body_len];

           uwsgi.RequestBody input = (uwsgi.RequestBody) env.get("jwsgi.input");

           int len = input.read(chunk);

           System.out.println("read " + len + " bytes");

           String body = new String(chunk, 0, len);

           Object[] response = { status, headers, body };

           return response;
       }
   }

Pay attention to the use of ``read(byte[])`` instead of the classical
``read()``. The latter inefficiently reads one byte at time, while the former
reads a larger chunk at a time.

JWSGI and Groovy
****************

Being low-level, the JWSGI standard can be used as-is in other languages
running on the JVM.  As an example this is a "Hello World" Groovy example:

.. code-block:: groovy

   static def Object[] application(java.util.HashMap env) {
        def headers = ["Content-Type":"text/html", "Server":"uWSGI"]
        return [200, headers, "<h1>Hello World</h1"]
   }

One serving a static file:

.. code-block:: groovy

   static def Object[] application(java.util.HashMap env) {
        def headers = ["Content-Type":"text/plain", "Server":"uWSGI"]
        return [200, headers, new File("/etc/services")]
   }

The second approach is very efficient as it will abuse uWSGI internal
facilities. For example if you have offloading enabled, your worker thread will
be suddenly freed.  To load Groovy code, remember to compile it:

.. code-block:: sh

   groovyc Foobar.groovy

Then run it:

.. code-block:: sh

   ./uwsgi --socket /tmp/uwsgi.socket --plugins jvm,jwsgi --jwsgi Foobar:application --threads 40

JWSGI and Scala
***************

Like Groovy, you can write JWSGI apps with Scala. You only need the entry point
function to use native Java objects:

.. code-block:: scala

   object HelloWorld {
        def application(env:java.util.HashMap[String, Object]): Array[Object] = {
                var headers = new java.util.HashMap[String, Object]()
                headers.put("Content-Type", "text/html")
                headers.put("Server", "uWSGI")
                return Array(200:java.lang.Integer, headers , "Hello World")
        }
   }

Or in a more Scala-ish way:

.. code-block:: scala

   object HelloWorld {
        def application(env:java.util.HashMap[String, Object]): Array[Object] = {
                val headers = new java.util.HashMap[String, Object]() {
                        put("Content-Type", "text/html")
                        put("Server", Array("uWSGI", "Unbit"))
                }
                return Array(200:java.lang.Integer, headers , "Hello World")
        }
   }

Once compiled with ``scalac <filename>`` you run like this:

.. code-block:: sh

   ./uwsgi --socket /tmp/uwsgi.socket --plugins jvm,jwsgi --jwsgi HelloWorld:application --threads 40
