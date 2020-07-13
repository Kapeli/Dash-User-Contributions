*************
Nengo history
*************

Some form of Nengo has existed since 2003.
From then until now,
students and researchers have used Nengo to create models
which help us understand the brain.
Nengo has evolved with that understanding.

We're currently in what could be called the fifth generation
of Nengo development. Many of the design decisions of this generation
are a result of lessons learnt from the first four generations.

**Summary**

Generation 1: NESim (Matlab) -> Nemo (Matlab)

Generation 2: NEO (Java) -> Nengo (Java) -> Nengo GUI (Piccolo2D)

Generation 3: Nengo scripting layer (Jython) -> Nengo Theano backend (Python)

Generation 4: Nengo AP -> Nengo reference implementation (Python, Jython, Theano, PyNN)

Generation 5: Nengo 2.0

Generation 1
============

When Chris Eliasmith and Charles H. Anderson released the book
Neural Engineering [Eliasmith2003]_,
they described a framework for creating models of spiking neurons
called the Neural Engineering Framework.
With the book, they provided a set of Matlab scripts
to facilitate the use of these methods in theoretical neuroscience research.

NESim (Neural Engineering Simulator) was that set of Matlab scripts,
along with a basic graphical user interface that allowed users
to set the parameters of simulations.
Its primary developers were Chris Eliasmith and Bryan Tripp.

NESim offered fast simulations by leveraging the computational power
of Matlab. And while the GUI may not have been pretty,
it enabled researchers to quickly test out ideas before
making a full model. The use of Matlab also meant that researchers could
do their simulation and analysis in the same Nemo.

However, there were some downsides to NESim. It was difficult
to communicate with other simulation environments.
The GUI, while functional, was not very eye-catching or dynamic.
The object model of Matlab is limited.
And, even though NESim is open source software,
Matlab itself is not, meaning that NESim
was not accessible to everyone.

.. [Eliasmith2003] Eliasmith, Chris, and Charles H. Anderson. Neural engineering:
   Computation, representation, and dynamics in neurobiological systems.
   MIT Press, 2003.

Generation 2
============

The desire for a more robust object hierarchy
and to interact with other simulation environments
resulted in the creation of NEO (Neural Engineering Objects)
in 2007 by Bryan Tripp. NEO was later renamed to Nengo,
also a short form of Neural Engineering Objects.

Nengo was created in Java, which encourages the use
of deeply nested object hierarchies.
This hierarchy of objects allowed Nengo to be flexible;
it could implement the same types of simulations as
NESim did, but it could also have those simulated objects
communicate with other types of objects.
Also, despite a common misconception about the speed of Java,
simulations in Nengo maintained the speed of the Matlab NESim.
Java, like Matlab, is multi-platform, meaning it would work
on any modern operating system, but unlike Matlab,
is available at no cost to the end user.
Java is common enough that, for most, installing Nengo
is quite easy.

Nengo was a robust neural simulator, but required modelers
to be proficient in Java. To overcome this,
in the summer of 2008, a graphical user interface
was created to make model creation and simulation
easy for anyone.

Check out `a demo video of this interface <https://www.youtube.com/watch?v=q4jxI26gUtA>`_.

The GUI leveraged the Java graphical toolkit Piccolo2D.java,
which makes it easy to make zoomable interfaces that
can play well with the Java Swing ecosystem.
The new GUI made it easy for beginners to become familiar
with the methods of the NEF, and gradually transition
to writing models outside of the GUI.

While Nengo and its GUI introduced many people
to the NEF, its deeply nested object hierarchy
proved difficult for many people to use productively.
While the GUI provided easy access for beginners,
the transition to being an expert user was difficult.
Additionally, while Java is cross platform and free to download,
it is not open source (though an open source version exists).
And while Java can simulate many networks quickly,
efforts to leverage non-standard computing devices
like GPUs were difficult to implement
in a cross-platform manner.

While new versions of Nengo followed,
this version remains in use to this day.
`nengo.ca <http://www.nengo.ca/>`_
contains documentation for this version,
now referred to as Nengo 1.4.

Generation 3
============

Shortly after the GUI was released,
Terry Stewart began making it possible
to make simulations using Nengo
through a simple Python scripting interface.
The interface was originally known as ``nef.py``
due to the first implementation's file name,
but it quickly became the preferred way
for modelers to create models due to its simplicity,
and therefore was incorporated with the rest of Nengo.
While the scripting interface used Python syntax,
it was still able to operate within the Java ecosystem
thanks for a Java implementation of Python called Jython.

Although this boost in productivity allowed for the creation of Spaun,
the simulation speed was still much to be desired. Because of that,
a project that had the same interface as the ``nef.py`` scripts,
but with an implementation that used Theano.

However, there were concerns that the Jython
and the Theano backed implementations would soon
diverge, fracturing the population of people building
nengo models.

Generation 4
============

In order to deal with the fracturing of the Nengo community,
the decision was made to standardize the API that
had been evolving since the introduction of ``nef.py``.
Because the name "Nengo" was now well known,
the name stuck, and the API was called the Nengo API.

Through a grueling weekend of meetings,
the CNRG tentatively decided on an API
that any software claiming to be "Nengo"
would have to implement. In addition to the API,
the CNRG would produce a reference implementation
in Python with as few dependencies as possible,
change the Jython version to conform to the new API,
and in Theano to continue the work making a fast backend.

Although these three implementations may choose to
implement their own specific capabilities,
since they all conform to the Nengo API,
they can all run the vast majority of models
that a modeler would want to run.

Generation 5
============

Issues with the implementation of Theano led to
a new effort to create an OpenCL-backed version of Nengo.
With so many possible backends, the Nengo API
switched focus to being able to provide a consistent
front-end experience while being able to run models
on different backends. The Nengo API, and a NumPy-backed
reference simulator, matured into what we have now released as
Nengo 2.0.

Since standardizing on the scripting frontend of Nengo 2.0,
new backends have begun development, for the BlueGene, Neurogrid,
SpiNNaker and other hardware.

We hope that, in this generation,
we have made all the right compromises such that
we can build large models with concise, expressive code,
and that we can create backends that can build and simulate
those models much more quickly than before.
Further, by making this API available,
we hope to be able to interact even further with
the rest of the neuroscience packages written in Python.
