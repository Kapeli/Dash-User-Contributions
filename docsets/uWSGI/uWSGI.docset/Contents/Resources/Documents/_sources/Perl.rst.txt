uWSGI Perl support (PSGI)
=========================

:term:`PSGI` is the equivalent of :term:`WSGI` in the Perl world.

* http://plackperl.org/
* https://github.com/plack/psgi-specs/blob/master/PSGI.pod

The PSGI plugin is officially supported and has an officially assigned uwsgi modifier, ``5``. So as usual, when you're in the business of dispatching requests to Perl apps, set the ``modifier1`` value to 5 in your web server configuration.

Compiling the PSGI plugin
-------------------------

You can build a PSGI-only uWSGI server using the supplied :file:`buildconf/psgi.ini` file. Make sure that 
the ``ExtUtils::Embed`` module and its prerequisites are installed before building the PSGI plugin.

.. code-block:: sh

    python uwsgiconfig.py --build psgi
    # or compile it as a plugin...
    python uwsgiconfig.py --plugin plugins/psgi
    # and if you have not used the default configuration
    # to build the uWSGI core, you have to pass
    # the configuration name you used while doing that:
    python uwsgiconfig.py --plugin plugins/psgi core
    
or (as always) you can use the network installer:

.. code-block:: sh

    curl http://uwsgi.it/install | bash -s psgi /tmp/uwsgi
    
to have a single-file uwsgi binary with perl support in /tmp/uwsgi

Usage
-----

There is only one option exported by the plugin: ``psgi <app>``

You can simply load applications using

.. code-block:: sh

    ./uwsgi -s :3031 -M -p 4 --psgi myapp.psgi -m
    # or when compiled as a plugin,
    ./uwsgi --plugins psgi -s :3031 -M -p 4 --psgi myapp.psgi -m


Tested PSGI frameworks/applications
-----------------------------------

The following frameworks/apps have been tested with uWSGI:

* MojoMojo_
* Mojolicious_
* Mojolicious+perlbrew+uWSGI+nginx_ install bundle

.. _MojoMojo: http://mojomojo.org/
.. _Mojolicious: http://mojolicio.us/
.. _Mojolicious+perlbrew+uWSGI+nginx: https://github.com/kraih/mojo/wiki/nginx-&-uwsgi(psgi)-&-perlbrew-&-mojolicious

Multi-app support
-----------------

You can load multiple almost-isolated apps in the same uWSGI process using the ``mount`` option or using the ``UWSGI_SCRIPT``/``UWSGI_FILE`` request variables.

.. code-block:: ini

    [uwsgi]
    
    mount = app1=foo1.pl
    mount = app2=foo2.psgi
    mount = app3=foo3.pl

.. code-block:: nginx

    server {
      server_name example1.com;
      location / {
        include uwsgi_params;
        uwsgi_pass 127.0.0.1:3031;
        uwsgi_param UWSGI_APPID app1;
        uwsgi_param UWSGI_SCRIPT foo1.pl;
        uwsgi_modifier1 5;
      }
    }
    
    server {
      server_name example2.com;
      location / {
        include uwsgi_params;
        uwsgi_pass 127.0.0.1:3031;
        uwsgi_param UWSGI_APPID app2;
        uwsgi_param UWSGI_SCRIPT foo2.psgi;
        uwsgi_modifier1 5;
      }
    }
    
    server {
      server_name example3.com;
      location / {
        include uwsgi_params;
        uwsgi_pass 127.0.0.1:3031;
        uwsgi_param UWSGI_APPID app3;
        uwsgi_param UWSGI_SCRIPT foo3.pl;
        uwsgi_modifier1 5;
      }
    }

The auto reloader (from uWSGI 1.9.18)
-------------------------------------

The option --perl-auto-reload <n> allows you to instruct uWSGI to monitor every single module imported by the perl vm.

Whenever one of the module changes, the whole instance will be (gracefully) reloaded.

The monitor works by iterating over %INC after a request is served and the specified number of seconds (from the last run) is elapsed (this number of seconds is the value of the option)

This could look sub-optimal (you wil get the new content starting from from the following request) but it is the more solid (and safe) approach for the way perl works.

If you want to skip specific files from the monitoring, just add them with --perl-auto-reload-ignore

Remember that always modules in %INC are scanned, if you want to monitor your .psgi files, you need to specify them using the classic --touch-reload option

Notes
-----

* Async support should work out-of-the-box.
* Threads are supported on ithreads-enabled perl builds. For each app, a new interpreter will be created for each thread. This shouldn't be too different from a simple multi-process fork()-based subsystem. 
* There are currently no known memory leaks.


Real world example, `HTML::Mason`
---------------------------------

1. Install the HTML::Mason PSGI handler from CPAN and create a directory for your site.
   
   .. code-block:: sh
      
      cpan install HTML::Mason::PSGIHandler
      mkdir mason

2. Create ``mason/index.html``:

   .. code-block:: html
   
       % my $noun = 'World';
       % my $ua = $r->headers_in;
       % foreach my $hh (keys %{$ua}) {
        <% $hh %><br/>
       % }
       Hello <% $noun %>!<br/>
       How are ya?<br/>
       Request <% $r->method %> <% $r->uri %><br/>

3. Create the PSGI file (``mason.psgi``):

   .. code-block:: perl
   
       use HTML::Mason::PSGIHandler;
       
       my $h = HTML::Mason::PSGIHandler->new(
    	      comp_root => "/Users/serena/uwsgi/mason", # required
       );
       
       my $handler = sub {
    	      my $env = shift;
    	      $h->handle_psgi($env);
       };
    
   Pay attention to ``comp_root``, it must be an absolute path!

4. Now run uWSGI:

   .. code-block:: sh

    ./uwsgi -s :3031 -M -p 8 --psgi mason.psgi -m

5. Then go to ``/index.html`` with your browser.
