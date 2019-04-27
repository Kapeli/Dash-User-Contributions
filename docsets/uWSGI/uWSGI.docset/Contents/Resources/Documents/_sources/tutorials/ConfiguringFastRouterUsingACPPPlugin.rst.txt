Configuring FastRouter using a C++ plugin
=========================================

Intro
-----

This tutorial assumes that you are familiar with the usage and purpose of the uwsgi fastrouter and you are facing an edge-case (like "Darth Vader wearing a t-shirt with your face") so you have to use some kind of code-driven "configuration". The fastrouter documentation page recommends `the --fastrouter-use-code-string commandline argument of uwsgi`_ to solve such terribly complicated routing problems by executing your own code/logic for each request to decide which gateway to send it to. The official documentation (at the previous link) shows an example where a python script provides the routing logic and the doc states that you can use any uwsgi-supported language to configure the fastrouter (although my uwsgi-2.0.3 seems to have the code_string feature only in its python and ruby plugins if I'm right...). This tutorial shows you how to write and compile a C++ plugin that contains the routing logic for the fastrouter. This document can also serve a partial/basic C++ plugin tutorial.

.. _the --fastrouter-use-code-string commandline argument of uwsgi: https://uwsgi-docs.readthedocs.io/en/latest/Fastrouter.html#way-5-fastrouter-use-code-string

To make things a bit more complicated I will do the development of this plugin on windows using a cygwin environment. In case of such a simple plugin this involves only 1-2 extra steps compared to building on linux, I will comment the differences. For production I'm using "original" Debian and Ubuntu distros so my examples work there for sure.

Prerequisites
-------------

- A ready-made uwsgi-2.0.3 executable or uwsgi-2.0.3 sources to build from. In case of older uwsgi releases the uwsgi binary-only solution may not be an option as uwsgi doesn't have the --build-plugin commandline argument in older releases.
- gcc and g++ (I use version 4.8.2, and also used 4.6 in a recent project release)
- If you are on windows you need cygwin of course

Plugin sources and build configs
================================

Create a directory for your plugin somewhere in your filesystem. Note that this directory doesn't have to be inside the extracted uwsgi source directory, put it anywhere. I will refer to this directory as ``$PLUGIN_DIR`` in this tutorial. The plugin directory will contain the following things:

#) The source code of the plugin.
#) An uwsgiplugin.py file that must be located exactly in the ``$PLUGIN_DIR`` and its name must be exactly uwsgiplugin.py because the uwsgiconfig.py script looks after this file in this directory with this name (its hardcoded). The code in uwsgiplugin.py is executed by uwsgiconfig.py when you build your plugin, you can do fancy configuration things here (like code generation) but often this script just gives some compile flags and source file lists to uwsgiconfig.py.
#) Build ini file(s) to feed to uwsgiconfig.py when building our minimal uwsgi executable that is good almost only to run as a fastrouter. Of course you don't need these ini files if you are working with a pre-built uwsgi binary. Note that you can put these ini files anywhere but we need the relative/absolute path of these files when building uwsgi. I put them into the ``$PLUGIN_DIR`` just because... After building uwsgi we will use it to build and load our plugin that provides the routing logic of our fastrouter. On cygwin we have 2 ini files because we need an extra ini file to build libuwsgi.a (that isn't needed in case of linux builds).

Here is the structure and contents of my ``$PLUGIN_DIR``:

::

    $PLUGIN_DIR
        my_router_config.cc
        uwsgiplugin.py
        my_uwsgi.ini
        my_uwsgi_lib.ini (needed only on cygwin)

*my_router_config.cc:* The extension is .cc because uwsgiconfig.py doesn't recognise the .cpp extension. In case of .cpp ext (and other unhandled extensions) uwsgiconfig.py appends an additional (default) .c extension and tries to compile the source as C (but it fails as it doesn't find the my_router_config.cc.c source file).

