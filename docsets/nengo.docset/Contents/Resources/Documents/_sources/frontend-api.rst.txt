******************
Nengo frontend API
******************

Nengo Objects
=============

.. autosummary::
   :nosignatures:

   nengo.Network
   nengo.Ensemble
   nengo.ensemble.Neurons
   nengo.Node
   nengo.Connection
   nengo.connection.LearningRule
   nengo.Probe

.. autoclass:: nengo.Network

.. autoclass:: nengo.Ensemble

.. autoclass:: nengo.ensemble.Neurons

.. autoclass:: nengo.Node

.. autoclass:: nengo.Connection

.. autoclass:: nengo.connection.LearningRule

.. autoclass:: nengo.Probe

Distributions
=============

.. automodule:: nengo.dists

   .. autoautosummary:: nengo.dists
      :nosignatures:
      :exclude-members: DistributionParam, DistOrArrayParam

Learning rule types
===================

.. automodule:: nengo.learning_rules

   .. autoautosummary:: nengo.learning_rules
      :nosignatures:
      :exclude-members: LearningRuleTypeParam, LearningRuleTypeSizeInParam

Neuron types
============

.. automodule:: nengo.neurons

   .. autoautosummary:: nengo.neurons
      :nosignatures:
      :exclude-members: NeuronTypeParam

Processes
=========

.. automodule:: nengo.processes

   .. autoautosummary:: nengo.processes
      :nosignatures:
      :exclude-members: PiecewiseDataParam

      nengo.Process

.. autoclass:: nengo.Process

Solvers
=======

.. automodule:: nengo.solvers

   .. autoautosummary:: nengo.solvers
      :nosignatures:
      :exclude-members: SolverParam

Solver methods
--------------

.. automodule:: nengo.utils.least_squares_solvers

   .. autoautosummary:: nengo.utils.least_squares_solvers
      :nosignatures:

Synapse models
==============

.. automodule:: nengo.synapses

   .. autoautosummary:: nengo.synapses
      :nosignatures:
      :exclude-members: SynapseParam

Transforms
==========

.. automodule:: nengo.transforms

   .. autoautosummary:: nengo.transforms
      :nosignatures:
      :exclude-members: SparseInitParam, ChannelShapeParam
