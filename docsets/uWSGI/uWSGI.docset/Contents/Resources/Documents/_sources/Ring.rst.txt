The Clojure/Ring JVM request handler
====================================

Thanks to the :doc:`JVM` plugin available from 1.9, Clojure web apps can be run on uWSGI.

The supported gateway standard is Ring, https://github.com/ring-clojure/ring . Its full specification is available here: https://github.com/ring-clojure/ring/blob/master/SPEC

A uWSGI build profile named "ring" is available for generating a monolithic build with both the JVM and Ring plugins.

From the uWSGI sources:

.. code-block:: sh

   UWSGI_PROFILE=ring make

The build system will try to detect your JDK installation based on various presets (for example on CentOS you can ``yum install 
java-1.6.0-openjdk.x86_64-devel`` or ``java-1.7.0-openjdk-devel.x86_64`` or on Debian/Ubuntu ``openjdk-6-jdk`` and so on...).

OSX/Xcode default paths are searched too.

After a successful build you will have the uwsgi binary and a uwsgi.jar file that you should copy in your CLASSPATH (or just remember
to set it in the uwsgi configuration every time).

.. seealso:: For more information on the JVM plugin check :doc:`JVM`

Our first Ring app
******************

A basic Clojure/Ring app could be the following (save it as myapp.clj):

.. code-block:: Clojure

   (ns myapp)

   (defn handler [req]
        {:status 200
         :headers { "Content-Type" "text/plain" , "Server" "uWSGI" }
         :body (str "<h1>The requested uri is " (get req :uri) "</h1>")
        }
   )

The code defines a new namespace called 'myapp', in which the 'handler' function is the Ring entry point (the function called at each web request)

We can now build a configuration serving that app on the HTTP router on port 9090 (call it config.ini):

.. code-block:: ini

   [uwsgi]
   http = :9090
   http-modifier1 = 8
   http-modifier2 = 1

   jvm-classpath = plugins/jvm/uwsgi.jar
   jvm-classpath = ../.lein/self-installs/leiningen-2.0.0-standalone.jar

   clojure-load = myapp.clj
   ring-app = myapp:handler

Run uWSGI:

.. code-block:: sh

   ./uwsgi config.ini

Now connect to port 9090 and you should see the app response.

As you can note we have manually added uwsgi.jar and the Leiningen standalone jar (it includes the whole Clojure distribution) to our classpath.

Obviously if you do not want to use Leiningen, just add the Clojure jar to your classpath.

The ``clojure-load`` option loads a Clojure script in the JVM (very similar to what ``jvm-class`` do with the basic jvm plugin).

The ``ring-app`` option specify the class/namespace in which to search for the ring function entry point.

In our case the function is in the 'myapp' namespace and it is called 'handler' (you can understand that the syntax is namespace:function)

Pay attention to the modifier configuration. The JVM plugin registers itself as 8, while Ring registers itself as modifier 2 #1, yielding an effective configuration of "modifier1 8, modifier2 1".

Using Leiningen
***************

Leiningen is a great tool for managing Clojure projects. If you use Clojure, you are very probably a Leiningen user.

One of the great advantages of Leiningen is the easy generation of a single JAR distribution. That means you can deploy a whole app
with a single file.

Let's create a new "helloworld" Ring application with the ``lein`` command.

.. code-block:: sh

   lein new helloworld

Move it to the just created 'helloworld' directory and edit the project.clj file

.. code-block:: Clojure

   (defproject helloworld "0.1.0-SNAPSHOT"
  :description "FIXME: write description"
  :url "http://example.com/FIXME"
  :license {:name "Eclipse Public License"
            :url "http://www.eclipse.org/legal/epl-v10.html"}
  :dependencies [[org.Clojure/Clojure "1.4.0"]])

We want to add the ``ring-core`` package to our dependencies (it contains a set of classes/modules to simplify the writing of ring apps) and obviously we need to change the description and URL:

.. code-block:: Clojure

   (defproject helloworld "0.1.0-SNAPSHOT"
  :description "My second uWSGI ring app"
  :url "https://uwsgi-docs.readthedocs.io/en/latest/Ring.html"
  :license {:name "Eclipse Public License"
            :url "http://www.eclipse.org/legal/epl-v10.html"}
  :dependencies [[org.Clojure/Clojure "1.4.0"] [ring/ring-core "1.2.0-beta1"]])

Now save it and run...

.. code-block:: sh

   lein repl

This will install all of the jars we need and move us to the Clojure console (just exit from it for now).

