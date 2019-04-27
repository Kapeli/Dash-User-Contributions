Aliasing Python modules
=======================

Having multiple version of a Python package/module/file is very common.

Manipulating PYTHONPATH or using virtualenvs are a way to use various versions without changing your code.

But hey, why not have an aliasing system that lets you arbitrarily map module names to files? That's why we have the ``pymodule-alias`` option!


Case 1 - Mapping a simple file to a virtual module
--------------------------------------------------

Let's say we have ``swissknife.py`` that contains lots of useful classes and functions.

It's imported in gazillions of places in your app. Now, we'll want to modify it, but keep the original file intact for whichever reason, and call it ``swissknife_mk2``.

Your options would be

1) to modify all of your code to import and use swissknife_mk2 instead of swissknife. Yeah, no, not's going to happen.
2) modify the first line of all your files to read ``import swissknife_mk2 as swissknife``. A lot better but you make software for money... and time is money, so why the fuck not use something more powerful?

So don't touch your files -- just remap!

.. code-block:: sh

    ./uwsgi -s :3031 -w myproject --pymodule-alias swissknife=swissknife_mk2
    # Kapow! uWSGI one-two ninja punch right there!
    # You can put the module wherever you like, too:
    ./uwsgi -s :3031 -w myproject --pymodule-alias swissknife=/mnt/floppy/KNIFEFAC/SWISSK~1.PY
    # Or hey, why not use HTTP?
    ./uwsgi -s :3031 -w myproject --pymodule-alias swissknife=http://uwsgi.it/modules/swissknife_extreme.py

You can specify multiple ``pymodule-alias`` directives.

.. code-block:: yaml

    uwsgi:
      socket: :3031
      module: myproject
      pymodule-alias: funnymodule=/opt/foo/experimentalfunnymodule.py
      pymodule-alias: uglymodule=/opt/foo/experimentaluglymodule.py


Case 2 - mapping a packages to directories
------------------------------------------

You have this shiny, beautiful Django project and something occurs to you: Would it work with Django trunk? On to set up a new virtualenv... nah. Let's just use ``pymodule-alias``!

.. code-block:: py

  ./uwsgi -s :3031 -w django_uwsgi --pymodule-alias django=django-trunk/django


Case 3 - override specific submodules
-------------------------------------

You have a Werkzeug project where you want to override - for whichever reason - ``werkzeug.test_app`` with one of your own devising. Easy, of course!

.. code-block:: python

    ./uwsgi -s :3031 -w werkzeug.testapp:test_app() --pymodule-alias werkzeug.testapp=mytestapp