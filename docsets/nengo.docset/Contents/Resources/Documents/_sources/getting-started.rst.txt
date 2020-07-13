***************
Getting started
***************

Installation
============

To install Nengo, we recommend using ``pip``.

.. code:: bash

   pip install nengo

``pip`` will do its best to install
all of Nengo's requirements when it installs Nengo.
However, if anything goes wrong during this process,
you can install Nengo's requirements manually
before doing ``pip install nengo`` again.

Installing NumPy
----------------

Nengo's only required dependency is NumPy,
and we recommend that you install it first.
The best way to install NumPy depends
on several factors, such as your operating system.
Briefly, what we have found to work best
on each operating system is:

- Windows: Use Anaconda_ or
  the `official installer <https://www.python.org/downloads/>`_ and
  unofficial binaries (www.lfd.uci.edu/~gohlke/pythonlibs/)
- Mac OS X: Use Anaconda_ or Homebrew_
- Linux: Use a package manager or install from source

For more options, see
`SciPy.org's installation page <https://www.scipy.org/install.html>`_.
For our recommended options, read on.

Anaconda
^^^^^^^^

If you're new to Python and just want to get up and running,
Anaconda_ is the best way to get started.
Anaconda provides an all-in-one solution
that will install Python, NumPy,
and other optional Nengo dependencies.
It works on all operating systems (Windows, Mac, Linux)
and does not require administrator privileges.
It includes GUI tools,
as well as a robust command line tool, ``conda``,
for managing your Python installation.

Package managers
^^^^^^^^^^^^^^^^

If you are comfortable with the command line,
operating systems other than Windows
have a package manager that can install Python and NumPy.

- **Mac OS X:** Homebrew_ has excellent Python support.
  After installing Homebrew, ``brew install python`` and ``pip install numpy``.
- **Linux:** Linux distributions come with a package manager
  capable of installing Python and NumPy.
  In Debian, Ubuntu, and other distributions with ``apt`` use:
  ``sudo apt-get install python-numpy``.
  In Fedora and others distributions with ``yum`` use:
  ``sudo yum install python-numpy``.
  For other package managers,
  try searching the package list for ``numpy``.

From source
^^^^^^^^^^^

If speed is an issue
and you know your way around a terminal,
installing NumPy from source
is flexible and performant.
See the detailed instructions
`here <https://hunseblog.wordpress.com/2014/09/15/installing-numpy-and-openblas/>`_.

Installing other packages
-------------------------

While NumPy is the only hard dependency,
some optional Nengo features require other packages.
These can be installed either through
Anaconda, a package manager, or through
Python's own package manager, ``pip``.

- Additional decoder solvers and other speedups
  require SciPy and scikit-learn.
- Running the test suite requires
  pytest, Matplotlib, and Jupyter.
- Building the documentation requires
  Sphinx, NumPyDoc and guzzle_sphinx_theme.

These additional dependencies can be installed
through ``pip`` when installing Nengo.

.. code-block:: bash

   pip install nengo[optional]  # Additional solvers and speedups
   pip install nengo[docs]  # For building docs
   pip install nengo[tests]  # For running the test suite
   pip install nengo[all]  # All of the above

.. _Anaconda: https://www.anaconda.com/products/individual#Downloads
.. _Homebrew: https://brew.sh/

Usage
=====

Everything in a Nengo model is contained within a
`nengo.Network`. To create a new ``Network``:

.. testcode::

   import nengo
   net = nengo.Network()

Creating Nengo objects
----------------------

A Nengo object is a part of your model that represents information.
When creating a new object, you must place it within a ``with``
block in order to inform Nengo which network your object
should be placed in.

There are two objects that make up a basic Nengo model.
A `nengo.Ensemble` is a group of neurons that represents
information in the form of real valued numbers.

.. testcode::

   with net:
       my_ensemble = nengo.Ensemble(n_neurons=40, dimensions=1)

In this case, ``my_ensemble`` is made up of
40 neurons (by default, Nengo uses leaky integrate-and-fire neurons)
and it is representing a one dimensional signal.
In other words, this ensemble represents a single number.

In order to provide input to this ensemble
(to emulate some signal that exists in nature, for example)
we create a `nengo.Node`.

.. testcode::

   with net:
       my_node = nengo.Node(output=0.5)

In this case, ``my_node`` emits the number 0.5.

In most cases, however, we want more dynamic information.
We can make a `nengo.Node` using a function as output
instead of a number.

.. testcode::

   with net:
       sin_node = nengo.Node(output=np.sin)

This node will represent a sine wave.

Connecting Nengo objects
------------------------

We can connect nodes to ensembles
in order to represent that information
in the activity a group of neurons.

.. testcode::

   with net:
       nengo.Connection(my_node, my_ensemble)

This connects ``my_node`` to ``my_ensemble``,
meaning that ``my_ensemble`` will now represent
0.5 in its population of 40 neurons.

Ensembles can also be connected to other models.
When the dimensionality of the objects being
connected are different, we can use Python's
slice syntax to route information from
one node or ensemble to another.
For example:

.. testcode::

   with net:
       two_d_ensemble = nengo.Ensemble(n_neurons=80, dimensions=2)
       nengo.Connection(sin_node, two_d_ensemble[0])
       nengo.Connection(my_ensemble, two_d_ensemble[1])

This creates a new ensemble that represents
two real-valued signals.
By connecting ``sin_node`` to ``two_d_ensemble``,
its first dimension now represents a sine wave.
Its second dimensions now represents the same
value as ``my_ensemble``.

When creating connections,
we can specify a function that
will be computed across the connection.


.. testcode::

   with net:
       square = nengo.Ensemble(n_neurons=40, dimensions=1)
       nengo.Connection(my_ensemble, square, function=np.square)

Functions can be computed over multiple dimensions, as well.

.. testcode::

   def product(x):
       return x[0] * x[1]

   with net:
       product_ensemble = nengo.Ensemble(n_neurons=40, dimensions=1)
       nengo.Connection(two_d_ensemble, product_ensemble, function=product)

Probing Nengo objects
---------------------

Once you have defined the objects in your model
and how they're connected,
you can decide what data you want to collect
by probing those objects.

If we wanted to collect data from
our 2D Ensemble and the Product of those two dimensions:

.. testcode::

   with net:
       two_d_probe = nengo.Probe(two_d_ensemble, synapse=0.01)
       product_probe = nengo.Probe(product_ensemble, synapse=0.01)

The argument ``synapse`` defines the time constant
on a causal low-pass filter,
which approximates a simple synapse model.
The output of ensembles of spiking neurons
can be very noisy, so a filter is recommended.

Running an experiment
---------------------

Once a model has been constructed and we have probed
certain objects, we can run it to collect data.

To run a model, we must first build a simulator
based on the model we've defined.

.. testcode::

   sim = nengo.Simulator(net)

.. testoutput::
   :hide:

   ...

We can then run that simulator.
For example, to run our model for five seconds:

.. testcode::

   sim.run(5.0)

.. testoutput::
   :hide:

   ...

Once a simulation has been run at least once
(it can be run for additional time if desired)
the data collected can be accessed
for analysis or visualization.

.. testcode::

   print(sim.data[product_probe][-10:])

.. testoutput::
   :hide:

   ...

.. testcleanup::

   sim.close()

For more details on these objects,
see :doc:`the API documentation <frontend-api>`.

Next steps
==========

* If you're wondering how this works and you're not
  familiar with the Neural Engineering Framework,
  we recommend reading
  `this technical overview <http://compneuro.uwaterloo.ca/files/publications/stewart.2012d.pdf>`_.
* If you have some understanding of the NEF already,
  or just want to dive in headfirst,
  check out :doc:`our extensive set of examples <examples>`.
* If you want to see the real capabilities of Nengo, see our
  `publications created with the NEF and Nengo <http://compneuro.uwaterloo.ca/publications.html>`_.
