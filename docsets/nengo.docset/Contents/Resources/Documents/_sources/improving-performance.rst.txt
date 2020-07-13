*********************
Improving performance
*********************

Once you start creating larger models, Nengo might become a little bit slow.
This section walks you through different things that might help you to get the
best performance out of Nengo.

In a nutshell
=============

To improve build time
---------------------

1. Set a seed on the top level model to enable decoder caching:

.. testcode::

   net = nengo.Network(seed=1)

2. Disable the operator graph optimizer:

.. testcode::

   with nengo.Simulator(net, optimize=False) as sim:
       ...

.. testoutput::
   :hide:

   ...

3. Reduce the number of neurons in very large ensembles, or consider using the
   `.RandomizedSVD` solver.

To improve run time
-------------------

1. Enable the operator graph optimizer
   (and install `SciPy <https://www.scipy.org/scipylib/download.html>`_):

.. testcode::

   with nengo.Simulator(net, optimize=True) as sim:
       ...

.. testoutput::
   :hide:

   ...

2. Consider switching to the `nengo_ocl <https://github.com/nengo/nengo-ocl>`_
   backend if you have a powerful GPU.

To lower peak memory consumption
--------------------------------

1. Disable the operator graph optimizer:

.. testcode::

   with nengo.Simulator(net, optimize=False) as sim:
       ...

.. testoutput::
   :hide:

   ...

2. Reduce the number of neurons in very large ensembles.
   Consider replacing them with
   multiple smaller ensembles (`.EnsembleArray` is useful for that).

3. Reduce the number of probes or their sampling intervals
   (with the ``sample_every`` argument).

Build and run time performance
==============================

The two main determiners of how long your model takes to run are the
build time and the run time. Build time is the time required to
translate the model description into the actual neural network that gets
simulated. A build happens when you create the simulator with
``nengo.Simulator(net)``. Run time is how long it takes to simulate this
network for the desired amount of simulation time. A run happens when you
call ``sim.run``.

Some of the techniques described below
will influence one of these variables, while others will
reduce one variable at the cost of increasing another.
While the run time is usually the most important variable,
sometimes the memory consumption can be the main problem.

Getting the best performance for your model depends on your model
and your computing environment.

Decoder caching
===============

*Influences build time.*

A significant amount of build time is spent on finding the NEF
decoders. Because of that, it is possible to cache the decoders. The first
build of a model will still take about the same time (technically a bit longer
because the computed decoders will be stored), but all subsequent builds of the
same model can load the stored decoders and will be faster.

To enable the decoder caching, set a seed on the network like so:

.. testcode::

   with nengo.Network(seed=1) as net:
       ...

There are :doc:`a few configuration options <nengorc>` for more
advanced control of the cache. The most important might be the possibility to
control the path where the cache files are stored. On high performance
clusters, certain file systems might provide better performance.

Operator graph optimizer
========================

*Influences build time, run time, and memory consumption.*

By default, Nengo optimizes its internal data structures
(the "operator graph") to access memory in a linear manner.
However, this can increase build time significantly
and in some cases it can be better to turn this
optimization off to speed up the build at the cost of slowing the run.
To turn the optimizer off,
set the simulator's ``optimize`` argument to ``False``:

.. testcode::

   with nengo.Simulator(net, optimize=False) as sim:
       ...

.. testoutput::
   :hide:

   ...

Another situation where it is helpful to disable the optimizer is when the peak
memory usage is too high. The optimizer can use up to three times as much
memory as would be required without the optimizer. Note that limiting the
number of optimization passes does not noticeably reduce memory consumption.

SciPy
=====

*Influences run time.*

To gain the maximum performance gain from the operator graph optimizer,
install `SciPy <https://www.scipy.org/scipylib/download.html>`_.
When the operator graph optimizer is deactivated,
installing SciPy has no effect on performance.

nengo_ocl
=========

*Improves run time.*

If you have a powerful GPU, you have the option to switch to the `nengo_ocl
<https://github.com/nengo/nengo-ocl>`_ backend. It will utilize your GPU,
which is optimized for the sorts of calculations done by Nengo.
Build times with ``nengo_ocl`` are usually comparable to Nengo,
but run times can be significantly faster.

Model structure
===============

*Influences build time, run time, and memory consumption.*

Some aspects of the model structure, apart from the size of the model,
influence performance. Ensembles with many neurons will take a long
time to build and consume a lot of memory. Sometimes it is
feasible to split large ensembles into multiple smaller ensembles (the
`.EnsembleArray` is helpful for that). Alternatively, using the
`.RandomizedSVD` decoder solver can reduce the build time.

However, be aware that many small ensembles will take longer to simulate if the
operator graph optimizer is deactivated.

Limiting probed data
====================

*Influences memory consumption.*

All data that gets probed in the model has to be stored in memory.
Depending on how long the simulation runs and how many things are probed,
this might consume a significant amount of memory. By reducing the number
of probed objects, the memory consumption can be reduced. An alternative
is to not record a value for every time step. Probes accept a
``sample_every=`` argument to reduce the number of recorded samples.

Note that in most cases,
probing data does not noticeably affect run time.