.. code:: c++

    #include "uwsgi.h"
    #include <stdlib.h>
    #include <stdio.h>

    struct SOptions
    {
        char* config_file;
    } options;

    struct uwsgi_option options_cfg[] =
    {
        {(char*)"my-router-cfg-file", required_argument, 0, (char*)"config file for my fastrouter logic", uwsgi_opt_set_str, &options.config_file, 0},
        { 0 }
    };

    void Deinit()
    {
        uwsgi_log("+++++ %s\n", __FUNCTION__);
        // TODO: Put your cleanup code here.
    }

    int Init()
    {
        uwsgi_log("+++++ %s config_file=%s\n", __FUNCTION__, options.config_file);
        if (!options.config_file)
        {
            uwsgi_log("The --my-router-cfg-file commandline argument is mandatory!\n");
            exit(1);
        }
        FILE* f = fopen(options.config_file, "r");
        if (!f)
        {
            uwsgi_log("Error opening config file: %s\n", options.config_file);
            exit(1);
        }
        // TODO: parse options
        fclose(f);
        // TODO: init you plugin
        atexit(Deinit);
        return UWSGI_OK;
    }

    char* CodeString(char *id, char *code, char *function, char *key, uint16_t keylen)
    {
        uwsgi_log("+++++ %s id=%s code=%s function=%s key=%.*s\n", __FUNCTION__, id, code, function, keylen, key);
        // TODO: Return a pointer to the gateway address string.
        // The pointer must be valid until the next call to this function.
        static char addr[] = "127.0.0.1:8001";
        return addr;
    }

    int Request(struct wsgi_request *wsgi_req)
    {
        // This dummy function should never be called in the fastrouter...
        uwsgi_log("+++++ %s\n", __FUNCTION__);
        return -1;
    }

    struct SPluginConfig : public uwsgi_plugin
    {
        SPluginConfig()
        {
            memset(this, 0, sizeof(*this));
            name = "my_router_config";
            modifier1 = 251;
            init = Init;
            code_string = CodeString;
            // Plugins with a request function pointer are "request handler plugins" while
            // the rest of the plugins are "generic plugins". We install a dummy request
            // handler function just to force uwsgi to put this plugin into the request
            // handler plugin table because the --fastrouter-use-code-string commandline
            // argument that we exploit searches among the request handler plugins.
            // Again, this request handler function is just a dummy function that should
            // never be called in the fastrouter...
            request = Request;
            // Optional, set this only if you want commandline arguments from uwsgi.
            options = options_cfg;
        }
    };

    // Note that the name of this exported symbol must be the name of your plugin
    // postfixed with "_plugin" otherwise it doesn't work. If you build this
    // as an external plugin then the name of the shared object must also be
    // the same (with .so extension) but when you load the external plugin with
    // uwsgi you have to specify only the name of the plugin without the "_plugin"
    // postfix for the --plugin commandline parameter.
    //
    // - plugin name: "my_router_config"
    // - name of the exported symbol that points to the plugin config: "my_router_config_plugin"
    // - name of the shared object file in case of external plugin: "my_router_config_plugin.so"
    // - uwsgi cmdline parameter when loading the external plugin: --plugin my_router_config
    SPluginConfig my_router_config_plugin __attribute__((visibility("default")));

*uwsgiplugin.py:*

.. code:: python

    NAME='my_router_config'

    CFLAGS = []
    LDFLAGS = []
    LIBS = ['-lstdc++']
    GCC_LIST = ['my_router_config.cc']

*my_uwsgi.ini:*

::

    [uwsgi]
    inherit = minimal
    main_plugin = corerouter, fastrouter

*my_uwsgi_lib.ini:* (needed only on cygwin)

::

    [uwsgi]
    inherit = minimal
    main_plugin = corerouter, fastrouter
    as_shared_library = true

The my_uwsgi_lib.ini file is needed only on cygwin and it is a copy of my_uwsgi.ini with an extra line appended: ``as_shared_library = true``. You need neither my_uwsgi.ini nor my_uwsgi_lib.ini if you are working with a pre-built new uwsgi binary that supports the --build-plugin commandline parameter but only uwsgi version ~2 and newer have it.

Building uwsgi (or uwsgi.exe and libuwsgi.a on cygwin)
------------------------------------------------------

