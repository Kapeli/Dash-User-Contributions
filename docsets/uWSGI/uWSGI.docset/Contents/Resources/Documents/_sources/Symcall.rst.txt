The Symcall plugin
==================

The symcall plugin (modifier 18) is a convenience plugin allowing you to write native uWSGI request handlers without the need of developing a full uWSGI plugin.

You tell it which symbol to load on startup and then it will run it at every request.

.. note::

   The "symcall" plugin is built-in by default in standard build profiles.

Step 1: preparing the environment
*********************************

The uWSGI binary by itself allows you to develop plugins and libraries without the need of external development packages or headers.

The first step is getting the ``uwsgi.h`` C/C++ header:

.. code-block:: sh

   uwsgi --dot-h > uwsgi.h
   
Now, in the current directory, we have a fresh uwsgi.h ready to be included.

Step 2: our first request handler:
**********************************

Our C handler will print the REMOTE_ADDR value with a couple of HTTP headers.

(call it mysym.c or whatever you want/need)

.. code-block:: c

   #include "uwsgi.h"

   int mysym_function(struct wsgi_request *wsgi_req) {
   
        // read request variables
        if (uwsgi_parse_vars(wsgi_req)) {
                return -1;
        }
        
        // get REMOTE_ADDR
        uint16_t vlen = 0;
        char *v = uwsgi_get_var(wsgi_req, "REMOTE_ADDR", 11, &vlen);
        
        // send status
        if (uwsgi_response_prepare_headers(wsgi_req, "200 OK", 6)) return -1;
        // send content_type
        if (uwsgi_response_add_content_type(wsgi_req, "text/plain", 10)) return -1;
        // send a custom header
        if (uwsgi_response_add_header(wsgi_req, "Foo", 3, "Bar", 3)) return -1;
        
        // send the body
        if (uwsgi_response_write_body_do(wsgi_req, v, vlen)) return -1;
        
        return UWSGI_OK;
   }

Step 3: building our code as a shared library
*********************************************

The uwsgi.h file is an ifdef hell (so it's probably better not to look at it too closely).

Fortunately the uwsgi binary exposes all of the required CFLAGS via the --cflags option.

We can build our library in one shot:

.. code-block:: c

   gcc -fPIC -shared -o mysym.so `uwsgi --cflags` mysym.c

you now have the mysym.so library ready to be loaded in uWSGI

Final step: map the symcall plugin to the ``mysym_function`` symbol
*******************************************************************

.. code-block:: sh

   uwsgi --dlopen ./mysym.so --symcall mysym_function --http-socket :9090 --http-socket-modifier1 18
   
With ``--dlopen`` we load a shared library in the uWSGI process address space.

The ``--symcall`` option allows us to specify which symbol to call when modifier1 18 is in place

We bind the instance to HTTP socket 9090 forcing modifier1 18.


Hooks and symcall unleashed: a TCL handler
******************************************

We want to write a request handler running the following TCL script (foo.tcl) every time:

.. code-block:: tcl

   # call it foo.tcl
   proc request_handler { remote_addr path_info query_string } {
        set upper_pathinfo [string toupper $path_info]
        return "Hello $remote_addr $upper_pathinfo $query_string"
   }
   
   
We will define a function for initializing the TCL interpreter and parsing the script. This function will be called on startup soon after privileges drop.

Finally we define the request handler invoking the TCL proc and passign args to it

.. code-block:: c


   #include <tcl.h>
   #include "uwsgi.h"

   // global interpreter
   static Tcl_Interp *tcl_interp;

   // the init function
   void ourtcl_init() {
        // create the TCL interpreter
        tcl_interp = Tcl_CreateInterp() ;
        if (!tcl_interp) {
                uwsgi_log("unable to initialize TCL interpreter\n");
                exit(1);
        }

        // initialize the interpreter
        if (Tcl_Init(tcl_interp) != TCL_OK) {
                uwsgi_log("Tcl_Init error: %s\n", Tcl_GetStringResult(tcl_interp));
                exit(1);
        }

        // parse foo.tcl
        if (Tcl_EvalFile(tcl_interp, "foo.tcl") != TCL_OK) {
                uwsgi_log("Tcl_EvalFile error: %s\n", Tcl_GetStringResult(tcl_interp));
                exit(1);
        }

        uwsgi_log("TCL engine initialized");
   }

   // the request handler
   int ourtcl_handler(struct wsgi_request *wsgi_req) {

        // get request vars
        if (uwsgi_parse_vars(wsgi_req)) return -1;

        Tcl_Obj *objv[4];
        // the proc name
        objv[0] = Tcl_NewStringObj("request_handler", -1);
        // REMOTE_ADDR
        objv[1] = Tcl_NewStringObj(wsgi_req->remote_addr, wsgi_req->remote_addr_len);
        // PATH_INFO
        objv[2] = Tcl_NewStringObj(wsgi_req->path_info, wsgi_req->path_info_len);
        // QUERY_STRING
        objv[3] = Tcl_NewStringObj(wsgi_req->query_string, wsgi_req->query_string_len);

        // call the proc
        if (Tcl_EvalObjv(tcl_interp, 4, objv, TCL_EVAL_GLOBAL) != TCL_OK) {
                // ERROR, report it to the browser
                if (uwsgi_response_prepare_headers(wsgi_req, "500 Internal Server Error", 25)) return -1;
                if (uwsgi_response_add_content_type(wsgi_req, "text/plain", 10)) return -1;
                char *body = (char *) Tcl_GetStringResult(tcl_interp);
                if (uwsgi_response_write_body_do(wsgi_req, body, strlen(body))) return -1;
                return UWSGI_OK;
        }

        // all fine
        if (uwsgi_response_prepare_headers(wsgi_req, "200 OK", 6)) return -1;
        if (uwsgi_response_add_content_type(wsgi_req, "text/plain", 10)) return -1;

        // write the result
        char *body = (char *) Tcl_GetStringResult(tcl_interp);
        if (uwsgi_response_write_body_do(wsgi_req, body, strlen(body))) return -1;
        return UWSGI_OK;
   }

   
You can build it with:

.. code-block:: sh

   gcc -fPIC -shared -o ourtcl.so `./uwsgi/uwsgi --cflags` -I/usr/include/tcl ourtcl.c -ltcl
   
The only differences from the previous example are the -I and -l for adding the TCL headers and library.

So, let's run it with:

.. code-block:: sh

   uwsgi --dlopen ./ourtcl.so --hook-as-user call:ourtcl_init --http-socket :9090 --symcall ourtcl_handler --http-socket-modifier1 18
   
Here the only new player is ``--hook-as-user call:ourtcl_init`` invoking the specified function after privileges drop.


.. note::

   This code is not thread safe! If you want to improve this tcl library to support multithreading, best approach will be having a TCL interpreter
   for each pthread instead of a global one.
   
Considerations
**************

Since uWSGI 1.9.21, thanks to the ``--build-plugin`` option, developing uWSGI plugins has become really easy.

The symcall plugin is for tiny libraries/pieces of code, for bigger needs consider developing a full plugin.

The tcl example we have seen before is maybe the right example of "wrong" usage ;)
