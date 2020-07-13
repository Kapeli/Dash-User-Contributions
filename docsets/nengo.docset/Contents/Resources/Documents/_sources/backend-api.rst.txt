*****************
Nengo backend API
*****************

Nengo is designed so that models created with the
:doc:`Nengo frontend API <frontend-api>`
work on a variety of different simulators, or "backends."
For example, backends have been created to take advantage of
`GPUs <https://github.com/nengo/nengo-ocl/>`_ and
`neuromorphic hardware <https://github.com/project-rig/nengo_spinnaker>`_.

Reference backend
=================

.. autosummary::
   :nosignatures:

   nengo.Simulator
   nengo.simulator.SimulationData

.. autoclass:: nengo.Simulator

.. autoclass:: nengo.simulator.SimulationData

The build process
=================

The build process translates a Nengo model
to a set of data buffers (`.Signal` instances)
and computational operations (`.Operator` instances)
which implement the Nengo model
defined with the :doc:`frontend API <frontend-api>`.
The build process is central to
how the reference simulator works,
and details how Nengo can be extended to include
new neuron types, learning rules, and other components.

`Bekolay et al., 2014
<http://compneuro.uwaterloo.ca/publications/bekolay2014.html>`_
provides a high-level description
of the build process.
For lower-level details
and reference documentation, read on.

.. autosummary::
   :nosignatures:

   nengo.builder.Model
   nengo.builder.Builder

.. autoclass:: nengo.builder.Model

.. autoclass:: nengo.builder.Builder

Basic operators
---------------

.. automodule:: nengo.builder.operator

   .. autoautosummary:: nengo.builder.operator
      :nosignatures:

Signals
-------

.. automodule:: nengo.builder.signal

   .. autoautosummary:: nengo.builder.signal
      :nosignatures:

Network builder
---------------

.. automodule:: nengo.builder.network
   :exclude-members: nullcontext

   .. autoautosummary:: nengo.builder.network
      :nosignatures:
      :exclude-members: nullcontext

Connection builder
------------------

.. automodule:: nengo.builder.connection

   .. autoautosummary:: nengo.builder.connection
      :nosignatures:

Ensemble builder
----------------

.. automodule:: nengo.builder.ensemble

   .. autoautosummary:: nengo.builder.ensemble
      :nosignatures:

Learning rule builders
----------------------

.. automodule:: nengo.builder.learning_rules

   .. autoautosummary:: nengo.builder.learning_rules
      :nosignatures:

Neuron builders
---------------

.. automodule:: nengo.builder.neurons

   .. autoautosummary:: nengo.builder.neurons
      :nosignatures:

Node builder
------------

.. automodule:: nengo.builder.node

   .. autoautosummary:: nengo.builder.node
      :nosignatures:

Probe builder
-------------

.. automodule:: nengo.builder.probe

   .. autoautosummary:: nengo.builder.probe
      :nosignatures:

Process builder
---------------

.. automodule:: nengo.builder.processes

   .. autoautosummary:: nengo.builder.processes
      :nosignatures:

Transform builders
------------------

.. automodule:: nengo.builder.transforms

   .. autoautosummary:: nengo.builder.transforms
      :nosignatures:

Decoder cache
-------------

.. automodule:: nengo.cache

   .. autoautosummary:: nengo.cache
      :nosignatures:

Optimizer
---------

.. automodule:: nengo.builder.optimizer

   .. autoautosummary:: nengo.builder.optimizer
      :nosignatures:

Exceptions
==========

.. automodule:: nengo.exceptions

   .. autoautosummary:: nengo.exceptions
      :nosignatures:
