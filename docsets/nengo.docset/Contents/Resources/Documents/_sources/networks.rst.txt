*****************
Reusable networks
*****************

Networks are an abstraction of a grouping of Nengo objects
(i.e., `.Node`, `.Ensemble`, `.Connection`, and `.Network` instances,
though usually not `.Probe` instances.)
Like most abstractions, this helps with code-reuse and maintainability.
You'll find the documentation
for the reusable networks included with Nengo below.

You may also want to build your own reusable networks.
Doing so can help encapsulate parts of your model,
making your code easier to understand,
easier to re-use, and easier to share.
The following examples will
help you build your own reusable networks:

.. toctree::

   examples/usage/network-design
   examples/usage/network-design-advanced

You may also find the :doc:`config system documentation <config>` useful.

Built-in networks
=================

.. Note: we don't use autoautosummary here because we want the canonical
   reference to these objects to be ``nengo.networks.Class`` even though they
   actually live in ``nengo.networks.module.Class``.

.. autosummary::
   :nosignatures:

   nengo.networks.EnsembleArray
   nengo.networks.BasalGanglia
   nengo.networks.Thalamus
   nengo.networks.AssociativeMemory
   nengo.networks.CircularConvolution
   nengo.networks.Integrator
   nengo.networks.Oscillator
   nengo.networks.Product
   nengo.networks.InputGatedMemory

.. autoclass:: nengo.networks.EnsembleArray

.. autoclass:: nengo.networks.BasalGanglia

.. autoclass:: nengo.networks.Thalamus

.. autoclass:: nengo.networks.AssociativeMemory

.. autoclass:: nengo.networks.CircularConvolution

.. autoclass:: nengo.networks.Integrator

.. autoclass:: nengo.networks.Oscillator

.. autoclass:: nengo.networks.Product

.. autoclass:: nengo.networks.InputGatedMemory
