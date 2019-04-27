Pump support
============

.. note:: Pump is not a PEP nor a standard.

Pump_ is a new project aiming at a "better" WSGI.

An example Pump app, for your convenience:

.. code-block:: python

    def app(req):
        return {
            "status": 200,
            "headers": {"content_type": "text/html"},
            "body": "<h1>Hello!</h1>"
        }

To load a Pump app simply use the ``pump`` option to declare the callable.

.. code-block:: sh

    uwsgi --http-socket :8080 -M -p 4 --pump myapp:app

``myapp`` is the name of the module (that must be importable!) and app is the callable. The callable part is optional -- by default uWSGI will search for a callable named 'application'.

.. _Pump: http://adeel.github.com/pump/