Of course you can skip this step if you are working with a new uwsgi binary. Otherwise download the uwsgi source (uwsgi-2.0.3.tar.gz in my case) and extract it, then enter the extracted source folder.

.. code:: bash

    ~$ wget https://projects.unbit.it/downloads/uwsgi-2.0.3.tar.gz
    ~$ tar xvf uwsgi-2.0.3.tar.gz
    ~$ cd uwsgi-2.0.3
    ~/uwsgi-2.0.3$

The "build system" of uwsgi is a python script called uwsgiconfig.py and when you run it your shell's current directory must be the extracted uwsgi source dir (where the uwsgiconfig.py is located). From now all commands will be executed in this source directory.

It is possible to build uwsgi with different configurations and its plugins can be built as either embedded plugins or external shared objects. Building external plugins for newer uwsgi releases can be done anytime and you need only an uwsgi binary and the compilers, there is no need for the uwsgi sources. (On cygwin you also need a libuwsgi.a lib file that can be built with a trick). On cygwin we first build libuwsgi.a but on linux you simply skip this step. Then we have to build the uwsgi binary (uwsgi on linux, uwsgi.exe on cygwin).

The uwsgiconfig.py script builds uwsgi on multiple threads. For some reason on my cygwin this multithreaded building fails (terminates without any error messages) and I worked this around by setting the CPUCOUNT env var to 1. You may, or may not need this workaround on cygwin... On linux multithreading build works fine. Now let's build the cygwin specific libuwsgi.a library:

.. code:: bash

    ~/uwsgi-2.0.3$ export CPUCOUNT=1
    ~/uwsgi-2.0.3$ python uwsgiconfig.py --build $PLUGIN_DIR/my_uwsgi_lib.ini
    ~/uwsgi-2.0.3$ mv uwsgi.exe libuwsgi.a

Note that these steps are needed only on cygwin. Now let's build uwsgi:

.. code:: bash

    ~/uwsgi-2.0.3$ python uwsgiconfig.py --build $PLUGIN_DIR/my_uwsgi.ini

The above command produces uwsgi on linux and uwsgi.exe on cygwin. We have used custom ini files to build a minimal uwsgi that serves only as a fastrouter that loads our fastrouter logic plugin. The use of this ini file results in an uwsgi that doesn't have dependencies on libs like ssl, pcre and it includes only the bare minimum set of uwsgi plugins needed for the fastrouter. From now you don't need the uwsgi sources (you can even delete them if you want). The only things we have to keep is the uwsgi binary (and libuwsgi.a on cygwin) because building an external uwsgi plugin can be done by running uwsgi with the --build-plugin parameter and the uwsgi binary has an embedded copies of the uwsgiconfig.py and uwsgi.h files needed for a plugin build.

Building our plugin:
--------------------

.. code:: bash

    ~/uwsgi-2.0.3$ ./uwsgi --build-plugin $PLUGIN_DIR

Now if you are lucky you have both the uwsgi binary and the my_router_config_plugin.so plugin in the current directory. Building the plugin by executing the uwsgi binary is very useful because this way it automatically uses the same uwsgiconfig.py and uwsgi.h files and the same CFLAGS that were used to build the uwsgi binary itself. Unfortunately older uwsgi releases don't have the --build-plugin commandline parameter and in that case you have to build the plugin with the uwsgiconfig.py script:

.. code:: bash

    ~/uwsgi-2.0.3$ python uwsgiconfig.py --plugin $PLUGIN_DIR

If you have a newer uwsgi that supports the --build-plugin option then I recommend using that to build your plugin.

Using the newly built uwsgi and the plugin as a fastrouter
----------------------------------------------------------

I assume that you more or less know about the usage/purpose of uwsgi fastrouter so I only show you how to start and parametrize uwsgi with our newly built plugin:

.. code:: bash

    ~/uwsgi-2.0.3$ ./uwsgi --master --fastrouter 127.0.0.1:9000 --fastrouter-use-code-string 251:: --plugin my_router_config --my-router-cfg-file my_config.cfg

