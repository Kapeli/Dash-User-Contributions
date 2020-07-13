**************************************
Converting from Nengo 1.4 to Nengo 2.0
**************************************

On this page, we'll go over the changes between Nengo 1.4 and 2.0.
They will first be reviewed heuristically in the section Big Changes, before
being broken down practically in Changes to Common Functions

Big changes
===========

Objects instead of strings
--------------------------

In the old API each object had to be assigned it's own unique string.

In the new Nengo, you can use strings to identify objects called ``labels``,
but they are not unique. Instead, if you want to identify an object, you just
make sure to assign it a variable in your network

No Origins and Terminations
---------------------------

Previously, each object had a set of origins and terminations,
which determined how the object produced output and
accepted input, respectively.
These two things have been collapsed into a single
Connection object, which contains
the logic of the origin and termination
in one place.

Because the model is defined separately
from when it's built,
the performance advantages of having
origins and terminations can be accomplished
during the build phase of the model instead.

Only Ensembles, Nodes, Networks and Probes
------------------------------------------

Many other objects have been removed,
in order to start with a very minimal
set of objects allowing a new user to get up and running without having
to spend all the effort of memorizing a large API.

Basically:

- Anything made with neurons is an Ensemble.
- Anything not made with neurons (inputs, interfaces) are Nodes.
- Probes are how you get data out of Nodes and Ensembles after simulating.
- Networks are dumb containers
  for Ensembles, Nodes, Probes, and other Networks.

A power user can easily divide his code and stop from repeating themselves
by encapsulating code that appears in multiple places in a Network.

Model and Simulator separation
------------------------------

There is now a clear separation between
model definition and model creation/simulation.
The motivation behind this is to allow
for testing models as they are being created.
For example, you can create a model,
add a node and an ensemble,
and the create a simulator based
on that model and run it
to make sure that your node and ensemble
are doing what you think they're doing.
Then, you can continue adding new objects
to your model---this will not be reflected
in the simulator that you've already created,
but you can create a new simulator
with this updated model and run it
without having to rerun your script
from the top.
Basically, it allows for a more
iterative and interactive modelling process,
and makes it more explicit which
decisions are made manually and which
are automatically determined
when the simulator is created.
Additionally, this means that the
simulator timestep (dt) is not
defined until the simulator is created,
meaning that you can run the same model
with different timesteps to see if
there is a marked functional difference.

Changes to common functions
---------------------------

Many commonly used functions have been
simplified or changed to be more explicit.

Making ensembles
----------------

Old API example::

   nef.Network.make('A', 40, 1, mode='spike')

New API example:

.. testsetup::

   net = nengo.Network()
   net.__enter__()

.. testcode::

   A = nengo.Ensemble(40, 1, neuron_type=nengo.LIF(), label='A')

See `nengo.Ensemble` for the full API specification.

Making ensemble arrays (i.e., network arrays)
---------------------------------------------

Network arrays were very tightly coupled
with the old API. In the new API,
they have been decoupled and are just dumb containers, which
you can easily import.
The functionality should still be identical,
though the syntax has changed.

Old API::

   nef.Network.make_array(name, neurons, length, dimensions, **args)

New API:

.. testsetup::

   neurons = 1
   n_ensembles = 1
   dimensions_per_ensemble = 1
   ens_args = {}

.. testcode::

   nengo.networks.EnsembleArray(neurons, n_ensembles, dimensions_per_ensemble, **ens_args)

See `nengo.networks.EnsembleArray` for more information.

Changes to common functions
===========================

Making nodes
------------

Previously, there were several different ways
to provide input to a Nengo model:
``SimpleNode``, ``FunctionInput``, and others.
All of these use cases should be covered
by `nengo.Node`.

In the old API, you could create your own
``SimpleNode``, or create a ``FunctionInput`` with::

   nef.Network.make_input(name, values, zero_after_time)

In the new API, you create a node with:

.. testsetup::

   output = [0]

.. testcode::

   nengo.Node(output)

where ``output`` is either a constant value
(float, list, NumPy array), a function, or
``None`` when passing through values unchanged.

See `nengo.Node` for more information.

Making inputs
-------------

In the old API, inputs were defined as::

   # Piecewise example
   net.make_input("contextinput", {0.0:[0, 0.1], 0.5:[1, 0], 1.0:[0, 1]})
   # Periodic white noise
   net.make_fourier_input('fin1', base=0.1, high=10, power=0.5, seed=12)

Inputs are just nodes whose sole function are to output a function.

Many of the :doc:`examples` use function output nodes.

Terminations and Origins
------------------------

Practically, to convert from one to the other, consider this table
that uses an example ensemble called ``ens`` who's input needs to be
transformed by a two-dimensional identity function, ``[[1,0],[0,1]]``.

Nengo 1.4::

   ens.addDecodedTermination("term_name", transform=MU.I(2))

Nengo 2.0:

.. testsetup::

   ens = nengo.Ensemble(2, 2)

.. testcode::

   # first create a simple pass-through node
   term_name = nengo.Node(size_in=2, label="term_name")
   # now connect the pass-through node to the ensemble
   nengo.Connection(term_name, ens, transform=np.eye(2))

Same, thing but instead of a decoded origin, we want one that connects
directly to the ensemble's neurons.

Nengo 1.4::

   ens.addTermination("term_name", transform=MU.I(2))

Nengo 2.0:

.. testcode::

   # first create a simple pass-through node
   term_name = nengo.Node(size_in=2, label="term_name")
   # now connect the pass-through node to the ensemble neurons
   nengo.Connection(term_name, ens.neurons, transform=np.eye(2))

One more time, but with an output and no transform.

Nengo 1.4::

   ens.addDecodedOrigin("origin_name")

Nengo 2.0:

.. testcode::

   # first create a simple pass-through node
   origin_name = nengo.Node(size_in=2, label="origin_name")
   # now connect the pass-through node to the ensemble
   nengo.Connection(ens, origin_name, transform=np.eye(2))

Connecting things
-----------------

A lot of the complexity of the old API
has been pushed down to the constructors
of the connection object.
In general, old API calls of the form::

   nef.Network.connect(pre, post)

are now:

.. testsetup::

   pre = nengo.Ensemble(10, 2)
   post = nengo.Ensemble(10, 2)

.. testcode::

   nengo.Connection(pre, post)

However, there are some changes in the additional arguments.
The old API used ``weight``, ``index_pre`` and ``index_post``
as a shortcut to define ``transform``;
in the new API, only the ``transform`` can be specified.
There are many NumPy functions that make transforms
easier to specify.
Additionally, we now utilize Python's slice syntax
to route dimensions easily:

.. testcode::

   nengo.Connection(pre[0], post[1])

The keyword argument ``pstc`` has been renamed to ``synapse``.

.. testcleanup::

   net.__exit__(None, None, None)
