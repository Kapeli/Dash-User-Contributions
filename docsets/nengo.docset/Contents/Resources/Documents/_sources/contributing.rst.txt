*********************
Contributing to Nengo
*********************

Please read our
`general contributor guide <https://www.nengo.ai/contributing/>`_
first.
The instructions below specifically apply
to the ``nengo`` project.

.. _dev-install:

Developer installation
======================

If you want to change parts of Nengo,
you should do a developer installation,
and install all of the optional dependencies.

.. code-block:: bash

   git clone https://github.com/nengo/nengo.git
   cd nengo
   pip install -e '.[all]' --user
   pre-commit install

If you are in a virtual environment, you can omit the ``--user`` flag.

How to run unit tests
=====================

Nengo contains a large test suite, which we run with pytest_.
To run these tests do

.. code-block:: bash

   pytest --pyargs nengo

Running individual tests
------------------------

Tests in a specific test file can be run by calling
``pytest`` on that file. For example

.. code-block:: bash

   pytest nengo/tests/test_node.py

will run all the tests in ``test_node.py``.

Individual tests can be run using the ``-k EXPRESSION`` argument. Only tests
that match the given substring expression are run. For example

.. code-block:: bash

   pytest nengo/tests/test_node.py -k test_circular

will run any tests with ``test_circular`` in the name, in the file
``test_node.py``.

Plotting the results of tests
-----------------------------

Many Nengo tests have the built-in ability to plot test results
for easier debugging. To enable this feature,
pass the ``--plots`` to ``pytest``. For example

.. code-block:: bash

   pytest --plots --pyargs nengo

Plots are placed in ``nengo.simulator.plots`` in whatever directory
``pytest`` is invoked from. You can also set a different directory:

.. code-block:: bash

  pytest --plots=path/to/plots --pyargs nengo

Getting help and other options
------------------------------

Information about ``pytest`` usage
and Nengo-specific options can be found with

.. code-block:: bash

   pytest --pyargs nengo --help

Writing your own tests
----------------------

When writing your own tests, please make use of
custom Nengo `fixtures <https://docs.pytest.org/en/latest/fixture.html>`_
and `markers <https://docs.pytest.org/en/latest/example/markers.html>`_
to integrate well with existing tests.
See existing tests for examples, or consult

.. code-block:: bash

   pytest --pyargs nengo --fixtures

and

.. code-block:: bash

   pytest --pyargs nengo --markers

.. _pytest: https://docs.pytest.org/en/latest/

How to build the documentation
==============================

The documentation is built with Sphinx,
which should have been installed as part
of the :ref:`developer installation <dev-install>`.

However, one additional requirement for building the Jupyter notebooks
that we include in the documentation is Pandoc_.
If you use a package manager (e.g., Homebrew, ``apt``)
you should be able to install Pandoc_ through your package manager.
Otherwise, see
`this page <https://pandoc.org/installing.html>`_
for instructions.

After you've installed all the requirements,
run the following command from the root directory of ``nengo``
to build the documentation.
It will take a few minutes, as all examples are run
as part of the documentation building process.

.. code-block:: bash

   sphinx-build -vW docs docs/_build

Depending on your environment,
you might have to set the Jupyter kernel
used to build the examples.
To set the kernel, use this command.

.. code-block:: bash

   sphinx-build -vW docs docs/_build -D nbsphinx_kernel_name=<kernelname>

.. _Pandoc: https://pandoc.org/

Getting help
============

If you have any questions about developing Nengo
or how you can best climb the learning curve
that Nengo and ``git`` present, please head to the
`Nengo forum <https://forum.nengo.ai/>`_
and we'll do our best to help you!