The above command starts the fastrouter that listens on loopback 9000 for incoming requests and the --fastrouter-use-code-string commandline parameter instructs the fastrouter to ask plugin modifer=251 (our plugin) for the target gateway for each incoming request. I think the --plugin and --my-router-cfg-file commandline arguments speak for themselves...

The extra argument of the --fastrouter-use-code-string is "251::". This is basically 3 strings separated by two ':' characters but our plugin doesn't need (ignores) the second and third string so I provided there empty strings. If you take a look at the linked Darth Vader example it solves the problem using the python plugin that actually utilizes these strings: `the --fastrouter-use-code-string commandline argument of uwsgi`_

Note that I've chosen 251 as the modifier of my plugin because based on my research modifier 1 has a lot to do with `The uwsgi Protocol`_ and moreover if you take a look at the plugins/example or plugins/cplusplus example plugins in the uwsgi source dir then you will see that those are using modifier1=250 and 251 seems to be a free id. Note that I've also tried 0 as the modifier1 that is the default modifier1 used by uwsgi and its very first plugin: the python plugin. This seems to work and it seems that this registers our plugin with modifier1=0 by "overriding the python plugin" but I wanted to be polite so I've chosen modifier=251.

.. _The uwsgi Protocol: https://uwsgi-docs.readthedocs.io/en/latest/Protocol.html

Programming the routing logic in our plugin
===========================================

We started the fastrouter with the "--fastrouter 127.0.0.1:9000 --fastrouter-use-code-string 251::" commandline arguments so it will be listening on loopback port 9000 for incoming requests and it will ask plugin modifier1=251 (our plugin) for the route for each request. I will use nginx to bomb requests on port 9000 of the fastrouter. Here is the location block from my nginx config:

::

    location /test {
        include         uwsgi_params;
        uwsgi_pass      127.0.0.1:9000;
        uwsgi_param     UWSGI_FASTROUTER_KEY    $request_uri;
    }

So nginx will route all requests coming to url path /test to the fastrouter by setting UWSGI_FASTROUTER_KEY (basically a "cgi variable") to a user defined string. UWSGI_FASTROUTER_KEY can be anything, you have put something into it that you can use in your plugin to decide where (which gateway) to send the request. In this case I've decided to send the $request_uri to my plugin but you can really put there anything you want. If you don't specify the UWSGI_FASTROUTER_KEY in the nginx config then the fastrouter will use something else instead of it as the fastrouter key (but I think specifying the UWSGI_FASTROUTER_KEY is highly recommended), more on that in the `Notes section of the fastrouter docs`_.

.. _Notes section of the fastrouter docs: https://uwsgi-docs.readthedocs.io/en/latest/Fastrouter.html#notes

With the above fastrouter + nginx config when the fastrouter receives a request from nginx it calls the ``CodeString()`` function of our plugin to ask for the gateway address to use for that request.

.. code:: c++

    char* CodeString(char *id, char *code, char *function, char *key, uint16_t keylen);

When the fastrouter calls your ``CodeString()`` function the values of the function parameters are the following:

- id: "uwsgi_fastrouter"
- code, function: We used the --fastrouter-use-code-string commandline parameter to pass 3 strings to uwsgi: "251", "", and "" with the "251::" argument. The code and function parameters are set to the second and third (empty) strings. You can of course specify something else instead of "251::" to pass something else as the code and function parameters.
- key, keylen: Here you receive the value of the UWSGI_FASTROUTER_KEY you specify in nginx. This is basically the useful stuff on which you can base your routing decisions.

The function must return with a pointer to a string that contains the gateway address, for example: "127.0.0.1:8001". On that gateway there must be another uwsgi instance listening on an uwsgi protocolled socket. The pointed string must be valid until the next call to the ``CodeString`` function. This is usually critical only if you are using extra threads in your plugin because otherwise the fastrouter itself is single threaded async stuff.

Victory!!!
==========

We have reached the end of the tutorial. Now you know how to handle in C/C++ a complex routing problem where Darth Vader wears a t-shirt with your face and you have also learnt how to build a C++ plugin using the uwsgi build system.
