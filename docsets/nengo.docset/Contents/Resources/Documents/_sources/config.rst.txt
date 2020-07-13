*******************************
Setting parameters with Configs
*******************************

Building models with the :doc:`Nengo frontend API <frontend-api>`
involves constructing many objects,
each with many parameters that can be set.
To make setting all of these parameters easier,
Nengo has a ``config`` system and
pre-set configurations.

The ``config`` system
=====================

Nengo's ``config`` system is used for two important functions:

1. Setting default parameters with a hierarchy of defaults.
2. Associating new information with Nengo classes and objects
   without modifying the classes and objects themselves.

A tutorial-style introduction to the ``config`` system
can be found below:

.. toctree::

   examples/usage/config

``config`` system API
---------------------

.. automodule:: nengo.config

    .. autoautosummary:: nengo.config
       :nosignatures:

Preset configs
==============

Nengo includes preset configurations that can be
dropped into your model to enable specific neural circuits.

.. automodule:: nengo.presets

   .. autoautosummary:: nengo.presets
      :nosignatures:

Quirks
======

.. toctree::

   examples/quirks/config

Parameters
==========

Under the hood, Nengo objects store information
using `.Parameter` instances,
which are also used by the config system.
Most users will not need to know about
`.Parameter` objects.

.. automodule:: nengo.params

   .. autoautosummary:: nengo.params
      :nosignatures:

      nengo.dists.DistributionParam
      nengo.dists.DistOrArrayParam
      nengo.learning_rules.LearningRuleTypeParam
      nengo.learning_rules.LearningRuleTypeSizeInParam
      nengo.neurons.NeuronTypeParam
      nengo.processes.PiecewiseDataParam
      nengo.solvers.SolverParam
      nengo.synapses.SynapseParam
      nengo.transforms.ChannelShapeParam
      nengo.transforms.SparseInitParam
