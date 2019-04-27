Web server integration
======================

uWSGI supports several methods of integrating with web servers. It is also capable of serving HTTP requests by itself.

Nginx
------------

.. seealso:: :doc:`Nginx`

The uWSGI module is included in the official Nginx distribution since version 0.8.40. A version supporting Nginx 0.7.x  is maintained in the uWSGI package.

This is a stable handler commercially supported by Unbit.


Apache
------

.. seealso:: :doc:`Apache`

The Apache2 `mod_uwsgi` module was the first web server integration module developed for uWSGI.
It is stable but could be better integrated with the Apache API.

It is commercially supported by Unbit.

Since uWSGI 0.9.6-dev a second Apache2 module called `mod_Ruwsgi` is included. It's more Apache API friendly. *mod_Ruwsgi is not commercially supported by Unbit.*

During the 1.2 development cycle, another module called `mod_proxy_uwsgi` has been added. In the near future this should be the best choice for Apache based deployments.


Lighttpd (Experimental)
-----------------------

This module is the latest developed, but its inclusion in the official Lighttpd distribution has been rejected, as the main author considers the :doc:`uwsgi protocol<Protocol>` a "reinventing the wheel" technology while suggesting a FastCGI approach. We respect this position. The module will continue to reside in the uWSGI source tree, but it is currently unmaintained.

There is currently no commercial support for this handler. We consider this module "experimental".


Twisted
-------

This is a "commodity" handler, useful mainly for testing applications without installing a full web server. If you want to develop an uWSGI server, look at this module. :doc:`Twisted`.


Tomcat
------

The included servlet can be used to forward requests from Tomcat to the uWSGI server.
It is stable, but currently lacks documentation.

There is currently no commercial support for this handler.


CGI
---

The CGI handlers are for "lazy" installations. Their use in production environments is discouraged.


Cherokee (Obsolete)
-------------------

.. seealso:: :doc:`Cherokee`

The Cherokee webserver officially supports uWSGI.
Cherokee is fast and lightweight, has a beautiful admin interface and a great community.
Their support for uWSGI has been awesome since the beginning and we recommend its use in most situations.
The userbase of the Cherokee uWSGI handler is probably the biggest of all. The Cherokee uWSGI handler is commercially supported by Unbit.


Mongrel2 (Obsolete)
--------

.. seealso:: :doc:`Mongrel2`


Support for the `Mongrel2 Project <http://mongrel2.org/>`_ has been available since 0.9.8-dev via the :doc:`ZeroMQ` protocol plugin.

In our tests Mongrel2 survived practically all of the loads we sent.

Very good and solid project. Try it :) 
