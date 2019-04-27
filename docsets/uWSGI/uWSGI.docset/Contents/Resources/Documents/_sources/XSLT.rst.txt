The XSLT plugin
===============

Since uWSGI 1.9.1 a new plugin named "xslt" is available, implementing XML Stylesheet Transformation both as request handler and routing instruction.

To successfully apply a transformation you need a 'doc' (an XML document) and a stylesheet (the XSLT file).

Additionally you can apply global params and set a specific content type (by default the generated output is set as text/html).

The request handler
*******************

Modifier1 23 has been assigned to the XSLT request handler.

The document path is created appending the ``PATH_INFO`` to the ``DOCUMENT_ROOT``.

The stylesheet path is created following these steps:

* If a specific CGI variable is set (via ``--xslt-var``) it will be used as the stylesheet path.
* If a file named like the document plus a specific extension (by default ``.xsl`` and ``.xslt`` are searched) exists it will be used as the stylesheet path.
* Finally a series of static XSLT files (specified with ``--xslt-stylesheet``) is tried.

Examples:

.. code-block:: sh

   uwsgi --http-socket :9090 --http-socket-modifier1 23 --xslt-ext .bar

If /foo.xml is requested (and the file exists) ``DOCUMENT_ROOT``+``foo.xml.bar`` will be searched as the xslt file.

.. code-block:: sh

   uwsgi --http-socket :9090 --http-socket-modifier1 23 --xslt-stylesheet /var/www/myfile1.xslt --xslt-stylesheet /var/www/myfile2.xslt

If /foo.xml is requested (and the file exists) ``/var/www/myfile1.xslt`` will be tried. If it does not exist, ``/var/www/myfile2.xslt`` will be tried instead.

.. code-block:: sh

   uwsgi --http-socket :9090 --http-socket-modifier1 23 --xslt-var UWSGI_XSLT

If /foo.xml is requested (and the file exists), the content of the ``UWSGI_XSLT`` variable (you can set it from your webserver) is used as the stylesheet path.

If a ``QUERY_STRING`` is available, its items will be passed as global parameters to the stylesheet.

As an example if you request ``/foo.xml?foo=bar&test=uwsgi``, "foo" (as "bar" and "test" (as "uwsgi") will be passed as global variables:

.. code-block:: xml

   <xsl:value-of select="$foo"/>
   <xsl:value-of select="$test"/>

The routing instruction
***********************

The plugin registers itself as internal routing instruction named "xslt". It is probably a lot more versatile then the request plugin.

Its syntax is pretty simple:

.. code-block:: ini

   [uwsgi]
   plugin = xslt
   route = ^/foo xslt:doc=${DOCUMENT_ROOT}/${PATH_INFO}.xml,stylesheet=/var/www/myfunction.xslt,content_type=text/html,params=foo=bar&test=unbit

This will apply the ``/var/www/myfunction.xslt`` transformation to ``foo.xml`` and will return it as ``text/html``.

The only required parameters for the routing instruction are ``doc`` and ``stylesheet``.
