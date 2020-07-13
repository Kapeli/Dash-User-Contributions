*****
Nengo
*****

Nengo is a Python library for building and simulating
large-scale neural models.
Nengo can create sophisticated
spiking and non-spiking neural simulations
with sensible defaults in a few lines of code:

.. testcode::

   import nengo
   import numpy as np
   import matplotlib.pyplot as plt

   with nengo.Network() as net:
       sin_input = nengo.Node(output=np.sin)
       # A population of 100 neurons representing a sine wave
       sin_ens = nengo.Ensemble(n_neurons=100, dimensions=1)
       nengo.Connection(sin_input, sin_ens)
       # A population of 100 neurons representing the square of the sine wave
       sin_squared = nengo.Ensemble(n_neurons=100, dimensions=1)
       nengo.Connection(sin_ens, sin_squared, function=np.square)
       # View the decoded output of sin_squared
       squared_probe = nengo.Probe(sin_squared, synapse=0.01)

   with nengo.Simulator(net) as sim:
       sim.run(5.0)
   plt.plot(sim.trange(), sim.data[squared_probe])

.. testoutput::
   :hide:

   ...

Yet, Nengo is highly extensible and flexible.
You can define your own neuron types and learning rules,
get input directly from hardware,
build and run deep neural networks,
drive robots, and even simulate your model
on a completely different neural simulator
or neuromorphic hardware.

.. toctree::
   :maxdepth: 2

   getting-started
   user-guide
   examples
   contributing
   project

* :ref:`genindex`