Now we want to write our Ring app, just edit the file src/helloworld/core.clj and place the following content in it:

.. code-block:: Clojure

   (ns helloworld.core
    (:use ring.util.response))

   (defn handler [request]
    (-> (response "Hello World")
    (content-type "text/plain")))


Then re-edit project.clj to instruct Leiningen on which namespaces to build:

.. code-block:: Clojure

   (defproject helloworld "0.1.0-SNAPSHOT"
  :description "FIXME: write description"
  :url "http://example.com/FIXME"
  :license {:name "Eclipse Public License"
            :url "http://www.eclipse.org/legal/epl-v10.html"}

  :aot [helloworld.core]

  :dependencies [[org.Clojure/Clojure "1.4.0"] [ring/ring-core "1.2.0-beta1"]])

As you can see we have added helloworld.core in the ``:aot`` keyword.

Now let's compile our code:

.. code-block:: sh

   lein compile

And build the full jar (the uberjar):

.. code-block:: sh

   lein uberjar

If all goes well you should see a message like this at the end of the procedure:

.. code-block:: sh

   Created /home/unbit/helloworld/target/helloworld-0.1.0-SNAPSHOT-standalone.jar

Take a note of the path so we can configure uWSGI to run our application.

.. code-block:: ini

   [uwsgi]
   http = :9090
   http-modifier1 = 8
   http-modifier2 = 1

   jvm-classpath = plugins/jvm/uwsgi.jar
   jvm-classpath = /home/unbit/helloworld/target/helloworld-0.1.0-SNAPSHOT-standalone.jar

   jvm-class = helloworld/core__init

   ring-app = helloworld.core:handler

This time we do not load Clojure code, but directly a JVM class.

Pay attention: when you specify a JVM class you have to use the '/' form, not the usual dotted form.

The __init suffix is automatically added by the Clojure system when your app is compiled.

The ``ring-app`` set the entry point to the helloworld.core namespace and the function 'handler'.

We can access that namespace as we have loaded it with ``jvm-class``

Concurrency
***********

As all of the JVM plugin request handlers, multi-threading is the best way to achieve concurrency.

Threads in the JVM are really solid, do not be afraid to use them (even if you can spawn multiple processes too)

.. code-block:: ini

   [uwsgi]
   http = :9090
   http-modifier1 = 8
   http-modifier2 = 1

   jvm-classpath = plugins/jvm/uwsgi.jar
   jvm-classpath = /home/unbit/helloworld/target/helloworld-0.1.0-SNAPSHOT-standalone.jar

   jvm-class = helloworld/core__init

   ring-app = helloworld.core:handler

   master = true
   processes = 4
   threads = 8

This setup will spawn 4 uWSGI processes (workers) with 8 threads each (for a total of 32 threads).

Accessing the uWSGI api
***********************

Clojure can call native Java classes too, so it is able to access the uWSGI API exposed by the JVM plugin.

The following example shows how to call a function (written in python) via Clojure:

.. code-block:: Clojure

   (ns myapp
    (import uwsgi)
   )

   (defn handler [req]
     {:status 200
      :headers { "Content-Type" "text/html" , "Server" "uWSGI" }
      :body (str "<h1>The requested uri is " (get req :uri) "</h1>" "<h2>reverse is " (uwsgi/rpc (into-array ["" "reverse" (get req :uri)])) "</h2>" )
     }
   )

The "reverse" function has been registered from a Python module:

.. code-block:: python
 
   from uwsgidecorators import *

   @rpc('reverse')
   def contrario(arg):
       return arg[::-1]

This is the used configuration:

.. code-block:: ini

   [uwsgi]
   http = :9090
   http-modifier1 = 8
   http-modifier2 = 1 
   jvm-classpath = plugins/jvm/uwsgi.jar
   jvm-classpath = /usr/share/java/Clojure-1.4.jar
   Clojure-load = myapp.clj
   plugin = python
   import = pyrpc.py
   ring-app = myapp:handler
   master = true

Another useful feature is accessing the uwsgi cache. Remember that cache keys are string while values are bytes.

The uWSGI Ring implementation supports byte array in addition to string for the response. This is obviously a violation of the standard
but avoids you to re-encode bytes every time (but obviously you are free to do it if you like).

Notes and status
****************

* A shortcut option allowing to load compiled code and specifying the ring app would be cool.
* As with the :doc:`JWSGI` handler, all of the uWSGI performance features are automatically used (like when sending static files or buffering input)
* The plugin has been developed with the cooperation and ideas of Mingli Yuan. Thanks!
