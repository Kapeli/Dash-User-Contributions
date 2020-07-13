********************
Connections in depth
********************

The `.Connection` object encapsulates different behaviors
depending on the attributes of the connection.
It can be helpful in debugging network behavior
to know what is happening under the hood
for different types of connections.

The biggest determiner of what happens
in a connection is the ``pre`` object.
When the ``pre`` object is an `.Ensemble`
with a neuron type other than `.Direct`,
Nengo will create a decoded connection.
When the ``pre`` object is anything else,
Nengo will create a direct connection.

The ``post`` object
is only used to determine
which signal will receive the data
produced by the connection.
If you're not sure what your connection
is doing, interrogate the ``pre`` object first.

Decoded connections
===================

Decoded connections are any connection
**from an ensemble to any other object**.
The following are all examples of decoded connections:

.. testcode::

   with nengo.Network() as net:
       ens1 = nengo.Ensemble(10, dimensions=2)
       node = nengo.Node(size_in=1)
       ens2 = nengo.Ensemble(4, dimensions=2)

       # Ensemble to ensemble
       nengo.Connection(ens1, ens2)
       # Ensemble slice to node
       nengo.Connection(ens1[0], node)
       # Ensemble to neurons slice
       nengo.Connection(ens1, ens2.neurons[:2])

The important thing about decoded connections
is that they do not directly compute the
``function`` defined for that connection
(keeping in mind that passing in no function
is equivalent to passing in the identity function).
Instead, the function is approximated
by solving for a set of decoding weights.
The output of a decoded connection
is the sum of the pre ensemble's neural activity
weighted by the decoding weights
solved for in the build process.

Mathematically, you can think of a decoded connection
as implementing the following equation:

.. math:: \mathbf{y}(t) = \sum_{i=0}^n \mathbf{d}^{f}_i a_i(x(t))

where

- :math:`\mathbf{y}(t)` is the output of the connection at time :math:`t`,
- :math:`n` is the number of neurons in the pre ensemble
- :math:`\mathbf{d}^{f}_i` is the decoding weight associated
  with neuron :math:`i` given the function :math:`f`,
- :math:`a_i(x(t))` is the activity of neuron :math:`i` given
  :math:`x(t)`, the input at time :math:`t`.

Note that the length of the :math:`\mathbf{d}` and :math:`\mathbf{y}` vectors
is the same, and is specified by the dimensionality of
the output of the function :math:`f` when applied to input :math:`x`.

While the equation above is straightforward,
there are several important implications
that one should keep in mind when using decoded connections.

- Decoders will be automatically solved for in the build process.

  Solving for decoders makes up the majority of build time,
  so if building your networks takes a long time,
  look at your decoded connections and
  try lowering the number of neurons
  or using different `.Solver` types.

- The function passed to the connection
  is used to determine decoders.
  It will never be run during the simulation.

  When you define a function in a node,
  it will be execute on every simulation timestep.
  That may lead you to think that the function
  passed to a connection is executed on every timestep,
  but that is *not* the case for decoded connections.
  The function passed to the connection will be executed
  in the decoder solving process determine an error
  to minimize, but never during the simulation.

- The characteristics of the ``pre`` ensemble
  are critically important to performance.

  If you determine that your decoded connection
  is not approximating the desired function well,
  examine the ``pre`` ensemble.
  The decoded value depends on the activity
  of the ``pre`` ensemble;
  does it represent its input reliably?
  If not, then a function of that input
  cannot be well approximated.
  If you think that your function may be incorrect,
  switch the ``pre`` ensemble to use
  the `.Direct` neuron type,
  which does not use decoders.
  If that function looks correct,
  move on to a simpler neuron type
  like `.RectifiedLinear` until you
  can determine why your function is not
  being approximated well.

  Concrete examples of how the properties of ``pre`` ensemble influence the
  desired function can be found in [1]_, [2]_.

Direct connections
==================

Any connection that is not a decoded connection
is a direct connection.

For simplicity and consistency,
Nengo exposes the same interface
for decoded and direct connections.
In all cases, data from the ``pre`` object
is sent to the ``post`` object,
with an optional ``synapse`` filter.
In decoded connections,
weights are automatically determined
through decoder solving.
In direct connections,
weights can be manually specified
through the ``transform`` argument. [3]_

The most common example of a direct connection
is a neuron-to-neuron connection.
These connections are the types of connections
you see in most neural simulators,
and can be used to reproduce networks
written in other simulators like
`Brian <http://briansimulator.org/>`_:

.. testcode::

   with nengo.Network() as net:
       ens1 = nengo.Ensemble(10, dimensions=1)
       ens2 = nengo.Ensemble(20, dimensions=2)

       # Neuron to neuron
       weights = np.random.normal(size=(ens2.n_neurons, ens1.n_neurons))
       nengo.Connection(ens1.neurons, ens2.neurons, transform=weights)

Note that it does not matter that the dimensionality of ``ens1``
does not match the dimensionality of ``ens2``.
It only matters that the ``transform``
is of the correct shape,
which in the case of neuron-to-neuron connections
is ``(post.n_neurons, pre.n_neurons)``.

In the vast majority of cases,
the above description is all you need to know.
Below we give some additional examples,
focusing on situations that differ from the description above.

Nodes and `.Direct` ensembles
-----------------------------

In connections from nodes and ensembles
using the `.Direct` neuron type,
the ``function`` argument is valid
and will result in the function being applied
to the input on every timestep.
This is in direct contrast to decoded connections,
in which the function is executed
during the build process and *not* during the simulation.

Examples:

.. testcode::

   with nengo.Network() as net:
       node = nengo.Node(output=[1])
       ens1 = nengo.Ensemble(1, dimensions=2, neuron_type=nengo.Direct())
       ens2 = nengo.Ensemble(10, dimensions=1)

       # Node to LIF ensemble
       nengo.Connection(node, ens2, function=lambda x: x**2)
       # Direct ensemble to LIF ensemble
       nengo.Connection(ens1, ens2, function=lambda x: x[0] * x[1])

Passthrough nodes
-----------------

When creating large networks,
it is often helpful to use passthrough nodes
to route signals from place to place
without introducing unnecessary ensembles.
For example, the `.EnsembleArray` network
is often used to represent a high-dimensional vector
with many lower-dimensional ensemble.
The high-dimensional vector is still available
as ``EnsembleArray.output`` through the use
of a passthrough node that collects the output
of all the lower-dimensional ensembles.

Unlike other types of nodes,
we explicitly disable the ``function`` argument
when connecting from passthrough nodes.
The reason for this is to ensure that users know
they are making a direct connection
and not a decoded connection.
The output of a network like `.EnsembleArray`
can usually be treated the same way
as the output of an `.Ensemble`,
except for the case of applying a function
to the output,
since decoders are not used to approximate
the function in the case of networks
using passthrough nodes.

As an example,
consider using an `.EnsembleArray` to compute a product:

.. testcode::

   with nengo.Network() as net:
       ea = nengo.networks.EnsembleArray(40, 2)
       product = nengo.Ensemble(30, dimensions=1)

       # Passthrough node to ensemble -- raises error
       nengo.Connection(ea.output, product, function=lambda x: x[0] * x[1])

.. testoutput::
   :hide:

   Traceback (most recent call last):
   ...
   nengo.exceptions.ValidationError: Connection.function: Cannot apply functions \
   to passthrough nodes

If this example did not raise an error,
the product would be computed nearly perfectly,
despite the fact that that computation
is impossible to decode from the ensembles
of the ensemble array.
Consider that the product
requires information from both dimensions of the signal
(i.e., the dimensions interact nonlinearly).
In order for nonlinearities to be decoded,
some neurons must encode information from
the nonlinearly-interacting dimensions.
Since the ensemble array represents each dimension independently,
no neurons will encode information from multiple dimensions,
and therefore the product cannot be approximated
by the ensemble array.

If you are aware that the function
will not be approximated but directly computed,
and you desire this behavior,
you can enable it by modifying the node so that it is
no longer a passthrough node,
but instead computes the identity function:

.. testcode::

   with nengo.Network() as net:
       ea = nengo.networks.EnsembleArray(40, 2)
       product = nengo.Ensemble(30, dimensions=1)

       # Make the node non-passthrough
       ea.output.output = lambda t, x: x
       # Node to ensemble -- no error
       nengo.Connection(ea.output, product, function=lambda x: x[0] * x[1])

If you're designing networks
that may have arbitrary function
applied to the output,
you should implement a way to make
decoded connections from the ensembles
in your network.
See the `.EnsembleArray.add_output` method
for an example of how that might be implemented.

Neuron-to-ensemble connections
------------------------------

As noted above,
a decoded connection is implemented by
solving for a set of decoding weights
and then weighting a sum of activities by those decoders.
If you already know the decoding weights
you want to use on a connection,
then you can skip the decoder solving step
by using a direct connection
from the neurons of an ensemble to another object.

In the example below,
we make two equivalent connections,
one using a decoded connection
and one using a direct connection:

.. testcode::

   with nengo.Network() as net:
       ens1 = nengo.Ensemble(20, dimensions=1, seed=0)
       ens2 = nengo.Ensemble(15, dimensions=1)

       # Decoded ensemble to ensemble connection
       conn1 = nengo.Connection(ens1, ens2, function=lambda x: x + 0.5)

   with nengo.Simulator(net) as sim:
       decoders = sim.data[conn1].weights

   with net:
       # Direct neurons to ensemble connection
       conn2 = nengo.Connection(ens1.neurons, ens2, transform=decoders)

.. testoutput::
   :hide:

   ...

In the above example, the shape of ``decoders`` is ``(1, 20)``.
If you run this example and probe the output of ``conn1``
and ``conn2``, you will see that their output is the same
(as long as a seed is set on ``ens1``):

.. testcode::

   with net:
       probe1 = nengo.Probe(conn1, "output", synapse=0.01)
       probe2 = nengo.Probe(conn2, "output", synapse=0.01)

   with nengo.Simulator(net) as sim:
       sim.run(0.1)

   assert np.allclose(sim.data[probe1], sim.data[probe2])

.. testoutput::
   :hide:

   ...

Both ``conn1`` and ``conn2`` can have learning rules applied,
so this type of direct connection can be useful
when saving the weights in a learning network
and loading it up in the future.

.. [1] Gosmann, Jan. Precise multiplications with the NEF.
       Waterloo, Ontario, Canada: University of Waterloo; 2015.
       Available from: https://zenodo.org/record/35680
.. [2] Gosmann, Jan, and Chris Eliasmith. “Optimizing Semantic Pointer
       Representations for Symbol-Like Processing in Spiking Neural Networks.”
       PLoS ONE 11, no. 2 (February 22, 2016): e0149928.
       `doi:10.1371/journal.pone.0149928
       <https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0149928>`_.
.. [3] Note that decoded connections
       also accept the ``transform`` argument.
       In the case of decoded connections,
       the ``transform`` is a linear operation
       that is applied after the function
       is applied to the input.
       In most cases, slicing the input
       or including the transform
       in the function is recommended.
